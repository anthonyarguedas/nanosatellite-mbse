# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Extraction

## Extraction design

Extraction is report-level by default. Create one extraction file for each included report. Use nested groups for EPS content, model representations, dynamic behavior occurrences, inputs, results, findings, and linked V&V and model assurance activities. Create another EPS case section only when a report contains materially separate models, implementations, or evaluations that cannot be represented clearly together.

Keep report-family resolution and cross-report artifact identity pending during the first report pass. Record concise family leads. Fully extract every material EPS model representation, model generation method, engineering workflow, reusable artifact, reported lineage, reuse claim, and reuse or tailoring application described by each report, including relationships among views, dynamic behavior when shown, procedural reporting detail, and report-bounded artifact, method, and workflow reuse levels. Resolve families and cross-report artifact-lineage identity after all report extractions are available, then create separate lineage-level and consolidated artifact-containing application records.

Report-level records remain fixed during the cross-report pass. That pass may update only `lineage_id` from its first-pass state to a stable resolved ID or `unresolved_after_review`. It does not backfill or overwrite any other report-level field.

Record each source fact once at its most detailed applicable location. Store representation identity, view classification, and content links in model representation records. Store ordered EPS behavior shown by a representation in its behavior occurrences. Store method definitions and steps in model generation methods. Store workflow definitions and activities in workflow records. Store actual workflow execution and deviations in implementation records. Store measurements, criteria and verdicts, comparators and rival explanations in the result set that reports them. Store implementation effort and burdens in implementation records. Store reuse and tailoring evidence in report-level applications. Give each nested row a stable ID, then link later findings, activities, reuse assessments, and consolidated records to those IDs instead of copying the content. Do not create separate top-level analytic objects for individual measurements, comparators, rival explanations, appraisal domains, or claim-support judgments.

### Common field rules

Create a codebook and machine-readable schema from this protocol before full extraction. The canonical property names, types, cardinalities, and evidence-status encoding are defined in the [report schema](protocol-extraction.schema.json), [family schema](protocol-extraction-family.schema.json), [lineage schema](protocol-extraction-lineage.schema.json), [consolidated tailoring-application schema](protocol-extraction-tailoring-application.schema.json), and [audit schema](protocol-extraction-audit.schema.json).

Start each record from its [report template](protocol-extraction.template.json), [family template](protocol-extraction-family.template.json), [lineage template](protocol-extraction-lineage.template.json), [consolidated tailoring-application template](protocol-extraction-tailoring-application.template.json), or [audit template](protocol-extraction-audit.template.json). Each template includes one illustrative row for every repeatable structure required to show the complete record shape. Replace every angle bracket placeholder and review every illustrative controlled value. Add, remove, or replace repeatable rows as the evidence requires. Use an allowed evidence-status object in place of an array only when the schema permits it. The audit template targets a report. Replace `report_id` with `lineage_id` for a lineage audit.

Every report, repeatable coded record, and nested coded row must have a stable ID. Each stable ID is unique within its ID type across the review. Citation IDs are also review-wide unique as stated below.

Each report extraction contains a `citations` table. Each citation row records:

- `citation_id`, unique across the review.
- `report_id`.
- `page`, using the one-based physical page in the stored source file.
- `quote`, copied verbatim from that page.
- optional `graphic`, identifying a figure, table, diagram, or other graphic containing the quote.
- optional `graphic_quote_description`, briefly describing where the quote appears in the graphic and how it supports the coding.

A citation containing `graphic` or `graphic_quote_description` is excluded from deterministic quote matching. The human auditor verifies its quote, graphic reference, and description against the cited page. For deterministic matching, normalize the quote and frozen page text to Unicode NFC, remove soft hyphens, collapse line endings and other whitespace to single spaces, and preserve case, punctuation, and visible hyphens. Split stored page text on `<!-- PDF_PAGE: n -->` markers. Store each citation once and reuse its ID. Split a quotation that crosses pages into one citation per page. Every source-backed field or compact group of fields records the applicable `citation_ids`. Each repeatable coded record and nested coded row also records:

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

### Linked normalization records

Report records use `schema_version = slr1-extraction/v4`. Lineage and consolidated application records use their corresponding version 3 constants. A record without its applicable current marker is a legacy record. Migrate it through source review before synthesis. Do not infer normalized links or typed values automatically from legacy prose.

Version 4 replaces composite or aggregate classifications with explicit arrays and scoped records. It pluralizes workflow scopes, exchange and dependency types, burden phases, evaluation design components, artifact types, variation-point targets, application objects, finding roles, and RQ2 and RQ3 lifecycle stages. It moves abstraction, decomposition visibility, and fidelity to representation records. It replaces artifact generality with scoped rows, aggregate automation with derived arrays, and aggregate direction codes with scoped direction-component rows. Revisit the source before migrating any legacy `multiple`, `mixed`, `both`, `cross_lifecycle`, `end_to_end_engineering`, combination application-object, or `mixed_methods` value.

From report context onward, every ordinary free text field preserves source wording and links its analytic meaning to stable records. An evidenced scalar keeps its source text in `value` and supplies `linked_record_refs`. A source text item inside a coded row or array supplies `source_text` and `linked_record_refs`. Each reference uses `record_kind:stable_id`, for example `quantity:quantity-004` or `eps_element:eps-element-012`. Use `normalization_status = not_for_synthesis` instead of links only for verbatim wording or a source label that will never be compared directly. Controlled values, stable IDs, paths, and evidence statuses keep their existing shapes.

Create each normalized fact once in `reference_catalog`, then link every use to it. The catalog contains:

- `entities` for missions, platforms, organizations, teams, people, roles, skills, modeling languages, concerns, problems, purposes, orbits, environment conditions, modes, scenarios, configurations, data sources, constructs, exchanged items, interfaces, procedure actions, methods, physical or operational items, artifact content, and study groups or arms. Each entity has a stable ID, controlled type, source name, review-wide canonical key, version when applicable, and parent IDs.
- `quantities` for physical values, mass, dimensions, orbit parameters, environment values, inputs, outputs, thresholds, counts, effort, duration, schedule, cost, statistics, sample size, uncertainty, margin, sensitivity, and degradation. Store the raw source value, typed numeric value or bounds, canonical unit, value basis, time basis, denominator, currency, and price year separately.
- `decisions` with a stable ID, decision type, lifecycle stages, status, alternatives, selected objects, and rationale.
- `relationships` with typed source and target references. Use them for tool and data flows, concern relationships, boundaries, procedure control flow, derivation traces, physical links, differences, mechanisms, and before-and-after traces.
- `rules` for entry, completion, decision, selection, inclusion, exclusion, normalization, abstraction, constraints, branching, iteration, unchanged use, tailoring, acceptance, quality, and missing-data handling.
- `checks` for quality, completeness, correctness, completion, acceptance, verification, validation, assurance, genericity, and model-to-test closure. Link each check to its target, criterion, and result. Use the RQ3 model assessment dimensions for comparable model and digital twin assurance classifications.
- `resources` for repositories, model files, datasets, standards, publications, scripts, procedures, documentation, infrastructure, and licences. Store location and availability once.
- `issues` for missing data, failures, exclusions, uncertainty, sensitivity, discrepancies, conflicts, limitations, future work, rival explanations, rework, and missing information. Link each issue to the affected records and its handling or resolution.

Use quantity `value_form` codes `number`, `interval`, `distribution`, `categorical`, `boolean`, `text`, or `unclear`. Use `value_basis` codes `nominal`, `worst_case`, `minimum`, `maximum`, `range`, `distribution`, `observed`, `expected`, `derived`, `other`, or `unclear`. Use `unit_vocabulary = UCUM` for canonical engineering units, `ISO_4217` for currencies, `count` for dimensionless counts, `source_only` when conversion would require assumptions, and `not_applicable` or `unclear` when appropriate. Preserve a source unit in `raw_source_value` when it cannot be converted without assumptions.

Use decision types `selection`, `sizing`, `trade_study`, `architecture`, `interface`, `verification_or_validation`, `risk`, `reuse_or_tailoring`, `governance`, `other`, or `unclear`. Use decision statuses `intended`, `considered`, `made`, `revised`, `deferred`, `planned`, or `unclear`.

Use relationship types `contains`, `part_of`, `uses`, `produces`, `consumes`, `provides`, `depends_on`, `precedes`, `branches_to`, `iterates_to`, `reworks`, `maps_to`, `traces_to`, `derives_from`, `transforms_to`, `refines`, `satisfies`, `verifies`, `validates`, `compares_with`, `differs_from`, `causes`, `contributes_to`, `supports`, `limits`, `inside_boundary`, `outside_boundary`, `same_as`, `version_of`, `tailors`, `other`, or `unclear`.

A linked source text field preserves evidence. Its catalog record holds the analytic value. Store each normalized value once and link every use to that record. Reuse a canonical key for equivalent concepts while keeping each source mention in its report record. Cross-report records reuse report-level catalog IDs and preserve contributing-report provenance. They do not create duplicate catalog entries.

## Report-level extraction fields

### Identity, eligibility, and review management

Record:

- `report_id`.
- `screening_record_id`.
- possible companion reports or shared implementations, derived as the union of possible related reports or artifacts in the report-level reuse records.
- `family_lead`, using `yes`, `no`, or `uncertain`.
- concise report-family lead reason, or `not_reported`.
- source-file path.

Read title, authors, year, full publication date, venue or issuing organization, DOI, arXiv metadata, other stable URLs, publication type, and publication status through `screening_record_id`. For a thesis or dissertation, also read degree level and completion status through that link. Do not copy these values into the extraction.

Use `family_lead` as follows:

- **`yes`:** at least one candidate companion report or shared implementation was identified.
- **`no`:** no candidate lead was found during complete source review. This does not prove that no companion exists.
- **`uncertain`:** a possible relationship exists, but the candidate cannot be identified or bounded reliably.

For an arXiv preprint, retain the version and version date with its arXiv ID in the screening record.

### Report and implementation context

Record:

- mission or platform source wording, linked to mission and platform entities.
- form factor or mass source wording, linked to platform entities and typed quantity records.
- mission purpose or domain source wording, linked to purpose or domain entities.
- orbit and environment source wording, linked to orbit and environment entities and typed quantity records.
- normalized `mission_entity_ids`, `platform_entity_ids`, `purpose_or_domain_entity_ids`, `form_factor_entity_ids`, `mass_quantity_ids`, `orbit_entity_ids`, `orbit_quantity_ids`, `environment_entity_ids`, and `environment_quantity_ids`.
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
- **`other`:** another identified lifecycle stage.
- **`unclear`:** the lifecycle stage cannot be classified.

Record every applicable lifecycle stage in the array. Represent continuity across stages through workflow scope, relationship, purpose, and lifecycle links rather than a composite stage code.

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

- problem addressed plus `problem_entity_ids`.
- intended decision plus `linked_decision_ids`.
- reason for using MBSE plus `motivation_entity_ids`.
- `model_generation_methods` using the structured method records below.
- `workflows` using the structured workflow records below.
- `modeling_languages`, preserving source-reported names and versions and linking each item through `linked_modeling_language_entity_ids`.
- `tools_and_versions` as structured tool or equipment records using the rules below. Link providers through `provider_organization_entity_ids`.
- toolchain and data flow, linked through `toolchain_entity_ids` and `toolchain_relationship_ids` whose endpoints are tool, resource, artifact, or entity IDs.
- `model_artifacts` as nested rows containing `model_artifact_id`, canonical key, source name or description, version, controlled artifact kind, controlled model roles, linked tool and resource IDs, per artifact availability, and parent artifact IDs.
- modeled systems-engineering concerns plus `linked_concern_entity_ids`.
- explicit relationships among concerns plus `concern_relationship_ids`.
- system boundary source wording plus `system_boundary_relationship_ids` that identify inside and outside objects.

A `model_artifact_id` identifies a persistent model, repository, package, file, export, script, dataset, documentation set, or other engineering asset. Use `artifact_kind` for this distinction. Give each artifact a review-wide `canonical_key` and source version identifier. Link its distribution location through `linked_resource_ids`, and record availability on the artifact. Use `parent_model_artifact_ids` only for source-supported containment or version structure. An individual diagram, table, matrix, tree, or generated view is a model representation within an EPS case. Link each representation to its containing artifacts. Create a separate model artifact for a representation only when the source identifies that representation as an independently persistent asset.

Use `artifact_kind` values `persistent_model`, `repository`, `package`, `file`, `export`, `script`, `dataset`, `documentation`, `other`, or `unclear`.

