# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Discovery and appraisal

> **Protocol parts:** [1 — Scope and definitions](protocol.md) · **2 — Discovery and appraisal** (this file) · [3 — Extraction and synthesis](protocol-extraction-and-synthesis.md) · [Supporting need assessment — Prior secondary reviews](protocol-prior-secondary-reviews.md)
>
> **Definitions used here:** [MBSE qualification](protocol.md#mbse-qualification), [eligible EPS evidence routes](protocol.md#eligible-eps-evidence-routes), and [bounded genericity](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring).

## Information sources

### Electronic databases, collections, and indexed online resources

The main search covers 15 sources or collections through 13 search interfaces. Engineering Village provides one interface for two databases, which must still be tracked separately. The ProQuest Platform provides one interface for two sources, which must be selected and searched in separate events.

Search these sources:

- **Scopus:** bibliographic database.
- **Web of Science Core Collection:** bibliographic and citation database on the Clarivate Web of Science platform.
- **IEEE Xplore:** bibliographic and full-text database.
- **arXiv:** the full multidisciplinary preprint repository.
- **Compendex** and **Inspec:** search these together through Engineering Village, but keep their records and counts separate.
- **Wiley Online Library:** the full publisher platform.
- **Springer Nature Link:** the full publisher platform.
- **Advanced Technologies & Aerospace Index:** select only this index on the ProQuest Platform.
- **ProQuest Dissertations & Theses Global (PQDT Global):** select only this database on the ProQuest Platform, in a separate search event.
- **AIAA Aerospace Research Central (ARC):** the full publisher-hosted collection.
- **IAF Digital Library:** the full database.
- **Open Access Theses and Dissertations (OATD):** the full public index of electronic theses and dissertations.
- **ESA Indico:** the full public event and contribution database.
- **NASA Technical Reports Server (NTRS):** the full public technical-report database.

For PRISMA-S, name PQDT Global as a database on the ProQuest Platform and describe OATD as an indexed online resource. For the PRISMA 2020 flow diagram, count OATD under websites and other methods. OATD is still a required source and keeps its own total.

As a rule specific to this review, count the other 14 bounded and structured collections in the databases/registers column as databases.

Keep separate totals for all 15 sources or collections.

Create the new-run source mapping and schemas under `searches/` as specified under [new-run source translations and search artifacts](#new-run-source-translations-and-search-artifacts).

The separate [prior-secondary-review need assessment](protocol-prior-secondary-reviews.md) searches only Scopus and Web of Science Core Collection. Its `PSR*` events, records, decisions, extractions, and counts are not part of the 15-source primary-evidence baseline or the main PRISMA flow, even though they reuse validated interface behavior and common search infrastructure.

### Supplementary discovery and citation searching

Also use backward citation searching, forward citation searching in both Scopus and Web of Science Core Collection, and Buruso et al. (2026), *Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review* (https://doi.org/10.1002/sys.70051), as a secondary-review seed and later recall check. Follow the [baseline and citation-search procedure](#completing-the-baseline-and-citation-searches), the [Part 1 evidence restrictions](protocol.md#need-for-this-review), and Buruso's separate role in the [prior-secondary-review search](protocol-prior-secondary-reviews.md).

## Search strategy

### Search streams and set construction

Use two complementary streams because an EPS thread inside a wider spacecraft model may not appear in bibliographic metadata.

- **Stream A — EPS-explicit:** Population × EPS × MBSE/system-model concepts.
- **Stream B — embedded-thread recall:** Population × MBSE/system-model concepts and conservative artifact or tailoring expansions, without requiring an EPS term. Every Stream B candidate must be checked at full text for an eligible EPS thread.

The 13 direct query families are Scopus, Web of Science Core Collection, IEEE Xplore, Engineering Village, Wiley Online Library, Springer Nature Link, Advanced Technologies & Aerospace Index, PQDT Global, OATD, AIAA ARC, IAF Digital Library, NASA Technical Reports Server (NTRS), and arXiv. Engineering Village covers two databases, Compendex and Inspec.

Use the following exact cross-source concept blocks. Source-native translations may change syntax, field wrappers, and validated wildcard use, but not the intended terms or Boolean relationships. At concept level, every multiword entry is an ordered phrase; a source may apply only validated punctuation or hyphen normalization. Acronyms must match standalone lexical tokens rather than substrings. Record and test the source-native implementation of these rules.

#### Population and EPS blocks

- **Population (`P`):** `CubeSat`, `CubeSats`, `cube sat`, `cube sats`, `cube-sat`, `cube-sats`, `cube satellite`, `cube satellites`, `nanosat`, `nanosats`, `nanosatellite`, `nanosatellites`, `nano-sat`, `nano-sats`, `nano sat`, `nano sats`, `nano-satellite`, `nano-satellites`, `nano satellite`, and `nano satellites`, `SmallSat`, `SmallSats`, `small satellite`, `small satellites`, `small sat`, and `small sats`.
- **High-specificity EPS (`E_H`):** `electrical power system`, `electrical power systems`, `electric power system`, `electric power systems`, `electrical power subsystem`, `electrical power subsystems`, `electric power subsystem`, `electric power subsystems`, `electrical energy subsystem`, `electrical energy subsystems`, `EPS`, `EPSs`, `power subsystem`, `power subsystems`, `power system`, `power systems`, `spacecraft power system`, `spacecraft power systems`, `power supply`, `power supplies`, `power distribution unit`, `power distribution units`, `PDU`, `PDUs`, `power processing unit`, `power processing units`, `power control and distribution`, `power management and distribution`, `electrical architecture`, `electrical architectures`, `power architecture`, `power architectures`, `DC power bus`, `DC power buses`, `PCDU`, `PCDUs`, `PMAD`, and `PMADs`.
- **Functional or analytical EPS (`E_F`):** `power budget`, `power budgets`, `energy budget`, `energy budgets`, `energy balance`, `energy balances`, `power balance`, `power balances`, `power margin`, `power margins`, `power generation`, `photovoltaic generator`, `photovoltaic generators`, `solar array`, `solar arrays`, `solar panel`, `solar panels`, `battery`, `batteries`, `battery management`, `state of charge`, `states of charge`, `energy storage`, `power electronics`, `power conditioning`, `power distribution`, `power management`, `power interface`, `power interfaces`, `power mode`, `power modes`, `load profile`, `load profiles`, `power consumption`, `power demand`, `power profile`, and `energy harvesting`.
- **All EPS (`E`):** `E_H ∪ E_F`.

#### MBSE and relationship blocks

- **High-specificity MBSE (`M_H`):** `model-based systems engineering`, `model based systems engineering`, `model-based system engineering`, `model based system engineering`, `model-driven systems engineering`, `model driven systems engineering`, `model-driven system engineering`, `model driven system engineering`, `model-centric systems engineering`, `model centric systems engineering`, `model-centric system engineering`, `model centric system engineering`, `MBSE`, `SysML`, `systems modeling language`, `systems modelling language`, `system modeling language`, `system modelling language`, `object-process methodology`, `object process methodology`, `OPM`, `object-oriented systems engineering method`, `object oriented systems engineering method`, `OOSEM`, `object-oriented systems engineering`, `object oriented systems engineering`, `Arcadia`, `Capella`, `model-based engineering`, `model based engineering`, `model-driven engineering`, `model driven engineering`, `model-based design`, `model based design`, `model-driven design`, `model driven design`, `MBE`, `MDE`, `MBD`, `MagicGrid`, `Harmony-SE`, `Harmony SE`, `RFLP`, `Cameo Systems Modeler`, `MagicDraw`, `IBM Engineering Systems Design Rhapsody`, `Rational Rhapsody`, `Vitech CORE`, `Vitech GENESYS`, `OpenMBEE`, `Enterprise Architect`, `MATLAB System Composer`, `System Composer`, and `Modelio`.
- **Broad structured model (`M_B`):** `system model`, `systems model`, `system modeling`, `systems modeling`, `system modelling`, `systems modelling`, `reference model`, `reference models`, `digital engineering`, `object-oriented systems model`, `object-oriented systems models`, `model-based system design`, `model based system design`, `model-based systems design`, `model based systems design`, `system architecture model`, `system architecture models`, `systems architecture model`, `systems architecture models`, `integrated system model`, `integrated system models`, `integrated systems model`, `integrated systems models`, `system-level model`, `system-level models`, `system level model`, `system level models`, `digital thread`, `digital threads`, `digital twin`, and `digital twins`.
- **All MBSE/system-model terms (`M`):** `M_H ∪ M_B`.
- **Systems-engineering relationship or concern (`R`):** `requirement`, `requirements`, `function`, `functions`, `functional`, `behavior`, `behaviors`, `behaviour`, `behaviours`, `behavioral`, `behavioural`, `architecture`, `architectures`, `architectural`, `interface`, `interfaces`, `traceability`, `trace`, `traceable`, `traced`, `allocation`, `allocate`, `allocated`, `constraint`, `constraints`, `parametric`, `parametrics`, `analysis`, `analyses`, `design`, `designs`, `designed`, `designing`, `decision`, `decisions`, `decision-making`, `decision making`, `trade study`, `trade studies`, `trade-off`, `trade-offs`, `tradeoff`, `tradeoffs`, `verification`, `verifications`, `verify`, `verifies`, `verified`, `verifying`, `validation`, `validations`, `validate`, `validates`, `validated`, and `validating`.

`M_B` requires `R` in direct B2 queries because its terms are otherwise broad. Stream A does not require `R`: the EPS block supplies the additional precision.

#### Artifact and tailoring blocks

For every construction described as *paired*, the left and right expressions must occur in either order in the same searchable field or prospectively defined local document route, with no more than five intervening lexical tokens. If an interface cannot express that rule, its pilot may accept a documented broader same-field implementation only when it cannot lose an exact-pair match; apply the exact rule locally where the available fields permit it and report the limitation.

- **Precise reusable model or template (`G_model`):** `generic model`, `generic models`, `generic system model`, `generic system models`, `reusable model`, `reusable models`, `reusable system model`, `reusable system models`, `configurable model`, `configurable models`, `configurable system model`, `configurable system models`, `model template`, and `model templates`; `mission-agnostic`, `mission agnostic`, `mission-independent`, and `mission independent`, each paired with `model`, `models`, `architecture`, or `architectures`.
- **Structural reusable artifact (`G_structure`):** `reference architecture`, `reference architectures`, `domain model`, `domain models`, `metamodel`, `metamodels`, `meta-model`, and `meta-models`; `product-line`, `product line`, `product-family`, and `product family`, each paired with `model` or `models`; and `variation point` or `variation points` paired with `model`, `models`, `architecture`, or `architectures`.
- **Conservative central asset (`C1`):** `reference model`, `reference models`, `system reference model`, `system reference models`, `model library`, `model libraries`, `system model library`, `system model libraries`, `model pattern`, `model patterns`, `modeling pattern`, `modeling patterns`, `modelling pattern`, `modelling patterns`, `system model pattern`, `system model patterns`, `systems model pattern`, `systems model patterns`, `model profile`, `model profiles`, `system model profile`, `system model profiles`, `systems model profile`, `systems model profiles`, `SysML profile`, and `SysML profiles`. Also include every pairing of the four phrases `domain-specific modeling language`, `domain specific modeling language`, `domain-specific modelling language`, and `domain specific modelling language` with one of these nine anchors: the four model-based system(s)-engineering spellings in `M_H`, `MBSE`, `SysML`, `systems modeling language`, `system model`, or `systems model`. Bare `library`, `pattern`, `profile`, or `language` never qualifies.
- **Model-linked tailoring (`T2`):** one of `reuse`, `reuses`, `reused`, `reusable`, `reusing`; `tailor`, `tailors`, `tailored`, `tailoring`; `customize`, `customizes`, `customized`, `customizing`, `customization`; `customise`, `customises`, `customised`, `customising`, `customisation`; `configure`, `configures`, `configured`, `configuring`, `configuration`; `parameterize`, `parameterizes`, `parameterized`, `parameterizing`, `parameterization`; `parameterise`, `parameterises`, `parameterised`, `parameterising`, `parameterisation`; `instantiate`, `instantiates`, `instantiated`, `instantiating`, `instantiation`; `variability`; `variation point`; `specialize`, `specializes`, `specialized`, `specializing`, `specialization`; `specialise`, `specialises`, `specialised`, `specialising`, `specialisation`; or `adapt`, `adapts`, `adapted`, `adapting`, `adaptation`, explicitly paired with `model`, `models`, `architecture`, or `architectures`.

`G_model`, `G_structure`, C1, and T2 are recall concepts, not eligibility tests or evidence of reuse. An `architecture` occurrence inside an artifact phrase cannot also satisfy an independent R tag through the same text span.

#### RQ2 and RQ3 identification during extraction

Do not use outcome, implementation-burden, or V&V terms as candidate-discovery blocks. Assess every included full text against the operational RQ2 and RQ3 definitions in [Part 1](protocol.md), regardless of the terminology used by the source. Automated keyword flags may be used only as optional quality-assurance aids; they cannot determine whether an outcome, burden, or V&V record is created.

#### Direct query schedule

Execute these nine semantic partitions in every direct query family unless a newly documented source limitation makes an exact translation impossible. A source may implement one semantic partition as a prospectively documented, lossless union of source-native query cells when a fixed query-length limit prevents one expression; preserve each cell's query, total, and stable identifiers and reconcile their union. A source-specific failure does not authorize an unrecorded narrower query.

| ID | Boolean form | Role |
|---|---|---|
| `A1` | `P AND E_H AND M_H` | Named EPS × explicit MBSE |
| `A2` | `P AND E_F AND (M_H OR M_B)` | EPS functions or analyses × all model terms |
| `A3` | `P AND E_H AND M_B` | Named EPS × broad structured model |
| `B1` | `P AND M_H` | Embedded-thread baseline |
| `B2` | `P AND M_B AND R` | Controlled broad-model expansion |
| `BG1` | `P AND G_model` | Precise reusable model or template |
| `BG2` | `P AND G_structure` | Structural reusable artifact |
| `BC1` | `P AND C1` | Conservative central asset |
| `BT2` | `P AND M_B AND T2` | Model-linked tailoring |

Therefore:

- `Stream A = A1 ∪ A2 ∪ A3`;
- `core Stream B = B1 ∪ B2`; and
- `expanded Stream B = BG1 ∪ BG2 ∪ BC1 ∪ BT2`.

Retain and screen every record returned by any planned partition while preserving each discovery event. Report intersections and records unique to each stream and expansion after within-source and cross-source deduplication.

### Controlled vocabulary and indexed terms

Free-text searching remains mandatory. When a source provides a genuine controlled vocabulary or a distinct indexed-term field, construct the applicable concept as the union of its free-text block and validated source-specific descriptors. Inspect thesaurus scope notes, hierarchy, narrower terms, and terms assigned to known relevant records; use explosion only when every included narrower concept is in scope. A generic `systems engineering` descriptor cannot satisfy `M_H` by itself: pair it with a model or modeling descriptor unless the source supplies a specific MBSE descriptor. Do not impose major-topic restrictions, and do not emulate controlled vocabulary on sources that do not provide it.

Record every accepted descriptor, field, hierarchy or explosion setting, mapping to the cross-source block, and known-item effect in the source packet. Controlled terms supplement the normative text words; they neither replace them nor change scientific eligibility.

### New-run source translations and search artifacts

Create the new-run search-infrastructure components in the [required discovery and screening artifact bundle](#required-discovery-and-screening-artifacts) before the first related pilot, and give each artifact provenance.

The protocol's concept blocks and Boolean schedule are normative. The new dictionary must reproduce them without adding or dropping a concept.

For each source or local method, record before final execution:

- source, database or collection, and interface;
- query or event IDs and the exact source-native translation of every planned partition;
- fields, filters, limits, date and language handling, and visible controls;
- stemming, lemmatization, automatic expansion, wildcard behavior, and any controlled-vocabulary or indexed-term fields, descriptors, hierarchies, and explosion settings;
- pagination, result ordering, stable identifiers, export or capture method, and source limits;
- the relationship between source-native queries and the cross-source semantic blocks;
- pilot refinements, failures, and the accepted final implementation

### Completing the baseline and citation searches

The independent baseline is complete only after all 15 planned sources or collections have either a complete, reconciled final run or a recorded final source or failure. Merge records only from complete successful events. Preserve separate Compendex and Inspec discovery instances and separate events for the two ProQuest sources. Keep every failure and reason in the new manifest and PRISMA counts.

Only after that baseline and failure register are complete, use Buruso et al. (2026) and the known-item registers. A missed known-item may guide prospective query refinement, but it can enter the review only through a recorded final search or citation-search event and normal screening. Report known-item recall and unique inclusions by stream and source.

Start backward and forward citation searching from every included full-text report and relevant secondary review:

- inspect each seed's complete reference list;
- search forward citations in both Scopus and Web of Science Core Collection;
- add each newly included report as a seed in the next numbered cycle; and
- stop only after one complete cycle of backward searching and both forward searches finds no new eligible report.

For every citation event, record the seed, platform, direction, cycle, source and retrieved totals, candidates, duplicates, decisions, failures, and stopping result. Use `discovery_route=citation_chasing`; citation provenance never bypasses screening.

## Data management and audit trail

Keep review methods, logs, controlled dictionaries, derived data, and analysis code in the Git-tracked `SLR/SLR1/` workspace.

Make deduplication reproducible. Review conflicts manually when identifiers disagree. Keep both the original metadata and the preferred normalized value, with the reason for choosing it.

Use Git history as the audit trail for text, code, schemas, and derived non-sensitive data.

### Required discovery and screening artifacts

The discovery and screening artifact bundle comprises:

- known-item registers for legacy reports and Buruso recall;
- a search log meeting PRISMA-S requirements;
- source-specific guidelines, pilot- and final-run manifest schemas, and failure-register schema;
- raw source-specific results];
- a merged and deduplicated candidate set and deduplication metadata and rationale for decisions;
- title-and-abstract screening, full-text screening, and retrieval logs; and
- the accessible report set and a table of cited full-text exclusions with one main reason per report.

Part 3 incorporates this bundle by reference rather than listing its components again.

## Inclusion and exclusion criteria

| Criterion | Plain-English rule | RQ(s) |
|---|---|---|
| Publication date | Include a report only when an eligible version is dated from 2011-01-01 through the common evidence cutoff in Part 1. Apply the canonical [report-version and date rules](protocol.md#report-versions-dates-and-review-status). | 1–3 |
| Language | The full report must be in English. English metadata does not prove that the report itself is in English. If the full text cannot be obtained, use `not_retrieved` instead of making a language assumption. | 1–3 |
| Publication type | Include a full primary-research journal article; conference, proceedings, or workshop paper; workshop presentation (for ESA Indico only); research chapter in an edited scholarly book; institutional technical report; arXiv preprint; completed master's thesis; or completed doctoral thesis or dissertation. Apply the canonical [version and review-status rules](protocol.md#report-versions-dates-and-review-status). | 1–3 |
| Scientific scope | The work must satisfy the canonical [nanosatellite population](protocol.md#nanosatellite-population), [EPS boundary](protocol.md#eps-boundary), [MBSE qualification](protocol.md#mbse-qualification), and [Route A or Route B](protocol.md#eligible-eps-evidence-routes) rules. | 1–3 |
| Secondary studies | Exclude secondary studies. | 1–3 |
| Abstract-only or non-research material | Exclude posters or abstracts without full papers; thesis or dissertation metadata and abstract stubs without the completed substantial report; proposals and prospectuses; incomplete degree work; undergraduate, bachelor's, or non-degree projects; advertisements; and non-scholarly web material. | 1–3 |
| Retrieval status | Scientific eligibility does not depend on open access. If the report is not obtained after the required retrieval attempts, including a restricted or embargoed thesis, record `not_retrieved`. Do not silently exclude it for scientific reasons. | 1–3 |

Apply the canonical distinction between [report eligibility and question contribution](protocol.md#report-eligibility-versus-question-contribution).

## Screening and eligibility procedure

### Title and abstract screening

- **Candidate:** the title or abstract clearly suggests EPS-primary MBSE or a likely embedded EPS thread, or the record appears to meet the nanosatellite and MBSE rules, but the abstract cannot confirm an embedded EPS thread.
- **Reject:** the record clearly has the wrong population, publication type, date, language, or is outside MBSE scope, or clearly has no qualifying EPS link.

Do not require an EPS or power term in a Stream B title or abstract. Embedded threads may be absent from metadata. If nanosatellite MBSE is plausible, retrieve the full text and resolve uncertainty there.

### Full-text decision

Assign exactly one final decision and give a source-located reason:

- `include_route_A_eps_primary`;
- `include_route_B_embedded_eps`;
- `exclude_no_qualifying_eps_thread`;
- `exclude_not_mbse`;
- `exclude_wrong_population`;
- `exclude_wrong_publication_type`;
- `exclude_wrong_date`;
- `exclude_wrong_language`;
- `exclude_secondary_study`;
- `not_retrieved`.

If thesis or dissertation completion status is unresolved, hold the record as `publication_type_unresolved` while looking for source-locatable clarification. If a record in the cutoff year gives only a year, or thesis dates conflict, hold it as `date_unresolved`. Do not silently turn either temporary status into an exclusion.

If a plausible completed report is unavailable because of access rights, an embargo, or a broken repository link, use `not_retrieved`. Do not call it the wrong publication type because it is unavailable.

## Units and identifiers

Use the canonical [units, counting rules, and ID structure](protocol.md#units-of-evidence-and-counting). During discovery and screening, preserve record-to-report identity, all discovery events, report-family evidence, and artifact-lineage evidence without moving facts between linked units. PRISMA flow counts remain at record and report level.

## Unit-level evidence appraisal

Appraisal will be executed after extraction.
Keep four judgments distinct:

1. **Coding confidence** is the assessor's certainty that a source was located and interpreted correctly.
2. **Methodological appraisal** assesses whether the design and conduct of the evaluation are fit for the particular claim.
3. **Claim support** assesses how strongly one evidence unit supports one bounded claim.
4. **Conclusion confidence** assesses a synthesis conclusion across contributing units.

Assign coding confidence as `high` for explicit and unambiguous source support, `moderate` when a bounded but supported interpretation or reconstruction is required, and `low` when material ambiguity remains. Apply the [evidence statuses](protocol.md#evidence-statuses) separately. Coding confidence cannot substitute for methodological credibility, and an operational or flight setting cannot automatically upgrade support for a claim it was not designed to test.

Create a scoped methodological-appraisal object when a report makes an empirical or evaluative claim used for RQ1, RQ2, or RQ3. Link it to the existing report, thread, artifact or profile, application, outcome or burden, and V&V IDs that it appraises. One object may support several records only when they use the same design, data, and analysis. Create separate objects when one report contains materially different evaluations, such as a simulation and an interview study.

Classify the evaluation design as one or more of: `model_or_simulation_evaluation`, `case_study_or_experience_report`, `comparative_observational`, `controlled_or_quasi_experimental`, `survey`, `interview_or_qualitative`, `mixed_methods`, `artifact_or_reuse_demonstration`, `other`, or `unclear`.

Appraise these common domains when applicable:

- clarity of the aim and fitness of the design to that aim;
- description and selection of the mission, cases, participants, scenarios;
- definition of the MBSE artifact or activity and any comparator;
- provenance and validity of inputs, data sources, measures, pass/fail criteria;
- execution fidelity, missing data, exclusions, failures, and adverse or null results;
- appropriateness and transparency of the analysis;
- treatment of confounders and credible rival explanations;
- traceability from observations through analysis to the stated conclusion; and
- limits on applicability outside the evaluated setting.

Also apply design-specific domains:

- **Model or simulation evaluation:** model verification, validation against an authoritative reference when claimed, input and calibration provenance, uncertainty and sensitivity analysis, and scenario coverage.
- **Comparative, controlled, or quasi-experimental evaluation:** case or group comparability, allocation or selection, treatment fidelity, outcome-measure validity, missingness or attrition, confounding, and appropriateness of statistical analysis.
- **Case study or experience report:** case-selection rationale, context, chain of evidence, triangulation, rival explanations, and the evaluator's role.
- **Survey:** sampling frame, representativeness, response and non-response, instrument validity, and analysis.
- **Interview or qualitative evaluation:** participant selection, data-collection transparency, analytic procedure, diversity of perspectives, reflexivity, and traceability from source material to interpretation.
- **Artifact or reuse demonstration:** artifact identity, distinction among applications, implementation-family dependence, independent adoption when claimed, post-tailoring assurance, and failed or conflicting applications. Apply the canonical [A/E/C/T/P/I bounded-reuse profile](protocol.md#rq1-dispositions-and-evidence-gates).

Code each applicable appraisal domain as `adequate`, `some_concerns`, `inadequate`, `not_reported`, `unclear`, or `not_applicable`, with a reason, evidence reference, and coding confidence. Use `inadequate` only for a source-supported methodological deficiency; use `not_reported` when conduct cannot be assessed from the available report. Do not sum, average, or convert domain codes into a pass or numerical score.

Appraise evidence at the unit that supports a finding:

- At report and EPS-thread level, use direct source support for mission context, MBSE qualification, anchors and bridges, inputs and assumptions, purpose, implementation footprint, availability, and limitations. Link a methodological appraisal when an evaluation supports a characterization or footprint claim.
- For reusable artifacts and tailoring applications, use the A/E/C/T/P/I gate vector, tier, lineage and adopter coding confidence, demonstrated coverage, assurance, failed or conflicting applications, and the methodological appraisal of any evaluation used to claim benefit or transfer.
- For RQ2, keep author attribution separate from reviewer assessment. Use claim kind, explicit EPS attribution, mechanism, measure directness, comparator adequacy when required, confounding, evaluation design and appraisal, dependence, and record-level claim support.
- For RQ3, use linkage scope, target and bridge, V&V object, criterion completeness, execution and timing, result or verdict, pass/fail criteria credibility when validation is claimed, model-to-test continuity, methodological appraisal, dependence, and record-level claim support.

Apply the canonical [evidence statuses](protocol.md#evidence-statuses) and [report-eligibility versus question-contribution rule](protocol.md#report-eligibility-versus-question-contribution).

### Appraisal meaning, reporting-bias assessment, and conclusion confidence

Interpret these unit-level structures under the [Part 1 engineering reporting framework](protocol.md#reporting-framework); do not reduce them to an unexplained “study quality” label.

Do not make a funnel plot or run a statistical publication-bias test. The evidence does not share one effect measure and is too varied. Instead, assess and report the following for each research-question synthesis:

- source and interface coverage, failures, and unique results across the 15 sources, 13 interfaces, and citation routes, with OATD in the website/other-methods channel;
- the effects of language, date, population, publication-type, retrieval, and source-access limits;
- specific access and coverage issues, geographic and institutional imbalance, embargoes, missing abstracts or metadata, uncertainty about degree status, and overlap between PQDT and OATD or between other ;
- reports that could not be obtained and records that were only leads;
- missing or selectively reported genericity claims, applicability limits, tailoring failures and burdens, outcomes and burdens, direct and surrogate measures, comparators, confounders, pass/fail criteria, null or adverse results, and limitations;
- dependence caused by reports from the same study or implementation family and repeated reports of the same artifact lineage or application;
- review-process limitations documented under the [Part 3 extraction-verification procedure](protocol-extraction-and-synthesis.md#sole-reviewer-extraction-and-verification); and
- protocol departures, search changes, and review-process limits that could affect interpretation.

Treat the sole-reviewer and model-assistance items as review-process limitations, not as publication or selective-reporting bias in the primary studies.

Give each conclusion a narrative confidence label: `higher`, `moderate`, `lower`, or `insufficient`. Give a source-locatable reason. Consider:

- the kind and scope of claim being synthesized;
- directness to a qualifying EPS thread;
- fitness and methodological appraisal of the contributing evaluation designs;
- whether measures are direct or are justified surrogates;
- comparator adequacy and treatment of confounding when the claim is comparative or causal;
- record-level claim support and applicability to the stated conclusion;
- the genericity profile and tier when relevant;
- maturity, independence, or physical validation only when they bear directly on the claim;
- consistency, including null, adverse, and failed-transfer evidence;
- independence of report families and tailoring applications; and
- limitations in the review process.

Evidence type and maturity remain descriptive and do not determine confidence by themselves. Never convert a genericity tier, coding-confidence value, methodological domain, publication type, or record-support label automatically into a conclusion-confidence label. Do not use a numerical cutoff or mechanical average.

- **Higher:** several materially independent, directly linked, methodologically credible records support the bounded conclusion, all requirements relevant to that kind of claim are met, and there is no major unexplained disagreement.
- **Moderate:** direct support exists, but there are important limitations in methodology, independence, precision, applicability, or consistency relevant to the conclusion.
- **Lower:** support is sparse, methodologically concerning, indirect, dependent, or importantly inconsistent.
- **Insufficient:** there is no eligible direct evidence for the conclusion.

Use these labels only as the narrative engineering framework defined here, consistently with the [Part 1 reporting framework](protocol.md#reporting-framework).

---

**Previous:** [Part 1 — Scope and definitions](protocol.md)  **Next:** [Part 3 — Extraction and synthesis](protocol-extraction-and-synthesis.md)
