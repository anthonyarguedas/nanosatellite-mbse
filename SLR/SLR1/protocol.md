# Review Protocol: Model-Based Systems Engineering for Nanosatellite Electrical Power Systems

- **Review run ID:** `eps-mbse-slr-2026`
- **Protocol version:** `1.0`
- **Approval date:** 2026-08-06

## Review status and restart policy

This protocol defines a **new systematic review run** focused on nanosatellite electrical power system (EPS) MBSE. It is not an amendment to the earlier whole-nanosatellite/EPS review.

The earlier searches, screening decisions, corpus, extractions, codebook, synthesis, and manuscript are treated as legacy or pilot artifacts. They do not determine eligibility or evidence membership in this run. In particular:

- no previously identified report is automatically included;
- all records must be found through a documented new-run search or citation-chasing route and screened against this protocol;
- previous reports may be used only as known-item recall checks when refining the search;
- every included report must be newly extracted from its full text against a new run-specific codebook; prior extraction may be consulted only during a later discrepancy audit and may not supply new-run evidence;
- prior counts and classifications must not be carried into the new synthesis; and
- DOI/title matching may retain a prior corpus ID only as a `legacy_corpus_id`; new-run report, EPS-thread, claim, and V&V-record identifiers must be run-specific.

The protocol becomes fixed when approved by the researcher and before the new searches begin. Any later deviation will be recorded prospectively in the new run's search or decision log.

## Approval and pre-search decision record

- **Approval/search authorization date:** 2026-08-06
- **Frozen version:** `1.0`
- **Working branch:** `slr1-1.0-restart`

The researcher supplied the `1.0-draft`, identified its material design choices, directed that the review be restarted on a new branch, and explicitly authorized production of the query plan and commencement of new searches. That instruction approved the freeze of version `1.0` before searching.

The identified choices were reviewed and retained as follows:

1. **PocketQube/picosatellite-only exclusion.** This is consistent with the CubeSat/nanosatellite population. Mixed studies remain eligible only when CubeSat/nanosatellite evidence is separable; searches do not deliberately target excluded platforms.
2. **Open RQ2 outcome set.** This avoids outcome-reporting bias. Reliability/mission assurance, reproducibility/reuse, and integrability/interoperability remain priority strata; other outcomes require the same explicit EPS-thread attribution and evidence coding.
3. **Tiering incomplete V&V records.** An EPS target, explicit model-to-V&V bridge, and reported V&V method/intent/artifact establish the lowest linked tier. Missing criterion, execution, verdict, or timing remains missing evidence and cannot support a higher tier.
4. **Broad Stream B.** This is necessary because embedded EPS threads may be absent from metadata. Query partitioning, count pilots, conservative title/abstract retention, and separate unique-yield accounting control workload without imposing an EPS keyword.
5. **New extraction for every included report.** Legacy extraction and synthesis files were removed. Retained source Markdown/PDF files may be reused only after independent rediscovery and new screening.

Pre-search anti-anchoring controls are part of this approval:

- legacy search results, screening, corpora, codebook, extractions, scoping review, and manuscript were removed before searching;
- `markdown/` and `pdfs/` were retained only as a source-file cache outside the search evidence base;
- retained files cannot supply candidates, eligibility decisions, IDs, or extracted data;
- matching against retained files is deferred until the independent primary-database candidate set is merged, and matches serve only as recall and retrieval checks; and
- old corpus or extraction data may not be reconstructed from Git history during new search or screening.

There were no deviations at search start. Any later change requires a prospective entry stating its date, rationale, affected artifacts, and protocol version.

## Review objective

To synthesize how nanosatellite EPSs are represented through MBSE, why those models are constructed, which inputs and assumptions they depend on, which EPS-linked outcomes are claimed, and how EPS verification and validation (V&V) are integrated before physical integration or test.

The analytic scope includes both:

1. **EPS-primary MBSE**, where the EPS is the principal modeled system or viewpoint; and
2. **embedded EPS model threads**, where a broader nanosatellite model contains an explicit, extractable chain linking EPS content to systems-engineering artifacts or activities.

Generic whole-spacecraft MBSE evidence does not answer the research questions merely because EPS and another artifact occur in the same report.

