# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Synthesis

Use a structured evidence map and narrative synthesis. Resolve every `record_kind:stable_id` reference before compiling a table. Compare controlled fields, canonical entity keys, typed quantities, and explicit relationships. Preserve linked source wording for auditability and exclude fields marked `not_for_synthesis` from direct comparison. Do not pool effect estimates because the models, outcomes, and evidence designs are expected to differ too much.

### Relationship to Buruso et al. (2026)

Buruso et al. (2026) is a broad secondary review of 126 selected space-MBSE studies and reports published from 2011 through 2023. It maps methods, languages, tools, five MBSE phases, and general challenges across many kinds of space work.

### RQ1

#### Representation and use

- Present Route A and Route B separately before combining them. Map report context through linked mission, platform, organization, problem, purpose, quantity, and decision records. Compare lifecycle use and project maturity through their controlled codes.
- Map EPS anchors and boundaries using typed elements, requirement records, linked exchanges, dependencies, and bridges. Compare every coded exchange and dependency type. Compare functions, behaviors, actors, external systems, subsystems, logical and physical components, interfaces, modes, scenarios, parameters, hazards, element hierarchy, abstraction, model inclusion, and boundary roles. Synthesize declared coverage, item level inclusions and exclusions, coverage basis, architecture, disciplinary viewpoints, purposes, supported decisions, maturity, and availability. Derive case-level abstraction, decomposition-visibility, and fidelity sets from the representation records.
- Treat each structured model representation as a nested analytic unit. Map source and normalized view types, representation forms, origin, completeness, abstraction levels, decomposition visibilities, fidelity levels, language or notation, containing artifacts, tools, represented content, and relationships among views. Compare context, requirement, use-case, behavior, activity, sequence, state, logical, physical, interface, data-flow, energy-flow, parametric, allocation, V&V, and generated-result views. For dynamic views, map behavior occurrences, order, actors or endpoints, exchanges, guards, branches, timing, and outputs.
- Synthesize model generation methods and engineering workflows separately from modeling languages, typed tool and equipment records, and toolchains. Map tool kinds and roles, explicit method-origin arrays, workflow-scope arrays, construction sources, generic-model derivation, ordered method steps, workflow activities and handoffs, linked artifacts, inputs and outputs, atomic and derived aggregate automation levels, governance, supporting materials, and procedural-detail levels.
- Synthesize item level inputs and assumptions, typed values, source types, uncertainty records, evaluation units, evaluation-design components, methods integration, execution, typed engineering outputs and statistics, criteria, implementation needs, burden phases, footprint, linked issues, and evaluative RQ1 claims. Use normalized characteristic codes for genericity, modularity, completeness, scalability, adaptability, reuse, replication, interoperability, and related claims. Preserve source labels and author rationales. Compare each claim with linked results, footprint, coverage, and inline support.

#### Reuse and tailoring

- Present all `report_reuse_level` values as source-bounded report-level artifact results. Synthesize artifact identity, artifact-type arrays, scoped generality, availability, licence, resolved lineages, applicability envelopes, reusable cores, variation-point target arrays, tailoring rules and procedure steps, application-object arrays, tailoring effort, assurance, independence, failures, demonstrated coverage, and `lineage_reuse_level` from the separate lineage-level records. Use lineage and consolidated-application denominators for deduplicated artifact conclusions, and keep unresolved report-level cases visible.
- Present all `method_reuse_level` values from M0 through M4 as source-bounded report-level results, separately from the R0–R4 artifact progression. Synthesize method applicability envelopes, stable cores, variation points, adaptation, effort, assurance, independence, failures, and demonstrated settings. Use model generation method and report-level method application denominators and account for report-family dependence. A single report can support M4 when it contains the required independent application and assurance evidence.
- Present all `workflow_reuse_level` values from W0 through W4 separately. Synthesize workflow boundaries, stable activities and handoffs, variation points, adaptation, effort, assurance, independence, failures, and demonstrated settings. Use workflow and report-level workflow application denominators.
- Cross-tabulate procedural-detail levels with reuse levels without treating either as a substitute for the other. Report the procedural-evidence profile flags and identify reports that combine a generic or reference model with an actionable construction or tailoring procedure. Treat `reproduction_ready` as reported procedural readiness, not as evidence that the review reproduced the procedure.

### RQ2

- Use only findings with `direct_synthesis = yes` for direct conclusions. Present near misses separately.
- Present claim kind and scope, role arrays, category, scoped author direction components, scoped evidence-supported direction components, mechanism, linked model representations, measure directness, evidence basis, support, comparator adequacy and rival explanations when required, applicability, and lifecycle-stage arrays.
- Present assertion-only findings separately from executed, comparative, stakeholder, physical, operational, and independent-transfer evidence.
- Preserve raw source values through their links. Compare typed values using canonical units, explicit time bases, denominators, groups or arms, sample sizes, and uncertainty records. Label reviewer-derived quantities.
- Keep benefits, null findings, adverse findings, and burdens visible without calculating a reviewer-defined net effect.

