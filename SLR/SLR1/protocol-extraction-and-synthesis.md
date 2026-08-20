# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Extraction and synthesis

> **Protocol parts:** [1 — Scope and definitions](protocol.md) · [2 — Discovery and appraisal](protocol-discovery-and-appraisal.md) · **3 — Extraction and synthesis** (this file) · [Supporting need assessment — Prior secondary reviews](protocol-prior-secondary-reviews.md)
>
> **Definitions used here:** [eligible EPS evidence routes](protocol.md#eligible-eps-evidence-routes), [bounded genericity](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring), and [unit-level evidence appraisal](protocol-discovery-and-appraisal.md#unit-level-evidence-appraisal).

## Extraction fields

Before extracting any report, create a new `extraction_codebook.json` for this run from this protocol. Earlier codebooks and forms do not govern this run. Do not copy their contents into new-run fields. Create and calibrate it under task [`E-001`](TASKS.md), then perform full extraction and validation under [`R-005`](TASKS.md).

For every controlled code that matters to the synthesis, record:

- the reason for the code;
- a direct quotation or source location when possible; and
- a coding-confidence rating of `high`, `moderate`, or `low`.

Coding confidence records how certain the extractor is that the source was located and interpreted correctly. Use `high` for explicit and unambiguous source support, `moderate` when a bounded interpretation or reconstruction is required but supported, and `low` when material ambiguity remains. A low coding-confidence value does not replace the controlled status `uncertain`; record both when appropriate. Coding confidence is not a judgment of methodological quality or evidential strength. Keep these four concepts distinct throughout the codebook and synthesis:

- **coding confidence:** certainty in extraction or classification;
- **methodological appraisal:** fitness and conduct of the evaluation used to support a claim;
- **record-level claim support:** support supplied by one evidence unit for one bounded claim; and
- **conclusion confidence:** confidence in a synthesis conclusion across contributing units.

Keep these statuses separate: `not_reported`, `not_applicable`, `none`, and `uncertain`. Also distinguish what the authors report from what the extractor infers.

### Shared extraction structures

Use shared structures rather than copying the same facts into several records:

- An **evidence reference** stores report ID, page or section, figure or table when relevant, quotation or cautious paraphrase, and coding confidence.
- A **setting tuple** stores platform and form factor; mission purpose and domain; orbit and environment; lifecycle use and decision; EPS boundary, architecture, components and interfaces; modes and load profile; abstraction or fidelity; required inputs; language, tool and version; organization, team and process; prerequisites; and exclusions or failure boundaries.
- An **implementation footprint** stores roles, skills and training; staffing; process and automation; tools, licences and infrastructure; model and data preparation; computing; integration and interoperability; governance and configuration control; effort, time, schedule and cost; maintenance; burdens; and mitigations.
- A **measurement** stores the construct claimed, the actual measure and its definition, and whether it is `direct`, `surrogate`, `intermediate_or_process`, or `unclear` for that construct. Also store the author's justification or validation for a surrogate; observed versus expected status; setting, scenario, population or observational unit; unit and time basis; sample size and denominator; source-reported values; central tendency and dispersion; absolute and relative differences; effect estimate, standard error or confidence interval, exact p-value and statistical method when reported; missing observations and exclusions; and practical interpretation. A measure can be direct for one narrow claim and surrogate for a broader claim, so record the claim scope.
- A **comparator** stores its type—`concurrent_control`, `before_after`, `historical_mission`, `earlier_model_or_version`, `manual_or_document_based_process`, `alternative_toolchain_or_method`, `none`, `other`, or `unclear`—and a complete description of the baseline. Record whether it is concurrent or historical and planned or retrospective; task, inputs, mission, lifecycle stage, team, experience, training, tools, automation, time available, outcome definition, and data completeness; material differences from the evaluated condition; and an adequacy judgment with reason, evidence reference, and coding confidence. A comparator is required only for a comparative or causal claim.
- A **confounder assessment** stores each factor that might offer an alternative explanation, including team experience, student or practitioner status, training, model maturity, inherited artifacts, automation, mission complexity, lifecycle stage, data quality, concurrent architecture or process changes, schedule pressure, organizational support, verification effort, and evaluator involvement. Record provenance as `author_identified`, `reviewer_noted_only`, `not_reported`, or `not_applicable`, and record all applicable handling tags from `measured`, `controlled_by_design`, `adjusted_in_analysis`, `discussed_uncontrolled`, and `not_reported`. Also record any reported direction, handling, residual concern, evidence reference, and coding confidence. Reviewer-noted factors inform appraisal but are not primary-study findings.
- A **derived-value record** preserves every reviewer calculation separately from the reported data. Store source measurement and value IDs, original values and units, formula or transformation, unit conversion, assumptions, missing-data handling, analysis-code path and version when used, extractor, deterministic recomputation or check details, linked verification-pass IDs, derived result, and sensitivity to reasonable alternative assumptions. Never overwrite a source-reported value with a reviewer-derived value.
- A **verification-pass record** documents one check without treating the checker as another evidence source. Store its pass ID; linked report and extraction IDs; actor type (`sole_reviewer`, `supervisor`, `llm`, or `deterministic_code`); pass kind; date; scope; whether the canonical extraction and other audit outputs were hidden or visible; codebook, prompt or procedure, source-file, rendered-input, and extraction hashes; model provider, exact model or snapshot identifier, reasoning and generation settings, tools, and document-ingestion route when applicable; pages, figures, tables, fields and record types covered; completion or failure status; secure versioned output reference and hash; and linked discrepancy IDs. It is an audit structure, not an analytic evidence unit or denominator.
- A **verification-discrepancy record** stores the linked pass, report, object and field; discrepancy type; original and proposed values; evidence references; whether the issue is material; final human disposition; final value; reason; affected linked objects; corrective or escalation action; and adjudication date. Preserve rejected model flags as well as accepted corrections so model behavior and human adjudication can be reported honestly.
- A **methodological-appraisal object** implements the scoped design and domain appraisal defined in [Part 2](protocol-discovery-and-appraisal.md#unit-level-evidence-appraisal). Store its appraisal ID; linked report, family, thread, artifact or profile, application, measurement, outcome or burden, and V&V IDs; design classification; domain statuses, reasons, evidence references, and coding confidence; and no aggregate score or pass.
- A **record-level claim-support object** stores the linked record and claim, claim kind and scope, relevant measurement, comparator, confounder and appraisal IDs, dependence and applicability, support classification of `unsupported`, `weak`, `moderate`, or `strong`, and a source-located reason. Evidence type and maturity are descriptors and cannot determine this classification by themselves.

Give each shared object an ID, scope, evidence reference, and coding confidence where interpretation is involved. Link it from report, thread, artifact, application, outcome, or V&V records as appropriate. Keep declared, planned, source-observed, and reviewer-derived values separate even when they use the same structure.

Use the claim-support classes consistently across questions, always within the recorded claim scope:

- **`unsupported`:** the source supplies no extractable observation or result bearing on the claim, or the supplied result does not measure the claimed construct.
- **`weak`:** there is an extractable basis, but it is materially indirect, relies on an unjustified surrogate, has serious methodological concerns, or lacks a minimum element required for that kind of claim.
- **`moderate`:** the minimum elements for the claim kind are present and a direct or justified measure supports a bounded result, but important limitations remain in method, independence, comparison, precision, or applicability.
- **`strong`:** direct or credibly justified measures and a fit, adequately conducted evaluation support the specific bounded claim; every comparator, counterfactual, and confounding requirement applicable to that claim is met, with no major unexplained methodological concern.

A strong classification can apply to a narrow within-case fact and does not imply prevalence, transferability, causality, or broad applicability unless those are the claims appraised.

### Report-level bibliographic and review-management fields

For each report, record:

- the new-run report ID, optional old corpus ID, and extraction-file path;
- full citation, title, authors, year, venue or institutional report series, publication type and status, DOI, arXiv identifier or URL, publisher or issuing organization, source or report ID, version used for extraction, version dates, any later formal counterpart, and any reported peer or technical review;
- every linked new-run discovery-event ID and source record ID; keep the exact query or citation route, date, rank, and raw-file provenance once in the new search log and manifest;
- title and abstract screening tier and reason;
- final full-text decision and exclusion reason, if excluded;
- Route A or Route B and the supporting evidence;
- contribution status for RQ1, RQ2, and RQ3;
- the number of linked artifact-lineage profiles and tailoring applications for RQ1;
- the number of eligible RQ2 outcome or burden records;
- the number of direct and near-miss RQ3 records;
- study or implementation report-family ID or IDs;
- linked artifact-lineage ID or IDs;
- the report's relationship to each family or artifact: `same_report_manifestation`, `derivative_report`, `companion_report`, `overlap_uncertain`, or another controlled value;
- the reason and evidence for family membership or artifact identity, overlap coding confidence, and notes on shared results; and
- overall coding confidence, primary human assessor, linked verification-pass and discrepancy IDs, and review-pass history.

For a thesis or dissertation, also record:

- degree level and name;
- institution, country, and department;
- completion status;
- persistent IDs from PQDT, OATD, and the repository;
- formal publication or issue date and the basis for that date;
- defence, approval, award, deposit, public-release, embargo, and indexing dates when reported;
- repository and full-text version;
- access, embargo, and licence status; and
- degree-examination status, kept separate from peer review.

For an arXiv preprint, also record:

- arXiv identifier and subject category;
- every version number and submission date;
- the earliest version containing the substantial completed report;
- the version available at the common evidence cutoff and the version used for extraction;
- any withdrawal, replacement, journal reference, DOI, or formal publication counterpart; and
- substantive differences among eligible manifestations when reported or observed.

### Report and implementation context and MBSE qualification

Record:

- mission or platform, form factor or mass when reported, mission name and domain, organization type, and project maturity;
- lifecycle stage actually demonstrated, kept separate from stages that authors only claim or plan;
- development setting: academic or student, agency, industry or NewSpace, distributed team, agile or concurrent design, rapid prototyping, resource-constrained mission, or `not_reported`;
- a general implementation-footprint link for reported MBSE needs and burdens, or `not_reported`;
- the authors' objective, problem, intended decision, and reason for using MBSE;
- each evaluation design used in the report and linked methodological-appraisal ID, keeping materially different evaluations separate;
- evidence that the work qualifies as MBSE: method or language, tools, system-model artifacts, modeled concerns, explicit relationships, and system boundary;
- model maturity: conceptual framework, reference or template, prototype, executable, used on a project, physically validated, operational or flight, or `not_reported`. More than one value may apply. Do not assume they form an order unless the report does;
- toolchain structure, data flow, interoperability method, ownership and handoff, and reported limits; and
- availability of models, profiles, libraries, scripts, data, configurations, and documentation.

### EPS-model-thread record

Create one record for each qualifying EPS thread. Record:

- thread ID and report ID;
- thread route and role: EPS-primary or embedded EPS;
- host-model anchor for an embedded thread;
- EPS model anchor and EPS system boundary;
- each explicit bridge, its relationship type, and source location;
- EPS concerns represented: requirements, function, behavior, architecture, components, ports or interfaces, modes or operations, parametrics or budgets, decisions or trades, risks or faults, V&V, or another concern;
- EPS elements represented: generation or solar array, storage or battery management, conversion or regulation, conditioning or distribution, protection, monitoring or control, bus or harness, loads or interfaces, modes, margins, degradation, fault management, or another element;
- model artifacts and tools that carry the thread;
- level of abstraction or fidelity and any phenomena deliberately left out;
- purpose and supported decisions: definition or sizing, requirements or traceability, trade study, interface management, executable analysis, V&V, reuse or tailoring, communication, continuity across the lifecycle, or another purpose;
- reuse or tailoring approach: template, reference model, profile, library, pattern, transformation, reusable workflow, open package, method guidance, mission-agnostic architecture, interface-focused model, mission-specific model with a reusable method, or another approach;
- tailoring choices, retained and omitted content, reasons and trade-offs, and links to the applicable implementation-footprint and application records;
- any author description such as *lightweight*, *scalable*, *comprehensive*, or *resource-intensive*. Do not impose a lightweight threshold or infer one from the mission class;
- linked artifact-lineage, profile, and tailoring-application IDs;
- genericity disposition and method- or workflow-only status when relevant; and
- thread maturity, lifecycle stage, availability, direct source support, coding confidence, limitations, and any methodological-appraisal or claim-support IDs used for evaluative characterizations.

### Reusable EPS artifact-lineage and genericity-profile record

Register every identifiable EPS-linked artifact. Create a separate profile for each lineage, version, or scope that needs separate assessment to avoid hiding a material change.

Record identity and provenance:

- artifact-lineage ID and genericity-profile ID;
- linked family, report, and thread IDs;
- every base-to-derived or version relationship supported by a source;
- artifact type: structured system model; reference or template model; metamodel; modeling profile; library or pattern; interface contract; parametric package; transformation or generator with persistent content; larger model with a separable EPS part; method or workflow only; toolchain only; another type; or `unclear`;
- artifact name, version, repository, package, and model IDs;
- owner or developer;
- availability and licence when reported; and
- lineage coding confidence and reason.

A common tool, organization, term, or topic does not prove a shared lineage.

Record the source's claim:

- exact source terminology and claim wording;
- the claimed object and the person or group making the claim;
- claimed reuse or genericity scope;
- whether the claim concerns the artifact, method or workflow, toolchain, language or profile, whole spacecraft, or is unclear; and
- genericity disposition: `not_an_artifact_or_method_only`, `artifact_no_reuse_indication`, `genericity_or_reuse_claim`, `reported_reuse_without_bounded_specification`, `bounded_reuse_candidate`, or `unclear`.

Record the declared applicability envelope as a declared setting tuple. Use `not_reported` separately for each missing dimension, preserve the source for every value, and record whether the minimum DAE in Part 1 is met.

Record the reusable design:

- retained core, including elements, relationships, constraints, meanings, interfaces, libraries or packages, and IDs, with source locations;
- each variation-point ID and location;
- allowed range or options and default;
- dependencies and constraints;
- type of operation and reason; and
- whether the source declares the variation point or it can only be reconstructed from an explicit base-to-derived mapping.

Record tailoring support:

- tailoring rules and process;
- required inputs and roles;
- governance and configuration control;
- automation;
- any bounded rule for reuse without change;
- linked tailoring-application IDs;
- claimed envelope and demonstrated setting tuples, kept separate;
- number of materially different applications after duplicate reporting is merged; and
- evidence used to decide whether applications differ materially.

Record the evidence assessment:

- status, reason, source location, and coding confidence for every A/E/C/T/P/I gate;
- failed condition or conditions;
- highest tier: `NA`, `G0_artifact_only`, `G1_claimed_or_unbounded`, `G2_bounded_reuse_specified`, `G3_bounded_reuse_demonstrated`, or `G4_independently_corroborated`;
- a locatable cumulative reason for that tier;
- claim agreement: `not_evaluated`, `supported_in_tested_contexts`, `partially_supported`, `mixed`, `not_supported`, or `unclear`; and
- failed and outside-envelope applications and other possible explanations.

Finally, record profile limits, model and data availability, dependence between report families and within the lineage, evidence source, coding confidence, and first- and second-check history.

Apply the gate rules in Part 1. Combine reports only after establishing a shared lineage, preserve report provenance for every combined field, and never transfer a result to another version or application without evidence.

### Tailoring-application record

Create one record for each application of an artifact lineage to a target setting. Include a justified unchanged adoption.

Record identity:

- tailoring-application ID;
- artifact-lineage and profile ID;
- linked family, report, and thread IDs;
- target model or configuration ID; and
- reason for treating reports as the same or different application.

Record one observed target-setting tuple for the application. Classify its relationship to the DAE as `inside`, `boundary case`, `outside`, `unclear`, or `DAE not reported`, and give the reason. State which material dimensions distinguish this application from other credited applications.

Record what happened to the artifact:

- base or core content retained, with evidence;
- content configured, parameterized, selected, specialized, extended, deleted, substituted, mapped, transformed or generated, rebuilt, or deliberately left unchanged;
- affected variation-point IDs;
- before-and-after or base-to-derived trace; and
- reason for the changes or unchanged use.

Record an application-scoped implementation footprint, including its tailoring inputs and assumptions. Do not assume that parameterization or a small mission means little effort.

Record the result:

- resulting artifact and use;
- decisions or analyses supported;
- availability and configuration ID;
- failures, rework, and trade-offs;
- whether this shows artifact reuse, only method or workflow reuse, or is unclear; and
- linked measurement, derived-value, comparator, confounder-assessment, methodological-appraisal, and claim-support IDs for any evaluative claim about the application.

Record post-tailoring assurance:

- intended-use criterion or oracle and its source;
- method;
- execution timing;
- result or verdict;
- discrepancies and how they were handled; and
- whether every P-gate condition is met.

Link an RQ3 record only if the application separately passes the RQ3 eligibility rule.

Record the adopter or evaluator relationship as one of:

- originating or same team;
- same organization but operationally separate team;
- outside organization or team;
- independent evaluation of only the originator's instance; or
- `unclear`.

Also record overlap in personnel and control of the implementation; the independent adopter or evaluator's own report, artifact, or data provenance; report-family evidence; separate evidence for adoption or tailoring and assurance; and whether the I gate is met.

Record the evidence source, coding confidence, methodological limitations, and extraction and second-check history.

One application can inform RQ1 and link to an RQ2 outcome or burden or an RQ3 V&V record. It enters those direct syntheses only when it separately meets their attribution and linkage rules.

### Input and assumption record

Create one record for every material input or assumption reported for an EPS thread. An item is **material** when it does at least one of the following:

- defines the EPS boundary;
- sets behavior or a scenario;
- supplies a criterion;
- affects a reported output or decision; or
- limits claimed applicability.

Record:

- input or assumption ID and thread ID;
- type: mission requirement; orbit or environment; operating mode or load profile; architecture or interface; generation; storage; conversion or distribution; component performance or loss; degradation or lifecycle; margin or uncertainty; control or fault; model-fidelity or tool assumption; V&V configuration; or another type;
- parameter or construct;
- reported value or description;
- units and time basis;
- whether it is nominal, worst-case, a range, or a distribution;
- source: mission requirement, standard or handbook, vendor data, test or flight data, heritage or earlier mission, literature, tool default, analyst assumption, calculation or derivation, or `not_reported`;
- handling of uncertainty, variability, margin, sensitivity, and degradation;
- stated reason: mission or environment limit, early-phase uncertainty or missing data, conservatism or safety, reuse or tailoring, computing or tool limit, interface standard, decision need, V&V need, or not stated;
- trace location in a requirement, model element, parameter, figure or table, data file, or external-tool link;
- reported effect on outputs or decisions; and
- evidence source and coding confidence.

Do not infer that an input is unnecessary because the source omits it. Use `not_reported` for source silence.

### EPS engineering outputs

Keep technical outputs separate from MBSE outcome and burden records. For each output, record:

- output ID and thread ID;
- linked measurement ID and the source-reported quantity or result in its original form, units, and time basis;
- scenario or configuration, input set, sample or repetition denominator when relevant, and missing or excluded observations;
- whether it was calculated, simulated, checked against a criterion, compared, or physically validated;
- criterion, comparator, uncertainty, sensitivity, and reported statistical information when present;
- decision or model artifact it informed;
- any linked derived-value ID, without replacing the reported value; and
- evidence reference and coding confidence.

An engineering output can be a direct measure of its stated quantity while remaining a surrogate for reliability, assurance, schedule, cost, or another broader construct. Link it to RQ2 or RQ3 only under those questions' normal attribution, measurement, and support rules.

### RQ2 outcome and implementation-burden evidence record

Create one atomic record for every candidate outcome or burden that is explicitly or plausibly linked to a qualifying EPS thread. Do not extract every general MBSE claim merely because it appears in an eligible report. Split a statement that reports several outcomes into separate records. Link records that share evidence through source IDs.

Record the claim and its scope:

- record ID and linked thread ID;
- exact result or claim, or a cautious paraphrase;
- primary claim kind: `descriptive_occurrence`, `feasibility_or_executed_result`, `technical_performance`, `comparative`, `causal_attribution`, `experiential_or_perceived`, `implementation_burden`, `transfer_or_generalization`, `other`, or `unclear`, with additional tags when one statement has more than one role;
- role: outcome, implementation burden, mixed trade-off, or another role;
- scope, target, population or observational unit, and time horizon;
- outcome category: EPS reliability; system or mission assurance; defect or error reduction; risk reduction; reproducibility or rerunnability; reuse or replication; integration or interoperability; interface consistency; traceability or requirements quality; completeness; continuity across the lifecycle; decision or trade support; cost; schedule; effort or automation; communication or knowledge; governance or value realization; or another category;
- reported direction: `beneficial`, `null/no observed effect`, `mixed/conditional`, `adverse`, or `unclear/not reported`;
- author-claimed direction using the same codes; and
- evidence-supported direction using `beneficial`, `null/no observed effect`, `mixed/conditional`, `adverse`, `unclear`, or `not_supported`, kept separate from the author's wording.

Record the basis for direction:

- linked measurement IDs and how each measure is interpreted for this claim;
- whether each measure is direct, surrogate, intermediate or process, or unclear for the claimed construct;
- criterion and linked comparator ID when applicable;
- magnitude, units, uncertainty, sample size or denominator, and conditions;
- linked derived-value IDs; and
- whether the result is source-observed, author-expected, or reviewer-derived.

For a burden, record:

- category: time or effort; skills or training; staffing; tools, licences, or infrastructure; model or data preparation; computing; integration or interoperability; maintenance, configuration, or governance; schedule; cost or resource use; another category; none reported; or not reported;
- affected person or group;
- whether it occurs during adoption or ongoing use;
- measurement method, including logs, accounting data, observation, survey, interview, or assertion;
- mitigation; and
- any linked benefit or trade-off.

For reliability, use the relevant subtype: EPS reliability, system or mission reliability, process reliability, model consistency or reliability, mission assurance, defect or error reduction, generic reliability claim, or not applicable. A technical proxy such as margin, trace count, or successful execution remains a surrogate unless the source validates its relationship to the reliability or assurance construct claimed.

Record the proposed MBSE mechanism:

- artifact traceability;
- requirements links;
- executable simulation;
- parametric analysis;
- reference-model reuse;
- automated generation;
- transformation;
- shared repository;
- tool integration;
- interface management;
- lifecycle-gate support;
- model-derived V&V; or
- another mechanism.

Also record the linked artifact or process and lifecycle stage.

Classify attribution as `explicit EPS-thread attribution`, `ambiguous attribution`, or `generic/not eligible`. Only explicit EPS-thread attribution enters direct RQ2 synthesis. Explicit attribution records what the authors attribute to MBSE; it does not by itself demonstrate association or causation. Record author attribution, observed association, and reviewer assessment of causal support separately.

Classify evidence type as:

- assertion only;
- conceptual or illustrative;
- single-case demonstration;
- executable result;
- trade or requirements-check result;
- quantitative metric without a comparator;
- quantitative comparison;
- stakeholder or expert evaluation;
- reuse or replication; or
- integration, test, operational, or flight evidence.

Evidence type is descriptive. It does not determine claim support. Link every eligible direct RQ2 record to:

- a comparator object when the claim is comparative or causal, and `not_applicable` otherwise;
- confounder assessments for material alternative explanations;
- the methodological-appraisal object for the evaluation supplying the evidence, or `not_applicable` with a reason when an assertion, concept, or illustration has no empirical or evaluative design to appraise; and
- one record-level claim-support object.

Apply the canonical record-level claim-support classes defined under [shared extraction structures](#shared-extraction-structures) and these RQ2-specific minimums:

- A descriptive occurrence can be strongly supported within one case by direct, locatable evidence and credible ascertainment; this says nothing about prevalence or transfer.
- A feasibility or executed-result claim requires a defined artifact or activity, execution, and result, plus a criterion when the claim entails checking. Successful execution alone does not establish validity.
- A comparative claim requires the same construct to be measured under an adequately described and reasonably comparable baseline.
- A causal claim requires a credible counterfactual and serious treatment of material confounding; explicit author attribution, temporal sequence, or a quantitative value alone is insufficient.
- An experiential or burden claim can be strongly supported by transparent sampling, collection and analysis of traceable participant evidence or work records; it does not require a comparator unless comparative language is used.
- A transfer or genericity claim remains governed by the A/E/C/T/P/I gates. Do not substitute this support label for a genericity tier.

Record evidence references, coding confidence, possible alternative explanations, dependence and report-family or nesting notes. Null, adverse, and beneficial directions use the same support rules.

### RQ3 V&V record

Create one atomic record for each candidate target–method–scenario activity or artifact. Keep plausible near misses so that exclusion from direct EPS-linked RQ3 synthesis can be audited. Do not extract every unrelated system-level V&V activity.

Record linkage and classification:

- V&V record ID and linked thread ID;
- EPS target, or system-level target with a clear EPS link;
- target type and requirement or criterion ID when reported;
- model element or artifact and explicit model-to-V&V bridge;
- the source's words for verification, validation, V&V, checking, or analysis;
- linkage scope: `eps_specific`, `system_wide_eps_linked`, `system_wide_cooccurrence`, or `unclear`, with evidence and reason;
- normalized V&V object: model verification, model validation, system or design verification, system or design validation, multiple, or `unclear`, with a coding reason; and
- eligibility disposition: analysis only, direct EPS-linked V&V, system-wide co-occurrence near miss, or `unclear`.

Record the activity:

- method or artifact: requirements-in-the-loop, parametric or constraint check, simulation scenario, model checking, trade verification, virtual integration, verification matrix, test case or process, generated test artifact, automated test, MIL, SIL, PIL, HIL, or another method;
- execution setting and hardware present;
- how physical the activity is relative to the target EPS;
- criterion or oracle and its source;
- timing relative to physical realization, integration, and testing;
- lifecycle stage; and
- status: proposed only, prepared or generated, executed virtually, result or verdict reported, downstream physical link demonstrated, or model-to-test closure demonstrated.

Record results and completeness:

- result or verdict;
- linked measurement and derived-value IDs, including directness of each measure for the asserted V&V claim;
- whether the result is EPS-specific, system-wide, or `not_reported`;
- how discrepancies were handled;
- later link to software integration, hardware integration, flat-sat or bench work, PIL or HIL, environmental testing, operational validation, or flight evidence;
- EPS-linked RQ3 eligibility as `yes`, `no`, or `uncertain` for the target–bridge–V&V-method/intent rule, including the failed condition when the answer is no;
- criterion-complete status as `yes`, `no`, or `uncertain`, with evidence; and
- demonstrated pre-physical execution as `yes`, `no`, or `uncertain`, with evidence about timing, physicality relative to the target, and result.

For every direct RQ3 record, link the methodological-appraisal object for the evaluation, or use `not_applicable` with a reason for a proposed or prepared activity with no evaluation to appraise. Link relevant confounder assessments and a comparator object only when a comparative or effectiveness claim requires one. Create at least one record-level claim-support object, and create separate objects when one V&V record is used to support more than one materially different claim, such as execution and validation.

Apply claim-specific support rules:

- target, explicit bridge, and V&V method or intent can support only the existence of an EPS-linked V&V activity;
- a criterion, execution, and result are required to support an executed-check or verification-result claim;
- model or design validation additionally requires a credible intended-use oracle or authoritative reference and an evaluation fit to that comparison;
- model-to-test continuity requires a source-supported link to the later physical artifact or activity; and
- closure requires compared results and reported handling of discrepancies.

A physical, operational, or flight setting strengthens only a claim that the linked evidence actually tests. It does not automatically validate a model, establish causal effectiveness, or upgrade another V&V claim. Record evidence references, coding confidence, methodological limitations, record-level claim support, applicability, dependence, and report-family or nesting notes.

### Limitations and open extraction

Record author-stated limits, assumptions, and scope boundaries. Use narrow controlled flags for substantive limitations such as prototype or future work, single case, no comparator, no independent validation, assumptions or data-quality limits, tool dependence, interoperability limits, and incomplete lifecycle coverage.

Do not manually duplicate conditions already represented by structured fields. Derive flags such as missing V&V criterion, unclear EPS linkage, missing DAE, unidentified reusable core, unclear lineage, same-family reuse only, absent post-tailoring assurance, unjustified surrogate, missing or inadequate required comparator, material uncontrolled confounding, or serious methodological concern during validation. This keeps the flag and its source field consistent.

Use emergent codes for unexpected findings that do not fit the controlled vocabulary. Do not silently add new controlled categories during extraction.

## Calibration, consistency, and validation

Before full screening and extraction, complete calibration task [`E-001`](TASKS.md):

1. Test the full-text eligibility rule on examples of clear Route A, clear Route B, general whole-spacecraft MBSE, and non-MBSE EPS work.
2. Test all forms and shared structures on a deliberately varied sample. This includes the thread, input and assumption, measurement, comparator, confounder, derived-value, methodological-appraisal, claim-support, verification-pass, verification-discrepancy, artifact-lineage and profile, tailoring-application, RQ2 outcome and burden, and RQ3 V&V structures. Include model or simulation evaluation, case or experience evidence, comparative evidence, survey or qualitative evidence when available, and mixed-method evidence.
3. Calibrate claim-specific support on deliberately contrasting examples: a direct single-case descriptive fact; a flight case that does not establish causal benefit; a credible qualitative burden finding; an unjustified surrogate; a confounded comparison; an executed virtual check; a validation claim without an adequate oracle; and a reviewer-derived calculation. Also include method-only versus artifact reuse, claim-only evidence, bounded specification, one versus several materially different settings, duplicate reports from one family, unchanged reuse, failed transfer, and post-tailoring assurance.
4. Pilot the full blind model-extraction, canonical-audit, cross-report-challenge, deterministic-reconciliation, and manual-fallback procedures on the varied sample. Include at least one report with material figures or tables and one multi-report family or lineage. Confirm complete codebook coverage, document coverage, structured-output validity, unit matching, discrepancy matching, failure detection, and human adjudication before accepting a route.
5. Revise and commit the run-specific codebook, prompts, procedures, and calibration decisions before full extraction.
6. Record all calibration decisions and examples.

### Sole-reviewer extraction and verification

One human reviewer performs the primary extraction and every final adjudication. Routine duplicate human extraction is not available. For every model-permitted included report, the verification design therefore combines one complete blind LLM extraction using the same substantive source, codebook and guidance as the human reviewer with a separate canonical-extraction audit. Use a two-pass sole-reviewer manual fallback otherwise. Also use separate cross-report challenges where a judgment depends on several reports, deterministic validation, a delayed sole-reviewer test–retest sample, and a small supervisor audit if the supervisor is available. The two model passes share the source and codebook and are not independent corroboration. An LLM pass is an automated error-detection aid, not an independent human review, co-reviewer, source of evidence, or final decision maker. A delayed re-extraction by the same reviewer is a consistency check, not independent human replication.

Under task [`E-001`](TASKS.md), freeze and calibrate before full extraction:

- the machine-actionable extraction, verification-pass, and discrepancy schemas;
- versioned prompts and orchestration for complete blind model extraction and canonical-extraction audit;
- the model-selection rule and required run metadata;
- document-ingestion, page and image coverage, OCR, context-limit, and structured-output checks;
- a per-route authorization, provider processing, training, retention, subprocessor, secure-storage, and publication assessment for licensed or restricted full text;
- technical failure, rerun, manual-fallback, and cross-report-bundle rules; and
- the exact sampling frame, strata, pseudorandom algorithm, seed derivation, tie and replacement rules for the test–retest and supervisor samples.

Use fresh contexts and high-capability models at their highest available reasoning or quality setting, with deterministic generation settings where the service offers them. Use different model families for the two passes when available. Exact model or snapshot identifiers and all settings must be recorded for each run; descriptions such as “state of the art” or “maximum settings” are not reproducible by themselves. Do not give either pass an earlier-run extraction, old codebook, prior conversational memory, or unrelated repository material. Freeze the blind model extraction and canonical-audit outputs before comparing them, and do not give either model the other model's output; this reduces direct anchoring but does not make the passes independent.

The human and blind LLM extraction must apply the same scientific eligibility, unit-identification, extraction, appraisal, claim-support, evidence-location, missingness, and coding-confidence rules to the same source content. Only actor and execution metadata may differ. The LLM may execute the codebook in validated stages when one structured response is impractical, but every required stage and every applicable field must complete and validate before the run counts as a full extraction. Missing, truncated, or failed modules make the extraction incomplete rather than a successful partial check.

Apply this sequence to every included report:

1. **Primary human extraction.** The reviewer extracts from the complete source into JSON conforming to the frozen codebook and records evidence references and coding confidence.
2. **Complete blind model extraction.** An LLM receives the complete permitted source and the same frozen codebook and substantive guidance used by the reviewer, but not the canonical human extraction or another audit output. It performs the full extraction task: identify every applicable unit; populate every applicable report, thread, shared-structure, artifact, application, input, output, RQ2, RQ3, methodological-appraisal and claim-support field; use the same controlled missingness values; and provide the required reasons, evidence locations and coding confidence. Save and hash the schema-valid model extraction before any comparison.
3. **Canonical-extraction audit.** In a separate fresh context, an LLM receives the source, codebook, and canonical human extraction, but not the blind model extraction. It checks every controlled value, evidence reference, source-versus-inference distinction, unit and link; challenges unsupported or over-broad interpretations; and searches for omitted or duplicate records. Save and hash its output before reconciliation. This pass may see the human extraction because its purpose is verification rather than blind extraction.
4. **Deterministic validation and reconciliation.** Validate both extractions and the audit output against the schema; check controlled values, IDs, links, counts, source and extraction hashes, and reproducible calculations; and recompute derived values with code where feasible. Use deterministic IDs when the codebook permits them. Otherwise retain model-local temporary IDs and align units using their report, type, scope, semantic identity and evidence locations. Record one-to-one matches, human-only and model-only units, and possible splits and merges; a split or merge difference is a discrepancy to adjudicate, not automatically an error. Only after both model outputs are frozen, compare every aligned field and the canonical-audit findings to generate candidate discrepancies.
5. **Human adjudication.** The reviewer resolves every model, deterministic, test–retest, or supervisor discrepancy against the source. For a report selected for test–retest, defer this step and withhold the canonical extraction and all comparison or audit outputs until the re-extraction is complete. No automated pass may write directly to the canonical extraction. Record accepted corrections, rejected suggestions, genuinely unresolved source ambiguity, and every affected linked object.

The per-report challenge passes must explicitly revisit the following high-consequence judgments while also checking the rest of the extraction:

- eligibility and Route A or Route B assignment for every included report, including every Route B EPS anchor, model anchor, bridge, and source location;
- each report's claimed family and artifact relationships, without deciding a cross-report merge from one source alone;
- every direct RQ2 attribution and linkage;
- every direct RQ3 linkage; and
- every reviewer-derived value used in a result or conclusion.

After all per-report discrepancies have been adjudicated and their corrections propagated, run a separate targeted challenge for every report-family or artifact-lineage merge or split and every G3 or G4 profile. Supply all reports and linked records needed to assess that judgment through a rights-permitted multi-report route. If one context cannot hold the complete materials, use a versioned staged bundle and reconciliation procedure that covers every potentially relevant source location rather than only the evidence already relied upon. Record stage and source coverage. If material content cannot be represented or reconciled without loss, use the complete manual fallback and do not count the limited bundle as a completed challenge. Any later material change to an input report or linked record invalidates and requires rerunning or manually rechecking every affected cross-report challenge. Never claim that a per-report pass verified a cross-report judgment.

A model route may be used only after the run records why transmission, processing, retention, and storage are permitted for that source and provider route; a no-training setting alone is not proof of permission. Use an authorized local or institutionally approved route where restrictions require it. If no permitted route can process an individual report, do not exclude the evidence and do not claim model verification. Replace the full blind model extraction with a delayed complete sole-reviewer re-extraction using the same source and codebook while the canonical extraction is hidden, then perform a separate visible manual field-and-link audit; record both as sole-reviewer passes and retain the lack of model coverage as a review-process limitation. If no permitted route can process a cross-report bundle, perform and record a complete manual challenge against all linked reports. Prioritize model-ineligible material for the supervisor sample when feasible. A pass is also failed if required pages, figures or tables were unavailable, input was truncated, OCR or parsing was materially defective, output did not validate, or the model did not complete the required scope. Rerun through an accepted route or use the defined manual fallback; never treat partial coverage as a successful pass. Secure model inputs and outputs according to source rights, retain content hashes and access-controlled storage references, and publish only a rights-safe manifest when the material cannot be redistributed.

At completion of full-text screening, freeze the initially included-report sampling frame, its sorted IDs, `N`, and a manifest hash. After all initial extractions are complete and before the reviewer sees any model comparison or discrepancy output or reopens the sealed canonical extraction for a sampled report, the sole reviewer must completely re-extract a reproducibly selected sample using the same frozen codebook. Use `n = min(N, max(3, min(10, ceil(0.10 × N))))`; this is a pragmatic capped audit, not a representative sample or a basis for a corpus-wide consistency estimate. Allocate prespecified strata for Route A and Route B when both exist and for reports containing complex artifact, RQ2, or RQ3 structures, choosing within each stratum by the frozen pseudorandom procedure; fill remaining slots from the rest of the frame randomly, and avoid selecting two reports from one family while alternatives exist. Keep purposive structural coverage separate from the random fill in reporting. Wait at least 14 calendar days after the sampled report's primary extraction, record both dates, and keep the primary extraction and all audit outputs sealed from the reviewer until the re-extraction is complete. Compare the two human extractions programmatically and adjudicate every difference. If an audited report later leaves the included set, retain its audit and select a reproducible replacement from the final included set when an unaudited replacement exists; otherwise report the reduced final included-report audit count. Apply the required delay and sealing rules to every replacement. Report this as test–retest consistency, not independent reviewer agreement.

Ask the supervisor to inspect `min(2, N)` reports from the audit sample, blind to the canonical extraction, model, test–retest, discrepancy, adjudication, and cross-report outputs: one Route A and one Route B where available, with at least one evidence-rich or model-ineligible report where the sample permits. If the supervisor agrees, provide orientation on the frozen codebook and one calibration example before the audit. Freeze whether the supervisor will perform complete duplicate extraction or a narrower field-level audit before selecting or supplying the audit reports. Label a narrower check as a field audit, not duplicate extraction. If the supervisor can assess only one report, only selected fields, or no reports, preserve the requested and actual scope and report the limitation; do not replace the missing human check by relabeling an LLM pass.

A candidate discrepancy is **confirmed** only when human source adjudication finds that the canonical extraction requires correction or that material source ambiguity remains. Classify it as material when it can change eligibility or route, the existence or identity of an analytic unit, a denominator, family or lineage dependence, an A/E/C/T/P/I gate or tier, outcome direction, direct RQ2 or RQ3 status, a methodological-appraisal judgment, claim-support class, a quantitative result, or a synthesis conclusion. Any material discrepancy requires a source-level recheck of all linked objects and all linked reports affected by the judgment. Treat issues as one error pattern when they arise from the same codebook field, decision rule, prompt behavior, ingestion failure, or transformation. Any one confirmed material issue that could be systemic, the same confirmed non-material pattern in two reports, or a material omission found by test–retest or supervisor audit that neither model-assisted process surfaced triggers review of the codebook, prompts and deterministic checks and a targeted recheck of every previously extracted report that could be affected. A codebook or prompt change creates a new version, requires focused recalibration, and requires rerunning every affected validation pass. Preserve genuinely unresolved material ambiguity using the protocol's uncertainty and coding-confidence fields and include it in sensitivity analysis. Record the rationale and coverage of every escalation.

During calibration, make sure the reviewer, supervisor when involved, and model-assisted procedures can distinguish:

- coding confidence from methodological appraisal, record-level claim support, and conclusion confidence;
- evidence type and maturity from support for the particular claim;
- a direct measure from a surrogate or intermediate measure;
- author attribution and observed association from reviewer assessment of causal support;
- an absent comparator from `not_applicable`, and an identified comparator from an adequate one;
- source-reported data from reviewer-derived values;
- a DAE from one observed case;
- a scenario sweep from tailoring;
- a model artifact from a method or workflow;
- separate reports from separate applications; and
- post-tailoring assurance from direct RQ3 V&V.

Do not calculate inter-rater reliability between the reviewer and an LLM or between LLMs. The small supervisor sample and sole-reviewer test–retest sample are audits and do not support a corpus-wide reliability claim. Report their raw pre-adjudication scope and field- and object-level discrepancies instead. For full blind model extractions, report completed and failed reports and modules, matched units, human-only and model-only units, split or merge candidates, field discrepancies and evidence-location discrepancies. For canonical-audit passes, report reports and objects covered, technical failures, flags raised, accepted corrections, rejected flags, unresolved issues, omitted records found, and material changes. Give every count a pre-adjudication denominator. Calculate an agreement statistic only if an additional human assessment design and sample genuinely support it.

Before synthesis, validate all extraction JSON against the codebook. Check exact controlled labels, record IDs, required evidence and reasons, distinct statuses, and all links among report families, reports, threads, measurements, comparators, confounder assessments, derived values, methodological appraisals, claim-support objects, artifact lineages, genericity profiles, tailoring applications, outcome or burden records, and V&V records. Confirm that no source-reported value was overwritten by a derived value and that evidence type or maturity was not used mechanically as claim support. Reconcile the verification manifest: every included report must have the required completed passes or a documented manual fallback; every required cross-report judgment must have a completed targeted challenge or manual fallback; every discrepancy must have a human disposition; every accepted change must propagate to linked objects and compiled data; and no unresolved technical failure may be represented as successful verification.

## Planned synthesis

Complete synthesis and reporting under task [`R-006`](TASKS.md). Use a structured evidence map and narrative synthesis. Do not pool effect estimates because the models, outcomes, and evidence designs are expected to differ too much.

### Relationship to Buruso et al. (2026)

Buruso et al. (2026) is a broad secondary review of 126 selected space-MBSE studies and reports published from 2011 through 2023. It maps methods, languages, tools, five MBSE phases, and general challenges across many kinds of space work.

Treat Buruso et al. as one known item in the separate [prior-secondary-review search and CRD/DARE assessment](protocol-prior-secondary-reviews.md). It enters that supporting assessment only through a successful final Scopus or Web of Science search and normal screening. The resulting scope and methods assessment contributes to the need-for-review rationale, not to RQ1–RQ3 evidence.

After the main independent baseline is complete, Buruso et al. may also be used for context, terminology, a later primary-report recall check, and recorded citation searching under Part 2. Do not use it as primary evidence or let either role insert one of its cited reports directly.

This review is not an update or replication of Buruso et al. It applies this protocol's narrower nanosatellite-EPS population, direct EPS linkage rule, and RQ1–RQ3 evidence structures. Do not treat system-wide MBSE or V&V as EPS evidence or compare the two reviews' counts as evidence of effectiveness.

For a descriptive view of currency and overlap, results may be split into 2011–2023, matching Buruso et al.'s evidence window, and 2024 through the common evidence cutoff set under task [`P-001`](TASKS.md). This split does not change eligibility or imply independence.

### RQ1

- Synthesize the report-and-implementation-context, EPS-thread, input-and-assumption, engineering-output, and implementation-footprint records defined above.
- Keep reported inputs and implementation needs separate from reviewer inference and missing information. Keep source-reported values separate from reviewer-derived values.
- Identify whether measures used to characterize implementation or performance are direct, surrogate, intermediate or process measures, or unclear for the stated construct.
- Use methodological appraisal and claim-specific support for evaluative RQ1 characterizations. Do not treat model maturity, physical use, publication type, or coding confidence as automatic evidential strength.
- Compare author labels such as *lightweight* or *scalable* with the reported footprint; do not turn them into eligibility or tailoring categories.
- Compare Route A with Route B without assuming that one route is more mature.
- Synthesize artifact-lineage profiles and tailoring applications under the gate and tier definitions in Part 1; keep method or workflow reuse separate from artifact reuse.
- Present tiers at artifact-lineage/profile level, with the full gate vector, DAE breadth, demonstrated coverage, claim agreement, and failures or conflicts kept separate.
- Merge duplicate reports of one application and use artifacts and applications—not publication counts—as transfer denominators. Distinguish same-family, separate-team, and independent use.
- Describe a tier only within the artifact scope and demonstrated settings. Do not call an artifact proven, universally generic, or generic without context.
- Include a tailoring check or burden in RQ3 or RQ2 only when it separately meets that question's linkage or attribution rule.

### RQ2

- Synthesize only outcomes and implementation burdens that the source explicitly attributes to a qualifying EPS thread.
- Keep EPS engineering outputs separate from evidence about value or burden caused by MBSE.
- Present together the claim kind and scope, record role, outcome category, author-claimed direction, evidence-supported direction, burden category, proposed mechanism, evidence type, measure role, comparator adequacy when applicable, material confounding, methodological appraisal, record-level claim support, applicability, and lifecycle stage.
- Report direct measures separately from surrogates and intermediate or process measures. Do not restate a proxy as the broader construct unless its relationship was credibly justified or validated.
- Present comparative and causal claims separately from descriptive, feasibility, and experiential claims. Do not infer causation from explicit author attribution, temporal order, a quantitative value, operational maturity, or flight use alone.
- Preserve source-reported quantitative values, denominators, uncertainty, and practical interpretation; label every reviewer-derived value and report sensitivity to material assumptions.
- Treat an unsupported claim as evidence that the claim was made, not that an effect was demonstrated.
- Never treat `not_reported` as a null result.
- Do not infer net benefit by counting positive and negative records.

### RQ3

- Map every EPS target-to-model-to-V&V chain.
- Separate `eps_specific` from `system_wide_eps_linked` records.
- Also organize evidence by V&V object, completeness of the criterion, execution before physical work, later model-to-test continuity, methodological appraisal, and record-level claim support.
- Report measurements, criteria and oracles in their stated scope. Distinguish a direct V&V measure from a surrogate for validity, assurance, or downstream performance.
- Use a comparator and confounder assessment when a report makes a comparative V&V-effectiveness claim; neither is required merely to document that a linked activity existed.
- Report analysis-only work, system-wide co-occurrence, and other missing-link near misses separately.
- Treat a missing criterion as incomplete evidence. Do not silently discard an otherwise explicit EPS-linked V&V record.
- Do not infer validation from successful execution, closure from continuity, causal effectiveness from physical maturity, or an EPS-specific verdict from a system-wide activity or from items that only appear in the same report.

### Cross-cutting safeguards

- Apply the [canonical units, denominator, and dependence rules](protocol.md#units-of-evidence-and-counting).
- Present Route A and Route B separately before combining them.
- Separate arXiv preprints, institutional technical reports, master's theses, doctoral theses or dissertations, and other grey literature from peer-reviewed scholarly reports. Show sensitivity views by publication provenance when useful. Do not automatically give a report less weight merely because it lacks journal peer review.
- Keep coding confidence, methodological appraisal, record-level claim support, and conclusion confidence separate in tables and prose.
- Treat evidence type, publication provenance, model maturity, operational use, physical validation, and flight status as descriptors. Use them to strengthen only conclusions they directly bear on.
- Use sensitivity views based on methodological concerns, record-level claim support, measure directness, comparator adequacy, material confounding, publication provenance, linkage and lineage coding confidence, and genericity gates. Useful subsets may include Route A only, records without serious methodological concerns, direct-measure records, adequately compared records where comparison is required, G3/G4 profiles, and available artifacts. Do not treat the genericity tier as a general evidence-quality score.
- Treat cross-tabulations as descriptive co-reporting unless extraction provides a direct link.
- Keep `not_reported`, `none`, `not_applicable`, `uncertain`, and invalid or unmapped values separate.
- Treat sparse direct evidence as a result of the review. Do not fill gaps with general whole-spacecraft MBSE claims.

## Required new-run artifacts

After clean-start task [`P-000`](TASKS.md) is complete, create these artifacts anew with run provenance. Do not restore an earlier run's log, dictionary, schemas, decisions, or data. Track search infrastructure under [`S-001`](TASKS.md), extraction forms under `E-001`, and the remaining artifacts under [`A-001`](TASKS.md):

- a dated methods decision log;
- a study or implementation report-family register;
- a reusable EPS artifact-lineage register;
- a tailoring-application table;
- read-only known-item registers for legacy reports and Buruso recall;
- the separate prior-secondary-review search bundle required by its [supporting protocol](protocol-prior-secondary-reviews.md#required-artifacts-and-reporting), including its CRD/DARE and overlap matrices and need-for-review statement;
- a new `search-log.md` meeting PRISMA-S requirements;
- a new `searches/search-concept-dictionary.json` and matching code generated from Part 2;
- new source/interface crosswalk, final-run manifest schema, and failure-register schema;
- raw source-specific search results and source-selection or interface proof;
- a search manifest with dates, interface details, restrictions, rights, and access status;
- a merged and deduplicated candidate set and deduplication report;
- title and abstract screening, full-text screening, and retrieval logs;
- the accessible report set and a table of cited full-text exclusions with one main reason per report;
- the run-specific corpus, IDs, and extraction codebook;
- per-report extraction files with links among threads, measurements, comparators, confounder assessments, derived values, methodological appraisals, claim-support objects, profiles, applications, outcomes or burdens, and V&V records;
- versioned full blind model-extraction, canonical-audit, cross-report-challenge and reconciliation prompts and procedures; run manifests; complete model extraction and audit outputs where rights permit; verification-pass records; discrepancy and human-adjudication records; deterministic-validation results; and sole-reviewer test–retest and supervisor-audit files;
- an artifact-level claim-to-evidence table;
- the compiled extraction data, bibliography, validation report, and analysis code; and
- machine-readable PRISMA count reconciliation, the official PRISMA 2020 flow diagram, synthesis outputs, and completed PRISMA-S and PRISMA 2020 checklists.

Do not publish licensed exports, copyrighted abstracts, or full texts when rights prevent it. Keep them secure where allowed. Publish or archive the exact methods, dates, manifests, derived counts and decisions, codebook, code, and a statement that explains what can and cannot be accessed.

## Completed-review reporting

The final report will call itself a systematic review and evidence map and will follow the PRISMA 2020 checklist and 12-item abstract guidance. It will:

- name every source actually used, give its search date and the common evidence cutoff set under `P-001`, and distinguish failed or planned-but-unused sources;
- link to the exact final source-native searches and PRISMA-S logs instead of showing only a cleaned example query;
- describe the sole-reviewer design, human and complete blind model extractions, canonical-audit and reconciliation sequence, test–retest sample selection and delay, requested and completed supervisor scope, discrepancies, escalation, and conflict handling exactly as performed;
- identify each model or snapshot, provider and execution date, reasoning and generation settings, prompt and codebook version, document-ingestion route, full-extraction module coverage and failures, human-only and model-only units, split or merge candidates, field discrepancies, and the number and disposition of audit flags;
- report the bounded prior-secondary-review search separately, including its two-source limitation, CRD/DARE assessment, overlap matrix, need disposition, and any resulting protocol change, without adding its records to the main PRISMA flow;
- never call model-assisted checking independent human review; never call same-reviewer test–retest independent replication; never infer corpus-wide agreement from the small human audit; and never describe source pilots as formal PRESS review;
- explain why no pooled effect estimate is planned;
- label every count or proportion with its denominator: report family, report, thread, artifact lineage or profile, tailoring application, outcome or burden, or V&V record;
- use the new-review PRISMA flow diagram for databases and other sources, with records and reports—not linked analytic units—in its boxes;
- cite apparently eligible reports excluded after full-text review and give source-located reasons;
- present methodological appraisal, record-level claim support, reporting-bias, and conclusion-confidence results under the [appraisal framework](protocol-discovery-and-appraisal.md#appraisal-meaning-reporting-bias-assessment-and-conclusion-confidence), without treating evidence type or maturity as a universal hierarchy; and
- report access to all three main parts and the supporting prior-secondary-review protocol, every dated methods change or departure, limits of the review process and evidence, and availability of data, code, and materials.

Complete the administrative declarations under task [`P-002`](TASKS.md) before publication, or clearly say that they are absent. The clean-document start condition does not imply that these declarations exist.

Apply the [clean-document start and change policy](protocol.md#review-status-and-restart-policy).

---

**Previous:** [Part 2 — Discovery and appraisal](protocol-discovery-and-appraisal.md)
