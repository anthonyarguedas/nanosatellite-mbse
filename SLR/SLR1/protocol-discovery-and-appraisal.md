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

Do not use outcome, implementation-burden, or V&V terms as candidate-discovery blocks. Assess every included full text against the operational RQ2 and RQ3 definitions in [Part 1](protocol.md), regardless of the terminology used by the source. Automated keyword flags may be used only as optional quality-assurance aids. They cannot determine whether an RQ2 finding or RQ3 activity is created.

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

Record every accepted descriptor, field, hierarchy or explosion setting, mapping to the cross-source block. Controlled terms supplement the normative text words; they neither replace them nor change scientific eligibility.

### New-run source translations and search artifacts

Create the new-run search-infrastructure components in the [required discovery and screening artifact bundle](#required-discovery-and-screening-artifacts) before the first related pilot, and give each artifact provenance.

The protocol's concept blocks and Boolean schedule are normative. The new dictionary must reproduce them without adding or dropping a concept.

For each source or local method, record before final execution:

- source, database or collection, and interface;
- exact source-native translation of every planned partition;
- fields, filters, limits, date and language handling;
- stemming, lemmatization, automatic expansion, wildcard behavior, and any controlled-vocabulary or indexed-term fields, descriptors, hierarchies, and explosion settings;
- pagination, result ordering, stable identifiers, export method, and source limits;
- pilot refinements

These source-specific guidelines will be recorded in `source-specific/`.
For PRISMA-S reporting, search rationales and strategies are linked to the cross-source query schedule and citation chasing strategy, so they are not source-specific.

### Finalizing searches and citation searches

Searches are finalized only after all 15 planned sources or collections have either a final run covering the entire source-specific schedule or a recorded final failure that excludes them from the review. Merge records only from complete successful events. Preserve separate Compendex and Inspec discovery instances and separate events for the two ProQuest sources.

Start backward and forward citation searching from every included full-text report and relevant secondary review:

- inspect each seed's complete reference list;
- search forward citations in both Scopus and Web of Science Core Collection;
- add each newly included report as a seed in the next numbered cycle; and
- stop only after one complete cycle of backward searching and both forward searches finds no new eligible report.

For every citation event, record the seed, platform, direction, cycle, source and retrieved totals, candidates, duplicates, decisions, failures, and stopping result. Use `discovery_route=citation_chasing`; citation provenance never bypasses screening.

Final searches are saved to `source-specific/*/final-searches/`, both for discovery and citation chasing (for Scopus and WoS only).

## Data management and audit trail

Make deduplication reproducible via a single `SLR/SLR1/deduplication.py`. Review conflicts manually when identifiers disagree. Keep both the original metadata and the preferred normalized value, with the reason for choosing it.

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

Use the canonical [units, counting rules, and ID structure](protocol.md#units-of-evidence-and-counting). During discovery and screening, preserve record-to-report identity and all discovery events. PRISMA flow counts are done at record and report level.

## Finding-level evidence appraisal

Appraisal is embedded in the extracted finding. Do not create a separate methodological-appraisal object, domain matrix, numerical score, or general report-quality label.

Keep three judgments distinct:

1. **Coding confidence** is the assessor's certainty that the source was located and interpreted correctly.
2. **Finding support** states how well the reported evidence supports one bounded evaluative claim or conclusion.
3. **Conclusion confidence** assesses a synthesis conclusion across contributing reports, families, lineages, findings, and activities.

Assign coding confidence as `high` for explicit and unambiguous source support, `moderate` when a bounded reconstruction is required, and `low` when material ambiguity remains. Apply the [evidence statuses](protocol.md#evidence-statuses) separately. Coding confidence does not measure evidential strength.

Give every evaluative RQ1 characterization, direct RQ2 finding, direct RQ3 activity, report-level reuse conclusion, and lineage-level reuse conclusion these inline fields:

- **`evidence_basis`**, using one or more of `assertion_only`, `worked_example`, `executed_result`, `comparison`, `stakeholder_evidence`, `physical_or_operational_check`, and `independent_transfer`;
- **`support`**, using `supported`, `limited`, `unsupported`, or `unclear`; and
- **`support_reason`**, one concise source-located sentence naming the strongest evidence and the main limitation.

Evidence basis is descriptive. It does not set support automatically.

Use the support codes as follows:

- **`supported`:** direct or credibly justified evidence from a method fit for the bounded claim supports it, with no major unresolved limitation relevant to that claim.
- **`limited`:** relevant evidence exists, but an important limitation in method, directness, comparison, precision, independence, or applicability remains.
- **`unsupported`:** the source provides assertion only, no observation bearing on the claim, or a result that does not measure the claimed construct.
- **`unclear`:** relevant evidence is reported, but ambiguity prevents a support judgment.

The report-level extraction captures evaluation design, context, inputs, data sources, execution, analysis, failures, exclusions, and limitations. Record additional appraisal fields only when the claim requires them:

- For comparative or causal claims, record the comparator, material differences, comparator adequacy, and major rival explanations.
- For model or design validation, record the criterion or oracle and why it is authoritative for the intended use.
- For survey, interview, or experience claims, record participants or observational units, sampling or selection, collection method, and analysis.
- For reuse claims, apply the [report-level and consolidated lineage assessment and reuse-level rules](protocol.md#report-level-and-consolidated-lineage-assessment-and-reuse-levels), including tailoring effort, post-tailoring assurance, and adopter independence at the applicable scope.

An executed model is evidence of execution. It supports accuracy, validity, effectiveness, transferability, or benefit only when the source reports evidence fitted to that wider claim. Apply the canonical [evidence statuses](protocol.md#evidence-statuses) and [report-eligibility versus question-contribution rule](protocol.md#report-eligibility-versus-question-contribution).

### Finding support, reporting-bias assessment, and conclusion confidence

Interpret the inline support fields under the [Part 1 engineering reporting framework](protocol.md#reporting-framework). Do not reduce a report to an unexplained “study quality” label.

Do not make a funnel plot or run a statistical publication-bias test. The evidence does not share one effect measure and is too varied. Instead, assess and report the following for each research-question synthesis:

- source and interface coverage, failures, and unique results across the 15 sources, 13 interfaces, and citation routes, with OATD in the website/other-methods channel;
- the effects of language, date, population, publication-type, retrieval, and source-access limits;
- specific access and coverage issues, geographic and institutional imbalance, embargoes, missing abstracts or metadata, uncertainty about degree status, and overlap between PQDT and OATD or other platforms;
- reports that could not be obtained and records that were only leads;
- missing or selectively reported reuse claims, applicability limits, tailoring effort, failures and burdens, outcomes and burdens, direct and surrogate measures, comparators, rival explanations, pass/fail criteria, null or adverse results, and limitations;
- dependence caused by reports from the same study or implementation family and repeated reports of the same artifact lineage or application;
- review-process limitations documented under the [Part 3 extraction-verification procedure](protocol-extraction-and-synthesis.md#sole-reviewer-extraction-and-verification); and
- protocol departures, search changes, and review-process limits that could affect interpretation.

Treat the sole-reviewer and model-assistance items as review-process limitations, not as publication or selective-reporting bias in the primary studies.

Give each conclusion a narrative confidence label: `higher`, `moderate`, `lower`, or `insufficient`. Give a source-locatable reason. Consider:

- the kind and scope of claim being synthesized;
- directness to a qualifying EPS thread;
- fitness of the contributing evaluation designs for the synthesized claim;
- whether measures are direct or are justified surrogates;
- comparator adequacy and major rival explanations when the claim is comparative or causal;
- finding-level evidence basis, support, and applicability;
- the artifact lineage, reuse level, demonstrated coverage, and tailoring effort when relevant;
- maturity, independence, or physical validation only when they bear directly on the claim;
- consistency, including null, adverse, and failed-transfer evidence;
- independence of report families and tailoring applications; and
- limitations in the review process.

Evidence basis and maturity remain descriptive and do not determine confidence by themselves. Never convert a reuse level, coding-confidence value, publication type, or finding-support label automatically into a conclusion-confidence label. Do not use a numerical cutoff or mechanical average.

- **Higher:** several materially independent, directly linked, credible findings or activities support the bounded conclusion, all requirements relevant to that kind of claim are met, and there is no major unexplained disagreement.
- **Moderate:** direct support exists, but there are important limitations in methodology, independence, precision, applicability, or consistency relevant to the conclusion.
- **Lower:** support is sparse, methodologically concerning, indirect, dependent, or importantly inconsistent.
- **Insufficient:** there is no eligible direct evidence for the conclusion.

Use these labels only as the narrative engineering framework defined here, consistently with the [Part 1 reporting framework](protocol.md#reporting-framework).

---

**Previous:** [Part 1 — Scope and definitions](protocol.md)  **Next:** [Part 3 — Extraction and synthesis](protocol-extraction-and-synthesis.md)