Record every applicable `model_roles` value for an artifact. Use an evidence status for an artifact that has no model role or whose role is unavailable. Use the roles as follows:

- **`mbse_system_model`:** the artifact contains a structured systems model used for an MBSE purpose.
- **`analysis_or_simulation_model`:** the artifact contains an analysis or simulation model.
- **`digital_twin`:** the source identifies the artifact as a digital twin with a physical counterpart or operational data connection. Do not infer this role from a stand-alone simulation.
- **`test_or_environment_model`:** the artifact represents a test environment, plant, stimulus, oracle, or other execution environment.
- **`transformation_or_generator`:** the artifact transforms or generates persistent model content.
- **`other`:** another source-described model role applies.
- **`unclear`:** relevant evidence does not resolve the model role.

Use these availability codes for report artifacts, EPS assets, reusable artifacts, procedure materials, workflows, and resulting tailored artifacts:

- **`public_complete`:** the source identifies public access to the complete asset.
- **`public_partial`:** only extracts, documentation, or part of the asset are public.
- **`available_on_request`:** access requires a request to an author or owner.
- **`restricted`:** access is proprietary, internal, controlled, or otherwise limited.
- **`described_only`:** the asset is described without an identified distribution route.
- **`unavailable`:** the source states that it is unavailable.
- **`unclear`:** the reported access condition cannot be classified.

#### Tool and equipment records

Create one `tools_and_versions` row for each source-identifiable software tool, runtime, library, integration facility, data format, test item, equipment item, or computing platform. Record `tool_id`, source name, version, kind, roles, provider or owner, and availability. Preserve the source name and version. Use tool IDs in methods, artifacts, workflows, implementation records, inputs, evaluations, V&V activities, and tailoring records. Keep settings, automation details, licences, and infrastructure descriptions in their existing context fields. Do not repeat the tool name there.

Use `tool_kind` as follows:

- **`modeling_environment`:** an MBSE or system-model authoring environment.
- **`software_application`:** another named software application.
- **`programming_language_or_runtime`:** a programming language, interpreter, or runtime.
- **`library_plugin_or_add_on`:** a library, plug-in, extension, or add-on.
- **`integration_middleware`:** software that connects tools or services.
- **`repository_or_collaboration_platform`:** a repository, product lifecycle platform, or collaboration environment.
- **`data_format_or_schema`:** a named interchange format, schema, or serialization.
- **`test_or_measurement_equipment`:** physical equipment used to test or measure.
- **`support_hardware_or_computing_platform`:** support hardware or a computing platform. Record target EPS or spacecraft hardware as typed EPS elements and link it from the V&V activity.
- **`other`:** another source-described kind.
- **`unclear`:** the kind cannot be classified.

Use one or more `roles`: `mbse_model_authoring`, `requirements_management`, `architecture_or_design`, `simulation_or_analysis`, `model_transformation_or_generation`, `verification_or_validation`, `test_management_or_execution`, `integration_or_interoperability`, `data_exchange_or_conversion`, `configuration_or_repository`, `documentation_or_reporting`, `software_development`, `test_or_measurement_equipment`, `computing_or_execution_platform`, `other`, or `unclear`.

#### Model generation methods

A model generation method is a reported procedure used to construct, populate, configure, transform, or generate the EPS MBSE model. A modeling language or tool alone is not a generation method. Create one row for each materially distinct method. Record:

- `model_generation_method_id` and linked `eps_case_id` values.
- source method name or description.
- method purpose and scope.
- `generation_method_types`, using one or more of the codes below.
- `method_origin_types`, using one or more of `named_method_adoption`, `requirements_or_standards_synthesis`, `literature_synthesis`, `heritage_generalization`, `expert_or_stakeholder_elicitation`, `empirical_or_operational_derivation`, `metamodel_or_ontology_driven`, `manual_author_construction`, `model_transformation`, `reverse_engineering`, `other`, or `unclear`.
- `construction_sources` as nested rows containing `construction_source_id`, source type, source identification, selection or inclusion basis, contribution to the model, and linked input-group, EPS-requirement, model-artifact, and tool IDs. Use source types `requirement`, `standard`, `literature`, `heritage_model_or_mission`, `expert_or_stakeholder_input`, `test_data`, `flight_or_operational_data`, `vendor_data`, `metamodel_or_ontology`, `tool_or_library`, `other`, or `unclear`.
- linked input-group IDs, source model-artifact IDs, output model-artifact IDs, and tool IDs.
- entry conditions.
- `method_steps` as nested rows containing `method_step_id`, sequence label, predecessor step IDs, action, material inputs, outputs, linked input-group, model-artifact, and tool IDs, responsible roles, tool settings, automation, decision rules, quality or exit checks, and branching, iteration, or rework.
- overall branching and iteration.
- completion conditions.
- `generic_model_derivation`, recording the generic-model target, selection and exclusion rules, synthesis and generalization operations, abstraction and normalization rules, conflict resolution, source-to-model trace, and genericity validation. Use `not_applicable` for each field when the method does not create a generic, reference, template, product-family, or mission-class model.
- supporting-material location and availability.
- `procedure_reporting` using the common procedural-detail fields below.

Use `method_entity_ids`, `purpose_entity_ids`, and `scope_refs` for method identity and scope. Each construction source uses `source_resource_ids`, `selection_rule_ids`, and `contribution_relationship_ids`. Link entry and completion conditions through `entry_rule_ids` and `completion_rule_ids`. Within each method step, use `input_refs`, `output_refs`, `responsible_role_entity_ids`, `tool_configuration_entity_ids`, `automation_level`, `decision_rule_ids`, `quality_check_ids`, `control_flow_relationship_ids`, and `rework_issue_ids`. Derive the overall branching and iteration account from those linked step relationships. Link method-level control flow and supporting resources once.

For `generic_model_derivation`, use `target_model_artifact_ids`, `selection_and_exclusion_rule_ids`, `derivation_relationship_ids`, `abstraction_and_normalization_rule_ids`, `conflict_issue_ids`, `source_to_model_relationship_ids`, and `genericity_check_ids`. Link supporting material to a resource record. Preserve the report wording in the existing fields.

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

Use method origin types as follows:

- **`named_method_adoption`:** an existing named method supplies the construction process.
- **`requirements_or_standards_synthesis`:** requirements or standards are selected and combined to form model content or rules.
- **`literature_synthesis`:** published literature is selected and combined.
- **`heritage_generalization`:** one or more prior missions or models are generalized into reusable content.
- **`expert_or_stakeholder_elicitation`:** expert or stakeholder input materially determines the method or model content.
- **`empirical_or_operational_derivation`:** test, flight, operational, or other observed data materially determines the method or model content.
- **`metamodel_or_ontology_driven`:** a metamodel, ontology, or formal conceptual structure governs construction.
- **`manual_author_construction`:** the authors formulate the method or model directly without another reported derivation basis.
- **`model_transformation`:** transformation from another model or structured representation supplies the content.
- **`reverse_engineering`:** existing documents, data, software, or hardware are reconstructed into model content.
- **`other`:** another identified origin applies.
- **`unclear`:** the origin cannot be classified.

The method-origin codes identify how the authors obtained or formulated the method and its model content. Record every supported origin in the array. Use `uncertain` for the complete field when the source reports a mixture but does not identify its components. Preserve the source description in the construction-source rows and generic-model-derivation fields. Construction-source types identify the concrete requirement, standard, publication, heritage model or mission, person or group, dataset, metamodel or ontology, tool or library, or other source used. Use links to input groups for detailed values and assumptions instead of copying them into a construction-source row. `unclear` means that relevant source evidence cannot be classified.

#### Engineering workflows

An engineering workflow is a source-identifiable sequence or network of activities, handoffs, decisions, and checks through which EPS-linked models, data, or engineering artifacts move. A workflow can contain model generation methods. A tool list, data-flow statement, lifecycle label, or unordered set of activities alone is not a workflow.

Create one workflow row for each materially distinct workflow. Record:

- `workflow_id`, linked EPS case IDs, and the source workflow name and version.
- `workflow_scope_types`, recording every applicable value from `model_generation`, `model_tailoring`, `analysis_or_decision`, `verification_or_validation`, `lifecycle_integration`, `other`, or `unclear`.
- purpose and boundary.
- linked model-generation-method and model-artifact IDs.
- entry conditions.
- `workflow_activities` as nested rows containing `workflow_activity_id`, sequence label, predecessor activity IDs, action, inputs, outputs, linked method, artifact, and tool IDs, responsible roles, tool settings, automation, decision rules, quality or exit checks, and branching, iteration, or rework.
- overall branching and iteration, exit conditions, handoffs and data flow, roles and responsibilities, linked tool IDs, automation, and governance and configuration control.
- supporting-material location and availability.
- `procedure_reporting` using the common procedural-detail fields below.

Apply the method-step linking rules to every workflow activity. At workflow level, use `workflow_entity_ids`, `purpose_entity_ids`, `scope_refs`, entry and exit rule IDs, control-flow and handoff relationship IDs, responsible role entity IDs, `automation_levels`, governance rule IDs, and supporting resource IDs. Derive the workflow automation-level array from its activity records when activity-level coding is available. Derive workflow-level branching and handoff summaries from activity links.

Use workflow scope types as follows:

- **`model_generation`:** the workflow constructs, populates, transforms, or generates a model.
- **`model_tailoring`:** the workflow configures or adapts reusable model content.
- **`analysis_or_decision`:** the workflow uses model content for analysis, trade studies, or decisions.
- **`verification_or_validation`:** the workflow connects model content to checking, verification, or validation.
- **`lifecycle_integration`:** the workflow carries model content across lifecycle stages or engineering functions.
- **`other`:** another identified workflow scope applies.
- **`unclear`:** workflow scope cannot be classified.

Code every supported scope for a workflow that the source calls end-to-end. Preserve that phrase in the source workflow name, purpose, or boundary. Use activity order and handoff relationships to establish integration among the scopes.

#### Procedural reporting detail

Apply the same procedural reporting assessment to each model generation method, workflow, and reusable tailoring procedure. Keep this assessment separate from the M0–M4 and W0–W4 reuse levels. For each component below, store `value = reported` and `basis_refs` when evidence is present. Use an evidence status when it is absent, inapplicable, unresolved, or unreported. Basis references point to the detailed records and replace narrative duplication.

- ordered or otherwise connected steps, linked to steps, activities, and control-flow relationships.
- material inputs, linked to input items, quantities, resources, requirements, or artifacts.
- outputs, linked to artifacts, resources, quantities, or result outputs.
- roles and responsibilities, linked to role and team entities.
- tools and settings, linked to tools, configurations, resources, or quantities.
- decision rules, linked to rule records.
- branching and iteration, linked to relationship and rule records.
- quality or completion checks, linked to check and criterion records.
- a worked example, linked to an application or result set.
- supporting materials and their access route, linked to resource records.

Assign `procedure_detail_level` as follows and give a concise reason:

- **`named_only`:** the procedure is identified without a usable account of its activities.
- **`narrative_outline`:** major activities are described, but missing sequence, inputs, outputs, decision rules, settings, or checks require material reconstruction.
- **`actionable_procedure`:** connected actions and the inputs, outputs, roles, tools, decision rules, and checks that matter in the reported setting are sufficiently specified for another qualified team to follow.
- **`reproduction_ready`:** the actionable procedure also identifies all material settings and accessible supporting materials needed to reproduce it without material reconstruction. This code assesses reported readiness. It does not establish independent reproduction.
- **`unclear`:** relevant procedural information exists, but its detail cannot be classified.

Do not infer an actionable procedure from a flowchart title, a named method, a tool script, or a successful result. Record missing components explicitly. Derive the level from component statuses and their basis references. Keep `detail_level_reason` concise and link it to the records that establish the level. The common evidence fields apply to every method, source, step, workflow, activity, reporting-detail field, and model-artifact row.

### EPS representation

For each report, record one EPS case section by default. Record:

- `eps_case_id`, including for the single default case.
- EPS anchor source wording, linked to the applicable EPS element or requirement records.
- model anchor for Route B, linked to the applicable representation and artifact records.
- EPS boundary source wording, linked to typed inside-boundary and outside-boundary relationships.
- `eps_elements` using the typed element records below.
- `eps_requirements` using the requirement records below.
- EPS architecture source wording, linked to the element, exchange, dependency, interface, and relationship records that define it.
- `eps_exchanges` as nested rows containing `eps_exchange_id`, linked source, destination, and interface element IDs, source endpoint, destination endpoint, named EPS interface when present, exchanged item, direction, `exchange_types` using every applicable value from `energy`, `information_or_control`, `material_or_other_resource`, `other`, or `unclear`, and `exchange_scope` using `within_eps`, `cross_subsystem`, `spacecraft_environment`, `external_system`, or `unclear`.
- `eps_dependencies` as nested rows containing `eps_dependency_id`, linked dependent and provider element IDs, dependent endpoint, provider or driver endpoint, description, linked exchange and EPS-requirement IDs when applicable, `dependency_types` using every applicable value from `electrical_power`, `information_or_control`, `thermal_or_environmental`, `mechanical_or_structural`, `functional_or_behavioral`, `operational_or_mode`, `requirement_or_constraint`, `shared_resource`, `other`, or `unclear`, and `dependency_scope` using `within_eps`, `cross_subsystem`, `spacecraft_environment`, `external_system`, or `unclear`.
- EPS modes and operations. Use element records for each named mode, state, scenario, operational activity, function, or behavior. Link residual source descriptions to those elements and to scenario, rule, relationship, quantity, and result records. Use behavior occurrences in the applicable representations for ordered actions, messages, events, transitions, guards, branches, and timing.
- `eps_model_representations` using the structured representation records below. Record `abstraction_levels`, `decomposition_visibilities`, and `fidelity_levels` on each representation.
- `eps_model_representation_relationships` for reported relationships among views.
- `modeled_disciplinary_viewpoints`, using one or more of `electrical_or_electronic`, `thermal`, `software_or_algorithmic`, `mechanical_or_structural`, `operational`, `other`, or `unclear`.
- EPS-to-model bridges using the structured relationship records below. Record every bridge needed to establish qualification and Route B eligibility.
- purposes, using one or more of `definition_or_sizing`, `requirements_or_traceability`, `trade_study`, `interface_management`, `executable_analysis`, `verification_and_validation`, `communication`, `lifecycle_continuity`, `reuse_or_tailoring`, or `other`, and the supported decisions.
- `coverage_assessment` using the scope and coverage records below.
- EPS model maturity, using the project-maturity codes at EPS-model scope.
- availability of the EPS model, profile, script, data, or documentation, using the shared availability codes.