## PICOC

| Population | Intervention | Comparison | Outcome | Context | Related RQ(s) |
|---|---|---|---|---|---|
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-primary MBSE or an explicit embedded EPS model thread | Not required | EPS representation, model purpose, required inputs and assumptions, abstraction, reuse, and tailoring | Nanosatellite systems engineering across the lifecycle | RQ1 |
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-linked MBSE artifacts, analyses, and model-enabled activities | When reported: document-centric practice, manual analysis, alternative toolchain, previous mission/model, or other explicit comparator | EPS-linked technical and engineering-process outcomes, especially reliability/mission assurance, reproducibility/reuse, and integrability/interoperability | Nanosatellite development and decision making | RQ2 |
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-linked model-based V&V before physical integration or test | Separate or document-based V&V, manual checking, another method, or no comparator when reported | Traceability to V&V artifacts, executable checks, verdicts, virtual integration, and model-to-test continuity | Pre-physical analysis and V&V, with downstream physical links recorded separately | RQ3 |

## Research questions

1. **RQ1 — representation, purpose, and prerequisites.** How are nanosatellite EPSs represented in EPS-primary MBSE models and embedded EPS model threads; for what stated purposes; what inputs, assumptions, and abstraction choices are reported; and how are the models intended to be reused or tailored?

2. **RQ2 — EPS-linked outcomes and evidence.** Which EPS-specific technical or engineering-process outcomes—particularly reliability/mission assurance, reproducibility/reuse, and integrability/interoperability—are explicitly attributed to EPS MBSE artifacts or model-enabled activities, through what mechanisms, and with what supporting evidence?

3. **RQ3 — EPS-linked pre-physical V&V.** How are pre-physical V&V activities explicitly linked to EPS requirements, model elements, analyses, or interfaces, and what level of preparation, execution, result reporting, and model-to-test continuity is demonstrated?

## Operational definitions

### Nanosatellite population

An eligible platform is an actual or intended orbital spacecraft that the source identifies as a CubeSat or nanosatellite, including recognized CubeSat form factors even when a particular implementation falls outside a strict 1--10 kg mass definition. A reference, template, or early-phase design model may qualify without a named or realized mission when its stated target population is orbital CubeSat/nanosatellite development.

Exclude:

- CanSats and other non-orbital educational demonstrators;
- PocketQube/picosatellite-only studies unless a separable CubeSat/nanosatellite case is also reported;
- larger small satellites or conventional spacecraft unless results for a CubeSat/nanosatellite case can be extracted separately; and
- mixed-platform evidence when nanosatellite-specific findings cannot be separated.

### EPS boundary

EPS content may include power generation; solar arrays; storage and battery management; conversion, conditioning, regulation, and distribution; protection, monitoring, and control; electrical buses and harnesses; power interfaces; operational modes; load and energy profiles; power/energy budgets and margins; degradation; faults and fault management; and relevant requirements.

Other subsystems are in scope only as explicit EPS loads, interfaces, environmental dependencies, operating-mode drivers, or sources of EPS requirements. Their internal design is not synthesized.

### MBSE qualification

A report need not use the acronym “MBSE,” but it must describe a structured system model used for a systems-engineering purpose and provide extractable evidence of modeled elements and relationships across at least two systems-engineering concerns, such as requirements, functions/behavior, architecture, interfaces, parametrics/analysis, design decisions, or V&V. For report eligibility, those relationships must involve the same EPS entity or thread used to justify inclusion; unrelated report-level MBSE does not qualify otherwise isolated EPS content.

Examples may include SysML, Arcadia/Capella, object-oriented systems models, reference models, or connected digital-engineering environments. A stand-alone circuit model, battery model, SPICE/MATLAB/Simulink simulation, optimization, power-budget spreadsheet, or component-sizing calculation is not MBSE by itself. It qualifies only when its inputs or outputs are explicitly bound, traced, transformed, or otherwise linked to a structured system model.

### Eligible EPS evidence routes

A full-text report is assigned one of two mutually exclusive eligibility routes. Route A takes precedence only when the stated objective, modeled viewpoint/boundary, and substantive method or results center on EPS. Otherwise, a qualifying report is Route B. A report may contain multiple EPS threads, but its report-level route remains fixed.

