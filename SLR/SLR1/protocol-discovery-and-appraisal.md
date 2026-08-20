# Protocol for a Systematic Review of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Discovery and appraisal

> **Protocol parts:** [1 — Scope and definitions](protocol.md) · **2 — Discovery and appraisal** (this file) · [3 — Extraction and synthesis](protocol-extraction-and-synthesis.md)
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

As a rule specific to this review, count the other 14 bounded and structured collections in the databases/registers column as databases. This rule applies even when a source uses a browser-only workflow or an unusual export format. Do not call any source a study register, and do not count a source in both columns.

Keep separate totals for all 15 sources or collections.

Create the new-run source mapping and schemas under `searches/` as specified under [new-run source translations and search artifacts](#new-run-source-translations-and-search-artifacts).

### Supplementary discovery and citation searching

Also use backward citation searching, forward citation searching in both Scopus and Web of Science Core Collection, and Buruso et al. (2026), *Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review* (https://doi.org/10.1002/sys.70051), as a secondary-review seed and later recall check. Follow the detailed procedure and stopping rule under [completing the baseline and citation searches](#completing-the-baseline-and-citation-searches). Buruso et al. is not primary evidence and cannot insert a report directly into this review.

## Search strategy

### Search streams and set construction

Use two complementary streams because an EPS thread inside a wider spacecraft model may not appear in bibliographic metadata.

- **Stream A — EPS-explicit:** Population × EPS × MBSE/system-model concepts.
- **Stream B — embedded-thread recall:** Population × MBSE/system-model concepts and conservative artifact or tailoring expansions, without requiring an EPS term. Every Stream B candidate must be checked at full text for an eligible EPS thread.

The 11 direct query families are Scopus, Web of Science Core Collection, IEEE Xplore, Engineering Village, Wiley Online Library, Springer Nature Link, Advanced Technologies & Aerospace Index, PQDT Global, OATD, AIAA ARC, and arXiv. Engineering Village covers two databases, Compendex and Inspec. IAF, ESA, and NTRS may use a broader source harvest followed by deterministic local matching when their interfaces cannot represent the direct queries without loss.

Use the following exact cross-source concept blocks. Source-native translations may change syntax, field wrappers, and validated wildcard use, but not the intended terms or Boolean relationships.

#### Population and EPS blocks

- **Population (`P`):** `CubeSat`, `CubeSats`, `cube sat`, `nanosat`, `nanosatellite`, `nanosatellites`, `nano-satellite`, `nano-satellites`, `nano satellite`, and `nano satellites`. A source may use `nanosat*` only after its corresponding `S-D*` or `S-L*` pilot in [`TASKS.md`](TASKS.md) confirms the behavior; otherwise list the finite forms. A named mission can establish population eligibility during screening, but no unspecified mission-name list is part of the direct strategy. Do not use `SmallSat` or “small satellite” as a positive concept.
- **High-specificity EPS (`E_H`):** `electrical power system`, `electric power system`, `electrical power subsystem`, `electric power subsystem`, `EPS`, `power subsystem`, `electrical architecture`, `power architecture`, `PCDU`, and `PMAD`.
- **Functional or analytical EPS (`E_F`):** `power budget`, `energy budget`, `energy balance`, `power generation`, `solar array`, `battery`, `batteries`, `energy storage`, `power conditioning`, `power distribution`, `power management`, `power interface`, `power mode`, `power modes`, and `load profile`.
- **All EPS (`E`):** `E_H ∪ E_F`.

#### MBSE and relationship blocks

- **High-specificity MBSE (`M_H`):** `model-based systems engineering`, `model based systems engineering`, `model-based system engineering`, `model based system engineering`, `MBSE`, `SysML`, `systems modeling language`, `Arcadia`, and `Capella`.
- **Broad structured model (`M_B`):** `system model`, `systems model`, `system modeling`, `systems modeling`, `system modelling`, `systems modelling`, `reference model`, `digital engineering`, and `object-oriented systems model`.
- **All MBSE/system-model terms (`M`):** `M_H ∪ M_B`.
- **Systems-engineering relationship or concern (`R`):** `requirement`, `requirements`, `function`, `functions`, `behavior`, `behaviors`, `behaviour`, `behaviours`, `architecture`, `architectures`, `interface`, `interfaces`, `traceability`, `parametric`, `parametrics`, `verification`, and `validation`.

`M_B` requires `R` in direct B2 queries because its terms are otherwise broad. Stream A does not require `R`: the EPS block supplies the additional precision.

#### Artifact and tailoring blocks

- **Precise reusable model or template (`G_model`):** `generic model`, `generic system model`, `reusable model`, `reusable system model`, `configurable model`, `configurable system model`, `model template`; mission-agnostic, `mission agnostic`, mission-independent, and `mission independent`, each paired with `model` or `architecture`.
- **Structural reusable artifact (`G_structure`):** `reference architecture`, `domain model`, `metamodel`, `meta-model`; product-line, `product line`, product-family, and `product family`, each paired with `model`; and `variation point` paired with `model` or `architecture`.
- **Conservative central asset (`C1`):** `reference model`, `system reference model`, `model library`, `model libraries`, `system model library`, `system model libraries`, `model pattern`, `modeling pattern`, `modelling pattern`, `system model pattern`, `systems model pattern`, `model profile`, `system model profile`, `systems model profile`, and `SysML profile`. Also include every pairing of the four phrases `domain-specific modeling language`, `domain specific modeling language`, `domain-specific modelling language`, and `domain specific modelling language` with one of these nine anchors: the four model-based system(s)-engineering spellings in `M_H`, `MBSE`, `SysML`, `systems modeling language`, `system model`, or `systems model`. Bare `library`, `pattern`, `profile`, or `language` never qualifies.
- **Model-linked tailoring (`T2`):** one of `reuse`, `reuses`, `reused`, `reusable`, `reusing`; `tailor`, `tailors`, `tailored`, `tailoring`; `customize`, `customizes`, `customized`, `customizing`, `customization`; `customise`, `customises`, `customised`, `customising`, `customisation`; `configure`, `configures`, `configured`, `configuring`, `configuration`; `parameterize`, `parameterizes`, `parameterized`, `parameterizing`, `parameterization`; `parameterise`, `parameterises`, `parameterised`, `parameterising`, `parameterisation`; `instantiate`, `instantiates`, `instantiated`, `instantiating`, `instantiation`; `variability`; `variation point`; `specialize`, `specializes`, `specialized`, `specializing`, `specialization`; `specialise`, `specialises`, `specialised`, `specialising`, `specialisation`; or `adapt`, `adapts`, `adapted`, `adapting`, `adaptation`, explicitly paired with `model`, `models`, `architecture`, or `architectures`.

`G_model`, `G_structure`, C1, and T2 are recall concepts, not eligibility tests or evidence of reuse. An `architecture` occurrence inside an artifact phrase cannot also satisfy an independent R tag through the same text span.

#### Outcome and V&V sensitivity blocks

Use the following finite sets consistently in direct sensitivity queries and equivalent local tags:

- **Probe EPS (`E_probe`):** `electrical power system`, `electric power system`, `power subsystem`, `power budget`, `energy budget`, `PCDU`, `PMAD`, and `EPS`.
- **Probe model (`M_probe`):** `model-based systems engineering`, `MBSE`, `SysML`, `system model`, `reference model`, and `digital engineering`.
- **V&V (`V1`):** `verification`, `validation`, `traceability`, `traceable`, `model verification`, `model validation`, `system verification`, `system validation`, `requirements-in-the-loop`, `model checking`, `virtual integration`, `MIL`, `model-in-the-loop`, `SIL`, `software-in-the-loop`, `PIL`, `processor-in-the-loop`, `HIL`, `hardware-in-the-loop`, `test case`, and `test procedure`.
- **Outcome or burden (`O1`):** `reliability`, `reliable`, `mission assurance`, `reproducibility`, `reproducible`, `reuse`, `reusable`, `integrability`, `integrable`, `interoperability`, `interoperable`, `traceability`, `traceable`, `benefit`, `benefits`, `impact`, `outcome`, `no effect`, `adverse`, `burden`, `effort`, `workload`, `overhead`, `cost`, `schedule`, `training`, `learning curve`, `licensing`, `license`, `licence`, and `adoption`.

V1 and O1 are mandatory sensitivity partitions, but their terms are not eligibility requirements and are not added to every query.

#### Direct query schedule

Execute these 11 semantic partitions in every direct query family unless a newly documented source limitation makes an exact translation impossible. A source-specific failure does not authorize an unrecorded narrower query.

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
| `V1` | `P AND E_probe AND M_probe AND V1` | V&V sensitivity query |
| `O1` | `P AND E_probe AND M_probe AND O1` | Outcome and burden sensitivity query |

Therefore:

- `Stream A = A1 ∪ A2 ∪ A3`;
- `core Stream B = B1 ∪ B2`; and
- `expanded Stream B = BG1 ∪ BG2 ∪ BC1 ∪ BT2`.

Retain and screen every record returned by any planned partition, including V1 and O1, while preserving each discovery event. Report intersections and records unique to each stream and expansion after within-source and cross-source deduplication.

For a local-harvest source, the minimum equivalent candidate logic is `P AND M` for core B, `P AND E AND M` for the Stream A tag, and separate `P AND G_model`, `P AND G_structure`, and `P AND C1` expansions. Apply T2, V1, O1, and independent R as separate tags. Terms may combine only within the source fields or document route prospectively defined for that local method. Local matching generates candidates; it does not establish scientific eligibility.

### New-run source translations and search artifacts

No source-specific query, adapter assumption, search log, concept dictionary, source crosswalk, manifest schema, or failure schema from an earlier attempt governs this run. Before the first related pilot, create the following anew from this protocol and give each artifact new-run provenance:

- `search-log.md`;
- the source/interface/PRISMA crosswalk;
- the final-run manifest schema; and
- the failure-register schema.

The protocol's concept blocks and Boolean schedule are normative. The new dictionary must reproduce them without adding or dropping a concept. Source-specific translations and controls must be regenerated and validated against the current interfaces rather than restored from Git history. **Task:** [`S-001`](TASKS.md).

For each source or local method, the new log must record before final execution:

- source, database or collection, platform, and interface;
- query or event IDs and the exact source-native translation of every planned partition;
- fields, filters, limits, date and language handling, and visible controls;
- stemming, lemmatization, automatic expansion, and wildcard behavior;
- source boundaries and selected databases;
- pagination, result ordering, stable identifiers, export or capture method, and source limits;
- the relationship between source-native queries and the cross-source semantic blocks;
- pilot refinements, failures, and the accepted final implementation; and
- the files and schemas that will preserve the final event.

A syntax or transport change that preserves the semantic blocks is an implementation refinement and belongs in the search log. A change to a concept, Boolean relationship, planned source, evidence window, or eligibility rule is a protocol change and must be committed before the affected final search is run.

### Source-specific guidelines

Source-specific guidelines are intentionally pending regeneration. Run the direct-source tasks `S-D01`–`S-D11` and local-source tasks `S-L01`–`S-L03` in [`TASKS.md`](TASKS.md). For each accepted method, add here the validated source boundary, translation approach, fields and controls, date and language handling, completeness and export method, limits, and failure rules. Keep exact run-specific strings and pilot evidence in the new search log. After all source tasks, complete reconciliation task [`S-002`](TASKS.md).

### Pilots and final search events

Run small, focused, no-screening pilots to validate each current interface and translation under tasks `S-D01`–`S-D11` and `S-L01`–`S-L03` in [`TASKS.md`](TASKS.md). Pilot records, identifiers, totals, and files are diagnostic only and can never become candidates or final discovery events. Keep pilot storage separate from clean final-run storage.

For every pilot and final event, record:

- exact query or matching operation and fields;
- controls and restrictions;
- platform, interface, date, time, and time zone;
- source-reported and retrieved totals;
- pagination or harvest coverage;
- refinements and failures;
- deduplication and coverage checks; and
- disposition and reason for stopping.

Use the source's normal authorized interface or a prospectively validated source-native route. Save proof of the selected source and controls. Retrieve every record in a successful result set. Where the source exposes a stable order, require two complete passes with the same identifiers in the same order. Otherwise define and validate an equivalent completeness check before final execution.

A rewritten query, stale or short page, changed or unreconciled total, duplicate or missing identifier, hidden cap, export mismatch, parse failure, or incomplete harvest makes the event a failure. Record its total as `null`, never zero or a partial count, and do not import any prefix. An explicit and reproducible source zero is valid. Access challenges must be handled through the normal interface without bypassing them; unresolved access is a recorded source failure.

Keep duplicate discovery events when the same record is found by different sources or partitions. Deduplicate only after every successful event has been completely retrieved and normalized.

### Known items and common limits

Create the read-only known-item registers under task [`R-001`](TASKS.md). A missed item may guide prospective query refinement, but it can enter the review only through a recorded final search or citation-search event and normal screening. Report known-item recall and unique inclusions by stream and source.

The evidence window begins on 2011-01-01 and ends on the common evidence cutoff stated in [Part 1](protocol.md). Set that exact cutoff under task [`P-001`](TASKS.md) before the first final search. Use it unchanged for every source and citation route, even when execution occurs later. When an interface cannot apply the exact window, preserve its unaltered total, apply the window locally, and report removed and unresolved records.

The full report must be in English. Apply a native English limit only after the new-run source validation shows that it is reliable; otherwise determine language during screening. Do not apply a publication-type, access, peer-review, venue, or content-type discovery limit unless a source boundary inherently supplies it or a newly logged source limitation requires it. Source scope does not by itself prove final publication type or report language.

### Local-harvest methods

Regenerate the IAF, ESA, and NTRS methods from the current interfaces under tasks [`S-L01`](TASKS.md), `S-L02`, and `S-L03`. A local method may use a complete population or source harvest followed by deterministic matching when direct Boolean translation would lose records. Before final execution, its new-run specification must define:

- the source universe and how completeness is established;
- metadata, text, or attachment fields included in each matching route;
- normalization, phrase, wildcard, acronym-boundary, and field-combination rules;
- exact implementation of P, E, M, `G_model`, `G_structure`, C1, R, T2, V1, and O1;
- candidate partitions, tags, invariants, and overlap accounting; and
- treatment of inaccessible, missing, or unparseable material.

Do not combine required terms across records or across independently defined routes. A failed retrieval or parse is a coverage failure, not a zero. No result, matrix, dictionary, or local classification from an earlier attempt is part of this run.

### Completing the baseline and citation searches

Execute and reconcile the electronic baseline under task [`R-002`](TASKS.md) and the recall and citation cycles under [`R-003`](TASKS.md). The independent baseline is complete only after all 15 planned sources or collections have either a complete, reconciled final run or a recorded final source or interface failure. Merge records only from complete successful events. Preserve separate Compendex and Inspec discovery instances and separate events for the two ProQuest sources. Keep every failure and reason in the new manifest and PRISMA counts.

Only after that baseline and failure register are complete, use Buruso et al. (2026) and the retained-file cache for recall audits. A missed report may trigger a prospective concept-level refinement or enter through a recorded citation route; never add it directly.

Start backward and forward citation searching from every included full-text report and relevant secondary review:

- inspect each seed's complete reference list;
- search forward citations in both Scopus and Web of Science Core Collection;
- do not waive one forward source because the other returns zero or lacks the seed;
- add each newly included report as a seed in the next numbered cycle; and
- stop only after one complete cycle of backward searching and both forward searches finds no new eligible report.

For every citation event, record the seed, platform, direction, exact route, cycle, source and retrieved totals, candidates, duplicates, decisions, failures, and stopping result. Use `discovery_route=citation_chasing`; citation provenance never bypasses screening.

Stop electronic searching only when A1, A2, A3, B1, B2, BG1, BG2, BC1, BT2, V1, and O1 have completed or failed explicitly for every direct family, and every prospectively specified local equivalent has completed or failed without a partial import. Also complete all source coverage checks and citation cycles. Record the execution date of every strategy. Additional searches should by then yield mainly duplicates rather than being stopped merely because they are inconvenient.

## Data management and audit trail

Keep review methods, logs, controlled dictionaries, derived data, and analysis code in the Git-tracked `SLR/SLR1/` workspace. List every file in a manifest with:

- path;
- query or event ID;
- source;
- timestamp

Record the database interface actually used.

Use UTF-8 JSON for derived machine-readable data. Use BibTeX for bibliographic transfer when available. Before every merge or synthesis, validate schemas, IDs, controlled values, and links between records.

Make deduplication reproducible. Review conflicts manually when identifiers disagree. Keep both the original metadata and the preferred normalized value, with the reason for choosing it.

Use Git history as the audit trail for text, code, schemas, and derived non-sensitive data.

## Inclusion and exclusion criteria

| Criterion | Plain-English rule | RQ(s) |
|---|---|---|
| Publication date | Include a report whose first formal publication or issue date is from 2011-01-01 through the common evidence cutoff in Part 1. Treat online-first and issue versions as one work. For a degree work, use the earliest date that can be verified as formal issue or publication of the completed thesis or dissertation, and keep the source's date label. Record defence, award, approval, repository deposit, public release, embargo end, and indexing dates separately. Do not silently substitute one of them for the publication date. | 1–3 |
| Language | The full report must be in English. English metadata does not prove that the report itself is in English. If the full text cannot be obtained, use `not_retrieved` instead of making a language assumption. | 1–3 |
| Publication type | Include a full primary-research journal article; conference, proceedings, or workshop paper; research chapter in an edited scholarly book; institutional technical report; completed master's thesis; or completed doctoral thesis or dissertation. A degree work needs stable institutional or authoritative dissertation-service provenance and substantial methods and results. Empirical comparisons and experience reports may qualify. Record degree acceptance or examination separately from peer or technical review; do not infer one from the other. | 1–3 |
| Population | The work must concern an actual or planned orbital CubeSat or nanosatellite-class mission, or a model tailored to that class. A generic SmallSat label is not enough. A mixed-platform report needs evidence that can be separated for CubeSats or nanosatellites. | 1–3 |
| MBSE threshold | The work must meet the [structured-system-model definition](protocol.md#mbse-qualification). | 1–3 |
| EPS threshold | At full text, the work must meet Route A or Route B. | 1–3 |
| Mixed system scope | Include only if an EPS thread can be extracted separately. Describe other subsystems only as EPS dependencies or interfaces. | 1–3 |
| Secondary studies | Exclude secondary studies, including Buruso et al. (2026), from primary evidence. Keep them separately for background, terminology, later recall checks, and citation searching. | 1–3 |
| Non-MBSE EPS studies | Exclude stand-alone component, circuit, control, optimization, sizing, simulation, or hardware-performance studies unless they have an explicit link to a structured system model. | 1–3 |
| Generic whole-spacecraft MBSE | Exclude a report without a qualifying EPS thread, even if it mentions an EPS or power budget. | 1–3 |
| Other-subsystem studies | Exclude unless they contain a qualifying EPS thread. A subsystem's power consumption alone is not enough. | 1–3 |
| Abstract-only or non-research material | Exclude posters or abstracts without full papers; thesis or dissertation metadata and abstract stubs without the completed substantial report; proposals and prospectuses; incomplete degree work; undergraduate, bachelor's, or non-degree projects; presentation- or slide-only records; recordings; editorials; tutorials; advertisements; patents; and non-scholarly web material. | 1–3 |
| Retrieval status | Scientific eligibility does not depend on open access. If the report is not obtained after the required retrieval attempts, including a restricted or embargoed thesis, record `not_retrieved`. Do not silently exclude it for scientific reasons. | 1–3 |

Do not make an outcome, V&V activity, reuse, genericity claim, or demonstrated tailoring a report-level inclusion test. Every eligible thread contributes to RQ1 and receives a disposition; create direct RQ2 and RQ3 records only when the relevant definitions are met. These later contribution codes cannot make an ineligible report eligible.

For retrieval, follow the run's PDF workflow:

1. try DOI and open-access routes, PQDT or OATD links, publisher pages, and authoritative institutional repositories;
2. when needed, make one recorded institutional, library, or manual-download attempt; and
3. record entitlement, repository link, embargo, licence, version, and broken-link status.

An OATD record does not prove that the linked full text is still available. Keep unresolved reports in PRISMA and retrieval records as `not_retrieved`. They do not enter full-text evidence synthesis, but do not describe lack of access as a scientific exclusion reason.

## Screening and eligibility procedure

Execute retrieval and screening under task [`R-004`](TASKS.md).

### Title and abstract screening

Use these tiers to set retrieval priority. They are not final evidence classes.

- **Core candidate:** the title or abstract clearly suggests EPS-primary MBSE or a likely embedded EPS thread.
- **Supporting candidate:** the record appears to meet the nanosatellite and possible MBSE rules, but the abstract cannot confirm an embedded EPS thread.
- **Rejected candidate:** the record clearly has the wrong population or publication type, is outside MBSE scope, or explicitly mentions EPS but clearly has no qualifying model link.

Do not require an EPS or power term in a Stream B title or abstract. Embedded threads may be absent from metadata. If nanosatellite MBSE is plausible, retrieve the full text and resolve uncertainty there. Test the EPS anchor and bridge at full text.

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
- `exclude_insufficient_primary_report`; or
- `not_retrieved`.

When using `exclude_wrong_publication_type`, also record one subtype:

- `undergraduate_or_bachelor`;
- `non_degree_project`;
- `proposal_or_prospectus`;
- `incomplete_degree_work`;
- `abstract_or_metadata_stub`; or
- `other`, with an explanation.

If completion status is unresolved, hold the record as `publication_type_unresolved` while looking for source-locatable clarification. If a record in the cutoff year gives only a year, or thesis dates conflict, hold it as `date_unresolved`. Do not silently turn either temporary status into an exclusion.

If a plausible completed report is unavailable because of access rights, an embargo, or a broken repository link, use `not_retrieved`. Do not call it the wrong publication type because it is unavailable.

For every Route B inclusion, record the EPS anchor, model anchor, explicit bridge, and supporting location. Check these details again during extraction.

Keep secondary reviews and general MBSE background sources outside the analytic denominator.

## Units and identifiers

Use the canonical [units, counting rules, and ID structure](protocol.md#units-of-evidence-and-counting). During discovery and screening, preserve record-to-report identity, all discovery events, report-family evidence, and artifact-lineage evidence without moving facts between linked units. PRISMA flow counts remain at record and report level.

## Quality checklist

Score each applicable item as follows:

- **No = 0**
- **Insufficiently = 0.5**
- **Yes = 1**
- **Not applicable:** remove the item from that score's denominator

Use quality scores to give context and for sensitivity views. Do not use them as automatic exclusion thresholds. A score cannot make an ineligible report, genericity profile, outcome or burden record, or V&V record eligible.

Do not include the A/E/C/T/P/I genericity profile or its `NA` and `G0`–`G4` tiers in this numerical checklist. Never average a genericity tier with a quality score.

### Report and EPS-thread quality

1. Is this primary research from a credible scholarly venue, an identifiable institutional technical-report series, or a completed degree from an identifiable degree-granting institution or authoritative dissertation service? Can the reviewer verify report type, provenance, completion, and any stated peer review, technical review, or degree examination?
2. Does the report describe the CubeSat or nanosatellite mission setting and lifecycle stage clearly enough to judge where the evidence applies?
3. Does it describe the MBSE method, model boundary, language and tools, artifacts, and modeled relationships clearly enough to confirm that it qualifies as MBSE?
4. Does it report the EPS anchor, model anchor, explicit bridge, and EPS boundary clearly enough to reconstruct the thread?
5. Does it state the model's purpose, decisions, intended users or roles, and lifecycle use?
6. Does it report important inputs and assumptions in enough detail, including values or ranges, units or time basis, source, uncertainty or margin, and reason?
7. Does it report model, tool, and data availability, configurations, interfaces, and reusable assets well enough to judge reproducibility?
8. Do the authors discuss limits, scope, uncertainty, threats to validity, or other explanations?

### RQ1 genericity-evidence audit, when applicable

Apply the [A/E/C/T/P/I gates and tier rules](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring) without a numerical score. Record a source location, status, reason, and confidence for every gate. Audit artifact and version identity, application identity, the separation of the declared envelope from demonstrated coverage, post-tailoring assurance, adopter independence, and failed or conflicting applications. Do not move evidence across uncertain lineages or applications or interpret a tier as general model quality.

### RQ2 outcome/burden quality, when applicable

9. Does the source explicitly link the outcome or implementation burden to a qualifying EPS thread and a stated MBSE mechanism, rather than to an EPS technology choice or MBSE in general?
10. Does a suitable metric, traceable case result, comparison, stakeholder assessment, reuse result, integration or test result, operational result, or other evidence support the stated direction or burden?

### RQ3 V&V quality, when applicable

11. Does the source clearly report the EPS target, linkage scope, model-to-V&V bridge, original terminology, normalized V&V object, method or artifact, criterion, lifecycle timing, and execution status?
12. If execution or closure is claimed, does the source give the result or verdict and evidence of any later software, hardware, integration, test, operational, or flight link?

Score items 1–3 and 8 at report level. Score items 4–7 for each EPS thread, items 9–10 for each direct RQ2 outcome or burden record, and items 11–12 for each EPS-linked RQ3 record.

Report the genericity audit separately at artifact-lineage/profile and tailoring-application level, without a numeric total. Any checklist total is descriptive and must state both its unit and applicable-item denominator. Keep confidence in linkage, lineage, and tiers separate from quality scores.

### Appraisal meaning, reporting-bias assessment, and conclusion confidence

This checklist measures reporting completeness, direct linkage to EPS, and strength of support across varied engineering evidence. It is not a validated clinical risk-of-bias tool. Report checklist areas and record-level evidence confidence at their actual units. Do not reduce them to an unexplained “study quality” label.

Do not make a funnel plot or run a statistical publication-bias test. The evidence does not share one effect measure and is too varied. Instead, assess and report the following for each research-question synthesis:

- source and interface coverage, failures, and unique results across the 15 sources, 13 interfaces, and citation routes, with OATD in the website/other-methods channel;
- the effects of language, date, population, publication-type, retrieval, and source-access limits;
- specific access and coverage issues, including PQDT entitlement, OATD's repository and participation limits, geographic and institutional imbalance, embargoes, missing abstracts or metadata, uncertainty about degree status, and overlap between PQDT and OATD;
- reports that could not be obtained and records that were only leads;
- missing or selectively reported genericity claims, applicability limits, tailoring failures and burdens, outcomes and burdens, criteria, results, and limitations;
- dependence caused by reports from the same study or implementation family and repeated reports of the same artifact lineage or application; and
- protocol departures, search changes, and review-process limits that could affect interpretation.

Give each conclusion a narrative confidence label: `higher`, `moderate`, `lower`, or `insufficient`. Give a source-locatable reason. Consider:

- directness to a qualifying EPS thread;
- report and record quality;
- the genericity profile and tier when relevant;
- evidence type and comparator;
- maturity and independent or physical validation;
- consistency, including null, adverse, and failed-transfer evidence;
- independence of report families and tailoring applications; and
- limitations in the review process.

Never convert a genericity tier automatically into a conclusion-confidence label. Do not use a numerical cutoff or mechanical average.

- **Higher:** several materially independent, directly linked, well-supported records and no major unexplained disagreement.
- **Moderate:** directly supporting evidence exists, but independence, maturity, or comparisons are limited.
- **Lower:** support is sparse, weak, indirect, dependent, or importantly inconsistent.
- **Insufficient:** there is no eligible direct evidence for the conclusion.

These labels form an engineering-review framework. They are not GRADE.

---

**Previous:** [Part 1 — Scope and definitions](protocol.md)  **Next:** [Part 3 — Extraction and synthesis](protocol-extraction-and-synthesis.md)