For the EPS domain boundary see [Part 1 - EPS boundary and elements](protocol.md#EPS boundary and elements).

#### Typed EPS model elements

Create one `eps_element_id` row for each source-identifiable element needed to map model content or scope. Record the source name or description and source element type. Normalize one or more element roles as `stakeholder_or_external_actor`, `external_system`, `environment`, `spacecraft_or_system`, `subsystem`, `capability`, `use_case`, `operational_activity`, `function`, `behavior`, `component_unspecified`, `logical_component`, `physical_component`, `software_or_algorithm`, `interface_or_port`, `mode_or_state`, `scenario`, `parameter_or_constraint`, `hazard_or_risk_control`, `other`, or `unclear`.

Record one or more abstraction levels using the EPS abstraction codes. Use `model_inclusion` as follows:

- **`explicit_model_element`:** the source exposes an identifiable element in a model view, table, export, or artifact.
- **`represented_model_content`:** the source clearly states that the content is represented, but no individual model element can be located.
- **`planned_model_content`:** the content is explicitly planned for later inclusion.
- **`reported_but_not_modeled`:** the source discusses the item and establishes that it is outside the represented model content.
- **`unclear`:** relevant evidence does not resolve model inclusion.

Record `boundary_role` as `inside_eps`, `on_eps_boundary`, `outside_eps_within_spacecraft`, `spacecraft_environment`, `external_system`, or `unclear`. Use parent element IDs for source-supported decomposition. Link each element to its model artifacts. Requirements, exchanges, dependencies, bridges, claims, findings, V&V activities, and coverage items point to the element ID from their own records. Preserve the source type separately from the normalized role so the coding remains independent of SysML, Arcadia, Capella, or an author-defined language.

Create each element once. Use its ID in exchanges, dependencies, bridges, claims, findings, V&V activities, requirements, and coverage items. Retain endpoint wording in exchange and dependency rows because it preserves the source relationship statement.

#### EPS requirement records

Create one `eps_requirement_id` row for each material mission, system, EPS, component, interface, operational, or external requirement needed for the planned synthesis. Record the source requirement ID, statement or description, EPS specificity, level, type, and MBSE inclusion.

Use `eps_specificity` as `eps_specific`, `allocated_to_eps`, `system_or_mission_with_eps_relevance`, `external_constraint_on_eps`, `not_eps_specific`, or `unclear`. Use `requirement_level` as `stakeholder_need`, `mission`, `system`, `eps_subsystem`, `eps_component`, `interface`, `operational`, `other`, or `unclear`. Use one or more requirement types: `functional`, `performance`, `interface`, `environmental`, `operational`, `safety`, `reliability_or_availability`, `design_constraint`, `verification_or_acceptance`, `other`, or `unclear`.

Use `mbse_inclusion` as follows:

- **`modeled_as_requirement`:** an identifiable requirement element exists in the MBSE model.
- **`linked_to_modeled_content`:** the requirement is outside the model or its location is unclear, but an explicit link to model content is reported.
- **`model_input_only`:** the requirement supplies an input without a reported persistent requirement element or trace.
- **`planned_for_model`:** later model inclusion is planned.
- **`reported_outside_mbse_model`:** the requirement is reported for the EPS work and is explicitly outside the MBSE model.
- **`unclear`:** relevant evidence does not resolve MBSE inclusion.

Use parent requirement IDs for source-supported decomposition. Link each requirement to its EPS elements and model artifacts. Use `constraint_rule_ids`, `quantity_ids`, and `verification_check_ids` for parsed constraints, quantitative content, and verification links. Construction sources, input groups, result criteria, RQ3 activities, model bridges, claims, findings, representations, and coverage items point to the requirement ID from their own records. Keep detailed input values and V&V thresholds in their existing input and criterion records.

#### Model representations and diagrams

Create one `model_representation_id` row for each source-identifiable diagram, table, matrix, model tree, package view, generated listing, chart, simulation view, or composite representation that contributes material EPS evidence. Keep the persistent model or repository as a model artifact and link each representation to that artifact. The representation row inherits the common citation metadata. Use `graphic` and `graphic_quote_description` to locate the published figure, table, panel, or excerpt.

Record the source name or caption, source representation type, source language or notation, reported purpose, origin, completeness, `abstraction_levels`, `decomposition_visibilities`, `fidelity_levels`, linked artifacts and tools, and all represented content through IDs. Use `linked_modeling_language_entity_ids`, `purpose_entity_ids`, and `linked_decision_ids` for normalized language, purpose, and decision links. Link elements, requirements, exchanges, dependencies, model bridges, input groups, result sets, outputs, and criteria from the representation row. Keep these links in one direction. Do not add reverse representation links to every content record.

Use one or more `representation_forms`: `diagram`, `table`, `matrix`, `model_tree_or_package_view`, `generated_text_or_listing`, `chart_or_plot`, `executable_or_simulation_view`, `other`, or `unclear`. Use `composite_of_views` under representation completeness when one published representation combines several views or forms.

Use one or more `normalized_view_types`: `context_or_boundary`, `requirements_or_traceability`, `capability_or_use_case`, `functional_or_behavioral`, `activity_or_control_flow`, `sequence_or_interaction`, `state_or_mode`, `structural_decomposition`, `logical_structure`, `physical_structure`, `interface_or_exchange`, `data_or_control_flow`, `energy_or_resource_flow`, `data_or_information_model`, `parametric_or_constraint`, `allocation_or_mapping`, `deployment_or_configuration`, `decision_or_trade_study`, `risk_or_hazard`, `vv_or_test`, `model_organization_or_package`, `generated_analysis_or_result`, `other`, or `unclear`. Apply every material semantic type shown by a representation. Preserve the source diagram or view type separately.

Use `representation_origin` as follows:

- **`native_model_view`:** the source presents a view directly from the model or modeling environment.
- **`source_redrawn_or_simplified`:** the authors redraw, simplify, or restyle model content for presentation.
- **`generated_from_model`:** a tool generates the representation from model content.
- **`reviewer_reconstructed`:** the reviewer reconstructs a view from separately reported model evidence.
- **`unclear`:** the representation origin cannot be classified.

Use `representation_completeness` as `complete_as_presented`, `partial_or_excerpt`, `composite_of_views`, or `unclear`. This code concerns what the report presents. It does not claim that the underlying model is complete.

For a sequence, activity, state, or interaction view, create one `behavior_occurrence_id` for each source-identifiable action, message, exchange occurrence, transition, control node, loop, or timing event needed for synthesis. Record occurrence type, source sequence label, predecessor occurrence IDs, action, message, or event wording, source and destination element IDs, contextual element IDs, linked exchanges and model bridges, guard or condition, branching or parallelism, timing, and output or result. Link an existing exchange or bridge whenever it supplies the static endpoints or relationship. Use the occurrence endpoint fields for occurrence-specific participants or when no existing relationship identifies them. Use occurrence types `action_or_activity`, `message_or_signal`, `exchange_occurrence`, `state_transition`, `state_entry_or_exit`, `decision_or_branch`, `merge_join_or_fork`, `loop_or_iteration`, `timing_event`, `other`, or `unclear`.

Behavior occurrences describe EPS or spacecraft behavior shown in a model representation. Use `action_or_item_entity_ids`, `guard_rule_ids`, `control_flow_relationship_ids`, `timing_quantity_ids`, and `output_refs` for action, guard, branch, loop, timing, and output meaning. Engineering method steps remain in `method_steps`, and engineering process activities remain in `workflow_activities`. Use `not_applicable` for behavior occurrences in a static representation. Use `not_reported` when the source identifies a dynamic representation but does not expose enough content to extract occurrences.

Create one representation-relationship row for each reported relationship between two representations. Record source and target representation IDs, the source relationship term, normalized relationship types, and a description. Use one or more types: `contains`, `excerpt_of`, `refines`, `abstracts`, `continues`, `complements`, `traces_to`, `alternate_view_of`, `generated_from`, `same_content_different_notation`, `cross_layer_mapping`, `other`, or `unclear`. Shared content can also be derived from the IDs linked by both representations, so do not create a relationship row solely because two views contain the same element. Use `none` when the evidence establishes that no relationship among the extracted representations is reported.

#### EPS model bridges

Each bridge records its source endpoint wording, linked EPS anchor element or requirement IDs, linked second-concern element or requirement IDs, linked artifacts, exchanges, dependencies, and result criteria, the source relationship term, normalized relationship types, and reconstructed meaning. Use one or more normalized types: `allocation`, `association_or_participation`, `include`, `extend`, `generalization`, `decomposition`, `derivation`, `refinement`, `realization`, `satisfaction`, `verification`, `trace`, `interface_or_flow`, `state_transition`, `parametric_binding`, `transformation`, `data_mapping`, `behavior_or_function_mapping`, `other`, or `unclear`.

#### Coverage assessment

Record the declared scope or denominator, overall coverage extent, assessment basis, item level coverage, linked RQ1 completeness claims, and an assessment reason. Use `denominator_refs` for every denominator member, `assessment_rule_ids` for the derivation, and issue IDs for limitations. Each coverage-item reason links through rule and issue IDs. Use overall extent `complete_against_declared_scope`, `partial_against_declared_scope`, `selected_or_illustrative`, `not_assessable`, or `unclear`. Use one or more bases: `author_statement`, `declared_scope_comparison`, `enumerated_model_content`, `available_artifact_inspection`, `reviewer_inference`, `other`, or `unclear`.

Create a coverage item for each material included, partly included, excluded, out-of-scope, or planned item needed to interpret coverage. Link it to existing element, requirement, exchange, dependency, model-artifact, and model-representation IDs. Use a free text name only when no linked record can identify the target. Code status as `included`, `partially_included`, `deliberately_excluded`, `outside_declared_scope`, `planned_or_future`, or `unclear`. The overall assessment is relative to the recorded scope or denominator. Do not infer a universal EPS completeness standard.

Use exchange type as follows:

- **`energy`:** electrical or other energy crosses the identified interface.
- **`information_or_control`:** data, status, commands, or control signals cross the identified interface.
- **`material_or_other_resource`:** matter or another nonenergy resource crosses the identified interface.
- **`other`:** another identified exchange type.
- **`unclear`:** the exchange type cannot be classified.

Record every applicable exchange type in `exchange_types`. Use `uncertain` for the complete field when evidence establishes a combined exchange but does not identify its types.

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

Record every applicable dependency type in `dependency_types`.

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

Use representation and element abstraction levels as follows:

- **`conceptual`:** high-level concepts and relationships without a complete logical architecture.
- **`logical`:** technology-independent functions, behaviors, or logical elements.
- **`physical_design`:** component-level architecture, technology choices, or design parameters.
- **`implementation`:** realized software, hardware, interface, or configuration detail.
- **`unclear`:** the abstraction level cannot be classified.

Use representation decomposition visibilities as follows:

- **`black_box`:** the representation shows externally visible EPS behavior, exchanges, or interfaces without internal decomposition.
- **`white_box`:** the representation shows internal EPS elements and their relationships.
- **`unclear`:** decomposition visibility cannot be classified.

Use representation fidelity levels as follows:

- **`qualitative`:** the representation contains no quantitative behavior.
- **`idealized_quantitative`:** simplified quantitative relations support bounded analysis.
- **`engineering_representative`:** mission-relevant parameters and constraints support engineering decisions.
- **`implementation_representative`:** the representation reflects implementation interfaces, timing, or configuration.
- **`as_built_or_calibrated`:** the representation is calibrated or parameterized against a physical instance.
- **`unclear`:** fidelity cannot be classified.

Record every supported abstraction, visibility, and fidelity classification on the representation. Derive EPS-case summaries as unions of the linked representation values. Use element abstraction levels for element-specific analyses. Do not copy the derived unions into the EPS case.

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

The common evidence fields apply to every exchange and dependency row. Preserve endpoint wording as source text. Link it to the endpoint elements already present in the row. Use `exchanged_item_entity_ids`, `exchange_quantity_ids`, and relationship IDs for exchanged content and flow values. Code `normalized_direction` as `source_to_destination`, `destination_to_source`, `bidirectional`, `undirected`, `variable`, or `unclear`. Dependency descriptions link to their typed dependency, requirement, exchange, and relationship records. An exchange or dependency is modeled EPS content. It counts as an EPS-to-model bridge only when it also meets the bridge definition above.

### Implementation footprint and effort records

Group related implementation facts by scope. Create one general implementation record by default. Create another record when a reuse or tailoring application or another bounded implementation has materially different roles, resources, effort, or burdens.

For each implementation record, record:

- `implementation_record_id`.
- scope.
- roles and affected teams.
- skills and training.
- staffing and number of people.
- linked `workflow_id` and `tool_id` values.
- workflow execution and deviations from the defined workflow.
- automation.
- tool licences, settings, and infrastructure details that are not represented by the linked tool records.
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
- `burden_phases`, recording every applicable value from `adoption`, `ongoing_use`, or `unclear`.
- reported burden.
- measurement method.
- mitigation.
- linked benefit or trade-off.

Use effort basis as follows:

- **`measured`:** effort was tracked or measured using a reported basis.
- **`author_estimated`:** the source provides a quantified estimate without direct tracking.
- **`asserted`:** the source characterizes effort without a reported measurement or estimation method.

Use burden phases as follows:

- **`adoption`:** the burden occurs during initial introduction, setup, migration, or training.
- **`ongoing_use`:** the burden occurs during routine operation, update, or maintenance.
- **`unclear`:** timing cannot be classified.

The burden-category codes identify labor, elapsed time, money, people, competence, tools, infrastructure, preparation, computing, integration, governance, maintenance, or rework burdens according to their labels. Record both `adoption` and `ongoing_use` when a burden occurs in both phases.

Keep measured values, author estimates, and unsupported characterizations distinct. Each implementation record supplies `scope_refs`, team, role, and skill entity IDs, quantity, resource, relationship, rule, issue, and decision IDs, linked RQ2 finding IDs, and controlled `automation_levels`. Use `manual`, `tool_assisted`, `partially_automated`, `fully_automated`, or `unclear`. Keep one `automation_level` on each atomic method step, workflow activity, tailoring step, and application operation. Derive workflow-level automation arrays from their activities and code their provenance as `reviewer_derived`. Record every additional implementation-level automation classification supported by work outside those linked workflows. Link each implementation source text item to these normalized records. Use team, role, and skill entities for people and competence. Use quantities for staffing, effort, duration, schedule, cost, computing, review, rework, and maintenance. Use resources for tools, licences, and infrastructure. Use relationships for workflow execution, deviations, integration, migration, and interoperability. Use rules for governance and configuration control. Use issues for burdens and rework, and decisions for mitigations and trade-offs. Link each implementation record to every applicable workflow. Link RQ2 burden findings and reuse or tailoring applications to the implementation record instead of copying its details.

### Input and assumption groups

Extract inputs and assumptions that define the EPS representation, materially shape an evaluation or result, establish a V&V configuration or criterion, inform a decision, or bound reuse or tailoring. Group related items as mission requirements, base assumptions, scenario inputs, model formulation, V&V configuration, or tool prerequisites. Do not inventory every model parameter.

For each group, record:

- `input_group_id`.
- `category`, using `mission_requirements`, `base_assumptions`, `scenario_inputs`, `model_formulation`, `vv_configuration`, `tool_prerequisites`, or `other`.
- linked EPS case and scenario or configuration. Link the scenario or configuration wording to its entity records.
- linked `model_generation_method_id` values when the input or assumption applies to a generation method.
- linked `workflow_id` values when the input or assumption applies to a workflow.
- linked `report_reuse_record_id` values when the input or assumption applies to reuse of an artifact, method, or workflow.
- linked EPS-requirement IDs and tool IDs when applicable.
- `input_items` as nested rows. Each row records `input_item_id`, source parameter or construct, linked entity and EPS-requirement IDs, typed value quantity IDs, source type, source resource IDs, uncertainty quantity IDs, linked issue IDs, rationale, and linked decision IDs.
- linked `result_output_id`, `result_criterion_id`, `rq3_activity_id`, or `report_application_id` values when applicable.

Create one input item for each value or assumption that needs an independent source, unit, uncertainty account, or downstream link. This row replaces parallel lists of parameter names, values, sources, and uncertainty. Store nominal, worst case, minimum, maximum, range, and distribution bases in the linked quantity records.

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
- `evaluation_design_components`, recording every applicable value from `model_or_simulation_evaluation`, `case_or_experience_report`, `comparative_observational`, `controlled_or_quasi_experimental`, `survey`, `interview_or_qualitative`, `artifact_or_reuse_demonstration`, `other`, or `unclear`.
- `methods_integration`, using `integrated`, `partially_integrated`, `not_integrated`, or `unclear`. Use `not_applicable` when the result set has one design component and no methods integration question arises.
- scenario or configuration source wording plus linked scenario and configuration entity IDs.
- linked input groups and tool IDs.
- `evaluation_units` as nested rows containing `evaluation_unit_id`, controlled unit type, linked entity IDs, count or sample size quantity IDs, selection rule IDs, assignment rule IDs, and source description.
- data-source resource IDs.
- method source wording linked to a normalized method entity or workflow.
- `execution_status`, using `planned`, `prepared`, `executed_complete`, `executed_partial`, `attempted_failed`, or `unclear`.
- analysis-method source wording and linked analysis-method entity IDs.
- issue IDs for evaluation-level missing data, failures, exclusions, uncertainty, and sensitivity.
- outputs as nested rows containing `result_output_id`, source quantity or construct wording, source-reported value, linked construct entity IDs, typed quantity IDs, comparator IDs, group or arm entity IDs, observed or expected status, issue IDs, and structured statistical evaluation rows.
- each statistical evaluation row records `statistical_evaluation_id`, source statistic term, statistic type, estimate quantity IDs, confidence interval quantity IDs, exact p-value quantity ID, sample size quantity IDs, comparator IDs, group or arm IDs, and method entity IDs. Use a status instead of this table for deterministic engineering outputs.
- `criteria` as nested rows containing `result_criterion_id`, source criterion or requirement ID, linked EPS-requirement IDs, source target wording and typed target references, source threshold wording with linked rule and quantity IDs, source resource IDs, `criterion_applicability`, source result wording, controlled verdict, linked output IDs, source scope and scope references, observed or expected status, authority explanation, and authority check IDs.
- comparators as nested rows containing `comparator_id`, source description, controlled comparator type, typed target references, material-difference relationship IDs, comparator adequacy, linked issue IDs, and rival explanations.
- decision IDs.
- physical or operational relationship IDs.

Use evaluation design components as follows:

- **`model_or_simulation_evaluation`:** a model or simulation is analyzed or executed to evaluate behavior or performance.
- **`case_or_experience_report`:** one or more implementations are described without a designed comparison.
- **`comparative_observational`:** existing cases or practices are compared without controlled assignment.
- **`controlled_or_quasi_experimental`:** a designed comparison uses controlled or nonrandom assignment.
- **`survey`:** data come primarily from a structured questionnaire.
- **`interview_or_qualitative`:** data come primarily from interviews, observations, or qualitative analysis.
- **`artifact_or_reuse_demonstration`:** the main evaluation is an artifact instantiation, transfer, or reuse demonstration.
- **`other`:** another identifiable evaluation design.
- **`unclear`:** the reported method cannot be classified.

Record each component of a mixed methods evaluation in `evaluation_design_components`. Use `methods_integration` as follows:

- **`integrated`:** the evaluation deliberately combines component methods in its design, analysis, or interpretation.
- **`partially_integrated`:** some component methods are connected while others remain separate.
- **`not_integrated`:** several methods are used in parallel without reported integration.
- **`unclear`:** several relevant methods are reported, but their integration cannot be established.

Preserve *mixed methods* in the source method wording when the report uses that term. A result set with several resolved components must also resolve `methods_integration`.

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

Each comparator can contain nested rows for material rival explanations that bear on the claim. Each row records `rival_explanation_id`, whether the explanation is author-identified or reviewer-noted, source explanation and handling wording, linked issue IDs, controlled handling code, and linked check IDs. Reviewer-noted rival explanations inform support. They are not primary-source findings.

The common evidence fields apply to every output, criterion, comparator, and rival-explanation row. An EPS engineering output is not an MBSE benefit by itself. Link it to RQ2 or RQ3 only when the Part 1 rules are met.

If the reviewer calculates or converts a value, keep it in a `reviewer_derived_values` table within the result set. Record `reviewer_derived_value_id`, linked input-item or result-output IDs, linked source and result quantity IDs, formula or transformation rule IDs, unit-conversion relationships, assumption rules, issue IDs for missing-data handling, analysis script resource or path, and sensitivity quantity IDs. Preserve concise source wording where required. Never overwrite or copy a source-reported value.

### RQ1 evaluative characterizations

Create a short row only when a report uses an evaluative characterization such as *lightweight*, *scalable*, *comprehensive*, *easy to implement*, *resource intensive*, or an equivalent claim.

Record:

- `rq1_claim_id`.
- claim wording.
- source-claimed characteristic.
- `claimed_characteristic_code`, using `genericity`, `modularity`, `completeness`, `scalability`, `adaptability_or_tailorability`, `reusability`, `replicability_or_reproducibility`, `interoperability_or_integrability`, `traceability`, `consistency`, `maintainability_or_extensibility`, `usability_or_ease`, `lightweightness`, `automation_or_efficiency`, `resource_intensity`, `reliability_or_assurance`, `other`, or `unclear`.
- author-stated rationale. Use `not_reported` when the report gives no reason.
- claim scope and object source wording plus `scope_refs` to the entities, scenarios, configurations, quantities, lifecycle objects, or other records that define the scope.
- linked model artifact, model representation, model generation method, workflow, EPS case, EPS element, EPS requirement, tool, coverage item, report reuse record, result set, result output, result criterion, comparator, or implementation record IDs when relevant.
- `evidence_basis`.
- `support`.
- `support_reason`.

Descriptive facts such as the tool used or diagrams present remain normal report fields and do not need a claim row.

- **`evidence_basis`**, using one or more of `assertion_only`, `worked_example`, `executed_result`, `comparison`, `stakeholder_evidence`, `physical_or_operational_check`, and `independent_transfer`;
- **`support`**, using `supported`, `limited`, `unsupported`, or `unclear`; and
- **`support_reason`**, one concise sentence naming the strongest evidence and main limitation, `basis_refs` to the records used, and one or more limitation codes: `none`, `method`, `directness`, `comparison`, `precision`, `independence`, `applicability`, `reporting`, `conflicting_evidence`, `missing_data`, or `other`.

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
- exclusion or uncertainty reason when not in direct synthesis, plus one or more `eligibility_reason_codes`. Use `not_applicable` when direct synthesis is `yes`.
- exact claim wording.
- `claim_kind`, using `descriptive_occurrence`, `feasibility_or_executed_result`, `technical_performance`, `comparative`, `causal_attribution`, `experiential_or_perceived`, `implementation_burden`, `transfer_or_generalization`, `other`, or `unclear`.
- `roles`, recording `outcome`, `implementation_burden`, or both when a trade-off cannot be split into separate findings.
- target and scope source wording, plus typed `target_refs` and `scope_refs`.
- `outcome_category`, using `eps_reliability`, `mission_or_system_assurance`, `defect_or_error_reduction`, `risk_reduction`, `reproducibility`, `reuse`, `integration_or_interoperability`, `interface_consistency`, `traceability_or_requirements_quality`, `completeness`, `lifecycle_continuity`, `decision_support`, `cost`, `schedule`, `effort_or_automation`, `communication_or_knowledge`, `governance`, `value_realization`, or `other`.
- `reliability_subtype` for a reliability finding, using `eps_reliability`, `system_or_mission_reliability`, `process_reliability`, `model_consistency`, `mission_assurance`, `defect_or_error_reduction`, `generic_reliability_claim`, or `unclear`.
- `author_claimed_directions` as direction-component rows containing `direction_component_id`, controlled direction, source description, scope references, linked result-output IDs, and condition-rule IDs.
- `evidence_supported_directions` using the same direction-component structure. This table also permits `unsupported`.
- `eps_attribution`, using `explicit_eps_attribution`, `ambiguous_attribution`, or `generic_or_ineligible`.
- mechanism, which is the explanation given by the source of how an EPS-linked model artifact or activity led to a claimed outcome or burden. Link each reported causal step through `mechanism_relationship_ids`. Do not infer a mechanism. Use `not_reported` when the source provides no explanation. A missing mechanism makes the claim harder to interpret but does not remove an otherwise clear EPS-attributed finding.
- linked EPS element, EPS requirement, tool, model representation, model artifact, model generation method, workflow, RQ3 activity, input group, result set, result output, result criterion, comparator, report reuse record, or implementation record IDs.
- `measure_directness`, using `direct`, `surrogate`, `intermediate_or_process`, or `unclear`.
- lifecycle stages, using every applicable shared lifecycle-stage code.
- `applicability`, using `reported_case_only`, `bounded_conditions`, `declared_envelope`, `broader_claim`, or `unclear`.
- `evidence_basis`.
- `support`.
- `support_reason`.

Use `direct_synthesis` for RQ2 findings and RQ3 activities as follows:

- **`yes`:** every RQ-specific condition for direct inclusion is met.
- **`no`:** at least one required condition fails.
- **`uncertain`:** relevant evidence exists, but at least one required condition cannot be resolved.

Use one or more eligibility-reason codes for a retained near miss: `missing_eps_attribution`, `missing_target`, `missing_model_link`, `missing_vv_intent`, `generic_only`, `system_wide_cooccurrence`, `ambiguous_scope`, `downstream_physical_only`, `other`, or `unclear`. Use `downstream_physical_only` for a physical activity retained to complete a V&V chain that lies outside the direct prephysical scope of RQ3. Use only `not_applicable` for a directly synthesized row.

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

Use roles as follows:

- **`outcome`:** the finding reports an outcome.
- **`implementation_burden`:** the finding reports an implementation burden.

Record both values when the source presents an inseparable trade-off. The shared finding row establishes that the roles belong to one inseparable statement.

Use direction components as follows:

- **`beneficial`:** movement toward the stated objective, target, or desired condition.
- **`null_or_no_observed_effect`:** no meaningful or observed change is reported.
- **`adverse`:** movement away from the objective or an increase in burden, harm, or failure.
- **`unclear`:** the statement is directional, but its direction cannot be classified.
- **`unsupported`:** no direction is warranted by the evidence. Use this only in `evidence_supported_directions`.

Create one component for each direction and link its measure, actor, scenario, or condition through `scope_refs`, `linked_result_output_ids`, and `condition_rule_ids`. Split the RQ2 finding when the components have materially different evidence or scope and can stand as separate findings. Keep direction components together only when the source statement is inseparable.

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
- **`reuse`:** repeated use of an artifact, method, or workflow across settings.
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

### RQ3 V&V and model assurance activities

Create one activity row for each materially distinct target, method, and scenario combination. Keep several criteria and verdicts in one activity when the method and scenario are shared. Create separate linked rows for successive MIL, SIL, PIL, HIL, physical, commissioning, or operational stages. Capture activities that assess the completeness, correctness, consistency, conformance, fidelity, or currency of an EPS-linked MBSE model, transformation, configuration, representation, or digital twin itself. Retain relevant near misses with `direct_synthesis = no`.

Reuse existing records to form the end-to-end thread. Represent a source-defined V&V campaign as a workflow whose `workflow_scope_types` include `verification_or_validation` and every other applicable scope, and link each RQ3 row to its exact workflow activities. Use report-application `linked_rq3_activity_ids` and `assurance_rq3_activity_ids` as the canonical links from tailoring to V&V. Use `target_refs`, model artifact links, configuration links, criteria, checks, and relationship records instead of copying their content into the activity.

Record:

- `rq3_activity_id` and `predecessor_rq3_activity_ids` for source-supported activity order.
- `control_flow_relationship_ids` for the corresponding order, branch, iteration, or rework evidence.
- `direct_synthesis`, using `yes`, `no`, or `uncertain` and the definitions under RQ2.
- failed eligibility condition or uncertainty reason when applicable, plus one or more `eligibility_reason_codes`. Use `not_applicable` when direct synthesis is `yes`.
- EPS target source wording plus typed `target_refs`.
- `target_types`, recording every applicable code from `eps_requirement_or_criterion`, `eps_model_element`, `eps_parameter_or_constraint`, `eps_mode_or_scenario`, `eps_interface_or_flow`, `eps_behavior_or_function`, `eps_component_or_architecture`, `eps_hazard_or_risk_control`, `system_target_traced_to_eps`, `mbse_model_artifact`, `digital_twin`, `model_configuration_or_baseline`, `model_transformation_or_generator`, `model_representation_or_view`, `other`, or `unclear`.
- source requirement or criterion ID when present, plus linked normalized EPS-requirement IDs.
- linked EPS element, EPS-model-bridge, model-artifact, model-representation, model-configuration entity, and coverage-item IDs.
- linked workflow, workflow-activity, and tool IDs when applicable.
- explicit model-to-V&V bridge wording and `model_to_vv_relationship_ids`.
- source terminology for verification, validation, V&V, checking, analysis, review, assurance, or assessment.
- linkage scope, using `eps_specific`, `system_wide_eps_linked`, `system_wide_cooccurrence`, or `unclear`.
- `normalized_vv_objects`, recording every applicable code from `model_verification`, `model_validation`, `system_or_design_verification`, `system_or_design_validation`, or `unclear`.
- normalized V&V object reason.
- method source wording and linked `vv_method_entity_ids`.
- `model_assessment_aspects` and `model_assessment_method_types` when the model, representation, transformation, configuration, or digital twin is assessed. Use `not_applicable` when the activity assesses only the represented design or physical system.
- `execution_settings`, using one or more of `mil`, `sil`, `pil`, `hil`, `virtual_testbed`, `other`, or `unclear`.
- `hardware_present`, using `no_hardware`, `support_hardware_only`, `representative_target_hardware`, `actual_target_component`, `actual_target_eps`, `integrated_spacecraft_hardware`, or `unclear`.
- `verification_levels`, recording every applicable product or integration level.
- `test_phases`, recording every applicable test purpose or campaign phase.
- `test_environment_refs`, pointing to the environment, plant, simulator, testbed, facility, configuration, data source, or other records that define the test environment.
- lifecycle stages, using every applicable shared lifecycle-stage code.
- linked result-set, result-criterion, result-output, and comparator IDs.
- `status`, a derived cumulative set using any attained values from `proposed`, `prepared_or_generated`, `result_reported`, `executed_virtual`, `executed_physical`, `downstream_physical_link`, and `model_to_test_closure`.
- measure directness, using `direct`, `surrogate`, `intermediate_or_process`, or `unclear` and the definitions under RQ2.
- discrepancies and resolution source wording plus `discrepancy_issue_ids`.
- `later_physical_link` source wording plus `later_physical_relationship_ids`.
- `model_to_test_closure` source wording plus `closure_check_ids`.
- `evidence_basis`, `support`, and `support_reason`.

The RQ3 target, V&V object, verification level, test phase, lifecycle stage, model role, assessment aspect, and assessment method dimensions use arrays when several classifications can apply. Record each applicable value directly. Do not use a composite `multiple` value. Code `unclear` alone. An evidence status applies to the complete field in place of the array.

#### V&V targets and objects

Use the existing EPS target types for requirements, model elements, parameters, modes, interfaces, behavior, architecture, hazards, and wider system targets. Use the model assessment target types as follows:

- **`mbse_model_artifact`:** a persistent structured system model is itself assessed.
- **`digital_twin`:** a source-identified digital twin is itself assessed. A stand-alone simulation does not establish this type.
- **`model_configuration_or_baseline`:** a selected model version, configuration, or baseline is assessed.
- **`model_transformation_or_generator`:** a transformation, generator, or its persistent output logic is assessed.
- **`model_representation_or_view`:** a diagram, matrix, table, view, export, or other representation is assessed.

Use every applicable normalized V&V object:

- **`model_verification`:** checking whether a model, transformation, configuration, or executable representation was implemented correctly against its specification or formulation.
- **`model_validation`:** checking whether a model or digital twin is adequate or credible for its intended use against an authoritative reference, data, or expected behavior.
- **`system_or_design_verification`:** checking whether the EPS or wider design meets stated requirements or criteria.
- **`system_or_design_validation`:** checking whether the design meets stakeholder, operational, or mission needs.
- **`unclear`:** relevant evidence does not resolve the V&V object.

For validation, link the criterion row that states why the criterion or oracle is authoritative for the intended use. Record the authority reason in the criterion and reflect any limitation in support. Running a method in a model does not establish model verification or model validation by itself. A virtual requirement check can be system or design verification.

An **EPS target** is a named EPS requirement, model element, parameter, mode, interface, behavior, function, hazard, model artifact, model configuration, or digital twin, or a wider system target clearly decomposed, allocated, or traced to named EPS content. A **model-to-V&V bridge** is a reported trace, shared ID, binding, port or data mapping, transformation, generated artifact, allocation, or another clear link. A **V&V method, intent, or artifact** is work presented as verification, validation, compliance or requirement checking, model assurance, virtual integration, model-derived testing, or another V&V function.

Use linkage scope as follows:

- **`eps_specific`:** both the target and the activity are clearly about the EPS.
- **`system_wide_eps_linked`:** a wider system activity includes a named EPS target and a bridge that can be reconstructed.
- **`system_wide_cooccurrence`:** system-wide V&V and EPS content appear in the same report without the required direct link.
- **`unclear`:** the report does not make the scope clear.

#### Verification levels and test phases

`verification_levels` identify the represented product or integration levels. They are independent of the V&V object, execution setting, hardware presence, lifecycle stage, and test phase.

- **`unit_or_component`:** one hardware, software, firmware, logical, or model element is checked independently.
- **`assembly_or_module`:** several integrated items are checked below complete EPS level.
- **`eps_subsystem`:** the complete EPS design, model scope, or implemented EPS is checked.
- **`cross_subsystem_integration`:** EPS interfaces or behavior are checked with one or more other spacecraft subsystems.
- **`integrated_spacecraft`:** the EPS is checked within the assembled spacecraft.
- **`mission_end_to_end`:** the activity includes the spacecraft and ground, operations, environment, or other mission elements as one thread.
- **`other`:** another source-described level applies.
- **`unclear`:** relevant evidence does not resolve the level.

Use `not_applicable` when a model assurance activity has no represented product or integration level, such as a general metamodel conformance check.

`test_phases` identify the purpose or maturity of the test campaign. They do not impose activity order. Use predecessor and control-flow links for reported order.

- **`exploratory_or_characterization`:** the activity learns behavior, estimates parameters, or characterizes limits before formal verification.
- **`development_verification`:** early or iterative verification occurs during design or implementation.
- **`qualification`:** the activity demonstrates that a design meets its specified operational or environmental envelope, including applicable qualification margins.
- **`acceptance`:** the activity checks a particular delivered or flight item for intended use and unacceptable workmanship defects.
- **`integration_and_checkout`:** the activity checks interfaces and behavior while items or subsystems are assembled, when no clearer qualification or acceptance purpose is reported.
- **`prelaunch_checkout`:** final checks are performed on integrated flight hardware before launch.
- **`commissioning`:** initial in-orbit verification is performed after deployment.
- **`operational_or_in_flight`:** verification or monitoring occurs during mission operations.
- **`regression_or_reverification`:** a check is repeated after a change, correction, discrepancy, or configuration update.
- **`other`:** another source-described phase applies.
- **`unclear`:** a test is reported, but its phase cannot be established.

Code a source-described protoflight campaign with both `qualification` and `acceptance`, and preserve *protoflight* in the source terminology. Use `not_applicable` for an activity, such as a static formal proof, that has no test campaign. Do not infer a test phase from MIL, SIL, PIL, HIL, hardware presence, or lifecycle stage.

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

#### Model and digital twin assessment

Record all applicable `model_assessment_aspects`:

- **Completeness:** `declared_scope_completeness`, `requirements_coverage`, `traceability_completeness`, `viewpoint_coverage`, `interface_coverage`, `scenario_or_mode_coverage`, and `data_or_parameter_completeness`.
- **Correctness and consistency:** `syntactic_or_metamodel_conformance`, `semantic_correctness`, `internal_consistency`, `cross_view_consistency`, `behavioral_correctness`, `constraint_or_equation_correctness`, `transformation_or_generation_correctness`, and `configuration_or_version_consistency`.
- **Digital twin quality:** `physical_correspondence`, `data_mapping_correctness`, `calibration_adequacy`, `fidelity`, `predictive_accuracy`, `synchronization_or_currency`, `uncertainty_adequacy`, and `provenance_or_data_quality`.
- **Residual classifications:** `other` and `unclear`.

Record all applicable `model_assessment_method_types`:

- **Review and rule checking:** `manual_model_review`, `automated_rule_check`, and `metamodel_conformance_check`.
- **Coverage and consistency:** `trace_or_coverage_analysis` and `consistency_analysis`.
- **Execution and formal analysis:** `formal_analysis_or_model_checking` and `simulation_based_check`.
- **Comparison and empirical assessment:** `reference_model_comparison`, `test_or_operational_data_comparison`, `calibration_assessment`, and `stakeholder_or_expert_review`.
- **Residual classifications:** `other` and `unclear`.

Keep the exact method in `method` and `vv_method_entity_ids`. For a completeness assessment, link the declared scope or denominator, applicable coverage items, criterion, and result. A completeness assertion without an assessed denominator remains an RQ1 claim rather than an executed completeness result. For correctness or validation, link the governing specification, metamodel, expected behavior, reference model, stakeholder judgment, test data, flight data, or other oracle through the criterion, resource, input, and check records. For a digital twin, use relationships to connect the twin to its physical counterpart and use input groups and result sets for operational data, timing, uncertainty, and comparison results.

#### Activity sequence and status

Keep `later_physical_link` and `model_to_test_closure` as required source-evidence fields in every activity. Link ordinary values to the corresponding relationship and check records. Link each post-tailoring assurance activity to the resulting model artifact and configuration recorded by its report application. Derive and store every attained status milestone. Every milestone after `proposed` requires `proposed`, and each attained execution milestone requires `result_reported`. A retained near miss can have an empty status set when it attains no milestone.

- **`proposed`:** the target, bridge, and V&V method, intent, or artifact are reported.
- **`prepared_or_generated`:** a linked criterion row gives a requirement, threshold, expected behavior, formal property, completeness denominator, or pass/fail criterion.
- **`result_reported`:** a linked output or criterion row reports a result or verdict.
- **`executed_virtual`:** cited evidence establishes execution before physical integration or testing of the target EPS, with `result_reported` attained.
- **`executed_physical`:** cited evidence establishes execution with representative or actual target hardware, with `result_reported` attained.
- **`downstream_physical_link`:** at least one `later_physical_relationship_id` connects the activity to a later physical artifact or activity.
- **`model_to_test_closure`:** at least one `closure_check_id` links model and physical results, comparison quantities or tolerances, discrepancies, and resolution. This milestone also requires `downstream_physical_link`.

A downstream physical activity retained only to complete the chain receives `direct_synthesis = no` and `eligibility_reason_codes = [downstream_physical_only]` under the current prephysical scope of RQ3. A physical activity can qualify directly when it independently meets the applicable RQ3 scope and linkage rules.

### Artifact and method reuse

A **reusable EPS MBSE artifact** is a source-identifiable structured-model asset, or documented package of assets, that contains a qualifying EPS thread or is explicitly connected to one. It can be:

- a reference or template model;
- a metamodel or profile that carries EPS meaning;
- a model library or pattern;
- an interface contract;
- a parametric-model package;
- a transformation or generator with persistent model content; or
- a larger reusable spacecraft model whose EPS part can be reconstructed separately.

The first report pass creates a complete source-bounded extraction for every identifiable EPS-linked artifact assessed for reuse, every model generation method, and every engineering workflow. Create a reuse record for each method and workflow even when the source makes no reuse claim. Also capture every reported artifact lineage and each toolchain or language reuse case. Create more than one reuse record when the report describes materially distinct artifacts, methods, workflows, or lineages. Create separate artifact, method, and workflow records when their reuse evidence or levels differ. Extract all evidence available in the report even when no companion report is known. Cross-report artifact identity remains pending.

An artifact relationship is one source-supported parent-to-derived connection. Store it as a nested row containing `artifact_relationship_id`, parent and derived model-artifact IDs, controlled `relationship_type`, source names and versions, relationship or derivation wording, and identity and derivation evidence. The model-artifact links are canonical. The wording preserves provenance. The common evidence fields apply to every relationship row.

Record once for the report:

- `lineage_mentioned`, using `yes`, `no`, or `uncertain`.
- lineage-mention reason and citation IDs.

Use `yes` when the report explicitly identifies or provides sufficient source evidence for continuity between a base artifact and a version, derived instance, or adoption. The report does not have to use the word *lineage*. Use `uncertain` when continuity is plausible but unresolved. Use `no` for a reuse claim or stand-alone artifact without a reported continuity relationship. Similar diagrams, authors, organizations, tools, topics, or terminology do not establish continuity.

For each report-level reuse record, record identity and provenance:

- `report_reuse_record_id`.
- `lineage_id`, using `pending_resolution` for a reported or uncertain artifact lineage and `not_applicable` when no artifact-lineage relationship is reported.
- linked `model_artifact_id` values when the record assesses an artifact.
- linked `model_generation_method_id` values when the record assesses a generation method.
- linked `workflow_id` values when the record assesses a workflow.
- artifact names and versions as source wording, linked to the canonical model-artifact records.
- artifact relationships using the structured rows defined above.
- repository or location, linked to resource IDs.
- owner or developer, linked to organization or team entities.
- `artifact_types`, recording every applicable value from `reference_or_template_model`, `metamodel_or_profile`, `model_library_or_pattern`, `interface_contract`, `parametric_model_package`, `transformation_or_generator`, `spacecraft_model_with_separable_eps_thread`, `other`, or `unclear`.
- `artifact_generality_scopes` as nested rows containing `artifact_generality_scope_id`, one controlled `generality`, source scope wording, and exact `scope_refs`. Use `single_target`, `product_family`, `mission_class_reference`, `platform_agnostic`, or `unclear`.
- EPS scope source wording, linked to EPS cases, elements, requirements, representations, or artifacts.
- availability, using the shared availability codes and the linked artifact and resource records.
- `license_category`, using `open_permissive`, `open_copyleft`, `public_domain`, `research_or_noncommercial`, `proprietary_or_commercial`, `custom_other`, `no_license_declared`, or `unclear`.
- exact reuse claim.
- `claimed_reuse_object`, using one or more of `artifact`, `method`, `workflow`, `toolchain`, `language`, `other`, or `unclear`.
- possible related reports or artifacts, linked to report IDs, model-artifact IDs, or typed candidate entities when unresolved.

For a method-only or workflow-only record, use `not_applicable` for linked model artifacts, artifact names and relationships, repository or location, artifact types, artifact generality scopes, EPS artifact scope, artifact availability, and licence. Keep method and workflow identity, supporting-material location, and availability in their linked records. Use the reuse record for the DAE, reusable procedural core, adaptation design, level, and support.

Use artifact types as follows:

- **`reference_or_template_model`:** a generic model intended for configuration or instantiation.
- **`metamodel_or_profile`:** a metamodel, profile, or domain extension that carries EPS meaning.
- **`model_library_or_pattern`:** a reusable collection, pattern, or packaged model element.
- **`interface_contract`:** a reusable specification of interfaces, ports, flows, or obligations.
- **`parametric_model_package`:** a reusable package of equations, constraints, parameters, or analyses.
- **`transformation_or_generator`:** a transformation or generator with persistent model content.
- **`spacecraft_model_with_separable_eps_thread`:** a larger spacecraft model whose EPS part can be reconstructed separately.
- **`other`:** another qualifying reusable artifact type.
- **`unclear`:** artifact type cannot be classified.

Use each artifact generality scope as follows:

- **`single_target`:** the linked scope is intended only for one named mission, platform, or configuration.
- **`product_family`:** the linked scope covers a defined family of related platform variants.
- **`mission_class_reference`:** the linked scope is a generic or reference representation for a mission or platform class, such as CubeSats.
- **`platform_agnostic`:** the linked scope is intended to apply without a specific target platform or mission class.
- **`unclear`:** the intended generality of the linked scope cannot be classified.

Create separate scope rows when materially different parts of an artifact have different generality. Link each row to the artifact, core members, model content, or other records that bound that classification. Do not store an artifact-wide mixed classification.

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

Record the declared applicability envelope (DAE). Preserve source wording for each dimension and add these normalized links:

- `target_refs` for target platform and mission entities.
- controlled `lifecycle_stages` and `linked_decision_ids`.
- `eps_scope_refs` for EPS boundaries and content.
- `model_scope_refs` for model boundaries and abstraction.
- `architecture_and_interface_refs`.
- `environment_mode_and_load_refs`.
- `required_input_refs`.
- linked tool IDs.
- `organizational_prerequisite_refs` for organizations, teams, roles, and skills.
- `limit_rule_ids` for exclusions and limits.

Each limit rule identifies its dimension, condition, operator, and linked quantity or object. A DAE dimension with ordinary source wording must link to its normalized records.

Record the reuse design:

- reusable-core source wording and `core_member_refs` to artifact content, method steps, workflow activities, rules, relationships, and checks.
- `variation_points` as nested rows containing `variation_point_id`, source name or target, controlled `target_types`, exact `target_refs`, linked artifact, method, and workflow IDs, source option wording, typed option quantity IDs, dependency relationship IDs, selection rule IDs, and controlled unchanged-use status. Record every applicable target type from `artifact_content`, `method_step`, `workflow_activity`, `other`, or `unclear`.
- overall unchanged-use source wording linked to rule IDs.
- overall dependency source wording plus `dependency_relationship_ids`.
- `tailoring_rules` as nested rows containing `tailoring_rule_id`, linked variation-point and tool IDs, source trigger wording and trigger rule IDs, operation types, source required inputs and typed input references, source responsible roles and role entity IDs, tool configuration IDs, source resulting output and output references, constraint rule IDs, acceptance check IDs, and rationale.
- `tailoring_procedure_steps` using the structured procedural-step linking rules.
- source required roles and skills plus `required_role_entity_ids` and `required_skill_entity_ids`.
- required tool IDs.
- source required data and settings plus `required_data_and_configuration_refs`.
- automation linked to procedure-action or configuration entities.
- governance source wording plus `governance_rule_ids`.
- `tailoring_procedure_reporting`, using linked procedural component assessments and the levels defined under MBSE approach.

Use one or more tailoring-operation types for each rule or executed application operation:

- **`unchanged_use`:** select the reusable content or procedure without changing it, based on a reported rule.
- **`configuration`:** choose or set a defined configuration.
- **`parameterization`:** assign target-specific parameter values.
- **`selection`:** choose among optional elements, variants, or paths.
- **`specialization`:** refine a general element or rule for the target.
- **`extension`:** add target-specific content while retaining the base content.
- **`deletion`:** remove base content for the target.
- **`substitution`:** replace base content with target-specific content.
- **`interface_mapping`:** map base interfaces, ports, flows, or identifiers to target interfaces.
- **`transformation`:** transform content into another model structure or representation.
- **`generation`:** generate persistent target model content or an application artifact.
- **`add_method_step`:** add a step to the reused method.
- **`remove_method_step`:** remove a step from the reused method.
- **`reorder_method_steps`:** change method-step order or dependencies.
- **`substitute_method_step`:** replace a method step.
- **`add_workflow_activity`:** add an activity to the reused workflow.
- **`remove_workflow_activity`:** remove an activity from the reused workflow.
- **`reorder_workflow_activities`:** change workflow-activity order or dependencies.
- **`substitute_workflow_activity`:** replace a workflow activity.
- **`tool_or_format_migration`:** change a required tool, integration, representation, or data format.
- **`other`:** another reported tailoring operation applies.
- **`unclear`:** the reported operation cannot be classified.

A variation point or tailoring rule must remain source identifiable. Do not split a broad source statement into several invented rules. Link each rule to every variation point it governs when the source supports the link.

Record the report-bounded reuse assessment:

- linked `report_application_id` values.
- `report_reuse_level`, using `NA` or one level from `R0_artifact_only` through `R4_independent_reuse_demonstrated`.
- report-reuse-level reason linked to the records satisfying or failing each prerequisite.
- `method_reuse_level`, using `NA` or one level from `M0_method_identified` through `M4_independent_method_reuse_demonstrated`.
- method-reuse-level reason linked to its basis records.
- `workflow_reuse_level`, using `NA` or one level from `W0_workflow_identified` through `W4_independent_workflow_reuse_demonstrated`.
- workflow-reuse-level reason linked to its basis records.
- conflicting evidence within the report, linked to issue records.
- `evidence_basis`.
- `support`.
- `support_reason` with basis references and limitation codes.

Use `report_reuse_level` only for artifact reuse, `method_reuse_level` only for a model generation method, and `workflow_reuse_level` only for an engineering workflow. Toolchain or language reuse alone remains described through `claimed_reuse_object` and receives all three reuse levels as `NA`. Create separate reuse records when artifact, method, or workflow conclusions require different evidence-basis or support judgments.

Derive artifact demonstrated settings, coverage, failed applications, and applications outside the declared envelope from linked artifact-containing applications. Derive method results from applications containing `method`. Derive workflow results from applications containing `workflow`. Do not copy these details into the reuse assessment.

Assign all reuse levels from evidence contained in this report only. A single report can support R3 or R4, M3 or M4, and W3 or W4. Assign a level of 3 or 4 only when the corresponding application below is complete, identifies what stayed the same and what changed, reports a relevant post-application check and result, and meets the required adopter condition. A companion report is not required for any report-bounded level.

A **reusable core** is the content that the source states or clearly shows remains across uses. For an artifact, it can include model elements, relationships, constraints, interfaces, meanings, or packaged assets. For a method, it can include stable steps, decision rules, roles, inputs, outputs, or assurance activities. For a workflow, it can include stable activities, order or dependencies, handoffs, roles, artifacts, decision gates, and checks.

A **variation point** is a source-described place, option, range, rule, dependency, method step, or workflow activity through which that core can vary.

**Tailoring or adaptation** means using a source-described process to create or select a target-specific artifact instance or to adapt a method or workflow to a target setting. It can involve configuration, parameterization, selection, specialization, extension, deletion or substitution, interface mapping, transformation or generation, changing method steps or workflow activities, tool or format migration, or a clearly justified decision to use the artifact, method, or workflow unchanged.

A parameter sweep or scenario run in one unchanged mission model is analysis, not tailoring across settings. Rebuilding a model without retained structure may show reuse of a method or workflow. It shows reuse of an artifact only when the source establishes the artifact lineage and retained core.

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

Table of workflow reuse level codes.
| Level | Minimum evidence | Meaning |
|---|---|---|
| **`NA`** | The record does not identify an engineering workflow | Workflow reuse does not apply to this record. |
| **`W0_workflow_identified`** | An engineering workflow is identified, with no reuse claim or materially distinct application reported | A workflow exists. Reuse has not been claimed or shown. |
| **`W1_workflow_reuse_claimed`** | The source claims or suggests that the identified workflow is reusable | Workflow reuse is asserted. Its range and adaptation process are not sufficiently specified. |
| **`W2_workflow_reuse_specified`** | The declared applicability envelope, stable workflow core, variation points or unchanged-use rule, adaptation process, and prerequisites are reported | Bounded workflow reuse is specified. Transfer does not have to be demonstrated. |
| **`W3_workflow_reuse_demonstrated`** | W2 is met, and at least one materially distinct target setting applies the identified workflow, reports what stayed the same and what changed, and reports a relevant post-application check and result | Workflow transfer is demonstrated in the reported setting. |
| **`W4_independent_workflow_reuse_demonstrated`** | W3 is met by at least one adopter operationally independent of the originating workflow team | Independent workflow transfer is demonstrated in the reported setting. |

Workflow levels are cumulative. Procedural detail and reuse evidence remain separate. An actionable procedure can remain at M0 or W0 when no reuse is claimed or demonstrated. A high reuse level requires the applicable reuse evidence even when the procedure is reproduction ready.

#### Report-level reuse or tailoring application

A **report-level application** is one use of an artifact lineage, model generation method, engineering workflow, or reported combination in one target setting. For an artifact, the original development mission counts only if the source identifies it as an adoption or configuration of the same reusable core and reports what was kept and changed, or why it was used unchanged. For a method or workflow, the originating use counts only if the source identifies it as an application of an already defined procedure and reports what was retained and adapted, or why it was used unchanged. Initial creation of an artifact or formulation of a method or workflow does not by itself show transfer.

Two applications are **materially distinct** only if they differ on at least one DAE dimension in a way that exercises or tests the reuse claim. Two papers, scenarios, revisions, or names for the same implementation do not count as two applications.

Create one `report_application_id` row for each actual reuse, adoption, or tailoring event described in the report. Merge repeated descriptions of the same event within the report. Keep an account of the same event in another report as a separate report-level row.

Record identity and setting:

- `report_application_id`.
- linked `report_reuse_record_id` values.
- `application_objects`, recording every applicable value from `artifact`, `method`, `workflow`, or `unclear`. Derive the resolved values from the artifact reuse record, model-generation-method links, and workflow links.
- `lineage_id`, inherited from the linked artifact reuse record until cross-report resolution, or `not_applicable` for an application without an artifact.
- linked `model_generation_method_id` values when applicable.
- linked `workflow_id` values when applicable.
- linked `eps_case_id` values.
- target model or configuration source wording plus `target_refs`.
- adopting team source wording plus `adopting_team_entity_ids`.
- relationship to the originator, using `originating_team`, `same_organization_operationally_separate`, `outside_originating_organization`, `independent_evaluation_only`, or `unclear`.
- lifecycle purpose source wording, controlled `lifecycle_stages`, and linked decision IDs.
- relationship to the declared applicability envelope, using `inside`, `boundary`, `outside`, or `unclear`.
- `material_setting_differences`, recording only differences from the linked report context, EPS case, or other applications that identify a distinct application or affect the envelope classification, plus `material_difference_relationship_ids`.

Read shared mission or platform, EPS architecture and interfaces, orbit, environment, modes and loads, model abstraction, tools and versions, and organization and process from the linked report, EPS case, MBSE approach, and implementation records. Do not copy them into the application.

Use application objects as follows:

- **`artifact`:** the application reuses or tailors an identifiable artifact.
- **`method`:** the application reuses or adapts an identifiable model generation method.
- **`workflow`:** the application reuses or adapts an identifiable engineering workflow.
- **`unclear`:** the application objects cannot be classified.

Record every applicable object in the same array. Each application containing `artifact` links an artifact reuse record. Each application containing `method` links at least one `model_generation_method_id` and its method reuse record. Each application containing `workflow` links at least one `workflow_id` and its workflow reuse record.

Use relationship to the originator as follows:

- **`originating_team`:** the team that originated the artifact, method, or workflow controls the application.
- **`same_organization_operationally_separate`:** a separate team in the same organization controls the application without substantive implementation or adaptation work by the originating team.
- **`outside_originating_organization`:** a team outside the originating organization controls the application.
- **`independent_evaluation_only`:** an independent party evaluates an originator-built artifact or originator-applied method or workflow without adopting or implementing it.
- **`unclear`:** control or team separation cannot be established.

`independent_evaluation_only` does not satisfy R4, M4, or W4 because the independent party does not control the adoption or implementation.

Use relationship to the DAE as follows:

- **`inside`:** every known relevant dimension lies within declared limits.
- **`boundary`:** at least one dimension lies at an explicit limit or tests a stated boundary.
- **`outside`:** at least one dimension exceeds an explicit limit.
- **`unclear`:** the envelope or application information does not support classification.

Record tailoring or adaptation performed:

- base artifact, method, or workflow source wording plus `base_refs` to exact versions or procedure records.
- retained source wording plus `retained_refs` to core members, method steps, rules, workflow activities, and handoffs.
- configured or changed source wording plus `changed_refs`.
- linked variation-point, tailoring-rule, and tailoring-procedure-step IDs.
- `executed_operations` as nested rows containing `application_operation_id`, sequence label, predecessor IDs, variation-point, rule, procedure-step, and tool IDs, operation types, exact target references, before state and after state references, reason rule IDs, input references, role entity IDs, tool configuration IDs, check IDs, and controlled operation result. Preserve source wording in the corresponding fields.
- an overall before-and-after source trace plus `before_after_relationship_ids`.
- reasons for changes or unchanged use plus `reason_rule_ids`.
- tailoring or adaptation inputs and assumptions plus linked input-item IDs.

Record tailoring or adaptation effort through linked `implementation_record_id` values. Keep the complete effort and burden details in those implementation records. Do not infer low effort from parameterization, automation, a small mission, or the absence of a reported burden.

Record result and assurance:

- resulting artifact source wording plus model-artifact IDs.
- source configuration identifier plus configuration entity IDs.
- availability, using the shared availability codes.
- source decisions or analyses plus decision IDs.
- `application_result`, using `success`, `partial`, `failure`, or `unclear`.
- source trade-offs plus RQ2 finding IDs.
- source post-tailoring criterion plus result-criterion IDs.
- source assurance method, timing, and result plus check and RQ3 activity IDs.
- source discrepancies and resolution plus issue IDs.
- linked report-level result sets.
- linked RQ2 findings.
- linked RQ3 activities.

For an application without a reused artifact, use `not_applicable` for resulting artifact and configuration fields unless the applied method or workflow produces an identifiable artifact. The post-tailoring criterion, assurance, and discrepancy fields then refer to the check performed after applying the method or workflow.

Use application result as follows:

- **`success`:** the application meets its stated purpose and applicable post-tailoring or post-application criterion.
- **`partial`:** it meets only part of its purpose or criterion.
- **`failure`:** it does not meet its stated purpose or criterion.
- **`unclear`:** the reported evidence does not establish the result.

Record independence:

- personnel overlap source wording, controlled overlap status, and implementing team IDs.
- implementation control source wording and controlling team IDs.
- adopter-attributable evidence for adoption plus typed evidence references.
- adopter-attributable evidence for assurance plus typed evidence references.

An outside team normally qualifies as independent when the artifact lineage, method identity, or workflow identity, adoption, and assurance are established. A team in the same organization qualifies only when it controls the implementation or adaptation, the originating team performs no substantive implementation or adaptation work, and the assured application is distinct.

### Procedural evidence profile

After completing and validating the report extraction, derive the following report-level flags. Each flag records `yes`, `no`, or `uncertain`, the IDs used as its basis, a controlled `derivation_rule`, and a concise derivation reason linked to its basis records. Do not attach new source claims to these flags.

- `generic_or_reference_model_reported`.
- `actionable_model_construction_procedure_reported`.
- `actionable_tailoring_procedure_reported`.
- `worked_tailoring_example_reported`.
- `post_tailoring_assurance_reported`.
- `generic_model_with_actionable_construction_or_tailoring`.

Derive the flags as follows:

- A generic or reference model is reported when an artifact reuse record contains an artifact generality scope coded `product_family`, `mission_class_reference`, or `platform_agnostic`, or its `artifact_types` include `reference_or_template_model`. Use `uncertain` when genericity remains unresolved.
- An actionable construction procedure is reported when a model generation method has `actionable_procedure` or `reproduction_ready` detail and is linked as an output-producing method for the generic or reference model. A detailed one-off method for another artifact does not satisfy this flag.
- An actionable tailoring procedure is reported when the reuse design for the generic or reference model has `actionable_procedure` or `reproduction_ready` tailoring detail.
- A worked tailoring example is reported when an application of the generic or reference model records executed operations, or a justified unchanged use, and identifies the resulting application.
- Post-tailoring assurance is reported when that application records a criterion, assurance method, timing, and result.
- The target-report flag is `yes` when a generic or reference model and at least one actionable construction or tailoring procedure are reported. Propagate material uncertainty instead of forcing `no`.

These flags support retrieval within the included report set. They do not replace the detailed fields or reuse levels.

### Limitations and open extraction

Record source wording for author-stated limitations, future work, source conflicts, reviewer uncertainties, and missing information relevant for interpretation. Link every item to one or more issue records. Each issue has a stable ID, controlled type, affected record references, status, and handling or resolution. Derive simple synthesis flags from issue types and statuses during compilation. Derive missing-information issues from field statuses where possible.

## Cross-report resolution and lineage-level extraction

Begin this pass only after all first-pass report extractions are complete and validated. Resolve report families first. Reports with `lineage_mentioned = yes` seed lineage resolution, and reports with `lineage_mentioned = uncertain` receive resolution review. Follow source-supported relationships to include every report in each candidate lineage, including linked reports with `lineage_mentioned = no`. Preserve report provenance for every lineage-level field.

Report-level extractions remain fixed throughout this pass. Update only `lineage_id` on the relevant artifact reuse records and artifact-containing application records. Assign a stable lineage ID to every matched artifact record, including a record initially marked `not_applicable` that another report links to the lineage. Keep `lineage_id = not_applicable` for method-only, workflow-only, and method-and-workflow records and applications. Use `unresolved_after_review` when a candidate artifact relationship cannot be resolved. A correction to any other report-level field follows the focused-audit and adjudication procedure outside this pass.

Create lineage-level extractions and consolidated artifact-containing application records. Treat all linked reports in a resolved artifact lineage as one evidence bundle when completing those records. Method and workflow reuse levels and applications without an artifact remain fixed, source-bounded report-level results. Do not merge method or workflow identities or applications without an artifact during the artifact-lineage pass. Do not copy lineage-level values into a report-level extraction.

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
- artifact types, using the artifact-type codes defined above.
- artifact generality scopes, linking each consolidated scope row to its contributing report-level scope rows.
- EPS scope.
- availability, using the shared availability codes.
- `license_category`, using the licence-category codes defined above.
- exact reuse claim.
- claimed reuse object, using the claimed-reuse-object codes defined above.

Record the declared applicability envelope with the source dimensions and normalized references defined for report-level records. Include linked report tool IDs and full contributing-report provenance.

Record the reuse design with the report-level source fields and normalized structures. Include core member references, structured variation points with linked report-level IDs, dependency relationships, structured tailoring rules and steps, role and skill entities, tool IDs, data and configuration references, governance rules, and linked procedural-component evidence.

Use the report-level variation-point, tailoring-rule, operation-type, procedure-step, and procedural-detail definitions. Merge duplicate definitions only when source-supported identity is clear. Preserve disagreements and report provenance.

Record the reuse assessment:

- linked consolidated tailoring-application IDs.
- `lineage_reuse_level`, using the R0 through R4 reuse level codes defined above.
- lineage-reuse-level reason linked to its prerequisite records.
- conflicting evidence linked to issue records.
- `evidence_basis`.
- `support`.
- `support_reason` with basis references and limitation codes.

Read contributing report artifact reuse levels from the linked report-level reuse records. Derive demonstrated settings, demonstrated coverage, failed applications, and applications outside the declared envelope from the linked consolidated tailoring applications. Do not copy these details into the lineage assessment.

Assign `lineage_reuse_level` from the combined lineage evidence. Do not assign R3 or R4 until the corresponding consolidated tailoring application below is complete, includes post-tailoring assurance, and meets the required adopter condition.

After resolving the lineage, assign its `lineage_id` to each matching report-level artifact reuse record and artifact-containing report-level application. This ID assignment is the only change made to those report-level records during the cross-report pass.

### Consolidated tailoring application

Create one separate row for each actual artifact adoption or tailoring event represented across the lineage reports. Include every report-level application whose `application_objects` contains `artifact`. Applications without an artifact are not consolidated in the artifact-lineage pass. Merge repeated reporting of the same event only in this consolidated row. Keep every contributing report-level application unchanged.

Record identity and setting:

- `tailoring_application_id`.
- `lineage_id`.
- linked `report_application_id` values.
- `application_objects`, which always contains `artifact` and also contains `method` or `workflow` when their links are present.
- linked `model_generation_method_id` values when applicable.
- linked `workflow_id` values when applicable.
- linked report IDs, family IDs, and `eps_case_id` values.
- target source wording and typed target references.
- adopting team source wording and team entity IDs.
- relationship to the originator, using `originating_team`, `same_organization_operationally_separate`, `outside_originating_organization`, `independent_evaluation_only`, or `unclear`.
- lifecycle purpose source wording, controlled lifecycle stages, and decision IDs.
- relationship to the declared applicability envelope, using `inside`, `boundary`, `outside`, or `unclear`.
- material setting difference source wording and relationship IDs.

Read shared setting details through the linked report applications and their source records. Do not copy mission or platform, EPS architecture and interfaces, orbit, environment, modes and loads, model abstraction, tool identities, or organization and process into the consolidated application. Link tool IDs from each executed operation.

Use the relationship-to-originator and relationship-to-DAE codes defined for report-level applications.

Record tailoring or adaptation performed with the source fields and normalized references defined for report-level applications. Consolidated operation rows also link their report-level application-operation IDs and preserve full contributing-report provenance.

Record tailoring or adaptation effort through the `implementation_record_id` values linked by the contributing report-level applications. Keep the complete effort and burden details in those implementation records. Do not infer low effort from parameterization, automation, a small mission, or the absence of a reported burden.

Record result and assurance with the report-level source fields and normalized links. Include resulting model-artifact IDs, configuration entity IDs, decision IDs, trade-off finding IDs, criterion IDs, assurance check and RQ3 activity IDs, discrepancy issue IDs, and linked report results.

Record independence:

- personnel overlap source wording, controlled overlap status, and implementing team IDs.
- implementation control source wording and controlling team IDs.
- adopter-attributable evidence for adoption plus typed evidence references.
- adopter-attributable evidence for assurance plus typed evidence references.

An outside team normally qualifies as independent when the artifact lineage, method identity, or workflow identity, adoption, and assurance are established. A team in the same organization qualifies only when it controls the implementation or adaptation, the originating team performs no substantive implementation or adaptation work, and the assured application is distinct.

## Simplified appraisal

Apply the inline appraisal defined in this section. Do not create a separate methodological-appraisal table or claim-support object.

Every evaluative RQ1 claim, every RQ2 finding, every RQ3 activity, every report-level artifact, method, or workflow reuse conclusion, and every lineage-level artifact reuse conclusion receives:

- `evidence_basis`.
- `support`.
- `support_reason`.

The support reason states the strongest evidence and the main claim-relevant limitation. It links `basis_refs` and records controlled `limitation_codes`. Keep it bounded to the claim. A narrow executed-result finding can be supported while a broad benefit or transfer claim from the same report is unsupported.

Record comparator adequacy only for comparative or causal claims. Record relationship to the originator and post-tailoring or post-application assurance only for reuse claims. These conditional fields provide the needed appraisal without a general domain matrix.

## Calibration, consistency, and validation

Before full extraction:

1. [ ] Test report-level eligibility and Route A or Route B coding on clear and borderline examples.
2. [ ] Test the complete report form on a varied sample containing Route A and Route B reports, reference catalog entities, typed quantities, decisions, relationships, rules, checks, resources, issues, typed tools and equipment, per artifact identity, model roles and availability, model generation methods, workflow-scope arrays, construction sources, ordered method steps and workflow activities, atomic and aggregate automation levels, generic-model derivation, linked procedural-detail assessments, typed EPS elements and requirements, linked exchange-type and dependency-type arrays and bridges, several structured model representations, relationships among views, sequence or activity behavior occurrences, boundary roles, coverage assessments, disciplinary viewpoints, representation-level abstraction, decomposition visibility and fidelity, item level inputs, evaluation-design components, methods integration, typed outputs and statistics, normalized RQ1 claims, RQ2 role, direction-component and lifecycle-stage arrays, ordered RQ3 activities, model and digital twin assessment aspects and methods, verification levels, test phases, virtual and physical execution, exact model configurations, figures or tables, structured variation points with target-type arrays, tailoring rules and procedure steps, executed tailoring operations, artifact-type arrays, scoped artifact generality, application-object arrays, procedural-evidence flags, complete reusable-artifact and report-level application fields, `lineage_mentioned`, and report-bounded artifact, method, and workflow reuse levels. Include a report that can reach R3 or R4, M3 or M4, or W3 or W4 by itself when available.
3. [ ] Test cross-report family and lineage-identity resolution, immutable report-level records, separate lineage-level extraction, and separate consolidated application, effort, assurance, independence, and reuse-level fields on at least one multi-report example.
4. [ ] Calibrate `named_only`, `narrative_outline`, `actionable_procedure`, `reproduction_ready`, and `unclear` on model generation, workflow, and tailoring examples. Confirm that procedural detail remains separate from reuse level.
5. [ ] Calibrate the difference between assertion, worked example, execution, comparison, physical or operational checking, and independent transfer.
6. [ ] Calibrate `supported`, `limited`, `unsupported`, and `unclear` on narrow and broad claims from the same report.
7. Revise and freeze the codebook, schema, audit procedure, and calibration decisions before full extraction.

### Sole-reviewer extraction and verification

One LLM reviewer performs the primary extraction, cross-report extraction, test–retest extraction, and final review judgments. One human auditor performs the focused audits and controls every write to the canonical extraction. Verification uses one focused audit, deterministic validation, and a delayed LLM test–retest sample.

Apply this sequence:

1. **Primary extraction.** The LLM reviewer extracts the complete report into the frozen report-level form.
2. **Focused audit.** For every included report, the human auditor checks eligibility and route, canonical entities, typed quantities, decisions, relationships, rules, checks, resources, issues, typed record references, typed tool records, per artifact metadata and model roles, artifact-type arrays and scoped generality, item level inputs, evaluation-design components, methods integration, typed outputs and statistics, EPS elements and requirements, exchange-type and dependency-type arrays, model representations, representation-level abstraction, decomposition visibility and fidelity, relationships among views, dynamic behavior occurrences, boundary roles, Route B anchors and bridges, coverage coding, omitted or duplicated groups, method steps, workflow activities, workflow-scope and aggregate automation arrays, generic-model derivation, procedural-detail levels, normalized RQ1 claims, direct RQ2 attribution, RQ2 role, direction-component and lifecycle-stage arrays, direct RQ3 linkage, RQ3 activity order, exact artifact and configuration links, verification levels, test phases, model and digital twin assessment coding, virtual and physical execution, model-to-test closure, `lineage_mentioned`, complete report-level reuse and application-object coding, variation-point target arrays, structured tailoring evidence, every report-level R3/R4, M3/M4, or W3/W4 assignment, procedural-evidence flags, citations, source-versus-inference distinctions, and reviewer-derived values. The auditor may see the extraction because the audit's purpose is error detection.
3. **Deterministic validation.** Validate schema versions, controlled values, canonical keys, IDs, typed record references, required fields, links, procedure-level prerequisites, reuse-level prerequisites, procedural-evidence flags, quantity forms, units, currencies, sample sizes, and reproducible calculations. Confirm each citation's report and page range. For citations without `graphic` or `graphic_quote_description`, confirm the verbatim quotation against the stored source using the frozen page-text extraction and normalization rule. Preserve source values and reviewer-derived values separately.
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

An issue is impactful when it can change eligibility or route, a report family or lineage, an artifact, method, or workflow reuse level, a procedural-detail level or profile flag, a reuse or tailoring application, direct RQ2 or RQ3 status, outcome direction, support, a quantitative result, or a synthesis conclusion. An impactful issue that may recur triggers a targeted check of every report or lineage that could be affected. Record any codebook change, focused recalibration, and recheck scope.

Do not calculate inter-rater reliability between the reviewer and an LLM. Report audit coverage, issues raised, accepted corrections, rejected flags, unresolved ambiguities, and test–retest differences with their denominators.

Before synthesis, validate every report-level extraction and every separate family, lineage, and consolidated application table against the frozen schema. Confirm that every included report has a completed focused audit, every raised issue has a recorded resolution or unresolved status in the audit summary and Git history, every derived value is reproducible, every lineage-level field preserves report provenance, and cross-report processing changed only report-level `lineage_id` values.