- **Route A — EPS-primary MBSE:** the EPS, electrical-power viewpoint, or a defined EPS function/architecture is the principal modeled boundary, and the report provides an identifiable EPS model artifact plus at least one explicit relation involving that EPS content and a second systems-engineering concern.
- **Route B — embedded EPS model thread:** a broader nanosatellite MBSE report contains at least one qualifying EPS thread meeting all three conditions below.

A qualifying embedded EPS model thread requires:

1. an **EPS anchor**: a named EPS requirement, function, behavior, component, interface, mode, load/profile, budget, parameter, constraint, or hazard;
2. a **model anchor**: an identifiable representation of that EPS content in a structured system-model artifact or explicitly connected analysis model; and
3. an **explicit bridge**: a reported, source-locatable relation connecting the EPS anchor to a second concern such as a requirement, behavior, architecture/interface, analysis, decision, output, or V&V artifact. Eligible bridges include allocation, trace, satisfy/refine/verify relations, interface/flow, parametric binding, transformation, and data mapping.

Containment in a generic spacecraft breakdown, an EPS label, or an equipment-list entry may establish where an anchor appears but is not a sufficient bridge by itself. The source need not name a formal relation type, but the relation's endpoints and meaning must be reconstructable. The anchors and bridge must be supported by text, a figure/table, a model extract, a trace record, or another locatable source. Keyword presence, reviewer inference, or report-level co-occurrence is insufficient.

### MBSE-enabled outcome versus EPS engineering output

An **EPS engineering/model output** is a result such as minimum state of charge, power margin, battery capacity, solar-array area, voltage/current, energy balance, or a selected architecture. Such outputs are extracted for RQ1 and may support RQ2 or RQ3, but they are not automatically evidence of MBSE value.

An **RQ2-eligible MBSE outcome claim** must provide:

1. an eligible EPS model thread or named EPS-linked model artifact/activity;
2. a claimed technical or engineering-process outcome explicitly attributed to that EPS artifact/activity rather than to an EPS technology choice; and
3. extractable claim wording and the evidence, if any, offered for it.

The proposed model-enabled mechanism is extracted when stated and coded `not_reported` when absent; missing mechanism reporting lowers interpretability but does not erase an otherwise explicit EPS-attributed claim. A generic claim about MBSE in a report containing EPS material is not EPS-specific evidence. Assertion-only claims may be retained as claims but must be classified as unsupported rather than as demonstrated effects.

A power or energy margin alone is not an EPS-reliability result. Reliability coding requires an explicit connection to failure, fault tolerance, availability, risk, assurance, or another defined reliability construct. Reproducibility/reuse and integrability/interoperability claims must likewise be kept distinct from mere model availability or diagram co-occurrence.

### Direct EPS-linked pre-physical V&V

An **EPS-linked RQ3 V&V record** requires:

1. an **EPS target**: a named requirement, model element, parameter, mode, interface, behavior, function, or hazard;
2. an **explicit model-to-V&V bridge**: a trace, shared identifier, binding, port/data mapping, transformation, generated artifact, or other reported link; and
3. a **V&V method, intent, or artifact**: the source presents the activity as verification, validation, compliance/requirement checking, virtual integration, a model-derived test activity, or another V&V function.

Criterion, execution, and result completeness are then stratified rather than used to suppress an otherwise explicit linked record:

- **EPS-linked V&V:** the target, bridge, and V&V method/intent/artifact are reported;
- **criterion-complete EPS-linked V&V:** the record additionally reports a requirement, threshold, expected behavior, formal property, acceptance criterion, or pass/fail oracle;
- **executed pre-physical V&V:** the linked method is executed virtually and a result or verdict is reported; and
- **model-to-test continuity/closure:** a downstream physical artifact or activity is linked, with closure reserved for reported comparison and disposition of results.

A simulation or trade study with no stated V&V/checking intent and no criterion is analysis rather than V&V. A source-claimed verification activity with an unreported criterion remains an EPS-linked record but is not criterion-complete. Generic system V&V and EPS content appearing in the same report without an explicit bridge are co-occurrence only and do not answer RQ3.

