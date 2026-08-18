# Protocol for a Systematic Review of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Extraction and synthesis

> **Protocol parts:** [1 — Scope and definitions](protocol.md) · [2 — Discovery and appraisal](protocol-discovery-and-appraisal.md) · **3 — Extraction and synthesis** (this file)
>
> **Normative definitions used here:** [eligible EPS evidence routes](protocol.md#eligible-eps-evidence-routes), [bounded genericity](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring), and the [quality checklist](protocol-discovery-and-appraisal.md#quality-checklist).

## Extraction fields

A new run-specific `extraction_codebook.json` must be created from this protocol before per-report extraction. Earlier codebooks and extraction forms are not authoritative for this run and may not be copied into new-run fields.

Every synthesis-critical controlled code requires a rationale, a direct quote or source location where possible, and a confidence rating. Preserve `not_reported`, `not_applicable`, `none`, and `uncertain` as distinct statuses. Distinguish author-reported facts from extractor inference.

### Report-level bibliographic and review-management fields

- New-run report ID; optional legacy corpus ID; extraction file path.
- Citation, title, authors, year, venue or institutional report series, publication type, DOI/URL, publisher/issuing organization, source/report identifier, and reported peer/technical-review status.
- For theses/dissertations: degree level/name, institution/country/department, completion status, PQDT/OATD and repository persistent identifiers, formal publication/issue date and date basis, defence/approval/award/deposit/public-release/embargo/indexing dates when reported, repository/full-text version, access/embargo/licence status, and degree-examination status kept separate from peer review.
- Every discovery event: run ID, database/source, exact query or citation route, date, source record ID, rank when available, and raw-search artifact.
- Title/abstract screening tier and rationale.
- Full-text eligibility decision and exclusion rationale, if applicable.
- Route A/Route B classification and evidence.
- RQ contribution status: RQ1; RQ1-G genericity dispositions and counts of linked artifact-lineage profiles/tailoring applications; count of eligible RQ2 outcome/burden records; count of direct and near-miss RQ3 records.
- Study/implementation report-family ID(s), linked artifact-lineage ID(s), report-to-family/artifact relationship (`same_report_manifestation`, `derivative_report`, `companion_report`, `overlap_uncertain`, or other controlled value), membership or identity rationale/evidence, overlap confidence, and shared-result notes.
- Extraction confidence and assessor/review-pass provenance.

### Study context and MBSE qualification

- Mission/platform, form factor/mass if reported, mission name/domain, organization type, and project maturity.
- Demonstrated lifecycle stage, separated from asserted or future lifecycle applicability.
- Development context: academic/student, agency, industry/NewSpace, distributed team, agile/concurrent design, rapid prototyping, resource-constrained mission, or not reported.
- Reported MBSE implementation requirements and burdens: roles, skills, training, staffing, time/effort, licensing/infrastructure, model/data preparation, computation, integration, governance, maintenance/configuration, cost, schedule, or not reported.
- Author's stated objective, pain point, intended decision, and rationale for using MBSE.
- MBSE qualification evidence: method/language, tools, system-model artifacts, modeled concerns, explicit relations, and system boundary.
- Model maturity: conceptual framework, reference/template, prototype, executable, project-applied, physically validated, operational/flight, or not reported. These may co-occur and are not assumed ordinal unless the paper supports an ordering.
- Toolchain architecture, data flow, interoperability mechanism, ownership/handoff, and reported limitations.
- Availability of models, profiles, libraries, scripts, data, configurations, and documentation.

### EPS-model-thread record

Create one record per qualifying thread:

- Thread ID and report ID.
- Thread route/role: EPS-primary or embedded EPS.
- Host-model anchor for embedded threads.
- EPS model anchor and EPS system boundary.
- Explicit bridge(s), relation type, and source location.
- EPS concerns represented: requirements, function, behavior, architecture, components, ports/interfaces, modes/operations, parametrics/budgets, decisions/trades, risks/faults, V&V, or other.
- EPS elements: generation/solar array, storage/battery management, conversion/regulation, conditioning/distribution, protection, monitoring/control, bus/harness, loads/interfaces, modes, margins, degradation, fault management, or other.
- Model artifacts and tools carrying the thread.
- Level of abstraction/fidelity and phenomena deliberately omitted.
- Purpose and decisions supported: definition/sizing, requirements/traceability, trade study, interface management, executable analysis, V&V, reuse/tailoring, communication, lifecycle continuity, or other.
- Reuse/tailoring mechanism: template, reference model, profile, library, pattern, transformation, reusable workflow, open package, method guidance, mission-agnostic architecture, interface-focused model, specific-mission model with reusable method, or other.
- Tailoring choices and implementation footprint: model/artifact scope, retained or omitted content, roles, tooling, automation, governance, required resources, rationale, and reported trade-offs. Preserve any author characterization such as lightweight, scalable, comprehensive, or resource-intensive, but do not impose a lightweight threshold or infer one from mission class.
- Linked artifact-lineage/profile and tailoring-application IDs; genericity disposition; method/workflow-only status where applicable.
- Thread-level maturity, lifecycle stage, availability, evidence confidence, and limitations.

### Reusable EPS artifact-lineage and genericity-profile record

Register every identifiable EPS-linked artifact and create one profile for each lineage/version/scope that can be assessed without concealing material change:

- Artifact-lineage ID, genericity-profile ID, linked report-family/report/thread IDs, and every source-supported base/derived or version relationship.
- Artifact object/type: structured system model; reference/template model; metamodel; modeling profile; library/pattern; interface contract; parametric package; transformation/generator with persistent content; larger model with separable EPS content; method/workflow only; toolchain only; other; or unclear.
- Artifact name, version, repository/package/model identifiers, owner/developer, availability, license where reported, and lineage confidence/rationale. Shared tool, organization, terminology, or topic is not lineage evidence.
- Exact source terminology and claim text; claim object and actor; claimed reuse/genericity scope; whether the claim concerns the artifact, a method/workflow, toolchain, language/profile, whole spacecraft, or is unclear.
- Genericity disposition: `not_an_artifact_or_method_only`; `artifact_no_reuse_indication`; `genericity_or_reuse_claim`; `reported_reuse_without_bounded_specification`; `bounded_reuse_candidate`; or `unclear`.
- DAE fields: intended target platform/mission/form factor; mission/domain/orbit/environment; lifecycle use, purpose, and decision; EPS boundary/architecture/interfaces; abstraction/fidelity; required inputs/data; modeling language/tool/version; organizational/process assumptions; prerequisites; stated exclusions and failure boundaries. Preserve `not_reported` by dimension and record whether the minimum DAE is met.
- Reusable core/invariants: retained elements, relations, constraints, semantics, interfaces, libraries/packages, identifiers, and source locations.
- Variation design: variation-point identifier/location; permitted range/options; default; dependencies/constraints; operation type; rationale; and whether the point is source-declared or only reconstructable from an explicit base/derived mapping.
- Tailoring rules/pathway, required inputs and roles, governance/configuration control, automation, and any bounded reuse-as-is rule.
- Linked tailoring-application IDs; claimed envelope versus demonstrated-context tuples; number of materially distinct applications after collapsing duplicate reporting; and evidence used to judge distinctness.
- A/E/C/T/P/I gate status, rationale, evidence location, and confidence for every gate; failed condition(s); highest genericity tier (`NA`, `G0_artifact_only`, `G1_claimed_or_unbounded`, `G2_bounded_reuse_specified`, `G3_bounded_reuse_demonstrated`, or `G4_independently_corroborated`) with a source-locatable cumulative rationale.
- Claim concordance: `not_evaluated`; `supported_in_tested_contexts`; `partially_supported`; `mixed`; `not_supported`; or `unclear`, preserving failed/out-of-envelope applications and alternative explanations.
- Profile-level limitations, model/data availability, report-family and lineage dependence, evidence source, extraction confidence, and first/second-check provenance.

Do not award a gate from source silence, source labels alone, a single observed mission, model openness, maturity, or reviewer knowledge. Integrate complementary reports only after lineage is established and retain which report supports each field; do not transfer results between versions or applications.

### Tailoring-application record

Create one record per artifact-lineage-to-target-context application, including a justified unchanged adoption:

- Tailoring-application ID, artifact-lineage/profile ID, linked family/report/thread IDs, target model/configuration identifier, and application identity/duplicate-report rationale.
- Target-context tuple: mission/platform/form factor; mission purpose/domain; orbit/environment; lifecycle use/decision; EPS architecture/components/interfaces; modes/load profile; model fidelity; language/tool/version; organization/team; and other material DAE dimensions.
- Relationship to the DAE: inside; boundary case; outside; unclear; or DAE not reported, with rationale. Record the material dimension(s) that distinguish this context from other credited applications.
- Base/core content retained and evidence; content configured, parameterized, selected, specialized, extended, deleted, substituted, mapped, transformed/generated, rebuilt, or intentionally unchanged; affected variation-point IDs; before/after or base/derived trace; and rationale.
- Tailoring inputs/assumptions, procedure, roles/skills, automation, tools/licenses/infrastructure, governance, effort/time/cost, maintenance, and other implementation footprint or burden. Do not infer low effort from parameterization or mission class.
- Resulting artifact/use, decisions or analyses supported, availability/configuration identifier, reported failures/rework/trade-offs, and whether the record demonstrates artifact reuse, method/workflow reuse only, or is unclear.
- Post-tailoring assurance: intended-use criterion/oracle and provenance; method; execution timing; result/verdict; discrepancies/disposition; and whether all P-gate conditions are met. Link an RQ3 record only when its independent eligibility rule is satisfied.
- Adopter/evaluator relationship: originating/same team; same organization but operationally separate team; external organization/team; independent evaluation of the originator's instance only; or unclear. Record personnel/implementation-control overlap, the independent adopter/evaluator's own report/artifact/data provenance, report-family evidence, separate adoption/tailoring and assurance evidence, and whether the I gate is met.
- Evidence source, confidence, limitations, and extraction/second-check provenance.

A single application may inform RQ1-G and also link to RQ2 burden/outcome or RQ3 V&V records, but it does not enter those direct syntheses unless their separate attribution/linkage rules are met.

### Input and assumption record

Create one record for each material reported input or assumption linked to its EPS thread. “Material” means that the input or assumption defines the EPS boundary, parameterizes behavior or a scenario, supplies a criterion, affects a reported output/decision, or limits claimed applicability:

- Input/assumption ID and thread ID.
- Type: mission requirement; orbit/environment; operational mode or load profile; architecture/interface; generation; storage; conversion/distribution; component performance/loss; degradation/lifecycle; margin/uncertainty; control/fault; model-fidelity/tool assumption; V&V configuration; or other.
- Parameter/construct, reported value or description, units, time basis, and nominal/worst-case/range/distribution status.
- Provenance: mission requirement; standard/handbook; vendor data; test/flight data; heritage/previous mission; literature; tool default; analyst assumption; calculated/derived; or not reported.
- Treatment of uncertainty, variability, margin, sensitivity, and degradation.
- Stated rationale: mission/environment constraint; early-phase uncertainty or unavailable data; conservatism/safety; reuse/tailoring; computational/tool limitation; interface standard; decision need; V&V need; or not stated.
- Trace location in a requirement, model element, parameter, figure/table, data file, or external-tool binding.
- Effect on model outputs or decisions, if reported.
- Evidence source and extraction confidence.

Do not infer that an input is unnecessary because it is not reported. Source silence is coded `not_reported`.

### EPS engineering outputs

Extract technical outputs separately from MBSE outcome/burden records:

- Output ID and thread ID.
- Quantity/result and units/time basis.
- Scenario/configuration and input set.
- Whether it is calculated, simulated, checked against a criterion, compared, or physically validated.
- Decision or model artifact informed.
- Evidence source and confidence.

### RQ2 outcome and implementation-burden evidence record

Create one atomic record for each candidate outcome or burden that is explicitly or plausibly linked to a qualifying EPS thread. Do not exhaustively extract generic MBSE claims merely because they occur in an eligible report. Split multi-outcome statements into atomic records and connect shared evidence through source IDs:

- Record ID and linked thread ID.
- Exact result/claim text or conservative paraphrase.
- Record role: outcome; implementation burden; mixed trade-off; or other.
- Claim scope and target.
- Outcome category: EPS reliability; system/mission assurance; defect/error reduction; risk reduction; reproducibility/rerunnability; reuse/replication; integrability/interoperability; interface consistency; traceability/requirements quality; completeness; lifecycle continuity; decision/trade support; cost; schedule; effort/automation; communication/knowledge; governance/value realization; or other.
- Reported direction: beneficial; null/no observed effect; mixed/conditional; adverse; unclear/not reported. Preserve author-claimed direction separately from evidence-supported direction.
- Direction basis: metric polarity, comparator or criterion, time horizon, magnitude/value/units, conditions, and whether the result is observed or anticipated.
- Implementation-burden category, when applicable: time/effort; skills/training; staffing; tooling/licensing/infrastructure; model/data preparation; computation; integration/interoperability; maintenance/configuration/governance; schedule; cost/resource use; other; none reported; or not reported. Record affected actor, adoption versus ongoing phase, mitigation, and any linked benefit/trade-off.
- Reliability subtype where relevant: EPS reliability, system/mission reliability, process reliability, model consistency/reliability, mission assurance, defect/error reduction, generic reliability claim, or not applicable.
- MBSE mechanism: artifact traceability, requirements linkage, executable simulation, parametric analysis, reference-model reuse, automated generation, transformation, shared repository, tool integration, interface management, lifecycle-gate support, model-derived V&V, or other.
- Artifact/process linked to the record and lifecycle stage.
- Attribution status: explicit EPS-thread attribution; ambiguous attribution; generic/not eligible. Only explicit EPS-thread attribution enters direct RQ2 synthesis.
- Evidence type: assertion only; conceptual/illustrative; single-case demonstration; executable result; trade/requirements-check result; quantitative metric without comparator; quantitative comparison; stakeholder/expert evaluation; reuse/replication; integration/test/operational/flight evidence.
- Metric or value indicator; baseline/comparator; observed effect, result, or burden.
- Evidence source, alternative explanations, and report-family/nesting notes.
- Evidence confidence:
  - **Unsupported:** assertion without extractable support;
  - **Weak:** plausible explanation or illustrative/single-case evidence without a result adequate to support the claimed direction or burden;
  - **Moderate:** traceable within-case evidence, executable/checking result, or metric, but limited comparator or independent validation;
  - **Strong:** appropriate comparative, repeated-reuse, independent, integration/test, operational, or flight evidence directly supporting the reported direction or burden.

### RQ3 V&V record

Create one atomic target–method–scenario record per candidate activity or artifact. Retain plausible linkage near misses so exclusion from EPS-linked RQ3 synthesis is auditable, but do not exhaustively extract unrelated generic system V&V:

- V&V record ID and linked thread ID.
- EPS target or system-wide target explicitly linked to EPS; target type and requirement/criterion identifier when reported.
- Model element/artifact and explicit model-to-V&V bridge.
- Source terminology for verification, validation, V&V, checking, or analysis.
- Linkage scope: `eps_specific`; `system_wide_eps_linked`; `system_wide_cooccurrence`; or `unclear`, with source evidence and rationale.
- Normalized V&V object: model verification; model validation; system/design verification; system/design validation; multiple; or unclear, with coding rationale.
- Eligibility disposition: analysis only; direct EPS-linked V&V; system-wide co-occurrence near miss; or unclear.
- Method/artifact: requirements-in-the-loop, parametric/constraint check, simulation scenario, model checking, trade verification, virtual integration, verification matrix, test case/procedure, generated test artifact, automated test, MIL, SIL, PIL, HIL, or other.
- Execution environment and hardware present; physicality relative to the target EPS.
- Criterion/oracle and its provenance.
- Timing relative to physical realization, integration, and test; lifecycle stage.
- Status: proposed only; prepared/generated; executed virtually; verdict/result reported; downstream physical link demonstrated; model-to-test closure demonstrated.
- Result/verdict, result scope (EPS-specific, system-wide, or not reported), and discrepancy handling, if reported.
- Downstream link: software integration, hardware integration, flat-sat/bench, PIL/HIL, environmental test, operational validation, or flight evidence.
- EPS-linked RQ3 eligibility: yes/no/uncertain for the target–bridge–V&V-method/intent rule, with the failed condition recorded when not eligible.
- Criterion-complete status: yes/no/uncertain, with criterion evidence.
- Demonstrated pre-physical execution status: yes/no/uncertain, with timing, target-relative physicality, and result evidence.
- Evidence source, confidence, limitations, and report-family/nesting notes.

### Limitations and open extraction

- Author-stated limitations, assumptions, and scope boundaries.
- Extractor-identified evidence gaps, with absence-based explanations only after completing the relevant fields.
- Narrow controlled limitation flags, including prototype/future work, single case, no comparator, no independent validation, no physical/model-to-test evidence, unavailable model/data, assumptions/data-quality limits, tool dependency, interoperability limits, incomplete lifecycle coverage, ambiguous EPS linkage, generic outcome attribution, missing V&V criterion, method/artifact conflation, missing or inferred DAE, unidentified reusable core, no explicit variation rule, tailoring claim without a reconstructable application, ambiguous artifact lineage, duplicate/same-family reuse only, no post-tailoring assurance, or unreported failed/out-of-envelope reuse.
- Emergent codes for unexpected findings that do not fit the controlled vocabulary; do not silently expand controlled categories during extraction.

## Calibration, consistency, and validation

Before full screening and extraction:

1. pilot the full-text eligibility rule on clear Route A, clear Route B, generic whole-spacecraft MBSE, and non-MBSE EPS examples;
2. pilot the thread, input/assumption, artifact-lineage/genericity-profile, tailoring-application, RQ2 outcome/burden, and RQ3 V&V forms on a deliberately varied sample, including method-only versus artifact reuse, claim-only, bounded specification, one versus multiple materially distinct contexts, same-family duplication, reuse-as-is, failed transfer, and post-tailoring assurance cases;
3. revise and commit the run-specific codebook before full extraction; and
4. document all calibration decisions and examples.

Use isolated assessment passes to reduce context carryover. All final Route B inclusions, artifact-lineage merges/splits, G3/G4 tier assignments, and direct RQ2/RQ3 linkage decisions must receive a second check. Calibrate the distinction between a DAE and an observed case, a scenario sweep and tailoring, a model artifact and method/workflow, separate reports and separate applications, and post-tailoring assurance and direct RQ3 V&V. Record whether each check was performed by another human assessor or by a model-assisted validation pass. Do not describe model-assisted validation as independent human review, and calculate an agreement statistic only when the assessment design genuinely supports it.

Validate all extraction JSON against the codebook, exact controlled labels, record IDs, required evidence/rationales, status distinctions, and report-family/report/thread/artifact-lineage/genericity-profile/tailoring-application/outcome-burden/V&V referential integrity before synthesis.

## Planned synthesis

The synthesis is a structured evidence map and narrative synthesis; no pooled effect estimate is planned because models, outcomes, and evidence designs are expected to be heterogeneous.

### Relationship to Buruso et al. (2026)

Buruso et al. (2026) is a broad secondary review of 126 selected space-MBSE studies and reports published from 2011 to 2023, mapping methods, languages, tools, five MBSE phases, and general challenges across heterogeneous space applications. It is used here for positioning, terminology, a deferred recall benchmark, and logged citation chasing, not as primary evidence.

This review is neither an update nor a replication of Buruso et al. It is restricted to orbital CubeSat/nanosatellite EPSs; requires a source-locatable EPS anchor, model anchor, and explicit bridge; and synthesizes material inputs and assumptions, all reported reuse and tailoring approaches, bounded artifact genericity and its evidential support, implementation footprint, direct EPS-attributed outcome direction and implementation burdens, and direct EPS target–model–V&V chains. It therefore addresses broader gaps concerning model tailoring and scalability, predominantly anecdotal value claims, and poor visibility of later integration, test, and V&V. System-wide MBSE or V&V is not treated as EPS evidence without the protocol's direct link. Cross-review counts are not compared as effectiveness evidence.

For descriptive currency and overlap, publication patterns may be shown separately for 2011--2023, corresponding to Buruso et al.'s evidence window, and 2024 through the common 2026-08-10 evidence cutoff. This temporal split does not change eligibility or imply that reports within either period are independent.

### RQ1

- Map EPS boundaries, model concerns, artifacts, purposes, abstraction levels, inputs/assumptions, provenance, uncertainty/margin handling, all reported reuse/tailoring approaches, implementation footprint, required roles/skills/resources, trade-offs, and lifecycle use.
- Distinguish reported inputs and implementation requirements from reviewer-inferred dependencies and from source silence.
- Where evidence permits, describe how authors characterize implementations as lightweight, scalable, comprehensive, or resource-intensive and compare those characterizations with the reported implementation footprint; lightweight status is not an eligibility filter or required tailoring category.
- Compare Route A and Route B without assuming either is more mature.

### RQ1-G

- Register identifiable EPS-linked artifact lineages and report method/workflow reuse separately from artifact reuse.
- Map source terminology and claims, DAE dimensions and missingness, reusable cores, variation points, tailoring pathways, implementation footprints, demonstrated target-context tuples, post-tailoring assurance, failures/boundaries, claim concordance, and A/E/C/T/P/I gates.
- Present `NA`, G0, G1, G2, G3, and G4 separately at artifact-lineage/profile level. Treat G1 as a claim/indication, G2 as specified bounded reuse, G3 as demonstrated bounded reuse in at least two materially distinct assured contexts, and G4 as independently corroborated bounded reuse.
- Report DAE breadth separately from evidence tier and show demonstrated coverage as a subset; never rank a broader claim above a narrower but better-supported artifact merely because of scope.
- Collapse duplicate reports of one tailoring application and distinguish same-family, same-organization/separate-team, and external/independent reuse. Use artifact identity and application denominators rather than publication counts as transfer evidence.
- Retain one-context tailoring, partial gates, missing assurance, failed/out-of-envelope use, burdens, and contradictory evidence in the profile even when they cannot support G3/G4.
- Use wording such as “G3 evidence supports bounded reuse of [artifact scope] in [demonstrated contexts], within the stated DAE.” Do not report a model as proven, universally, truly, or context-free generic.
- A post-tailoring assurance record or tailoring burden enters direct RQ3 or RQ2 synthesis only when its separate linkage/attribution rule is satisfied; genericity tier alone demonstrates neither V&V integration nor benefit.

### RQ2

- Synthesize only explicitly EPS-thread-attributed outcomes and implementation burdens.
- Keep EPS engineering outputs separate from records of MBSE-enabled value or burden.
- Present record role, outcome category, author-claimed and evidence-supported direction, burden category, proposed mechanism, evidence type, comparator, confidence, and lifecycle stage together.
- Treat unsupported claims as evidence about claim prevalence, not demonstrated effects; do not equate `not_reported` with a null result or infer net benefit from record counts.

### RQ3

- Map EPS target-to-model-to-V&V chains and stratify linkage scope (`eps_specific` versus `system_wide_eps_linked`), V&V object, criterion completeness, executed pre-physical evidence, and downstream model-to-test continuity.
- Report analysis-only, system-wide co-occurrence, and missing-link near misses separately; report a missing criterion as an evidence-completeness limitation rather than silently discarding an otherwise explicit EPS-linked V&V record.
- Do not infer EPS-specific V&V integration or an EPS-specific verdict from a system-wide activity or report-level co-occurrence.

### Cross-cutting safeguards

- Report separate denominators for study/implementation report families, reports, EPS model threads, reusable-artifact lineages/profiles, tailoring applications, input/assumption records, outcome/burden records, and V&V records. PRISMA flow counts remain record/report based.
- Treat tailoring applications, outcome/burden records, and V&V records as linked to reports and dependent within report families; do not treat report counts as independent artifact reuse.
- Stratify Route A and Route B before presenting combined totals.
- Identify recurring reports from the same study/implementation family; do not count them as independent replication.
- Stratify institutional technical reports, master's-level theses, doctoral dissertations/theses, and other grey literature from peer-reviewed scholarly reports and include publication-provenance sensitivity views where informative; do not automatically downweight a degree work solely because journal peer review is absent.
- Use quality, linkage/lineage confidence, and genericity-gate sensitivity views, including Route-A-only, high-confidence, G3/G4, and artifact-available subsets where informative; do not convert the genericity tier into a numerical quality score.
- Interpret cross-tabs only as descriptive co-reporting unless a direct extracted link supports a relationship.
- Retain `not_reported`, `none`, `not_applicable`, `uncertain`, and invalid/unmapped values distinctly.
- Treat sparse direct evidence as a review finding rather than filling gaps with generic whole-spacecraft MBSE claims.

## Required new-run artifacts

Once the clean-document start rule is met, the restarted review must generate or regenerate, with run provenance:

- dated methodological decision log, study/implementation report-family registry, reusable EPS artifact-lineage registry, tailoring-application table, and read-only legacy and Buruso-recall known-item registers;
- exact PRISMA-S-compatible search log, current source-matching dictionary/code, and raw source-specific search results, including PQDT selection proof and OATD interface/pagination artifacts;
- search manifest with source dates, interface details, restrictions, and rights/access status;
- merged/deduplicated candidate set and deduplication report;
- title/abstract and full-text screening log, retrieval log, accessible corpus, and cited full-text exclusion table with one primary reason per report;
- run-specific corpus, identifiers, and extraction codebook;
- per-report extraction files with thread, artifact-lineage/profile and tailoring-application links, outcome/burden, and V&V records, plus an artifact-level claim-to-evidence table;
- compiled extraction dataset, bibliography, validation report, and analysis code; and
- machine-readable PRISMA count reconciliation, official PRISMA 2020 flow diagram, synthesis outputs, and completed PRISMA-S/PRISMA 2020 checklists.

Licensed exports, copyrighted abstracts, and full texts need not be made public where rights prohibit it. Preserve them securely where permitted and publish or archive the exact methods, dates, manifests, derived counts/decisions, codebook, code, and a rights-aware availability statement.

## Completed-review reporting

The final report will identify itself as a systematic review and use the PRISMA 2020 checklist and 12-item abstract guidance. It will:

- report every information source actually used, its execution date, and the common 2026-08-10 evidence cutoff, with failed/planned-but-unused sources distinguished;
- link to verbatim final source-native strategies and PRISMA-S logs rather than a cleaned representative query;
- describe screening, extraction, second checks, conflict handling, and model assistance exactly as performed, never calling model-assisted checking independent human review;
- explain that no pooled effect estimate is planned and label every descriptive count/proportion by its report-family, report, thread, artifact-lineage/profile, tailoring-application, outcome/burden, or V&V denominator;
- use the new-review databases-and-other-sources flow diagram with records/reports—not linked analytic units—in its boxes;
- cite apparently eligible full reports excluded at full text with source-locatable reasons;
- present appraisal, reporting-bias, and conclusion-confidence results using the [appraisal framework](protocol-discovery-and-appraisal.md#appraisal-meaning-reporting-bias-assessment-and-conclusion-confidence); and
- report access to the current protocol and query plan, every dated methodological change/deviation, review-process and evidence limitations, and data/code/material availability.

The exact administrative declarations intentionally deferred in the [reporting framework](protocol.md#reporting-framework) must be completed or explicitly reported as absent before publication; they are not silently implied by the clean-document start rule.

All dated source-interface, bounded-genericity/search, source-addition, completion, IAF, and PQDT/OATD pilots are logged as no-screening diagnostics. This model-assisted protocol and search review involved no human information specialist; model-assisted checks and source pilots are not represented as formal PRESS review or independent human peer review. No pilot output, calibration record, or opaque source identifier is a candidate, and every discovery method—including PQDT, OATD, and IAF—must write clean final-run artifacts. The review may start solely when `protocol.md`, `protocol-discovery-and-appraisal.md`, `protocol-extraction-and-synthesis.md`, and `query-search-plan.md` have no uncommitted changes; there is no protocol/query-plan version, freeze, separate authorization, or cumulative pre-final gate.

---

**Previous:** [Part 2 — Discovery and appraisal](protocol-discovery-and-appraisal.md)