### RQ3

- Use only activities with `direct_synthesis = yes` for direct conclusions. Present system-wide co-occurrence, downstream physical activities retained only for continuity, and other near misses separately.
- Map each linked activity sequence from its EPS target, requirements, tailored model artifact and configuration through its workflow activities, V&V objects, verification levels, test phases, environments, methods, criteria, execution settings, hardware presence, results, discrepancies, cumulative status, and model-to-test closure.
- Compare model and digital twin assurance by target type, model role, assessment aspect, assessment method, declared completeness denominator, correctness or validation oracle, result, evidence basis, and support.
- Compare controlled arrays by their individual values and reported combinations. Do not collapse combinations into aggregate categories.
- Keep EPS-specific and system-wide EPS-linked activities separate.
- Distinguish model verification, model validation, system or design verification, system or design validation, virtual execution, physical execution, and model-to-test closure.
- Record comparator adequacy and rival explanations only for comparative or causal V&V-effectiveness claims.

### Cross-cutting safeguards

- Apply the canonical units, denominator, and dependence rules in Part 1.
- Separate peer-reviewed reports from preprints, technical reports, and theses in descriptive or sensitivity views when useful.
- Apply the [finding-support and conclusion-confidence framework](#finding-support-reporting-bias-assessment-and-conclusion-confidence) below.
- Use sensitivity views by route, evidence basis, support, measure directness, comparator adequacy when required, publication provenance, lineage confidence, reuse level, and artifact availability.
- Treat cross-tabulations as descriptive co-reporting unless extraction establishes a direct link.
- Treat sparse direct evidence as a result. Do not fill gaps with whole-spacecraft MBSE claims.

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
- present evidence basis, finding support, reporting-bias considerations, reuse levels, and conclusion confidence under the framework below.
- report all protocol changes and departures.
- state access to the protocol, data, code, and materials.

## Finding support, reporting-bias assessment, and conclusion confidence

Do not make a funnel plot or run a statistical publication-bias test. The evidence does not share one effect measure and is too varied. Instead, assess and report the following for each research-question synthesis:

- source and interface coverage, failures, and unique results across the 15 sources, 13 interfaces, and citation routes, with OATD in the website/other-methods channel;
- the effects of language, date, population, publication-type, retrieval, and source-access limits;
- specific access and coverage issues, geographic and institutional imbalance, embargoes, missing abstracts or metadata, uncertainty about degree status, and overlap between PQDT and OATD or other platforms;
- reports that could not be obtained and records that were only leads;
- missing or selectively reported generation methods, workflows, method inputs and assumptions, construction sources, generic-model derivation, procedural components, reuse claims, applicability limits, tailoring or adaptation effort, failures and burdens, outcomes and burdens, direct and surrogate measures, comparators, rival explanations, pass/fail criteria, null or adverse results, and limitations;
- dependence caused by reports from the same study or implementation family and repeated reports of the same artifact lineage, method, or application;
- review-process limitations documented under the [extraction-verification procedure](protocol-extraction.md#sole-reviewer-extraction-and-verification); and
- protocol departures, search changes, and review-process limits that could affect interpretation.

Treat the sole-reviewer and model-assistance items as review-process limitations, not as publication or selective-reporting bias in the primary studies.

Give each conclusion a narrative confidence label: `higher`, `moderate`, `lower`, or `insufficient`. Give a source-locatable reason. Consider:

- the kind and scope of claim being synthesized;
- directness to a qualifying EPS thread;
- fitness of the contributing evaluation designs for the synthesized claim;
- whether measures are direct or are justified surrogates;
- comparator adequacy and major rival explanations when the claim is comparative or causal;
- finding-level evidence basis, support, and applicability;
- the artifact lineage, generation method, or workflow, applicable reuse and procedural-detail levels, demonstrated coverage, and tailoring or adaptation effort when relevant;
- maturity, independence, or physical validation only when they bear directly on the claim;
- consistency, including null, adverse, and failed-transfer evidence;
- independence of report families and reuse or tailoring applications; and
- limitations in the review process.

Evidence basis and maturity remain descriptive and do not determine confidence by themselves. Never convert a reuse level, coding-confidence value, publication type, or finding-support label automatically into a conclusion-confidence label. Do not use a numerical cutoff or mechanical average.

- **Higher:** several materially independent, directly linked, credible findings or activities support the bounded conclusion, all requirements relevant to that kind of claim are met, and there is no major unexplained disagreement.
- **Moderate:** direct support exists, but there are important limitations in methodology, independence, precision, applicability, or consistency relevant to the conclusion.
- **Lower:** support is sparse, methodologically concerning, indirect, dependent, or importantly inconsistent.
- **Insufficient:** there is no eligible direct evidence for the conclusion.