For this review, **pre-physical V&V** means a model-based V&V artifact or activity prepared or executed before physical integration or physical testing of the target EPS design. Model-derived preparation for a later physical test is included as preparation. SIL may qualify when it remains virtual with respect to the target EPS hardware. HIL, bench, environmental, integration, operational, and flight evidence are recorded as downstream model-to-test continuity, not relabeled as wholly pre-physical evidence. When timing is not reported clearly, it is coded uncertain and is not counted as demonstrated pre-physical execution.

## Information sources

### Primary bibliographic databases

- Scopus
- IEEE Xplore

### Supplementary discovery and citation searching

- Semantic Scholar, for targeted supplementary discovery and forward/backward citation metadata
- Google Scholar, for targeted fallback discovery, cited-by searching, and recovery of poorly indexed conference or chapter records
- Backward and forward citation chasing from included reports and relevant secondary reviews

Semantic Scholar and Google Scholar searches must be logged with exact query text, date, result limit, and selection procedure. They are not to be described as unrestricted exhaustive database searches.

arXiv and other repositories may be used to retrieve an accessible version of an eligible peer-reviewed report, but unpublished preprints are not primary evidence.

## Search strategy

Use two complementary search streams so that embedded EPS threads absent from titles or abstracts are not systematically lost:

- **Stream A — EPS-explicit:** combine Population × EPS × MBSE/system-model concepts to identify EPS-primary reports and explicit embedded threads.
- **Stream B — embedded-thread recall:** combine Population × MBSE/system-model concepts without requiring an EPS term, then screen full texts for a qualifying EPS thread. Stream B is intentionally broader and its unique yield is reported separately.

The concept blocks, adapted to each source's syntax, are:

1. **Population:** CubeSat, nanosatellite, nano-satellite, nanosat, or an explicitly nanosatellite-class mission;
2. **EPS:** electrical power system/subsystem, EPS, power subsystem, electrical architecture, power/energy budget, energy balance, battery/storage, solar array/generation, power conditioning/distribution, PCDU, or PMAD; and
3. **MBSE/system model:** model-based systems engineering, MBSE, SysML, system model/modeling, reference model, digital engineering, Arcadia, Capella, or another validated structured-system-model term.

Targeted RQ2 and RQ3 searches may add outcome, traceability, verification, validation, simulation, model checking, requirements-in-the-loop, SIL, HIL, or test terms. These terms will not be mandatory in every query because doing so could suppress relevant RQ1 and embedded-thread reports.

Searches will be piloted in small, targeted sets. The new search log must record exact strings, fields, filters, dates, database-reported totals, retrieved totals, refinements, failed or overbroad queries, deduplication, coverage checks, and stopping rationale. Refining source-specific syntax or precision within these fixed concept streams is search implementation, not a change to review eligibility; every version and the final used set must remain in the log.

Previously identified reports may be listed before searching in a read-only known-item register. They may guide query refinement if missed, but they enter the corpus only through a logged search or citation-chasing event followed by new screening. Known-item recall and unique inclusions from each search stream are reported separately.

Backward and forward citation chasing starts from every full-text-included report and relevant secondary review. Newly found eligible reports are also chased; iteration stops when one complete backward/forward cycle yields no new eligible report. Every citation route is logged.

Searching stops when both streams, the prespecified concept clusters, and known relevant lineages have been tested; citation chasing is complete; and additional searches are predominantly redundant rather than merely convenient or precise. The final search date closes the review's evidence window.

## Inclusion and exclusion criteria

