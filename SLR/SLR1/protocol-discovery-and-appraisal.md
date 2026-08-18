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

Keep separate totals for all 15 sources or collections. For Engineering Village, also keep the combined total and separate Compendex and Inspec totals. For each of the two ProQuest sources, keep separate proof of the selected database, search event, count, export, and provenance.

The final-run files under `searches/` define the current machine-readable source mapping and the rules for null totals, zero totals, and failures. They also contain the manifest and failure-register schemas. Validate these files structurally.

### Supplementary discovery and citation searching

Also use:

- backward citation searching of the full reference lists of every included report and relevant secondary review;
- forward citation searching of those reports in both Scopus and Web of Science Core Collection; and
- Buruso et al. (2026), *Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review* (https://doi.org/10.1002/sys.70051), as a named secondary-review seed and a recall check to be used later.

Do not treat Buruso et al. (2026) as primary evidence. A report cited by that review can enter this review only if a planned source search or a recorded citation search finds it and it then passes normal screening. Report separately:

- overlap with Buruso et al.;
- rediscovery by each source;
- reports found through citation searching; and
- reasons for excluding reports that looked relevant.

## Search strategy

### Search streams

Use two search streams. This is necessary because an EPS thread inside a wider spacecraft model may not appear in the title or abstract.

- **Stream A — EPS-explicit:** combine the Population, EPS, and MBSE/system-model concepts. This stream finds reports focused on EPS and embedded threads that explicitly mention EPS. In the 11 direct query families, implement Stream A as `A1 ∪ A2 ∪ A3`. A3 restores precise combinations of EPS terms with broad model terms. In IAF, ESA, and NTRS, use the equivalent local tag `P AND E AND M`.
- **Stream B — embedded-thread recall:** combine the Population concept with precise MBSE or structured-model terms. Also search for precise reusable artifacts, conservative central model assets, and model-linked tailoring terms. Do not require an EPS term. Check the full text for an eligible EPS thread. Report records found only by Stream B separately. The current design uses core B and separate `B-G`, `B-C1`, and, where core B does not already contain it, `B-T2` partitions.

There are 11 direct source/query families. They cover 12 databases or collections because the Engineering Village family searches Compendex and Inspec together. For these families, **core B is the union `B1 ∪ B2`**:

- **B1** combines Population with precise MBSE terms.
- **B2** combines Population and broader structured-model terms with the required systems-engineering relationship or concern block, called R. The R block controls the otherwise broad model terms.

PQDT and OATD use the same 11 semantic partitions. Do not add thesis or dissertation terms because those sources already contain only degree works. IAF, ESA, and NTRS use a local core-B rule, `P AND M`, within one route or record. An optional R tag can be kept for exact G or C1 artifact matches. This does not make R optional in bibliographic B2 searches.

### Search concept blocks

Adapt these blocks to each source's syntax and searchable fields:

1. **Population (`P`):** CubeSat, CubeSats, `cube sat`, nanosat, nanosatellite, nanosatellites, singular and plural forms of hyphenated or spaced `nano satellite`, or a clearly named nanosatellite-class mission. Do not use generic `SmallSat` or “small satellite” as a positive search concept. Those terms are also not enough to prove eligibility.
2. **EPS (`E`):** electrical or electric power system or subsystem; EPS; power subsystem; electrical or power architecture; power or energy budget; energy balance; battery, batteries, or storage; solar array or power generation; power conditioning, distribution, management, or interface; power mode or modes; load profile; PCDU; or PMAD.
3. **MBSE/system model (`M`):** singular and plural forms of model-based system or systems engineering; MBSE; SysML or systems modeling language; US and UK forms of system or systems modeling/modelling; reference systems model; object-oriented systems model; digital engineering; Arcadia; Capella; or another structured-system-model term that has been validated.
4. **Precise reusable artifact (`G`):** exact phrases for a complete generic, reusable, or configurable model or system model; model template; mission-agnostic or mission-independent model or architecture; reference architecture; domain model; metamodel or meta-model; product-line or product-family model; or a variation point linked to a model or architecture. Prefer `P AND G` without the R block. These exact phrases already limit the search. Requiring R can wrongly let the word `architecture` satisfy its own relationship test and can miss records whose metadata omit relationship words.
5. **Conservative central asset (`C1`):** phrases for a reference model, system-reference model, model library, model pattern, model profile, or SysML profile. Include a domain-specific modeling/modelling-language phrase only when it is linked to an MBSE or system-model anchor. Never search for bare `library`, `pattern`, `profile`, or language terms in this block.
6. **Model-linked tailoring (`T2`):** use a B2 structured-model block together with explicit terms for reuse, tailoring, customization, configuration, parameterization, instantiation, variability or variation points, specialization, or adaptation. These terms must be linked to a model or architecture. Use source-supported wildcards or list the finite word forms.

Use `B-G`, `B-C1`, and `B-T2` to generate candidates only when two conditions hold: the source's core B does not already contain that partition, and completed no-screening pilots support possible unique results or preserve that possibility in advance. These partitions do not require EPS terms and never replace core B.

For G and C1 records, R may be kept as an optional precision and provenance tag. A term such as *reference architecture* cannot satisfy R through the same overlapping word *architecture*. Search terminology about genericity or tailoring is not an eligibility requirement and is not part of the genericity grade. Finding a record through an expansion does not show that its artifact is reusable.

Targeted sensitivity searches for RQ2 and RQ3 may add terms for:

- benefits;
- null or adverse outcomes;
- burden, effort, cost, or training;
- traceability;
- verification, validation, or V&V of models, systems, or designs;
- simulation or model checking;
- requirements-in-the-loop; and
- MIL, SIL, PIL, HIL, or testing.

Every direct `V1` or `O1` query, and every local IAF, ESA, or NTRS tag, must use the same exact finite term sets defined in the query plan and dictionary. Do not assume that a wildcard or automatic expansion on one source is equivalent. These terms do not have to appear in every query because that would miss RQ1 reports and embedded EPS threads.

The old T1 probe was fully contained in core B and added no identifiers. The newer `T2` design replaces the bibliographic B2 relationship gate with a narrow tailoring block tied to a model or architecture. It found additional opaque identifiers in Scopus and IEEE. Therefore, the T1 result is not a reason to omit T2.

### Pilots, logs, and final search rules

Run searches in small, focused pilot sets before the final searches. For each relevant event, the new search log must record:

- the exact search string and fields;
- filters and visible controls;
- platform and interface;
- date, time, and time zone;
- the total shown by the source and the number retrieved;
- pagination or event-harvest coverage;
- whether stemming, lemmatization, or term expansion was on, off, or unavailable;
- refinements;
- failed or overly broad searches;
- deduplication;
- coverage checks; and
- the reason for stopping.

Changing source syntax or improving precision within the concept streams above is search implementation, not an eligibility change. Record each dated refinement and the final query set in the log. Do not assign document version numbers for these refinements.

Run every final query through the source's normal browser interface. Use the source-native strings and visible settings in [`query-search-plan.md`](query-search-plan.md). Save proof of the interface and selected source or database. Match a stable source total to complete pagination and source identifiers. When the source provides an ordered list of records, make two passes and require the same identifiers in the same order.

Treat any of the following as a failed event: a rewritten query, a stale or short page, a changed total, duplicate or missing identifiers, an export mismatch, or a timeout. Give a failed event a total of `null`, not zero and not a partial count. Never import part of a failed result set.

Keep the same record as a separate discovery event when more than one source finds it. Deduplicate only after every successful source event has been fully retrieved and normalized.

### Required controls for individual sources

#### Engineering Village: Compendex and Inspec

- Run every `C-*` query once as a paired Compendex-and-Inspec event. Clear All and Knovel.
- Use `KY` concept fields.
- Set Published to 2011–Latest and also use the literal year and English clauses.
- Turn autostemming off. Sort by Relevance.
- Use a fixed visible page size of 25.
- Do not use a discovery document-type filter.
- Turn source-side duplicate removal off.

The page size controls only transport through the results; it does not change what the search means. Save proof of the exact controls and query. Require a stable total and complete pagination. Every page except the last must show exactly 25 rows, and the final page must match the expected remainder.

Make two identical, ordered, value-blind passes that record `(database label, source handle)` for every row. Reconcile the complete native RIS export with the complete paired ledger before normalization and merging.

Keep:

- the combined total;
- separate Compendex and Inspec totals;
- the database label for each row;
- the overall rank; and
- both database instances through later deduplication.

A Compendex-only or Inspec-only troubleshooting search cannot replace the paired final event. Do not accept or import any failed or partial prefix.

#### Wiley Online Library

- Search the full platform with the documented Anywhere/`AllField` expressions.
- Use the 20-record Articles & Chapters result pages.
- Run and log the separate Collections coverage route.
- Do not apply a venue, content-type, access, or language discovery filter that the interface does not support.

Keep the source total and apply the exact-day cutoff. Save the ordered DOI ledger and page-level native RIS files with abstracts. Preserve provenance when merging the normalized files.

#### Springer Nature Link

- Search the full Link platform with unrestricted Keywords.
- Select English.
- Set custom dates from 2011 through 2026, then apply the common 2026-08-10 cutoff.
- Sort by Relevance and use 20 records per page.
- Do not filter by content type, brand, discipline, venue, or access.

Twice reconcile the full ordered ledger of DOIs or canonical URLs. If an authorized account is available and the result is within the source's 1,000-record limit, use and save the normal native CSV export. Otherwise, retrieve all normal result pages. If a final result would exceed a source limit, divide it in advance into non-overlapping date ranges.

#### Advanced Technologies & Aerospace Index on ProQuest

- Select only the exact **Advanced Technologies & Aerospace Index**.
- Use the documented `NOFT` expressions with year and English clauses.
- Sort by Relevance and use 20 records per page.
- Record the final state of spelling and word-form expansion.
- Do not use a full-text, peer-review, source-type, or document-type limit.
- Turn source duplicate exclusion off.

Save proof of the selected database and complete ledgers of page, rank, and source ID. Test a normal native RIS export first and then use batches where available. Keep source provenance after normalization. Never replace this index with its broader parent collection or a sibling database.

#### ProQuest Dissertations & Theses Global

Use a separate ProQuest event from the aerospace index.

- Select only the exact **PQDT Global** database.
- Run all 11 `PQDT-*` translations.
- Use the same `NOFT`, year, English, no-type-limit, no-access-limit, source-deduplication-off, and Relevance rules.

Do not copy page-size, result-limit, database-selection, or export assumptions from the aerospace adapter. First run a PQDT-specific live check. Save proof of the exact selected database before every query.

Reconcile all ranks and source IDs in two passes. Test native RIS first, then export safe batches. Preserve degree and source metadata and a stable record URL that does not depend on the session.

If a challenge or login page appears, wait, focus the normal browser page, and retry as specified in the query plan. If access rights remain unresolved, database selection is unclear, or a result cap cannot be verified, mark the source as failed with total `null`.

#### Open Access Theses and Dissertations

- Search the complete native OATD index.
- Run all 11 finite `OATD-*` semantic translations through the validated basic `q` syntax.
- Recheck at execution that the defaults are Relevance and 30 records per page.
- Do not apply a native date, language, institution, degree, Creative Commons, or extra access limit.
- Apply the date range from 2011-01-01 through 2026-08-10 and the English rule locally.

Year or language controls in a composer may replace local handling only after a separately recorded test shows equivalent result sets and adequate metadata quality.

Save the exact URL and query echo, source total, sort order, page size, and full stable record-ID or canonical-URL ledger. Make two ordered passes when the interface exposes an order. Keep the linked repository as provenance.

If a challenge, busy page, or access message appears, follow the wait, focus, and retry rule. A hidden result cap, incomplete pages, missing stable identity, or unresolved interface or rights problem makes the total `null`. A repository linked by OATD is a route for obtaining the report; it cannot silently become a new discovery source.

#### AIAA Aerospace Research Central

- Search all content across the source with Anywhere/`AllField` and `access=on`.
- Use January 2011 through August 2026, then apply the common 2026-08-10 cutoff.
- Sort by Relevance and use fixed pages of 20 records.
- Do not apply a language, publication-type, venue, topic, or open-access discovery filter.

Keep the month-based source total. Make two complete DOI pagination passes. For each visible record, use Tools → Download citation to save its RIS exactly as received. Reconcile every RIS record to its DOI.

If a challenge appears, follow the wait, focus, and retry rule. If a row has no DOI, or the interface has changed, stop the run and set the total to `null` until a documented source-native fallback is available. Do not discard the row or replace ARC with another index.

#### arXiv

Search the full repository through Advanced Search. Use All fields and every direct query partition. Do not limit by subject category.

Save complete pagination by canonical arXiv ID, available abstracts, and submission and version details. During screening, apply the English rule, eligible publication-type rule, and common first-formal-publication-date rule. Do not treat an arXiv submission date as a formal publication date.

#### IAF Digital Library

Run the complete Population query across the whole Digital Library. Do not restrict by event code, conference series, or venue. Retrieve the complete public result set and title and abstract metadata from each landing page. Reconcile the results twice.

Apply deterministic local classification for P, M, G, C1, E, R, T2, V1, and O1. Keep event metadata only as record provenance, not as the boundary of the search.

Use only public, browser-visible result and landing pages. Do not use manuscript, full-text, or authenticated routes. Keep leads that have no abstract. Apply the common 2026-08-10 first-formal-publication cutoff during screening.

### Known items, limits, and date handling

Reports known before the search may be listed in a read-only known-item register. A missed item may guide query refinement. It can enter the review only when a recorded search or citation search finds it and it passes new screening. Report known-item recall and the number of unique inclusions from each stream and source.

Do not use a publication-type or content-type discovery filter in a query-based source unless the final log records a source-required change before the final run. PQDT and OATD are already limited by their source scope to degree works. Confirm completed degree or report type during screening.

Apply an English filter during searching in:

- Scopus;
- Web of Science Core Collection;
- IEEE Xplore;
- paired Engineering Village;
- Springer Nature Link;
- Advanced Technologies & Aerospace Index; and
- PQDT Global,

but only where the planned interface provides a reliable control. Check language during screening for Wiley, OATD, AIAA ARC, IAF, arXiv, ESA, and NTRS because no reliable discovery control was validated there.

Use the same evidence cutoff, 2026-08-10, for every source and citation route. Some source controls admit later records. These include Scopus, IEEE, paired Engineering Village, Wiley, Springer, both ProQuest events, AIAA ARC, and IAF. Keep each source's original total unchanged, then apply and log the first-formal-publication-date cutoff. Record how many records were removed and how many remained unresolved. OATD has no native date limit, so apply the full date window locally and keep the same exact-day accounting.

### ESA Indico and NTRS local processing

For **ESA Indico**, first list all event and contribution material through the common cutoff. Do this before deciding which records are candidates. Then take the union of:

- deterministic core `P × M` matches; and
- complete, relationship-free `P × G/C1` artifact matches.

Apply these rules separately to joined metadata and to each attachment whose text can be extracted. Keep R, T2, V1, and O1 as separate tags. Material that cannot be accessed or parsed is a coverage failure. Do not combine one required term from metadata with another from an attachment.

For **NTRS**, the final run completed on 2026-08-13 and covered 940 separate cells:

- 10 Population terms × 18 core model terms;
- the same 10 Population terms × 25 exact G terms; and
- the same 10 Population terms × 51 exact C1 atoms.

The C1 set includes every combination of four language spellings and nine model anchors. After deduplicating the union of core B, B-G, and B-C1, the run applied the full deterministic E and T dictionaries and the exact finite V1 and O1 sets.

Across cells, 40 source records reduced to a six-record union:

- core = 6;
- G = 1;
- C1 = 0;
- core ∩ G = 1;
- core-only = 5; and
- expansion-only = 0.

The local tags were:

- full-E core = 1;
- expansion-E = 0;
- T2 = 0;
- V1 = 3; and
- O1 = 5.

Stream A is the E-explicit subset of NTRS core B. It is already contained in that core, so `A-only = 0`. The protected final artifacts and full execution details are in [`query-search-plan.md`](query-search-plan.md) and [`search-log.md`](search-log.md). When ESA is run, use the same local-tag reporting rules.

### Completing the baseline and citation searches

The independent baseline is complete only after all 15 operational sources or collections have either:

- a complete and reconciled final run; or
- a clearly recorded final source or interface failure.

Merge results only from complete successful sources. For each successful paired Engineering Village event, keep the separate Compendex and Inspec discovery instances. Keep every failed-source status and reason in the manifest and PRISMA-S/PRISMA counts. Never import the partial beginning of a failed result set.

Use Buruso et al. (2026) and the retained-file cache for recall audits only after the successful-source baseline and the failed-source register are complete. A missed report cited by Buruso et al. may trigger a recorded concept-level probe or enter through a recorded citation-search route. Never add it directly.

Start backward and forward citation searching from every included full-text report and every relevant secondary review:

- For backward searching, inspect the complete reference list.
- For forward searching, search both Scopus and Web of Science Core Collection.
- A zero result or indexing failure in one forward-citation source does not remove the need to search the other.
- If a newly found report is eligible, include it as a seed in the next numbered cycle.
- Stop only when one complete cycle of backward searching and both forward searches finds no new eligible report.

For every citation-search event, record the seed, platform, direction, exact route, cycle, source total, retrieved total, candidates, duplicates, decisions, failures, and stopping result. Give these records `discovery_route=citation_chasing`, separate from their bibliographic source. They must still pass normal eligibility screening.

Stop searching only when every planned version of both streams has either completed at every planned source or failed explicitly without a partial import. This includes:

- all direct-source A1, A2, and A3 queries;
- every core, B-G, B-C1, and applicable B-T2 partition;
- every required local V1 and O1 tag; and
- the full-database IAF route.

Also require every source-specific coverage check and planned concept cluster to complete or fail explicitly. Test relevant report families and artifact lineages found during the new run. Complete citation searching. Additional searches should by then produce mostly duplicates, not merely have become inconvenient or narrow. Report the execution date for every source and strategy. The evidence window always ends on 2026-08-10.

## Data management and audit trail

Keep review methods, logs, controlled dictionaries, derived data, and analysis code in the Git-tracked `SLR/SLR1/` workspace. Where licences allow, keep raw source files read-only. List every file in a manifest with:

- path;
- query or event ID;
- source;
- timestamp;
- byte size;
- access or rights status; and
- software that created it.

Record the database interface and software versions actually used. Do not assume that the draft environment stayed unchanged.

Use UTF-8 JSON, JSONL, or CSV for derived machine-readable data. Use RIS, BibTeX, CSV, or another source-native structured format for bibliographic transfer when available. Before every merge or synthesis, validate schemas, IDs, controlled values, and links between records.

Make deduplication reproducible. Review conflicts manually when identifiers disagree. Keep both the original metadata and the preferred normalized value, with the reason for choosing it.

Use Git history as the audit trail for text, code, schemas, and derived non-sensitive data. Keep licensed raw exports and full texts in access-controlled storage. The repository or search manifest must give their durable location and backup status. Do not publish licensed exports, copyrighted abstracts, or full texts merely to satisfy a checklist.

## Inclusion and exclusion criteria

| Criterion | Plain-English rule | RQ(s) |
|---|---|---|
| Publication date | Include a report whose first formal publication or issue date is from 2011-01-01 through 2026-08-10. Treat online-first and issue versions as one work. For a degree work, use the earliest date that can be verified as formal issue or publication of the completed thesis or dissertation, and keep the source's date label. Record defence, award, approval, repository deposit, public release, embargo end, and indexing dates separately. Do not silently use one of them as the publication date. | 1–3 |
| Language | The full report must be in English. English metadata does not prove that the report itself is in English. If the full text cannot be obtained, use `not_retrieved` instead of making a language assumption. | 1–3 |
| Publication type | Include a full primary-research journal article; conference, proceedings, or workshop paper; research chapter in an edited scholarly book; institutional technical report; completed master's thesis; or completed doctoral thesis or dissertation. A degree work needs stable institutional or authoritative dissertation-service provenance and substantial methods and results. Empirical comparisons and experience reports may qualify. Record degree acceptance or examination separately from peer or technical review; do not infer one from the other. | 1–3 |
| Population | The work must concern an actual or planned orbital CubeSat or nanosatellite-class mission, or a model tailored to that class. A generic SmallSat label is not enough. A mixed-platform report needs evidence that can be separated for CubeSats or nanosatellites. | 1–3 |
| MBSE threshold | The work must meet the [structured-system-model definition](protocol.md#mbse-qualification). | 1–3 |
| EPS threshold | At full text, the work must meet Route A or Route B. | 1–3 |
| RQ1a contribution | Extract the representation, purpose, inputs and assumptions, abstraction, implementation needs, and reuse or tailoring practices for every eligible EPS thread. Use `not_reported` for missing fields. | 1a |
| RQ1b contribution | Give each eligible EPS thread an RQ1b disposition. For identifiable EPS-linked artifacts, create lineage profiles and tailoring applications where relevant. | 1b |
| RQ2 contribution | Include in direct RQ2 synthesis only atomic outcome or implementation-burden records that the source explicitly links to a qualifying EPS thread. Code direction, mechanism, and evidence completeness separately. | 2 |
| RQ3 contribution | Include in direct RQ3 synthesis only `eps_specific` or `system_wide_eps_linked` records that have the required target, explicit bridge, and reported V&V method, intent, or artifact. Report scope, object, criterion completeness, and execution separately. | 3 |
| Mixed system scope | Include only if an EPS thread can be extracted separately. Describe other subsystems only as EPS dependencies or interfaces. | 1–3 |
| Secondary studies | Exclude secondary studies, including Buruso et al. (2026), from primary evidence. Keep them separately for background, terminology, later recall checks, and citation searching. | 1–3 |
| Non-MBSE EPS studies | Exclude stand-alone component, circuit, control, optimization, sizing, simulation, or hardware-performance studies unless they have an explicit link to a structured system model. | 1–3 |
| Generic whole-spacecraft MBSE | Exclude a report without a qualifying EPS thread, even if it mentions an EPS or power budget. | 1–3 |
| Other-subsystem studies | Exclude unless they contain a qualifying EPS thread. A subsystem's power consumption alone is not enough. | 1–3 |
| Abstract-only or non-research material | Exclude posters or abstracts without full papers; thesis or dissertation metadata and abstract stubs without the completed substantial report; proposals and prospectuses; incomplete degree work; undergraduate, bachelor's, or non-degree projects; presentation- or slide-only records; recordings; editorials; tutorials; advertisements; patents; and non-scholarly web material. A record from PQDT, OATD, ESA Indico, or NTRS may be kept as a lead to a different eligible full report, but it cannot supply primary evidence itself. | 1–3 |
| Retrieval status | Scientific eligibility does not depend on open access. If the report is not obtained after the required retrieval attempts, including a restricted or embargoed thesis, record `not_retrieved`. Do not silently exclude it for scientific reasons. | 1–3 |

Do not make any of the following a report-level inclusion test: an outcome, V&V, reuse, a genericity claim, or demonstrated tailoring. A Route A or Route B report can answer only RQ1a and still be included. Assign genericity dispositions, profiles, and tiers only after the report passes scientific eligibility. They cannot make an ineligible report eligible.

For retrieval, follow the run's PDF workflow:

1. try DOI and open-access routes, PQDT or OATD links, publisher pages, and authoritative institutional repositories;
2. when needed, make one recorded institutional, library, or manual-download attempt; and
3. record entitlement, repository link, embargo, licence, version, and broken-link status.

An OATD record does not prove that the linked full text is still available. Keep unresolved reports in PRISMA and retrieval records as `not_retrieved`. They do not enter full-text evidence synthesis, but do not describe lack of access as a scientific exclusion reason.

## Screening and eligibility procedure

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

If completion status is unresolved, hold the record as `publication_type_unresolved` while looking for source-locatable clarification. If a 2026 record gives only a year, or thesis dates conflict, hold it as `date_unresolved`. Do not silently turn either temporary status into an exclusion.

If a plausible completed report is unavailable because of access rights, an embargo, or a broken repository link, use `not_retrieved`. Do not call it the wrong publication type because it is unavailable.

For every Route B inclusion, record the EPS anchor, model anchor, explicit bridge, and supporting location. Check these details again during extraction.

Keep secondary reviews and general MBSE background sources outside the analytic denominator.

## Units of evidence and identifiers

Use seven linked units of analysis. Report families and artifact lineages can cross reports and implementations, so these units do not form a simple nested hierarchy.

1. **Study/implementation report family:** one underlying investigation, evaluation, mission or design implementation, reference-model release, or substantially shared model or toolchain use that appears in one or more reports. Require documented overlap. A shared topic, organization, or tool is not enough. Do not move evidence silently between family members.
2. **Report:** one distinct publication, institutional technical report, or completed thesis or dissertation. Merge online-first and issue versions, and duplicate PQDT, OATD, or repository copies of the same degree work, as versions of one report. Keep a thesis and a substantially different article or technical report as separate reports, but link them to one family when overlap is documented.
3. **EPS model thread:** one qualifying EPS-primary or embedded chain within a report. One report may contain several threads.
4. **Reusable EPS artifact lineage and genericity profile:** one identifiable base artifact and its source-supported versions or derived instances, linked to every relevant report, family, and EPS thread. Start separate lineages when the retained core or derivation identity differs materially or is uncertain. Make a separate profile for a materially different version or scope when one combined profile would hide changes in claims or gate evidence.
5. **Tailoring application:** one application of an artifact lineage to a target setting, including a justified reuse-without-change case. Merge repeated reports of the same underlying application for context and assurance counts, but keep all report provenance.
6. **Outcome or implementation-burden record:** one atomic outcome direction or burden linked, or possibly linked, to a thread. If one statement contains several outcomes, directions, or burdens, create separate records that may point to the same quotation.
7. **V&V record:** one target–method–scenario activity or artifact linked, or possibly linked, to a thread. Use linked atomic records for multiple targets, methods, or scenarios instead of one combined record.

For every report-family link, record:

- family ID;
- report-to-family relationship type;
- reason for membership;
- evidence location; and
- confidence in the overlap.

A report may belong to more than one family if it genuinely covers separate implementations or evaluations. Do not count reports from one family as independent replications.

An artifact lineage may span several implementation families. This alone does not prove independent reuse; the I gate still needs source support. In the other direction, a shared organization or artifact name does not by itself justify merging lineages.

Every artifact-level field that combines reports must keep report provenance. Do not use a linking report to assign an unreported fact or result to another report, artifact version, or application.

Families and lineages describe dependence and identity. They are not PRISMA flow units. Keep PRISMA identification and selection counts at the record and report level.

New-run IDs must show their linked units. Examples are:

- `family_id`;
- `artifact_lineage_id:genericity_profile_id`;
- `artifact_lineage_id:tailoring_application_id`;
- `report_id:thread_id:outcome_burden_id`; and
- `report_id:thread_id:vnv_id`.

Use a normalized DOI as the preferred identity key for reports across runs. Add NTRS or report numbers and source IDs where available. Confirm title–author–year matches manually. To identify an artifact, require the lineage evidence defined under [bounded genericity](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring). Old IDs and old discovery paths are provenance only.

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

### RQ1b genericity-evidence audit, when applicable

Apply the [A/E/C/T/P/I gates and tier rules](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring). Do not give this audit a numerical score. Record a source location and status for every gate. Also check that:

- the claim is about an EPS-linked model artifact, not only a method, tool, workflow, or general whole-spacecraft idea;
- the artifact or version lineage and every credited tailoring application can be identified without moving evidence across uncertain versions or duplicate reports;
- the DAE is kept separate from demonstrated coverage and from reviewer guesses about applicability;
- the source reports the retained core, variation points, actual changes, work required, and any reason for using the artifact unchanged;
- every setting credited to G3 or G4 has a criterion relevant after tailoring, a check that was run, and a result relevant to intended use;
- G4 means that an independent adopter tailored or adopted and assured the artifact and that an independent-adopter or evaluator source confirms it. An originator's statement, independent review, publication, different author list, or repeated evaluation of the originator's own instance is not enough; and
- failed, mixed, outside-envelope, or conflicting applications remain in the claim-agreement results.

A genericity tier measures how complete and independent the evidence is for reuse within stated limits. It does not say that an artifact is high quality, useful, widely applicable, or better than another artifact.

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
