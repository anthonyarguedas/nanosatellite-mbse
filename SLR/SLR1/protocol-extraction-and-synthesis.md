# Protocol for a Systematic Review of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Extraction and synthesis

> **Protocol parts:** [1 — Scope and definitions](protocol.md) · [2 — Discovery and appraisal](protocol-discovery-and-appraisal.md) · **3 — Extraction and synthesis** (this file)
>
> **Definitions used here:** [eligible EPS evidence routes](protocol.md#eligible-eps-evidence-routes), [bounded genericity](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring), and the [quality checklist](protocol-discovery-and-appraisal.md#quality-checklist).

## Extraction fields

Before extracting any report, create a new `extraction_codebook.json` for this run from this protocol. Earlier codebooks and forms do not govern this run. Do not copy their contents into new-run fields.

For every controlled code that matters to the synthesis, record:

- the reason for the code;
- a direct quotation or source location when possible; and
- a confidence rating.

Keep these statuses separate: `not_reported`, `not_applicable`, `none`, and `uncertain`. Also distinguish what the authors report from what the extractor infers.

### Shared extraction structures

Use shared structures rather than copying the same facts into several records:

- An **evidence reference** stores report ID, page or section, figure or table when relevant, quotation or cautious paraphrase, and extractor confidence.
- A **setting tuple** stores platform and form factor; mission purpose and domain; orbit and environment; lifecycle use and decision; EPS boundary, architecture, components and interfaces; modes and load profile; abstraction or fidelity; required inputs; language, tool and version; organization, team and process; prerequisites; and exclusions or failure boundaries.
- An **implementation footprint** stores roles, skills and training; staffing; process and automation; tools, licences and infrastructure; model and data preparation; computing; integration and interoperability; governance and configuration control; effort, time, schedule and cost; maintenance; burdens; and mitigations.

Give each shared object an ID, scope, evidence reference, and confidence. Link it from report, thread, artifact, application, outcome, or V&V records as appropriate. Keep declared, planned, and actually observed values separate even when they use the same structure.

### Report-level bibliographic and review-management fields

For each report, record:

- the new-run report ID, optional old corpus ID, and extraction-file path;
- full citation, title, authors, year, venue or institutional report series, publication type, DOI or URL, publisher or issuing organization, source or report ID, and any reported peer or technical review;
- every linked new-run discovery-event ID and source record ID; keep the exact query or citation route, date, rank, and raw-file provenance once in the new search log and manifest;
- title and abstract screening tier and reason;
- final full-text decision and exclusion reason, if excluded;
- Route A or Route B and the supporting evidence;
- contribution status for RQ1a, RQ1b, RQ2, and RQ3;
- the number of linked artifact-lineage profiles and tailoring applications for RQ1b;
- the number of eligible RQ2 outcome or burden records;
- the number of direct and near-miss RQ3 records;
- study or implementation report-family ID or IDs;
- linked artifact-lineage ID or IDs;
- the report's relationship to each family or artifact: `same_report_manifestation`, `derivative_report`, `companion_report`, `overlap_uncertain`, or another controlled value;
- the reason and evidence for family membership or artifact identity, confidence in overlap, and notes on shared results; and
- extraction confidence, assessor, and review-pass history.

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

### Study context and MBSE qualification

Record:

- mission or platform, form factor or mass when reported, mission name and domain, organization type, and project maturity;
- lifecycle stage actually demonstrated, kept separate from stages that authors only claim or plan;
- development setting: academic or student, agency, industry or NewSpace, distributed team, agile or concurrent design, rapid prototyping, resource-constrained mission, or `not_reported`;
- a general implementation-footprint link for reported MBSE needs and burdens, or `not_reported`;
- the authors' objective, problem, intended decision, and reason for using MBSE;
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
- thread maturity, lifecycle stage, availability, evidence confidence, and limitations.

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
- confidence in and reason for the lineage.

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

- status, reason, source location, and confidence for every A/E/C/T/P/I gate;
- failed condition or conditions;
- highest tier: `NA`, `G0_artifact_only`, `G1_claimed_or_unbounded`, `G2_bounded_reuse_specified`, `G3_bounded_reuse_demonstrated`, or `G4_independently_corroborated`;
- a locatable cumulative reason for that tier;
- claim agreement: `not_evaluated`, `supported_in_tested_contexts`, `partially_supported`, `mixed`, `not_supported`, or `unclear`; and
- failed and outside-envelope applications and other possible explanations.

Finally, record profile limits, model and data availability, dependence between report families and within the lineage, evidence source, extraction confidence, and first- and second-check history.

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
- failures, rework, and trade-offs; and
- whether this shows artifact reuse, only method or workflow reuse, or is unclear.

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

Record the evidence source, confidence, limitations, and extraction and second-check history.

One application can inform RQ1b and link to an RQ2 outcome or burden or an RQ3 V&V record. It enters those direct syntheses only when it separately meets their attribution and linkage rules.

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
- evidence source and extraction confidence.

Do not infer that an input is unnecessary because the source omits it. Use `not_reported` for source silence.

### EPS engineering outputs

Keep technical outputs separate from MBSE outcome and burden records. For each output, record:

- output ID and thread ID;
- quantity or result, units, and time basis;
- scenario or configuration and input set;
- whether it was calculated, simulated, checked against a criterion, compared, or physically validated;
- decision or model artifact it informed; and
- evidence source and confidence.

### RQ2 outcome and implementation-burden evidence record

Create one atomic record for every candidate outcome or burden that is explicitly or plausibly linked to a qualifying EPS thread. Do not extract every general MBSE claim merely because it appears in an eligible report. Split a statement that reports several outcomes into separate records. Link records that share evidence through source IDs.

Record the claim and its scope:

- record ID and linked thread ID;
- exact result or claim, or a cautious paraphrase;
- role: outcome, implementation burden, mixed trade-off, or another role;
- scope and target;
- outcome category: EPS reliability; system or mission assurance; defect or error reduction; risk reduction; reproducibility or rerunnability; reuse or replication; integration or interoperability; interface consistency; traceability or requirements quality; completeness; continuity across the lifecycle; decision or trade support; cost; schedule; effort or automation; communication or knowledge; governance or value realization; or another category;
- reported direction: `beneficial`, `null/no observed effect`, `mixed/conditional`, `adverse`, or `unclear/not reported`; and
- author-claimed direction, kept separate from the direction supported by the evidence.

Record the basis for direction:

- how the metric is interpreted;
- comparator or criterion;
- time horizon;
- magnitude, value, and units;
- conditions; and
- whether the result is observed or expected.

For a burden, record:

- category: time or effort; skills or training; staffing; tools, licences, or infrastructure; model or data preparation; computing; integration or interoperability; maintenance, configuration, or governance; schedule; cost or resource use; another category; none reported; or not reported;
- affected person or group;
- whether it occurs during adoption or ongoing use;
- mitigation; and
- any linked benefit or trade-off.

For reliability, use the relevant subtype: EPS reliability, system or mission reliability, process reliability, model consistency or reliability, mission assurance, defect or error reduction, generic reliability claim, or not applicable.

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

Classify attribution as `explicit EPS-thread attribution`, `ambiguous attribution`, or `generic/not eligible`. Only explicit EPS-thread attribution enters direct RQ2 synthesis.

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

Record the metric or value, baseline or comparator, observed effect or burden, evidence source, possible alternative explanations, and report-family or nesting notes.

Give each record an evidence-confidence level:

- **Unsupported:** an assertion with no extractable support.
- **Weak:** a plausible explanation or illustrative or single-case evidence, but no result strong enough to support the claimed direction or burden.
- **Moderate:** a traceable within-case result, executable or checking result, or metric, but with little comparison or independent validation.
- **Strong:** suitable comparative, repeated-reuse, independent, integration or test, operational, or flight evidence that directly supports the direction or burden.

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
- whether the result is EPS-specific, system-wide, or `not_reported`;
- how discrepancies were handled;
- later link to software integration, hardware integration, flat-sat or bench work, PIL or HIL, environmental testing, operational validation, or flight evidence;
- EPS-linked RQ3 eligibility as `yes`, `no`, or `uncertain` for the target–bridge–V&V-method/intent rule, including the failed condition when the answer is no;
- criterion-complete status as `yes`, `no`, or `uncertain`, with evidence; and
- demonstrated pre-physical execution as `yes`, `no`, or `uncertain`, with evidence about timing, physicality relative to the target, and result.

Also record evidence source, confidence, limitations, and report-family or nesting notes.

### Limitations and open extraction

Record author-stated limits, assumptions, and scope boundaries. Use narrow controlled flags for substantive limitations such as prototype or future work, single case, no comparator, no independent validation, assumptions or data-quality limits, tool dependence, interoperability limits, and incomplete lifecycle coverage.

Do not manually duplicate conditions already represented by structured fields. Derive flags such as missing V&V criterion, unclear EPS linkage, missing DAE, unidentified reusable core, unclear lineage, same-family reuse only, or absent post-tailoring assurance during validation. This keeps the flag and its source field consistent.

Use emergent codes for unexpected findings that do not fit the controlled vocabulary. Do not silently add new controlled categories during extraction.

## Calibration, consistency, and validation

Before full screening and extraction:

1. Test the full-text eligibility rule on examples of clear Route A, clear Route B, general whole-spacecraft MBSE, and non-MBSE EPS work.
2. Test all forms on a deliberately varied sample. This includes the thread, input and assumption, artifact-lineage and profile, tailoring-application, RQ2 outcome and burden, and RQ3 V&V forms. Include examples of method-only versus artifact reuse, claim-only evidence, bounded specification, one versus several materially different settings, duplicate reports from one family, unchanged reuse, failed transfer, and post-tailoring assurance.
3. Revise and commit the run-specific codebook before full extraction.
4. Record all calibration decisions and examples.

Use separate assessment passes to reduce carryover from earlier judgments. Require a second check for:

- every final Route B inclusion;
- every decision to merge or split artifact lineages;
- every G3 or G4 tier;
- every direct RQ2 linkage; and
- every direct RQ3 linkage.

During calibration, make sure assessors can distinguish:

- a DAE from one observed case;
- a scenario sweep from tailoring;
- a model artifact from a method or workflow;
- separate reports from separate applications; and
- post-tailoring assurance from direct RQ3 V&V.

Record whether another human or a model-assisted validation pass performed each check. Never describe a model-assisted check as independent human review. Calculate an agreement statistic only if the assessment design truly supports it.

Before synthesis, validate all extraction JSON against the codebook. Check exact controlled labels, record IDs, required evidence and reasons, distinct statuses, and all links among report families, reports, threads, artifact lineages, genericity profiles, tailoring applications, outcome or burden records, and V&V records.

## Planned synthesis

Use a structured evidence map and narrative synthesis. Do not pool effect estimates because the models, outcomes, and evidence designs are expected to differ too much.

### Relationship to Buruso et al. (2026)

Buruso et al. (2026) is a broad secondary review of 126 selected space-MBSE studies and reports published from 2011 through 2023. It maps methods, languages, tools, five MBSE phases, and general challenges across many kinds of space work.

Use that review for context, terminology, a later recall check, and recorded citation searching. Do not use it as primary evidence.

This review is not an update or replication of Buruso et al. It applies this protocol's narrower nanosatellite-EPS population, direct EPS linkage rule, and RQ1–RQ3 evidence structures. Do not treat system-wide MBSE or V&V as EPS evidence or compare the two reviews' counts as evidence of effectiveness.

For a descriptive view of currency and overlap, results may be split into 2011–2023, matching Buruso et al.'s evidence window, and 2024 through the common evidence cutoff. This split does not change eligibility or imply independence.

### RQ1a

- Synthesize the study-context, EPS-thread, input-and-assumption, engineering-output, and implementation-footprint records defined above.
- Keep reported inputs and implementation needs separate from reviewer inference and missing information.
- Compare author labels such as *lightweight* or *scalable* with the reported footprint; do not turn them into eligibility or tailoring categories.
- Compare Route A with Route B without assuming that one route is more mature.

### RQ1b

- Synthesize artifact-lineage profiles and tailoring applications under the gate and tier definitions in Part 1; keep method or workflow reuse separate from artifact reuse.
- Present tiers at artifact-lineage/profile level, with the full gate vector, DAE breadth, demonstrated coverage, claim agreement, and failures or conflicts kept separate.
- Merge duplicate reports of one application and use artifacts and applications—not publication counts—as transfer denominators. Distinguish same-family, separate-team, and independent use.
- Describe a tier only within the artifact scope and demonstrated settings. Do not call an artifact proven, universally generic, or generic without context.
- Include a tailoring check or burden in RQ3 or RQ2 only when it separately meets that question's linkage or attribution rule.

### RQ2

- Synthesize only outcomes and implementation burdens that the source explicitly attributes to a qualifying EPS thread.
- Keep EPS engineering outputs separate from evidence about value or burden caused by MBSE.
- Present together the record role, outcome category, author-claimed direction, evidence-supported direction, burden category, proposed mechanism, evidence type, comparator, confidence, and lifecycle stage.
- Treat an unsupported claim as evidence that the claim was made, not that an effect was demonstrated.
- Never treat `not_reported` as a null result.
- Do not infer net benefit by counting positive and negative records.

### RQ3

- Map every EPS target-to-model-to-V&V chain.
- Separate `eps_specific` from `system_wide_eps_linked` records.
- Also organize evidence by V&V object, completeness of the criterion, execution before physical work, and later model-to-test continuity.
- Report analysis-only work, system-wide co-occurrence, and other missing-link near misses separately.
- Treat a missing criterion as incomplete evidence. Do not silently discard an otherwise explicit EPS-linked V&V record.
- Do not infer EPS-specific V&V integration or an EPS-specific verdict from a system-wide activity or from items that only appear in the same report.

### Cross-cutting safeguards

- Apply the [canonical units, denominator, and dependence rules](protocol.md#units-of-evidence-and-counting).
- Present Route A and Route B separately before combining them.
- Separate institutional technical reports, master's theses, doctoral theses or dissertations, and other grey literature from peer-reviewed scholarly reports. Show sensitivity views by publication provenance when useful. Do not automatically give a degree work less weight merely because it lacks journal peer review.
- Use sensitivity views based on quality, linkage and lineage confidence, and genericity gates. Useful subsets may include Route A only, high-confidence records, G3/G4 profiles, and available artifacts. Do not turn the genericity tier into a numerical quality score.
- Treat cross-tabulations as descriptive co-reporting unless extraction provides a direct link.
- Keep `not_reported`, `none`, `not_applicable`, `uncertain`, and invalid or unmapped values separate.
- Treat sparse direct evidence as a result of the review. Do not fill gaps with general whole-spacecraft MBSE claims.

## Required new-run artifacts

After the clean-document start condition is met, create these artifacts anew with run provenance. Do not restore an earlier run's log, dictionary, schemas, decisions, or data:

- a dated methods decision log;
- a study or implementation report-family register;
- a reusable EPS artifact-lineage register;
- a tailoring-application table;
- read-only known-item registers for legacy reports and Buruso recall;
- a new `search-log.md` meeting PRISMA-S requirements;
- a new `searches/search-concept-dictionary.json` and matching code generated from Part 2;
- new source/interface crosswalk, final-run manifest schema, and failure-register schema;
- raw source-specific search results and source-selection or interface proof;
- a search manifest with dates, interface details, restrictions, rights, and access status;
- a merged and deduplicated candidate set and deduplication report;
- title and abstract screening, full-text screening, and retrieval logs;
- the accessible report set and a table of cited full-text exclusions with one main reason per report;
- the run-specific corpus, IDs, and extraction codebook;
- per-report extraction files with links among threads, profiles, applications, outcomes or burdens, and V&V records;
- an artifact-level claim-to-evidence table;
- the compiled extraction data, bibliography, validation report, and analysis code; and
- machine-readable PRISMA count reconciliation, the official PRISMA 2020 flow diagram, synthesis outputs, and completed PRISMA-S and PRISMA 2020 checklists.

Do not publish licensed exports, copyrighted abstracts, or full texts when rights prevent it. Keep them secure where allowed. Publish or archive the exact methods, dates, manifests, derived counts and decisions, codebook, code, and a statement that explains what can and cannot be accessed.

## Completed-review reporting

The final report will call itself a systematic review and will follow the PRISMA 2020 checklist and 12-item abstract guidance. It will:

- name every source actually used, give its search date and the common evidence cutoff, and distinguish failed or planned-but-unused sources;
- link to the exact final source-native searches and PRISMA-S logs instead of showing only a cleaned example query;
- describe screening, extraction, second checks, conflict handling, and model assistance exactly as performed;
- never call model-assisted checking independent human review or describe source pilots as formal PRESS review;
- explain why no pooled effect estimate is planned;
- label every count or proportion with its denominator: report family, report, thread, artifact lineage or profile, tailoring application, outcome or burden, or V&V record;
- use the new-review PRISMA flow diagram for databases and other sources, with records and reports—not linked analytic units—in its boxes;
- cite apparently eligible reports excluded after full-text review and give source-located reasons;
- present appraisal, reporting-bias, and conclusion-confidence results under the [appraisal framework](protocol-discovery-and-appraisal.md#appraisal-meaning-reporting-bias-assessment-and-conclusion-confidence); and
- report access to all three parts of the current protocol, every dated methods change or departure, limits of the review process and evidence, and availability of data, code, and materials.

Complete the administrative declarations deferred in the [reporting framework](protocol.md#reporting-framework) before publication, or clearly say that they are absent. The clean-document start condition does not imply that these declarations exist.

Apply the [clean-document start and change policy](protocol.md#review-status-and-restart-policy).

---

**Previous:** [Part 2 — Discovery and appraisal](protocol-discovery-and-appraisal.md)