| Criterion | Rule | Applicable RQ(s) |
|---|---|---|
| Publication date | First formal publication date from 2013 through the final search date in 2026; online-first and issue versions of the same report are one work | 1--3 |
| Language | Report written in English; inability to retrieve the full text is handled separately as `not_retrieved` | 1--3 |
| Publication type | Full scholarly primary-research journal article, conference/proceedings paper, or research chapter in edited scholarly proceedings/volume; document type and venue provenance are verified from source or publisher metadata where possible | 1--3 |
| Population | Actual or intended orbital CubeSat/nanosatellite-class mission or a nanosatellite-tailored model; separable evidence required in mixed-platform reports | 1--3 |
| MBSE threshold | Must meet the structured-system-model definition above | 1--3 |
| EPS threshold | Must meet Route A or Route B at full text | 1--3 |
| RQ1 contribution | Every eligible EPS thread contributes its reported representation, purpose, inputs/assumptions, abstraction, and reuse/tailoring information; missing fields remain `not_reported` | 1 |
| RQ2 contribution | Only atomic claims explicitly attributed to a qualifying EPS thread enter direct RQ2 synthesis; mechanism and evidence completeness are coded separately | 2 |
| RQ3 contribution | Only records with an EPS target, explicit bridge, and reported V&V method/intent/artifact enter EPS-linked RQ3 synthesis; criterion-complete and executed subsets are reported separately | 3 |
| Mixed system scope | Include only when an EPS thread is separately extractable; synthesize other subsystems only as EPS dependencies/interfaces | 1--3 |
| Secondary studies | Exclude from primary evidence; retain separately for positioning, terminology, and citation chasing | 1--3 |
| Non-MBSE EPS studies | Exclude stand-alone component, circuit, control, optimization, sizing, simulation, or hardware-performance studies without an explicit structured-system-model link | 1--3 |
| Generic whole-spacecraft MBSE | Exclude reports lacking a qualifying EPS thread, even if they mention EPS or a power budget | 1--3 |
| Other subsystem studies | Exclude unless they contain a qualifying EPS thread; a subsystem's power consumption alone is insufficient | 1--3 |
| Abstract-only/non-research material | Exclude posters/abstracts without full papers, presentations, editorials, tutorials, advertisements, patents, and non-scholarly web material | 1--3 |
| Retrieval status | Scientific eligibility is independent of open-access status. Reports not obtained after the defined retrieval process are logged as `not retrieved`, not silently excluded on scientific grounds | 1--3 |

Outcome presence is not a report-level inclusion criterion. A Route A or B report may answer only RQ1 and still be included.

Retrieval follows the run's PDF workflow: DOI/open-access and publisher/repository routes are attempted first, followed by one documented institutional/manual-download pass where needed. Unresolved reports remain in the PRISMA and retrieval records as `not_retrieved`; they do not enter full-text evidence synthesis, but lack of access is not presented as a scientific exclusion reason.

## Screening and eligibility procedure

### Title and abstract screening

Use screening tiers only to prioritize retrieval; they are not final evidence classes:

- **core candidate:** title/abstract gives clear evidence of EPS-primary MBSE or a likely embedded EPS thread;
- **supporting candidate:** the record meets the nanosatellite and possible MBSE threshold, but a qualifying embedded thread cannot be confirmed without full text; and
- **rejected candidate:** clearly fails population, publication, or MBSE scope, or an EPS-explicit record clearly lacks a qualifying model link.

Because embedded threads may not appear in abstracts, Stream B records do not require a power/EPS term at this stage. Uncertainty is resolved toward retrieval when nanosatellite MBSE is plausible; the EPS anchor and bridge are tested at full text.

### Full-text decision

Assign one final decision with a source-located rationale:

- `include_route_A_eps_primary`;
- `include_route_B_embedded_eps`;
- `exclude_no_qualifying_eps_thread`;
- `exclude_not_mbse`;
- `exclude_wrong_population`;
- `exclude_wrong_publication_type`;
- `exclude_wrong_date`;
- `exclude_wrong_language`;
- `exclude_secondary_study`;
- `exclude_insufficient_primary_report`;
- `not_retrieved`.

For every Route B inclusion, screening must record the EPS anchor, model anchor, explicit bridge, and supporting location. These data are rechecked during extraction.

Secondary reviews and generic MBSE sources used for background or citation chasing are maintained outside the analytic denominator.

## Units of evidence and identifiers

The review distinguishes four nested units:

1. **Report:** one publication reporting a study, model, or implementation.
2. **EPS model thread:** one qualifying EPS-primary or embedded chain within a report. A report may contain more than one thread.
3. **Outcome claim:** one atomic claimed outcome linked or potentially linked to a thread. When one sentence asserts several outcomes, create separate claim-outcome records that may share the same quotation.
4. **V&V record:** one target–method–scenario activity or artifact linked or potentially linked to a thread. Multiple targets, methods, or scenarios use linked atomic records rather than one aggregate record.

