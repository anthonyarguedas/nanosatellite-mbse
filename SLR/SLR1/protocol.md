# Protocol for a Systematic Review of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems

- **Review run ID:** `eps-mbse-slr-2026`
- **Protocol version:** `1.1` (pre-search freeze candidate)
- **Scope-decision approval date:** 2026-08-06
- **Pre-freeze interface/consistency review:** completed 2026-08-06
- **Final freeze/search authorization:** pending researcher confirmation

## Review status and restart policy

This protocol defines a **new systematic review run** focused on nanosatellite electrical power system (EPS) MBSE. It is not an amendment to, or an update of, the earlier whole-nanosatellite/EPS review.

The earlier searches, screening decisions, corpus, extractions, codebook, synthesis, and manuscript are treated as legacy or pilot artifacts. A failed attempt under version 1.0 was abandoned and its search outputs were removed; it supplies no discovery events, records, decisions, or evidence to this run. In particular:

- no previously identified report is automatically included;
- all records must be found through a documented version-1.1 search or citation-chasing route and screened against this protocol;
- previous reports may be used only as known-item recall checks when refining the search;
- every included report must be newly extracted from its full text against a new run-specific codebook; prior extraction may be consulted only during a later discrepancy audit and may not supply new-run evidence;
- prior counts and classifications must not be carried into the new synthesis; and
- DOI/title matching may retain a prior corpus ID only as a `legacy_corpus_id`; new-run report-family, report, EPS-thread, outcome/burden, and V&V-record identifiers must be run-specific.

Version 1.1 is the pre-search freeze candidate. No valid new-run discovery search has begun. The dated source-interface diagnostics used to validate syntax, controls, and export behavior before freeze are pilots only: they do not create the independent candidate set, and aggregate pilot observations cannot determine evidence membership. After final authorization, any deviation will be recorded prospectively in the new run's search or decision log.

## Reporting framework

PRISMA-P (2015) guides this protocol and its amendment history; PRISMA-S (2021) guides the design, execution, preservation, and reporting of every search in [`query-search-plan.md`](query-search-plan.md); and PRISMA 2020 will guide the completed review, abstract, checklist, and flow diagram. These are reporting guidelines, not evidence-validity instruments. Health-review terminology is adapted to this engineering evidence map without inventing clinical effect measures, risk-of-bias tools, or GRADE ratings.

This is a new review, not an update. The completed review will use the PRISMA 2020 flow template for a new systematic review using databases and other sources. Identification and selection are counted at record/report level; report families, EPS threads, outcome/burden records, and V&V records are linked analytic units reported with separate denominators.

Official guidance to use at the applicable stage:

- [PRISMA-P protocols and checklist](https://www.prisma-statement.org/protocols);
- [PRISMA-S search reporting](https://www.prisma-statement.org/prisma-search) and [Rethlefsen et al. (2021)](https://doi.org/10.1186/s13643-020-01542-z); and
- [PRISMA 2020 statement](https://www.prisma-statement.org/prisma-2020-statement), [checklist](https://www.prisma-statement.org/prisma-2020-checklist), [abstract guidance](https://www.prisma-statement.org/abstracts), and [flow templates](https://www.prisma-statement.org/prisma-2020-flow-diagram).

Registration/contact declarations, contributor and guarantor details, funding/sponsor and competing-interest declarations, and the final search-update policy are intentionally deferred at this stage. Their absence must be stated accurately; this freeze candidate is not represented as administratively PRISMA-P-complete.

## Approval, amendment, and pre-search decision record

- **Scope-decision approval date:** 2026-08-06
- **Freeze/search authorization date:** pending researcher confirmation
- **Freeze candidate:** `1.1`, ready for authorization
- **Search state:** source-interface pilots complete; no valid new-run discovery search executed
- **Working branch:** `slr1-1.1-restart`

The researcher reviewed the failed version-1.0 run and prospectively approved the methodological scope decisions incorporated into version 1.1. Version 1.0 remains the superseded baseline in version control. Version 1.1 becomes the governing protocol for valid searches and later review activity only when its final freeze/search authorization is recorded.

| Change | Date | Timing | Rationale and consequence |
|---|---|---|---|
| `1.0` to `1.1` | 2026-08-06 | Before freeze and any valid new-run search | Remove stale search-start claims; extend the evidence window to 2011; expand information sources and admit substantive institutional technical reports; define Buruso (2026) as a secondary-review seed and recall benchmark; make the generic SmallSat exclusion explicit; extract outcome direction and implementation burdens; distinguish V&V scope and object; formalize the study/implementation report-family unit; and clarify that all reported model reuse/tailoring is in scope, with lightweight status only a possible synthesis characterization and never a filter. Version 1.1 will govern all valid searches and evidence decisions after authorization. |

The identified choices were reviewed and retained or amended as follows:

1. **CubeSat/nanosatellite population.** PocketQube/picosatellite-only, CanSat, and generic `SmallSat`/small-satellite studies are excluded. Mixed studies remain eligible only when the source identifies a CubeSat/nanosatellite-class case and its evidence is separable; searches do not deliberately target excluded platforms.
2. **Evidence window.** The lower publication-year limit is 2011 so that foundational CubeSat/nanosatellite MBSE reports are not removed by an arbitrary 2013 cutoff.
3. **Expanded source coverage.** Scopus, IEEE Xplore, Compendex, the full Wiley Online Library publisher database, the full ESA Indico event database, and the NASA Technical Reports Server (NTRS) are searched using source-appropriate methods.
4. **Open, direction-neutral RQ2 set.** This avoids directional outcome-reporting bias. Beneficial, null, mixed, and adverse outcomes and implementation burdens are extracted when explicitly attributed to a qualifying EPS thread. Reliability/mission assurance, reproducibility/reuse, and integrability/interoperability remain priority domains; all domains and directions use the same attribution and evidence rules.
5. **Tiered and differentiated V&V records.** A named EPS target, or a system-wide target explicitly linked to EPS, together with a model-to-V&V bridge and reported V&V method/intent/artifact establishes the lowest linked tier. EPS-specific versus system-wide EPS-linked scope and the object of V&V are coded separately. Missing criterion, execution, verdict, or timing remains missing evidence and cannot support a higher tier.
6. **Broad Stream B.** This is necessary because embedded EPS threads may be absent from metadata. Query partitioning, count pilots, conservative title/abstract retention, and separate unique-yield accounting control workload without imposing an EPS keyword.
7. **Buruso (2026) as secondary evidence only.** The review is used for positioning, a deferred recall benchmark, and logged citation chasing. It does not supply primary evidence or bypass independent discovery and new screening.
8. **New extraction for every included report.** Legacy extraction and synthesis files were removed. Retained source Markdown/PDF files may be reused only after independent rediscovery and new screening.
9. **All model tailoring is in scope.** Eligibility and discovery do not require a lightweight implementation. Extract every reported reuse/tailoring approach and its implementation footprint; discuss lightweight, scalable, comprehensive, or resource-intensive characteristics only where the source or extracted evidence supports them.

Pre-search anti-anchoring controls are part of this approval:

- legacy and failed-run search results, screening, corpora, codebook, extractions, scoping review, and manuscript were removed before the valid version-1.1 search;
- `markdown/` and `pdfs/` were retained only as a source-file cache outside the search evidence base;
- retained files cannot supply candidates, eligibility decisions, IDs, or extracted data;
- matching against retained files is deferred until the independently discovered candidate set from all six planned electronic sources is merged, and matches serve only as recall and retrieval checks; and
- old corpus or extraction data may not be reconstructed from Git history during new search or screening.

Any change after final freeze requires a prospective entry stating its date, exact decision or wording change, rationale, affected artifacts and records, consequences for synthesis, and protocol version.

## Review objective

To synthesize how nanosatellite EPSs are represented through MBSE, why those models are constructed, which inputs and assumptions they depend on, how they are reused or tailored, which beneficial, null, mixed, or adverse EPS-linked outcomes and implementation burdens are reported, and how EPS verification and validation (V&V) are integrated before physical integration or test.

The analytic scope includes both:

1. **EPS-primary MBSE**, where the EPS is the principal modeled system or viewpoint; and
2. **embedded EPS model threads**, where a broader nanosatellite model contains an explicit, extractable chain linking EPS content to systems-engineering artifacts or activities.

Generic whole-spacecraft MBSE evidence does not answer the research questions merely because EPS and another artifact occur in the same report.

## PICOC

| Population | Intervention | Comparison | Outcome | Context | Related RQ(s) |
|---|---|---|---|---|---|
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-primary MBSE or an explicit embedded EPS model thread | Not required | EPS representation, model purpose, required inputs and assumptions, abstraction, reuse, tailoring, and required roles/resources | Nanosatellite systems engineering across the lifecycle | RQ1 |
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-linked MBSE artifacts, analyses, and model-enabled activities | When reported: document-centric practice, manual analysis, alternative toolchain, previous mission/model, or other explicit comparator | Beneficial, null, mixed, or adverse EPS-linked technical and engineering-process outcomes and implementation burdens, especially reliability/mission assurance, reproducibility/reuse, and integrability/interoperability | Nanosatellite development and decision making | RQ2 |
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-specific or system-wide EPS-linked model-based V&V before physical integration or test | Separate or document-based V&V, manual checking, another method, or no comparator when reported | V&V scope and object, traceability to V&V artifacts, executable checks, verdicts, virtual integration, and model-to-test continuity | Pre-physical analysis and V&V, with downstream physical links recorded separately | RQ3 |

## Research questions

1. **RQ1 — representation, purpose, and prerequisites.** How are nanosatellite EPSs represented in EPS-primary MBSE models and embedded EPS model threads; for what stated purposes; what inputs, assumptions, abstraction choices, roles, skills, and resources are reported; and how are the models reused or tailored?

2. **RQ2 — EPS-linked outcomes, burdens, and evidence.** Which beneficial, null, mixed, or adverse EPS-specific technical or engineering-process outcomes, and which implementation burdens, are explicitly attributed to EPS MBSE artifacts or model-enabled activities; through what mechanisms; and with what supporting evidence?

3. **RQ3 — EPS-linked pre-physical V&V.** How are EPS-specific or system-wide EPS-linked pre-physical V&V activities connected to EPS requirements, model elements, analyses, or interfaces; what is the object of verification or validation; and what level of preparation, execution, result reporting, and model-to-test continuity is demonstrated?

RQ1–RQ3 are co-primary mapping questions. Within RQ2, reliability/mission assurance, reproducibility/reuse, and integrability/interoperability are prespecified priority presentation strata, not eligibility filters; the open outcome/burden set is coded and reported direction-neutrally without post-hoc suppression of other domains.

## Operational definitions

### Nanosatellite population

An eligible platform is an actual or intended orbital spacecraft that the source identifies as a CubeSat or nanosatellite, including recognized CubeSat form factors even when a particular implementation falls outside a strict 1--10 kg mass definition. A reference, template, or early-phase design model may qualify without a named or realized mission when its stated target population is orbital CubeSat/nanosatellite development.

`SmallSat` and “small satellite” are not treated as synonyms for the eligible population. A generic SmallSat/small-satellite label alone does not establish CubeSat/nanosatellite-class eligibility, even when the report may be relevant to broader small-spacecraft engineering.

Exclude:

- CanSats and other non-orbital educational demonstrators;
- PocketQube/picosatellite-only studies unless a separable CubeSat/nanosatellite case is also reported;
- generic SmallSat/small-satellite studies, larger small satellites, or conventional spacecraft unless the source also identifies a CubeSat/nanosatellite-class case and its results can be extracted separately; and
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

### MBSE-enabled outcomes and implementation burdens versus EPS engineering outputs

An **EPS engineering/model output** is a result such as minimum state of charge, power margin, battery capacity, solar-array area, voltage/current, energy balance, or a selected architecture. Such outputs are extracted for RQ1 and may support RQ2 or RQ3, but they are not automatically evidence of MBSE value.

An **RQ2-eligible outcome or implementation-burden record** must provide:

1. an eligible EPS model thread or named EPS-linked model artifact/activity;
2. a reported beneficial, null, mixed, or adverse technical or engineering-process outcome, or an implementation burden, explicitly attributed to that EPS artifact/activity rather than to an EPS technology choice; and
3. extractable result or claim wording and the evidence, if any, offered for it.

The proposed model-enabled mechanism is extracted when stated and coded `not_reported` when absent; missing mechanism reporting lowers interpretability but does not erase an otherwise explicit EPS-attributed record. A generic claim about MBSE in a report containing EPS material is not EPS-specific evidence. Assertion-only claims may be retained but must be classified as unsupported rather than as demonstrated effects.

A null outcome requires an evaluated result indicating no observed effect or difference; it is not synonymous with `not_reported`, missing evidence, or absence of a claim. Split separable benefits, adverse effects, null findings, and burdens into atomic records. Use `mixed/conditional` only when direction varies inseparably by scenario, metric, actor, or condition. An implementation burden may coexist with a beneficial outcome and must not be netted against it by reviewer inference. Generic project- or report-level MBSE burdens may be retained as RQ1 context, but they enter direct RQ2 synthesis only when explicitly attributed to the qualifying EPS thread.

A power or energy margin alone is not an EPS-reliability result. Reliability coding requires an explicit connection to failure, fault tolerance, availability, risk, assurance, or another defined reliability construct. Reproducibility/reuse and integrability/interoperability claims must likewise be kept distinct from mere model availability or diagram co-occurrence.

### Direct EPS-linked pre-physical V&V

An **EPS-linked RQ3 V&V record** requires:

1. an **EPS target**: a named EPS requirement, model element, parameter, mode, interface, behavior, function, or hazard, or a system-wide target explicitly decomposed, allocated, or traced to such EPS content;
2. an **explicit model-to-V&V bridge**: a trace, shared identifier, binding, port/data mapping, transformation, generated artifact, allocation, or other reported link; and
3. a **V&V method, intent, or artifact**: the source presents the activity as verification, validation, compliance/requirement checking, virtual integration, a model-derived test activity, or another V&V function.

Classify each candidate record independently by **linkage scope**:

- **`eps_specific`:** the V&V target and activity are explicitly EPS-specific;
- **`system_wide_eps_linked`:** a broader system-level activity contains a named, reconstructable EPS target and bridge;
- **`system_wide_cooccurrence`:** system-wide V&V and EPS content occur in the same report without the required direct link; or
- **`unclear`:** the scope cannot be resolved from the report.

Both `eps_specific` and `system_wide_eps_linked` records may enter direct RQ3 synthesis, but they are always reported separately and the scope of any result or verdict is retained. `system_wide_cooccurrence` is a near miss and cannot support an EPS-specific conclusion.

Classify the **object of V&V** separately from scope and execution environment:

- **model verification:** whether a model, transformation, or executable representation was implemented correctly against its specification or formulation;
- **model validation:** whether a model is adequate or credible for its stated intended use against an authoritative reference, data, or expected behavior;
- **system/design verification:** whether the EPS or wider system design satisfies specified requirements or criteria;
- **system/design validation:** whether the design supports intended stakeholder, operational, or mission needs;
- **multiple:** more than one of these objects is explicitly demonstrated; or
- **unclear.**

Preserve the source's terminology separately from the reviewer's normalized code and rationale. Executing a method in a model does not automatically make the activity model verification or model validation; for example, a virtual requirement check may be system/design verification. MIL, SIL, PIL, HIL, virtual testbeds, and other execution environments are likewise coded separately from the object of V&V.

Criterion, execution, and result completeness are then stratified rather than used to suppress an otherwise explicit linked record:

- **EPS-linked V&V:** the target, bridge, and V&V method/intent/artifact are reported;
- **criterion-complete EPS-linked V&V:** the record additionally reports a requirement, threshold, expected behavior, formal property, acceptance criterion, or pass/fail oracle;
- **executed pre-physical V&V:** the linked method is executed before physical integration or test of the target EPS and a result or verdict is reported; and
- **model-to-test continuity/closure:** a downstream physical artifact or activity is linked, with closure reserved for reported comparison and disposition of results.

A simulation or trade study with no stated V&V/checking intent and no criterion is analysis rather than V&V. A source-claimed verification activity with an unreported criterion remains an EPS-linked record but is not criterion-complete. Generic system V&V and EPS content appearing in the same report without an explicit bridge are co-occurrence only and do not answer RQ3.

For this review, **pre-physical V&V** means a model-based V&V artifact or activity prepared or executed before physical integration or physical testing of the target EPS design. Model-derived preparation for a later physical test is included as preparation. MIL and SIL may qualify when the target EPS hardware remains virtual. PIL and HIL are classified by the hardware actually present: they are not counted as wholly pre-physical when target EPS hardware participates, but representative or non-target hardware does not by itself convert a still-virtual target EPS into a physical EPS test. Bench, environmental, integration, operational, and flight evidence are recorded as downstream model-to-test continuity. When timing or target-relative physicality is unclear, it is coded uncertain and is not counted as demonstrated pre-physical execution.

## Information sources

### Electronic databases and repositories

- Scopus, bibliographic database
- IEEE Xplore, bibliographic/full-text database
- Compendex on the Engineering Village platform, bibliographic database
- Wiley Online Library, searched as a general publisher database across the full platform
- ESA Indico, searched as a general event/contribution database across the full public instance
- NASA Technical Reports Server (NTRS), searched across the full public technical-report database

Wiley and ESA Indico are general source searches for this review, not targeted venue searches. They are not restricted to INCOSE publications or ESA MBSE workshops, and NTRS is not restricted to a predetermined NASA series. INCOSE International Symposium content in Wiley and ESA MBSE workshop content in Indico are prespecified coverage checks, not source boundaries.

### Supplementary discovery and citation searching

- Backward and forward citation chasing from included reports and relevant secondary reviews
- Buruso et al. (2026), *Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review* (https://doi.org/10.1002/sys.70051), as a named secondary-review seed and deferred recall benchmark

Buruso et al. (2026) is excluded from primary evidence. A report cited by it may enter the corpus only through a logged version-1.1 database/additional-source discovery event or protocol-compliant citation-chasing event followed by new screening. Its overlap, source-specific rediscovery, citation-chasing yield, and exclusions of apparently relevant reports will be reported separately.

arXiv, Semantic Scholar, and Google Scholar searches CANNOT be used.

## Search strategy

Use two complementary search streams so that embedded EPS threads absent from titles or abstracts are not systematically lost:

- **Stream A — EPS-explicit:** combine Population × EPS × MBSE/system-model concepts to identify EPS-primary reports and explicit embedded threads.
- **Stream B — embedded-thread recall:** combine Population × MBSE/system-model concepts without requiring an EPS term, then screen full texts for a qualifying EPS thread. Stream B is intentionally broader and its unique yield is reported separately.

The concept blocks, adapted to each source's syntax and searchable metadata, are:

1. **Population:** CubeSat, nanosatellite, nano-satellite, nanosat, or an explicitly nanosatellite-class mission. Generic `SmallSat`/“small satellite” is neither a positive search concept nor sufficient eligibility evidence;
2. **EPS:** electrical power system/subsystem, EPS, power subsystem, electrical architecture, power/energy budget, energy balance, battery/storage, solar array/generation, power conditioning/distribution, PCDU, or PMAD; and
3. **MBSE/system model:** model-based systems engineering, MBSE, SysML, system model/modeling, reference model, digital engineering, Arcadia, Capella, or another validated structured-system-model term.

Targeted RQ2 and RQ3 searches may add benefit, null/adverse outcome, burden, effort, cost, training, traceability, verification, validation, model verification/validation, system/design verification/validation, simulation, model checking, requirements-in-the-loop, MIL, SIL, PIL, HIL, or test terms. These terms will not be mandatory in every query because doing so could suppress relevant RQ1 and embedded-thread reports.

Searches will be piloted in small, targeted sets. The new search log must record, as applicable, exact strings or request bodies, fields, filters, platform/interface, dates and time zone, source-reported totals, retrieved totals, pagination or event-harvest coverage, refinements, failed or overbroad queries, deduplication, coverage checks, and stopping rationale. Refining source-specific syntax or precision within these fixed concept streams is search implementation, not a change to review eligibility; every version and the final used set must remain in the log.

Previously identified reports may be listed before searching in a read-only known-item register. They may guide query refinement if missed, but they enter the corpus only through a logged search or citation-chasing event followed by new screening. Known-item recall and unique inclusions from each stream and source are reported separately.

The independent baseline consists of the merged results from all six electronic databases and repositories. Only after that baseline is frozen will Buruso et al. (2026) and the retained-file cache be used for deferred recall audits. A missed Buruso-cited report can prompt a logged concept-level probe or enter through a logged citation-chasing route; it is never inserted directly.

Backward and forward citation chasing starts from every full-text-included report and relevant secondary review. Newly found eligible reports are also chased; iteration stops when one complete backward/forward cycle yields no new eligible report. Every seed, index/platform, direction, cycle, candidate, and decision is logged.

Searching stops when both streams, every planned source and source-specific coverage check, the prespecified concept clusters, and relevant report families discovered during the new run have been tested; citation chasing is complete; and additional searches are predominantly redundant rather than merely convenient or precise. The last search date for every source and strategy is reported; the latest of those dates closes the review's evidence window.

## Data management and audit trail

Manage review methods, logs, controlled dictionaries, derived data, and analysis code in the version-controlled `SLR/SLR1/` workspace. Preserve raw source artifacts as read-only files where licensing permits and index every artifact in a manifest with path, query/event ID, source, timestamp, byte size, SHA-256 checksum, access/rights status, and creating software/version. Record the actual database interface and software versions at execution rather than assuming the draft environment remains unchanged.

Use UTF-8 JSON/JSONL or CSV for derived machine-readable data and RIS/BibTeX/CSV or source-native structured exports for bibliographic transfer as available. Validate schemas, identifiers, controlled values, and referential integrity before each merge or synthesis. Deduplication is reproducible but manually adjudicated where identifiers conflict; preserve both the original metadata and the preferred normalized value with rationale. Git history supplies the audit trail for text, code, schemas, and derived non-sensitive data; raw licensed exports and full texts remain in access-controlled storage with the repository/search manifest recording their durable location and backup status. Do not publicly redistribute licensed exports, copyrighted abstracts, or full texts merely for checklist compliance.

## Inclusion and exclusion criteria

| Criterion | Rule | Applicable RQ(s) |
|---|---|---|
| Publication date | First formal publication date from 2011 through the final search date in 2026; online-first and issue versions of the same report are one work | 1--3 |
| Language | Report written in English; inability to retrieve the full text is handled separately as `not_retrieved` | 1--3 |
| Publication type | Full primary-research journal article, conference/proceedings or workshop paper, research chapter in an edited scholarly volume, or institutional technical report with stable provenance and substantive methods/results; empirical comparison and experience reports are eligible when they meet all other criteria. Document type, provenance, and reported review status are verified where possible | 1--3 |
| Population | Actual or intended orbital CubeSat/nanosatellite-class mission or a nanosatellite-tailored model; a generic SmallSat/small-satellite label alone is excluded, and separable CubeSat/nanosatellite evidence is required in mixed-platform reports | 1--3 |
| MBSE threshold | Must meet the structured-system-model definition above | 1--3 |
| EPS threshold | Must meet Route A or Route B at full text | 1--3 |
| RQ1 contribution | Every eligible EPS thread contributes its reported representation, purpose, inputs/assumptions, abstraction, and reuse/tailoring information; missing fields remain `not_reported` | 1 |
| RQ2 contribution | Only atomic outcome or implementation-burden records explicitly attributed to a qualifying EPS thread enter direct RQ2 synthesis; direction, mechanism, and evidence completeness are coded separately | 2 |
| RQ3 contribution | Only `eps_specific` or `system_wide_eps_linked` records with the required target, explicit bridge, and reported V&V method/intent/artifact enter direct RQ3 synthesis; scope, object, criterion completeness, and execution are reported separately | 3 |
| Mixed system scope | Include only when an EPS thread is separately extractable; synthesize other subsystems only as EPS dependencies/interfaces | 1--3 |
| Secondary studies | Exclude from primary evidence, including Buruso et al. (2026); retain separately for positioning, terminology, deferred recall checking, and citation chasing | 1--3 |
| Non-MBSE EPS studies | Exclude stand-alone component, circuit, control, optimization, sizing, simulation, or hardware-performance studies without an explicit structured-system-model link | 1--3 |
| Generic whole-spacecraft MBSE | Exclude reports lacking a qualifying EPS thread, even if they mention EPS or a power budget | 1--3 |
| Other subsystem studies | Exclude unless they contain a qualifying EPS thread; a subsystem's power consumption alone is insufficient | 1--3 |
| Abstract-only/non-research material | Exclude posters/abstracts without full papers, presentation- or slide-only records, recordings, editorials, tutorials, advertisements, patents, and non-scholarly web material. Such records from ESA Indico or NTRS may be logged as discovery leads to a distinct eligible full report but cannot themselves supply primary evidence | 1--3 |
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

The review distinguishes five linked analytic units; the report-family relation is cross-report and therefore the units are not assumed to form a strictly nested hierarchy:

1. **Study/implementation report family:** one underlying investigation, evaluation, mission/design implementation, reference-model release, or materially shared model/toolchain application represented by one or more reports. Family membership requires documented overlap; shared topic, organization, or tool alone is insufficient, and evidence does not transfer between family members.
2. **Report:** one distinct publication or institutional technical report. Online-first and issue manifestations of the same work are collapsed, while substantively distinct companion reports remain separately citable and are linked to their family.
3. **EPS model thread:** one qualifying EPS-primary or embedded chain within a report. A report may contain more than one thread.
4. **Outcome or implementation-burden record:** one atomic outcome direction or burden linked or potentially linked to a thread. When one statement reports several outcomes, directions, or burdens, create separate records that may share the same quotation.
5. **V&V record:** one target–method–scenario activity or artifact linked or potentially linked to a thread. Multiple targets, methods, or scenarios use linked atomic records rather than one aggregate record.

Assign a report-family ID, report-to-family relationship type, membership rationale, evidence location, and overlap confidence. A report may map to more than one family when it genuinely reports distinct underlying implementations or evaluations. Reports from the same family are not treated as independent replications. Families are analytic dependence units, not PRISMA flow-diagram units: PRISMA identification and selection counts remain at record/report level.

New-run IDs must qualify linked records, for example `family_id`, `report_id:thread_id:outcome_burden_id`, and `report_id:thread_id:vnv_id`. A normalized DOI is the preferred cross-run report identity key; NTRS/report numbers and source IDs supplement it, and title–author–year matching requires manual confirmation. Legacy IDs and prior discovery paths are provenance only.

## Quality checklist

All applicable items use:

- No = 0
- Insufficiently = 0.5
- Yes = 1
- Not applicable = excluded from that score's denominator

Quality scores contextualize confidence and sensitivity analyses; they are not automatic exclusion thresholds and cannot make an ineligible report, outcome/burden record, or V&V record eligible.

### Report and EPS-thread quality

1. Was the primary research published in a credible scholarly venue or identifiable institutional technical-report series, with report type, provenance, and review status verifiable?
2. Is the CubeSat/nanosatellite mission context and lifecycle stage described clearly enough to assess applicability?
3. Are the MBSE method, model boundary, language/toolchain, artifacts, and modeled relations described clearly enough to verify MBSE qualification?
4. Are the EPS anchor, model anchor, explicit bridge, and EPS boundary reported clearly enough to reconstruct the qualifying thread?
5. Are the model's stated purpose, intended decisions, users/roles, and lifecycle use reported?
6. Are material inputs and assumptions reported with sufficient detail about value/range, units or time basis, provenance, uncertainty/margin, and rationale?
7. Are model/tool/data availability, configurations, interfaces, and reusable assets reported sufficiently to assess reproducibility?
8. Do the authors discuss limitations, scope boundaries, uncertainty, threats to validity, or alternative explanations?

### RQ2 outcome/burden quality, when applicable

9. Is the outcome or implementation burden explicitly linked to a qualifying EPS thread and a stated MBSE mechanism rather than to EPS technology choice or generic MBSE?
10. Is its reported direction or burden supported by an appropriate metric, traceable case result, comparator, stakeholder assessment, reuse, integration/test result, or operational evidence?

### RQ3 V&V quality, when applicable

11. Are the EPS target, linkage scope, model-to-V&V bridge, source terminology, normalized V&V object, method/artifact, criterion, lifecycle timing, and execution status explicitly reported?
12. When execution or closure is claimed, are the result/verdict and any downstream software, hardware, integration, test, operational, or flight link evidenced?

Items 1--3 and 8 are scored at report level; items 4--7 at EPS-thread level; items 9--10 for each direct RQ2 outcome/burden record; and items 11--12 for each EPS-linked RQ3 record. Any roll-up is descriptive and retains its unit and applicable-item denominator. Linkage confidence is also retained separately from quality score.

### Appraisal meaning, reporting-bias assessment, and conclusion confidence

The checklist assesses reporting completeness, direct EPS linkage, and strength of support in heterogeneous engineering evidence; it is not presented as a validated clinical risk-of-bias instrument. Report checklist domains and record-level evidence confidence at their actual units rather than collapsing them into an unqualified “study quality” label.

No funnel plot or statistical publication-bias test is planned because there is no common effect estimate and the evidence types are heterogeneous. Instead, assess and report, for each RQ synthesis:

- coverage/interface limitations and unique yield across the six sources and citation routes;
- effects of the English, date, population, publication-type, retrieval, and source-access limits;
- unavailable full reports and lead-only material;
- selective or missing outcome/burden, criterion, result, and limitation reporting;
- dependence created by shared study/implementation report families; and
- protocol deviations, search refinements, or review-process limitations that could change interpretation.

Assign conclusion-level confidence narratively as `higher`, `moderate`, `lower`, or `insufficient`, with a source-locatable rationale. Consider directness to a qualifying EPS thread, report and record quality, evidence type and comparator, maturity/independent or physical validation, consistency including null/adverse evidence, report-family independence, and review-process limitations. No numerical quality cutoff or mechanical averaging determines confidence. `Higher` requires multiple materially independent, directly linked and well-supported records with no major unexplained inconsistency; `moderate` permits limited independence, maturity, or comparators but still requires directly supporting evidence; `lower` denotes sparse, weak, indirect, dependent, or materially inconsistent support; and `insufficient` denotes no eligible direct evidence for the conclusion. These labels are an engineering-review framework, not GRADE.

## Extraction fields

A new run-specific `extraction_codebook.json` must be created from this protocol before per-report extraction. Earlier codebooks and extraction forms are not authoritative for this run and may not be copied into new-run fields.

Every synthesis-critical controlled code requires a rationale, a direct quote or source location where possible, and a confidence rating. Preserve `not_reported`, `not_applicable`, `none`, and `uncertain` as distinct statuses. Distinguish author-reported facts from extractor inference.

### Report-level bibliographic and review-management fields

- New-run report ID; optional legacy corpus ID; extraction file path.
- Citation, title, authors, year, venue or institutional report series, publication type, DOI/URL, publisher/issuing organization, source/report identifier, and reported peer/technical-review status.
- Every discovery event: run ID, database/source, exact query or citation route, date, source record ID, rank when available, and raw-search artifact.
- Title/abstract screening tier and rationale.
- Full-text eligibility decision and exclusion rationale, if applicable.
- Route A/Route B classification and evidence.
- RQ contribution status: RQ1; count of eligible RQ2 outcome/burden records; count of direct and near-miss RQ3 records.
- Study/implementation report-family ID(s), report-to-family relationship, membership rationale/evidence, overlap confidence, and shared-result notes.
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
- Narrow controlled limitation flags, including prototype/future work, single case, no comparator, no independent validation, no physical/model-to-test evidence, unavailable model/data, assumptions/data-quality limits, tool dependency, interoperability limits, incomplete lifecycle coverage, ambiguous EPS linkage, generic outcome attribution, or missing V&V criterion.
- Emergent codes for unexpected findings that do not fit the controlled vocabulary; do not silently expand controlled categories during extraction.

## Calibration, consistency, and validation

Before full screening and extraction:

1. pilot the full-text eligibility rule on clear Route A, clear Route B, generic whole-spacecraft MBSE, and non-MBSE EPS examples;
2. pilot the thread, input/assumption, RQ2 outcome/burden, and RQ3 V&V forms on a deliberately varied sample;
3. revise and then freeze the run-specific codebook before full extraction; and
4. document all calibration decisions and examples.

Use isolated assessment passes to reduce context carryover. All final Route B inclusions and all direct RQ2/RQ3 linkage decisions must receive a second check. Record whether that check was performed by another human assessor or by a model-assisted validation pass. Do not describe model-assisted validation as independent human review, and calculate an agreement statistic only when the assessment design genuinely supports it.

Validate all extraction JSON against the codebook, exact controlled labels, record IDs, required evidence/rationales, status distinctions, and report-family/report/thread/outcome-burden/V&V referential integrity before synthesis.

## Planned synthesis

The synthesis is a structured evidence map and narrative synthesis; no pooled effect estimate is planned because models, outcomes, and evidence designs are expected to be heterogeneous.

### Relationship to Buruso et al. (2026)

Buruso et al. (2026) is a broad secondary review of 126 selected space-MBSE studies and reports published from 2011 to 2023, mapping methods, languages, tools, five MBSE phases, and general challenges across heterogeneous space applications. It is used here for positioning, terminology, a deferred recall benchmark, and logged citation chasing, not as primary evidence.

This review is neither an update nor a replication of Buruso et al. It is restricted to orbital CubeSat/nanosatellite EPSs; requires a source-locatable EPS anchor, model anchor, and explicit bridge; and synthesizes material inputs and assumptions, all reported reuse and tailoring approaches, implementation footprint, direct EPS-attributed outcome direction and implementation burdens, and direct EPS target–model–V&V chains. It therefore addresses broader gaps concerning model tailoring and scalability, predominantly anecdotal value claims, and poor visibility of later integration, test, and V&V. System-wide MBSE or V&V is not treated as EPS evidence without the protocol's direct link. Cross-review counts are not compared as effectiveness evidence.

For descriptive currency and overlap, publication patterns may be shown separately for 2011--2023, corresponding to Buruso et al.'s evidence window, and 2024 through the final search date. This temporal split does not change eligibility or imply that reports within either period are independent.

### RQ1

- Map EPS boundaries, model concerns, artifacts, purposes, abstraction levels, inputs/assumptions, provenance, uncertainty/margin handling, all reported reuse/tailoring approaches, implementation footprint, required roles/skills/resources, trade-offs, and lifecycle use.
- Distinguish reported inputs and implementation requirements from reviewer-inferred dependencies and from source silence.
- Where evidence permits, describe how authors characterize implementations as lightweight, scalable, comprehensive, or resource-intensive and compare those characterizations with the reported implementation footprint; lightweight status is not an eligibility filter or required tailoring category.
- Compare Route A and Route B without assuming either is more mature.

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

- Report separate denominators for study/implementation report families, reports, EPS model threads, input/assumption records, outcome/burden records, and V&V records. PRISMA flow counts remain record/report based.
- Treat outcome/burden and V&V records as nested within reports and dependent within report families, not as independent studies.
- Stratify Route A and Route B before presenting combined totals.
- Identify recurring reports from the same study/implementation family; do not count them as independent replication.
- Stratify institutional technical reports and other gray literature from peer-reviewed scholarly reports and include publication-provenance sensitivity views where informative.
- Use quality and linkage-confidence sensitivity views, including Route-A-only and high-confidence subsets where informative.
- Interpret cross-tabs only as descriptive co-reporting unless a direct extracted link supports a relationship.
- Retain `not_reported`, `none`, `not_applicable`, `uncertain`, and invalid/unmapped values distinctly.
- Treat sparse direct evidence as a review finding rather than filling gaps with generic whole-spacecraft MBSE claims.

## Required new-run artifacts

After protocol approval, the restarted review must generate or regenerate, with run provenance:

- integrated protocol approval/version/amendment record, study/implementation report-family registry, and read-only legacy and Buruso-recall known-item registers;
- exact PRISMA-S-compatible search log, versioned source-matching dictionary/code, and raw source-specific search results;
- search manifest with file checksums, source dates, interface details, restrictions, and rights/access status;
- merged/deduplicated candidate set and deduplication report;
- title/abstract and full-text screening log, retrieval log, accessible corpus, and cited full-text exclusion table with one primary reason per report;
- run-specific corpus, identifiers, and extraction codebook;
- per-report extraction files with thread, outcome/burden, and V&V records;
- compiled extraction dataset, bibliography, validation report, and analysis code; and
- machine-readable PRISMA count reconciliation, official PRISMA 2020 flow diagram, synthesis outputs, and completed PRISMA-S/PRISMA 2020 checklists.

Licensed exports, copyrighted abstracts, and full texts need not be made public where rights prohibit it. Preserve them securely where permitted and publish or archive the exact methods, dates, manifests, derived counts/decisions, codebook, code, and a rights-aware availability statement.

## Completed-review reporting

The final report will identify itself as a systematic review and use the PRISMA 2020 checklist and 12-item abstract guidance. It will:

- report every information source actually used and its last search date, with failed/planned-but-unused sources distinguished;
- link to verbatim final source-native strategies and PRISMA-S logs rather than a cleaned representative query;
- describe screening, extraction, second checks, conflict handling, and model assistance exactly as performed, never calling model-assisted checking independent human review;
- explain that no pooled effect estimate is planned and label every descriptive count/proportion by its report-family, report, thread, outcome/burden, or V&V denominator;
- use the new-review databases-and-other-sources flow diagram with records/reports—not linked analytic units—in its boxes;
- cite apparently eligible full reports excluded at full text with source-locatable reasons;
- present appraisal, reporting-bias, and conclusion-confidence results using the framework above; and
- report protocol access/version, every amendment/deviation, review-process and evidence limitations, and data/code/material availability.

The exact administrative declarations intentionally deferred above must be completed or explicitly reported as absent before publication; they are not silently implied by methodological freeze.

The source-interface pilots and consistency checks recorded in the search log are complete, and version 1.1 is ready for final freeze/search authorization. On authorization, record the freeze date here before any valid new-run search; subsequent changes then require a prospective, versioned deviation record.