Reports from the same mission, reference-model lineage, toolchain, or implementation are not treated as independent replications. Assign a work/lineage identifier where overlap is evident.

New-run IDs must qualify nested records, for example `report_id:thread_id:claim_id`. A normalized DOI is the preferred cross-run report identity key; title–author–year matching requires manual confirmation. Legacy IDs and prior discovery paths are provenance only.

## Quality checklist

All applicable items use:

- No = 0
- Insufficiently = 0.5
- Yes = 1
- Not applicable = excluded from that score's denominator

Quality scores contextualize confidence and sensitivity analyses; they are not automatic exclusion thresholds and cannot make an ineligible report, claim, or V&V record eligible.

### Report and EPS-thread quality

1. Was the primary research published in a credible scholarly venue, with report type and provenance verifiable?
2. Is the CubeSat/nanosatellite mission context and lifecycle stage described clearly enough to assess applicability?
3. Are the MBSE method, model boundary, language/toolchain, artifacts, and modeled relations described clearly enough to verify MBSE qualification?
4. Are the EPS anchor, model anchor, explicit bridge, and EPS boundary reported clearly enough to reconstruct the qualifying thread?
5. Are the model's stated purpose, intended decisions, users/roles, and lifecycle use reported?
6. Are material inputs and assumptions reported with sufficient detail about value/range, units or time basis, provenance, uncertainty/margin, and rationale?
7. Are model/tool/data availability, configurations, interfaces, and reusable assets reported sufficiently to assess reproducibility?
8. Do the authors discuss limitations, scope boundaries, uncertainty, threats to validity, or alternative explanations?

### RQ2 claim quality, when applicable

9. Is the outcome explicitly linked to a qualifying EPS thread and a stated MBSE mechanism rather than to EPS technology choice or generic MBSE?
10. Is the claim supported by an appropriate metric, traceable case result, comparator, stakeholder assessment, reuse, integration/test result, or operational evidence?

### RQ3 V&V quality, when applicable

11. Are the EPS target, model-to-V&V bridge, method/artifact, criterion, lifecycle timing, and execution status explicitly reported?
12. When execution or closure is claimed, are the result/verdict and any downstream software, hardware, integration, test, operational, or flight link evidenced?

Items 1--3 and 8 are scored at report level; items 4--7 at EPS-thread level; items 9--10 for each direct RQ2 claim; and items 11--12 for each EPS-linked RQ3 record. Any roll-up is descriptive and retains its unit and applicable-item denominator. Linkage confidence is also retained separately from quality score.

## Extraction fields

A new run-specific `extraction_codebook.json` must be created from this protocol before per-report extraction. Earlier codebooks and extraction forms are not authoritative for this run and may not be copied into new-run fields.

Every synthesis-critical controlled code requires a rationale, a direct quote or source location where possible, and a confidence rating. Preserve `not_reported`, `not_applicable`, `none`, and `uncertain` as distinct statuses. Distinguish author-reported facts from extractor inference.

### Report-level bibliographic and review-management fields

- New-run report ID; optional legacy corpus ID; extraction file path.
- Citation, title, authors, year, venue, publication type, DOI/URL, publisher.
- Every discovery event: run ID, database/source, exact query or citation route, date, source record ID, rank when available, and raw-search artifact.
- Title/abstract screening tier and rationale.
- Full-text eligibility decision and exclusion rationale, if applicable.
- Route A/Route B classification and evidence.
- RQ contribution status: RQ1; count of eligible RQ2 claims; count of direct and near-miss RQ3 records.
- Mission/reference-model/toolchain lineage and shared implementation notes.
- Extraction confidence and assessor/review-pass provenance.

### Study context and MBSE qualification

- Mission/platform, form factor/mass if reported, mission name/domain, organization type, and project maturity.
- Demonstrated lifecycle stage, separated from asserted or future lifecycle applicability.
- Development context: academic/student, agency, industry/NewSpace, distributed team, agile/concurrent design, rapid prototyping, resource-constrained mission, or not reported.
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
- Thread-level maturity, lifecycle stage, availability, evidence confidence, and limitations.

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

Extract technical outputs separately from MBSE outcome claims:

- Output ID and thread ID.
- Quantity/result and units/time basis.
- Scenario/configuration and input set.
- Whether it is calculated, simulated, checked against a criterion, compared, or physically validated.
- Decision or model artifact informed.
- Evidence source and confidence.

### RQ2 outcome claim-evidence record

Create one atomic record for each candidate claim that is explicitly or plausibly linked to a qualifying EPS thread. Do not exhaustively extract generic MBSE claims merely because they occur in an eligible report. Split multi-outcome statements into claim-outcome records and connect shared evidence through source IDs:

- Claim ID and linked thread ID.
- Exact claim text or conservative paraphrase.
- Claim scope and target.
- Outcome category: EPS reliability; system/mission assurance; defect/error reduction; risk reduction; reproducibility/rerunnability; reuse/replication; integrability/interoperability; interface consistency; traceability/requirements quality; completeness; lifecycle continuity; decision/trade support; cost; schedule; effort/automation; communication/knowledge; governance/value realization; or other.
- Reliability subtype where relevant: EPS reliability, system/mission reliability, process reliability, model consistency/reliability, mission assurance, defect/error reduction, generic reliability claim, or not applicable.
- MBSE mechanism: artifact traceability, requirements linkage, executable simulation, parametric analysis, reference-model reuse, automated generation, transformation, shared repository, tool integration, interface management, lifecycle-gate support, model-derived V&V, or other.
- Artifact/process linked to the claim and lifecycle stage.
- Attribution status: explicit EPS-thread attribution; ambiguous attribution; generic/not eligible. Only explicit EPS-thread attribution enters direct RQ2 synthesis.
- Evidence type: assertion only; conceptual/illustrative; single-case demonstration; executable result; trade/requirements-check result; quantitative metric without comparator; quantitative comparison; stakeholder/expert evaluation; reuse/replication; integration/test/operational/flight evidence.
- Metric or value indicator; baseline/comparator; observed effect or result.
- Evidence source, alternative explanations, and nesting/lineage notes.
- Evidence confidence:
  - **Unsupported:** assertion without extractable support;
  - **Weak:** plausible explanation or illustrative/single-case evidence without a result adequate to support the claimed effect;
  - **Moderate:** traceable within-case evidence, executable/checking result, or metric, but limited comparator or independent validation;
  - **Strong:** appropriate comparative, repeated-reuse, independent, integration/test, operational, or flight evidence directly supporting the claim.

### RQ3 V&V record

Create one atomic target–method–scenario record per candidate activity or artifact. Retain plausible linkage near misses so exclusion from EPS-linked RQ3 synthesis is auditable, but do not exhaustively extract unrelated generic system V&V:

- V&V record ID and linked thread ID.
- EPS target and target type; requirement or criterion identifier when reported.
- Model element/artifact and explicit model-to-V&V bridge.
- Classification: feasibility/analysis only, verification, validation, mixed V&V, or unclear.
- Method/artifact: requirements-in-the-loop, parametric/constraint check, simulation scenario, model checking, trade verification, virtual integration, verification matrix, test case/procedure, generated test artifact, automated test, SIL, HIL, or other.
- Criterion/oracle and its provenance.
- Timing relative to physical realization, integration, and test; lifecycle stage.
- Status: proposed only; prepared/generated; executed virtually; verdict/result reported; downstream physical link demonstrated; model-to-test closure demonstrated.
- Result/verdict and discrepancy handling, if reported.
- Downstream link: software integration, hardware integration, flat-sat/bench, HIL, environmental test, operational validation, or flight evidence.
- EPS-linked RQ3 eligibility: yes/no/uncertain for the target–bridge–V&V-method/intent rule, with the failed condition recorded when not eligible.
- Criterion-complete status: yes/no/uncertain, with criterion evidence.
- Demonstrated pre-physical execution status: yes/no/uncertain, with timing and result evidence.
- Evidence source, confidence, limitations, and lineage/nesting notes.

### Limitations and open extraction

- Author-stated limitations, assumptions, and scope boundaries.
- Extractor-identified evidence gaps, with absence-based explanations only after completing the relevant fields.
- Narrow controlled limitation flags, including prototype/future work, single case, no comparator, no independent validation, no physical/model-to-test evidence, unavailable model/data, assumptions/data-quality limits, tool dependency, interoperability limits, incomplete lifecycle coverage, ambiguous EPS linkage, generic outcome attribution, or missing V&V criterion.
- Emergent codes for unexpected findings that do not fit the controlled vocabulary; do not silently expand controlled categories during extraction.

## Calibration, consistency, and validation

Before full screening and extraction:

1. pilot the full-text eligibility rule on clear Route A, clear Route B, generic whole-spacecraft MBSE, and non-MBSE EPS examples;
2. pilot the thread, input/assumption, RQ2 claim, and RQ3 V&V forms on a deliberately varied sample;
3. revise and then freeze the run-specific codebook before full extraction; and
4. document all calibration decisions and examples.

Use isolated assessment passes to reduce context carryover. All final Route B inclusions and all direct RQ2/RQ3 linkage decisions must receive a second check. Record whether that check was performed by another human assessor or by a model-assisted validation pass. Do not describe model-assisted validation as independent human review, and calculate an agreement statistic only when the assessment design genuinely supports it.

Validate all extraction JSON against the codebook, exact controlled labels, record IDs, required evidence/rationales, status distinctions, and report/thread/claim/V&V referential integrity before synthesis.

## Planned synthesis

The synthesis is a structured evidence map and narrative synthesis; no pooled effect estimate is planned because models, outcomes, and evidence designs are expected to be heterogeneous.

### RQ1

- Map EPS boundaries, model concerns, artifacts, purposes, abstraction levels, inputs/assumptions, provenance, uncertainty/margin handling, reuse/tailoring mechanisms, and lifecycle use.
- Distinguish reported inputs from reviewer-inferred dependencies and from source silence.
- Compare Route A and Route B without assuming either is more mature.

### RQ2

- Synthesize only explicitly EPS-thread-attributed claims.
- Keep EPS engineering outputs separate from claims of MBSE-enabled value.
- Present outcome category, proposed mechanism, evidence type, comparator, confidence, and lifecycle stage together.
- Treat unsupported claims as evidence about claim prevalence, not demonstrated effects.

### RQ3

- Map EPS target-to-model-to-V&V chains and stratify EPS-linked, criterion-complete, executed pre-physical, and downstream model-to-test evidence.
- Report analysis-only, co-occurrence, and missing-link near misses separately; report a missing criterion as an evidence-completeness limitation rather than silently discarding an otherwise explicit EPS-linked V&V record.
- Do not infer V&V integration from report-level co-occurrence.

### Cross-cutting safeguards

- Report separate denominators for reports, EPS model threads, input/assumption records, outcome claims, and V&V records.
- Treat claims and V&V records as nested within reports and lineages, not as independent studies.
- Stratify Route A and Route B before presenting combined totals.
- Identify recurring reports from the same mission, implementation, reference model, or toolchain; do not count them as independent replication.
- Use quality and linkage-confidence sensitivity views, including Route-A-only and high-confidence subsets where informative.
- Interpret cross-tabs only as descriptive co-reporting unless a direct extracted link supports a relationship.
- Retain `not_reported`, `none`, `not_applicable`, `uncertain`, and invalid/unmapped values distinctly.
- Treat sparse direct evidence as a review finding rather than filling gaps with generic whole-spacecraft MBSE claims.

## Required new-run artifacts

After protocol approval, the restarted review must generate or regenerate, with run provenance:

- integrated protocol approval/version record and read-only legacy known-item register;
- exact search log and raw source-specific search results;
- merged/deduplicated candidate set;
- title/abstract and full-text screening log;
- retrieval log and accessible corpus;
- run-specific corpus and identifiers;
- run-specific extraction codebook;
- per-report extraction files with thread, claim, and V&V records;
- compiled extraction dataset and bibliography;
- validation report; and
- new PRISMA flow and synthesis outputs.

This protocol was reviewed and frozen before the new-run searches began. Subsequent changes require a prospective, versioned deviation record.
