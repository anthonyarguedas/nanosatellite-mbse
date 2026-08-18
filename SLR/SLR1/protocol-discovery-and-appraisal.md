# Protocol for a Systematic Review of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Discovery and appraisal

> **Protocol parts:** [1 — Scope and definitions](protocol.md) · **2 — Discovery and appraisal** (this file) · [3 — Extraction and synthesis](protocol-extraction-and-synthesis.md)
>
> **Normative definitions used here:** [MBSE qualification](protocol.md#mbse-qualification), [eligible EPS evidence routes](protocol.md#eligible-eps-evidence-routes), and [bounded genericity](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring).

## Information sources

### Electronic databases, collections, and indexed online resources

The operational baseline comprises fifteen independently searched sources/collections through thirteen interfaces. Engineering Village is one simultaneous interface for two separately preserved databases; the ProQuest Platform hosts two separately selected and executed source events:

- Scopus, bibliographic database
- Web of Science Core Collection on the Clarivate Web of Science platform, bibliographic and citation database
- IEEE Xplore, bibliographic/full-text database
- arXiv, searched across the full multidisciplinary preprint repository
- Compendex and Inspec on the Engineering Village platform, queried separately
- Wiley Online Library, searched as a general publisher database across the full platform
- Springer Nature Link, searched across the full publisher platform
- Advanced Technologies & Aerospace Index on the ProQuest Platform, with only that exact index selected
- ProQuest Dissertations & Theses Global (PQDT Global) on the ProQuest Platform, with only that exact database selected
- AIAA Aerospace Research Central (ARC), searched source-wide across its publisher-hosted collection
- IAF Digital Library, searched across the full database
- Open Access Theses and Dissertations (OATD), searched across the whole public ETD index
- ESA Indico, searched as a general event/contribution database across the full public instance
- NASA Technical Reports Server (NTRS), searched across the full public technical-report database

PRISMA-S records PQDT Global as a named database on the ProQuest Platform and OATD as an indexed online resource. PRISMA 2020 identification accounting places OATD records in the website/other-methods channel while still treating OATD as a mandatory operational source; it preserves separate totals for all fifteen sources/collections. As an explicit review-specific classification decision, the other fourteen bounded, structured operational collections are reported in the databases/registers column as databases, regardless of browser workflow or export format; none is treated as a study register, and no source is counted in both columns. Engineering Village additionally preserves its simultaneous combined total and separate Compendex/Inspec counts, and each ProQuest source retains its own selection proof, event, count, export, and provenance. The current machine-readable source mapping and null/zero/failure contracts are kept with the final-run crosswalk, manifest schema, and failure-register schema under `searches/`. They may be validated structurally.

### Supplementary discovery and citation searching

- Backward chasing from the complete reference lists of included reports and relevant secondary reviews, and forward citation chasing in both Scopus and Web of Science Core Collection
- Buruso et al. (2026), *Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review* (https://doi.org/10.1002/sys.70051), as a named secondary-review seed and deferred recall benchmark

Buruso et al. (2026) is excluded from primary evidence. A report cited by it may enter the corpus only through a logged planned-source discovery event or protocol-compliant citation-chasing event followed by new screening. Its overlap, source-specific rediscovery, citation-chasing yield, and exclusions of apparently relevant reports will be reported separately.

## Search strategy

Use two complementary search streams so that embedded EPS threads absent from titles or abstracts are not systematically lost:

- **Stream A — EPS-explicit:** combine Population × EPS × MBSE/system-model concepts to identify EPS-primary reports and explicit embedded threads. In the eleven direct source/query families, the complete implementation is `A1 ∪ A2 ∪ A3`, where A3 restores high-specificity EPS × broad-model combinations; in IAF, ESA, and NTRS it is the equivalent local `P AND E AND M` tag.
- **Stream B — embedded-thread recall:** combine Population with structured-model/MBSE, precise reusable-artifact, conservative central-asset, or model-coupled tailoring concepts without requiring an EPS term, then screen full texts for a qualifying EPS thread. Stream B is intentionally broader and its unique yield is reported separately. The current implementation uses core routes and separately provenance-coded `B-G`, `B-C1`, and, where not structurally contained in core B, `B-T2` partitions.

For the eleven direct source/query families—covering twelve databases/collections because Engineering Village searches Compendex and Inspec together—**core B means the retained union B1∪B2**: B1 is population plus high-specificity MBSE terms, while B2 combines population and broader structured-model terms with the established systems-engineering relation/concern block needed to control those broader terms. PQDT and OATD use the same eleven semantic partitions without adding thesis/dissertation terms, because their source boundaries already restrict them to degree works. IAF, ESA, and NTRS instead implement local core B as `P AND M` within one route/record. Accordingly, an optional R tag for exact G/C1 artifacts does not make R optional in bibliographic B2.

The concept blocks, adapted to each source's syntax and searchable metadata, are:

1. **Population:** CubeSat/CubeSats, `cube sat`, nanosat, nanosatellite/nanosatellites, singular/plural hyphenated and spaced `nano satellite` variants, or an explicitly nanosatellite-class mission. Generic `SmallSat`/“small satellite” is neither a positive search concept nor sufficient eligibility evidence;
2. **EPS:** electrical/electric power system or subsystem, EPS, power subsystem, electrical/power architecture, power/energy budget, energy balance, battery/batteries or storage, solar array/power generation, power conditioning/distribution/management/interface, power mode(s), load profile, PCDU, or PMAD;
3. **MBSE/system model (`M`):** singular/plural model-based system(s) engineering, MBSE, SysML/systems modeling language, singular/plural US/UK system(s) modeling/modelling, reference or object-oriented systems model, digital engineering, Arcadia, Capella, or another validated structured-system-model term;
4. **Precise reusable-artifact (`G`):** complete generic/reusable/configurable model or system-model phrases; model template; mission-agnostic or mission-independent model/architecture; reference architecture; domain model; metamodel/meta-model; product-line/product-family model; or a variation point coupled to model/architecture. The preferred query-source form is relation-free `P AND G`, because exact phrases bound the expansion and an R requirement can both self-satisfy through `architecture` and suppress records whose metadata omit relation words;
5. **Conservative central asset (`C1`):** reference/system-reference model, model-library, model-pattern, model-profile, or SysML-profile phrases, plus a domain-specific modeling/modelling-language phrase only when coupled to an MBSE/system-model anchor. Bare `library`, `pattern`, `profile`, or language terms are prohibited; and
6. **Model-coupled tailoring (`T2`):** a B2 structured-model block plus explicit reuse, tailoring, customization, configuration, parameterization, instantiation, variability/variation-point, specialization, or adaptation forms coupled to model(s) or architecture(s). Source-supported wildcards or finite inflections are required.

`B-G`, `B-C1`, and `B-T2` are candidate-generating terminology partitions only where their source adaptation is not structurally contained in core B and complete no-screening pilots support or prospectively preserve possible unique yield. They do not require EPS terms and never replace core B. For G/C1 expansion records, R may be retained as an optional precision/provenance tag; an architecture-bearing artifact cannot qualify that tag through its own overlapping token. Genericity/tailoring terminology is not required for eligibility or grading, and retrieval through any expansion is no evidence that an artifact is reusable.

Targeted RQ2 and RQ3 sensitivity probes may add benefit, null/adverse outcome, burden, effort, cost, training, traceability, verification, validation, model verification/validation, system/design verification/validation, simulation, model checking, requirements-in-the-loop, MIL, SIL, PIL, HIL, or test terms. Every direct `V1`/`O1` query and IAF/ESA/NTRS local tag uses the same exact finite subsets in the query plan and dictionary; no source may rely on wildcard or implicit expansion equivalence. These terms are not mandatory in every query because doing so could suppress relevant RQ1 and embedded-thread reports. The old T1 probe was a logical subset of core B and added no IDs; the later `T2` design replaces the bibliographic B2 relation gate with a tightly model/architecture-coupled tailoring block and did add opaque IDs in Scopus/IEEE, so the T1 result does not justify dropping T2.

Searches will be piloted in small, targeted sets. The new search log must record, as applicable, exact strings, fields, filters, platform/interface, dates and time zone, source-reported totals, retrieved totals, pagination or event-harvest coverage, automatic stemming/lemmatization/term-expansion state or absence, refinements, failed or overbroad queries, deduplication, coverage checks, and stopping rationale. Refining source-specific syntax or precision within these specified concept streams is search implementation, not a change to review eligibility; record each dated refinement and the final used set in the log without assigning document versions.

Every final query must be conducted through the source's normal browser interface using the documented source-native strings and visible controls in [`query-search-plan.md`](query-search-plan.md). Preserve the exact interface and source/database selection, reconcile a stable source total to complete pagination and source IDs, and complete two identical ordered-ID passes where the source exposes an ordered record ledger. Query rewrites, stale/short pages, changed totals, duplicate/missing identifiers, export mismatches, and timeouts remain failures with total `null`, never zero or partial candidate imports. Preserve source overlap as separate discovery events and deduplicate only after each source event has been retrieved and normalized.

The following source-specific controls are mandatory:

- **Engineering Village:** run every `C-*` query as one paired Compendex+Inspec event only, with All and Knovel clear, `KY` concept fields, Published 2011–Latest plus literal year/English clauses, autostemming off, Relevance, **fixed visible 25/page**, no discovery document-type filter, and source-side duplicate removal off. Fixed visible page size is an enumeration transport setting, not search-set semantics. Require the exact controls/query, stable total, complete pagination with exactly 25 visible rows on every nonterminal page and exact terminal arithmetic, and two identical ordered value-blind `(database label, source handle)` passes. Reconcile complete native RIS to the complete paired ledger before normalization/merge; preserve the combined total, separate database totals, row-level database label, global rank, and both database instances through later deduplication. A Compendex-only or Inspec-only troubleshooting run cannot replace the paired final event, and no failed or partial prefix may be accepted or imported.
- **Wiley Online Library:** search the full platform with the documented Anywhere/`AllField` expressions, 20-record Articles & Chapters pages, the separately logged Collections coverage route, and no discovery venue, content-type, access, or language filter unsupported by the interface. Preserve the source total, exact-day cutoff, ordered DOI ledger, native page-scoped RIS with abstracts, and normalized merge provenance.
- **Springer Nature Link:** search the full Link platform through unrestricted Keywords with English, custom 2011–2026 dates followed by the common 2026-08-10 cutoff, Relevance, 20/page, and no content-type, brand, discipline, venue, or access facet. Reconcile the complete ordered DOI/canonical-URL ledger twice. Use and preserve the normal native CSV where an authorized account and the 1,000-record source ceiling permit it; otherwise use complete normal-page retrieval. Partition prospectively into disjoint date cells when a source ceiling would truncate a final set.
- **Advanced Technologies & Aerospace Index on ProQuest:** select only that exact Index; use the documented `NOFT` expressions with year and English clauses, Relevance, 20/page, spelling/form expansion in its recorded final state, no full-text/peer-review/source-type/document-type limiter, and source duplicate exclusion off. Preserve selected-database proof, complete page/rank/source-ID ledgers, a normal native RIS preflight and batches where available, and normalized source provenance; never substitute the broader parent or sibling databases.
- **ProQuest Dissertations & Theses Global:** in a separate ProQuest event, select only the exact PQDT Global database and run all eleven `PQDT-*` translations with the same `NOFT`, year, English, no-type/no-access-limiter, source-deduplication-off, and Relevance semantics. Do not inherit the aerospace adapter's page size, ceiling, selector, or export assumptions without a PQDT-specific live gate. Preserve exact-database proof before every query, complete two-pass rank/source-ID reconciliation, a native RIS preflight and safe batches, degree/source metadata, and a stable session-free record URL. For a challenge or login interstitial, apply the wait/focus/retry rule above. An unresolved entitlement failure, ambiguous selection, or unverified cap is a source failure with total `null`.
- **Open Access Theses and Dissertations:** search the whole native OATD index with all eleven finite `OATD-*` semantic translations through the validated basic `q` grammar, default Relevance/30 controls as re-verified at execution, and no native date, language, institution, degree, Creative-Commons, or additional access limiter; apply the 2011-01-01 through 2026-08-10 date and English rules locally. Composer year/language controls may replace local handling only after a separately logged set-equivalence and metadata-quality gate. Preserve exact URL/query echo, source total, sort/page size, complete stable record-ID or canonical-URL ledgers, two-pass ordering where exposed, and repository-link provenance. For a challenge or busy/access interstitial, apply the wait/focus/retry rule above. A hidden cap, incomplete pagination, missing stable identity, or unresolved interface/rights failure is total `null`; a linked repository is retrieval only and cannot become an unlogged discovery source.
- **AIAA Aerospace Research Central:** search source-wide All content through Anywhere/`AllField` with `access=on`, January 2011 through August 2026, Relevance, fixed 20-record pages, and no language, publication-type, venue, topic, or open-access discovery facet. Preserve the month-granular source total and apply the common 2026-08-10 cutoff. Require complete two-pass DOI pagination and the visible per-record Tools → Download citation RIS route with exact-byte native preservation and DOI reconciliation. For a challenge, apply the wait/focus/retry rule above. A DOI-less row or changed interface stops the run with total `null` pending a documented source-native fallback; do not discard the row or substitute another index.
- **arXiv:** search the full repository through Advanced Search using All fields and every direct source/query partition, with no subject-category restriction. Preserve complete canonical arXiv-ID pagination, available abstracts, and submission/version metadata; apply the English, eligible-publication-type, and common first-formal-publication-date rules during screening rather than treating an arXiv submission date as a formal publication date.
- **IAF Digital Library:** run the complete population query across the full Digital Library without an event-code, conference-series, or venue restriction; retrieve and reconcile the complete public result set and landing-page title/abstract metadata twice; and apply deterministic local P/M/G/C1 plus E/R/T2/V1/O1 classification. Preserve event metadata only as record provenance, not as search scope. Use only public browser-visible result and landing-page routes; do not use manuscript/full-text or authenticated routes. Retain missing-abstract leads and apply the common 2026-08-10 first-formal-publication cutoff during screening.

Previously identified reports may be listed before searching in a read-only known-item register. They may guide query refinement if missed, but they enter the corpus only through a logged search or citation-chasing event followed by new screening. Known-item recall and unique inclusions from each stream and source are reported separately.

No query-based source uses a discovery publication/content-type filter unless the final log prospectively records a source-mandated implementation change; source scope already limits PQDT/OATD to degree works, and completed degree/report type is verified during screening. Apply English in Scopus, Web of Science Core Collection, IEEE Xplore, paired Engineering Village, Springer Nature Link, Advanced Technologies & Aerospace Index, and PQDT Global where the planned interface exposes a reliable control; Wiley, OATD, AIAA ARC, IAF, arXiv, ESA, and NTRS language is screened because no reliable discovery control was validated. Every source and citation route uses the common 2026-08-10 evidence cutoff. Source year/month controls that admit later records—including Scopus, IEEE, paired Engineering Village, Wiley, Springer, both ProQuest events, AIAA ARC, and IAF—retain their unaltered source totals and receive a logged first-formal-publication-date cutoff with the number removed or left unresolved; OATD's unrestricted native total receives the same locally applied window and exact-day accounting.

For ESA Indico, inventory every event/contribution material through the common cutoff before candidate gating and union deterministic core P×M with relation-free complete P×G/C1 artifact matches from joined metadata and each individual extractable attachment; retain independent-R, T2, V1, and O1 as separate tags; inaccessible/unparseable materials are coverage failures and terms may not be combined across metadata and attachment routes. For NTRS, the completed 2026-08-13 final run exhausted 940 separate cells: ten population terms × eighteen core model terms, the same ten × twenty-five exact G terms, and the same ten × fifty-one exact C1 atoms. The C1 set includes every four-language-spelling × nine-model-anchor combination. The final run applied the full deterministic E/T dictionaries and exact finite V1/O1 subsets to the deduplicated core-B∪B-G∪B-C1 union. It reconciled 40 source records across cells to a six-record union: core = 6, G = 1, C1 = 0, core∩G = 1, core-only = 5, and no expansion-only records; full-E core tag = 1, expansion-E = 0, T2 = 0, V1 = 3, and O1 = 5. Stream A remains the E-explicit tag within core B; it is structurally contained in NTRS core B (`A-only = 0`). The access-controlled final artifacts and execution details are recorded in [`query-search-plan.md`](query-search-plan.md) and [`search-log.md`](search-log.md). ESA remains subject to the same local-tag reporting rules when it is run.

Complete the independent baseline after each of the fifteen operational sources/collections has either a complete, reconciled final run or an explicitly documented final source/interface failure. Merge only successful complete-source results, including separate Compendex and Inspec discovery instances from each successful paired Engineering Village event; retain every failed-source status and reason in the manifest and PRISMA-S/PRISMA accounting, and never import a failed source's partial prefix. Use Buruso et al. (2026) and the retained-file cache for deferred recall audits only after that successful-source baseline and failed-source register are complete and recorded. A missed Buruso-cited report can prompt a logged concept-level probe or enter through a logged citation-chasing route; it is never inserted directly.

Backward and forward citation chasing starts from every full-text-included report and relevant secondary review. Backward chasing inspects the complete source reference list; forward chasing searches both Scopus and Web of Science Core Collection. A zero result or indexing failure in one forward-citation platform does not waive the other. Newly found eligible reports are chased in the next numbered cycle; iteration stops when one complete backward and dual-platform forward cycle yields no new eligible report. Every seed, platform, direction, exact route, cycle, source/retrieved total, candidate, duplicate, decision, failure, and stopping result is logged. Citation records retain `discovery_route=citation_chasing` separately from their bibliographic source and never bypass normal eligibility screening.

Searching stops only when every planned implementation of both streams has completed at every planned source—or the affected final source/interface has failed explicitly without partial candidate import. This includes all direct-source A1/A2/A3 queries; every core, B-G, B-C1, and source-applicable B-T2 partition; every mandatory local V1/O1 tag; and the full-database IAF route. In addition, every source-specific coverage check and prespecified concept cluster must have completed or failed explicitly, relevant report families/artifact lineages discovered during the new run must have been tested, citation chasing must be complete, and additional searches must be predominantly redundant rather than merely convenient or precise. The execution date for every source and strategy is reported, but the review's evidence window closes uniformly on 2026-08-10.

## Data management and audit trail

Manage review methods, logs, controlled dictionaries, derived data, and analysis code in the Git-tracked `SLR/SLR1/` workspace. Preserve raw source artifacts as read-only files where licensing permits and index every artifact in a manifest with path, query/event ID, source, timestamp, byte size, access/rights status, and creating software. Record the actual database interface and software versions at execution rather than assuming the draft environment remains unchanged.

Use UTF-8 JSON/JSONL or CSV for derived machine-readable data and RIS/BibTeX/CSV or source-native structured exports for bibliographic transfer as available. Validate schemas, identifiers, controlled values, and referential integrity before each merge or synthesis. Deduplication is reproducible but manually adjudicated where identifiers conflict; preserve both the original metadata and the preferred normalized value with rationale. Git history supplies the audit trail for text, code, schemas, and derived non-sensitive data; raw licensed exports and full texts remain in access-controlled storage with the repository/search manifest recording their durable location and backup status. Do not publicly redistribute licensed exports, copyrighted abstracts, or full texts merely for checklist compliance.

## Inclusion and exclusion criteria

| Criterion | Rule | Applicable RQ(s) |
|---|---|---|
| Publication date | First formal publication/issue date from 2011-01-01 through the common 2026-08-10 evidence cutoff; online-first and issue versions of the same report are one work. For a degree work, use the earliest verifiable formal issue/publication date of the completed thesis/dissertation and retain the source's date label; defence, award, approval, repository deposit, public release, embargo end, and indexing dates are recorded separately and are not silently substituted | 1--3 |
| Language | Report written in English; translated English metadata does not establish full-report language, and inability to retrieve the full text is handled separately as `not_retrieved` | 1--3 |
| Publication type | Full primary-research journal article, conference/proceedings or workshop paper, research chapter in an edited scholarly volume, institutional technical report, completed master's-level thesis, or completed doctoral dissertation/thesis with stable institutional or authoritative dissertation-service provenance and substantive methods/results; empirical comparison and experience reports are eligible when they meet all other criteria. Degree examination/acceptance and reported peer/technical-review status are recorded separately and neither is inferred from the other | 1--3 |
| Population | Actual or intended orbital CubeSat/nanosatellite-class mission or a nanosatellite-tailored model; a generic SmallSat/small-satellite label alone is excluded, and separable CubeSat/nanosatellite evidence is required in mixed-platform reports | 1--3 |
| MBSE threshold | Must meet the [structured-system-model definition](protocol.md#mbse-qualification) | 1--3 |
| EPS threshold | Must meet Route A or Route B at full text | 1--3 |
| RQ1 contribution | Every eligible EPS thread contributes its reported representation, purpose, inputs/assumptions, abstraction, and reuse/tailoring information and receives an RQ1-G disposition; identifiable EPS-linked artifacts receive artifact-lineage profiles and tailoring applications where applicable; missing fields remain `not_reported` | 1, including RQ1-G |
| RQ2 contribution | Only atomic outcome or implementation-burden records explicitly attributed to a qualifying EPS thread enter direct RQ2 synthesis; direction, mechanism, and evidence completeness are coded separately | 2 |
| RQ3 contribution | Only `eps_specific` or `system_wide_eps_linked` records with the required target, explicit bridge, and reported V&V method/intent/artifact enter direct RQ3 synthesis; scope, object, criterion completeness, and execution are reported separately | 3 |
| Mixed system scope | Include only when an EPS thread is separately extractable; synthesize other subsystems only as EPS dependencies/interfaces | 1--3 |
| Secondary studies | Exclude from primary evidence, including Buruso et al. (2026); retain separately for positioning, terminology, deferred recall checking, and citation chasing | 1--3 |
| Non-MBSE EPS studies | Exclude stand-alone component, circuit, control, optimization, sizing, simulation, or hardware-performance studies without an explicit structured-system-model link | 1--3 |
| Generic whole-spacecraft MBSE | Exclude reports lacking a qualifying EPS thread, even if they mention EPS or a power budget | 1--3 |
| Other subsystem studies | Exclude unless they contain a qualifying EPS thread; a subsystem's power consumption alone is insufficient | 1--3 |
| Abstract-only/non-research material | Exclude posters/abstracts without full papers, thesis/dissertation metadata or abstract stubs without the completed substantive report, proposals/prospectuses, incomplete degree works, undergraduate/bachelor or non-degree projects, presentation- or slide-only records, recordings, editorials, tutorials, advertisements, patents, and non-scholarly web material. Such records from PQDT, OATD, ESA Indico, or NTRS may be logged as discovery leads to a distinct eligible full report but cannot themselves supply primary evidence | 1--3 |
| Retrieval status | Scientific eligibility is independent of open-access status. Reports not obtained after the defined retrieval process—including embargoed or subscription-restricted theses/dissertations—are logged as `not retrieved`, not silently excluded on scientific grounds | 1--3 |

Outcome, V&V, reuse, genericity-claim, or demonstrated-tailoring presence is not a report-level inclusion criterion. A Route A or B report may answer only the non-genericity portions of RQ1 and still be included. Genericity dispositions, profiles, and tiers are assigned only after scientific eligibility and cannot rescue an ineligible report.

Retrieval follows the run's PDF workflow: DOI/open-access, PQDT/OATD-linked, publisher, and authoritative institutional-repository routes are attempted first, followed by one documented institutional/library/manual-download pass where needed. Record entitlement, repository-link, embargo, licence, version, and broken-link status without treating OATD discovery as proof that a full text remains accessible. Unresolved reports remain in the PRISMA and retrieval records as `not_retrieved`; they do not enter full-text evidence synthesis, but lack of access is not presented as a scientific exclusion reason.

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

For `exclude_wrong_publication_type`, also record one controlled subtype: `undergraduate_or_bachelor`, `non_degree_project`, `proposal_or_prospectus`, `incomplete_degree_work`, `abstract_or_metadata_stub`, or `other` with text. Unresolved completion status is held as `publication_type_unresolved`, and a year-only 2026 or conflicting thesis date is held as `date_unresolved`, while source-locatable clarification is sought; neither interim status is silently converted into exclusion. A scientifically plausible completed report unavailable because of entitlement, embargo, or a broken repository link follows `not_retrieved` rather than an access-based publication-type exclusion.

For every Route B inclusion, screening must record the EPS anchor, model anchor, explicit bridge, and supporting location. These data are rechecked during extraction.

Secondary reviews and generic MBSE sources used for background or citation chasing are maintained outside the analytic denominator.

## Units of evidence and identifiers

The review distinguishes seven linked analytic units. Report-family and artifact-lineage relations can cross reports and implementations, so the units are not assumed to form a strictly nested hierarchy:

1. **Study/implementation report family:** one underlying investigation, evaluation, mission/design implementation, reference-model release, or materially shared model/toolchain application represented by one or more reports. Family membership requires documented overlap; shared topic, organization, or tool alone is insufficient, and evidence does not transfer silently between family members.
2. **Report:** one distinct publication, institutional technical report, or completed thesis/dissertation. Online-first/issue versions and duplicate PQDT/OATD/repository deposits of the same degree work are collapsed as manifestations of one report, while a thesis and a substantively distinct derivative article or technical report remain separately citable reports linked to the same family on documented overlap.
3. **EPS model thread:** one qualifying EPS-primary or embedded chain within a report. A report may contain more than one thread.
4. **Reusable EPS artifact lineage and genericity profile:** one identifiable base artifact and its source-supported versions/derived instances, linked to every contributing report, family, and EPS thread. Create separate lineages when the retained core or derivation identity is materially different or uncertain. One lineage receives one profile per materially distinct artifact version/scope when a combined profile would conceal changed claims or gates.
5. **Tailoring application:** one artifact-lineage-to-target-context application, including a justified reuse-as-is case. Multiple reports of the same underlying application are collapsed for context and assurance counts while retaining all report provenance.
6. **Outcome or implementation-burden record:** one atomic outcome direction or burden linked or potentially linked to a thread. When one statement reports several outcomes, directions, or burdens, create separate records that may share the same quotation.
7. **V&V record:** one target–method–scenario activity or artifact linked or potentially linked to a thread. Multiple targets, methods, or scenarios use linked atomic records rather than one aggregate record.

Assign a report-family ID, report-to-family relationship type, membership rationale, evidence location, and overlap confidence. A report may map to more than one family when it genuinely reports distinct underlying implementations or evaluations. Reports from the same family are not treated as independent replications. An artifact lineage may span multiple implementation families, but this does not establish independent reuse unless the I gate is source-supported. Conversely, shared organization or artifact name does not justify merging lineages. Each integrated artifact-level field retains report provenance; linking reports must not attribute an unreported fact or result to another report/version. Families and lineages are analytic dependence/identity units, not PRISMA flow-diagram units: PRISMA identification and selection counts remain at record/report level.

New-run IDs must qualify linked records, for example `family_id`, `artifact_lineage_id:genericity_profile_id`, `artifact_lineage_id:tailoring_application_id`, `report_id:thread_id:outcome_burden_id`, and `report_id:thread_id:vnv_id`. A normalized DOI is the preferred cross-run report identity key; NTRS/report numbers and source IDs supplement it, and title–author–year matching requires manual confirmation. Artifact identity requires the lineage evidence in the [bounded-genericity definition](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring). Legacy IDs and prior discovery paths are provenance only.

## Quality checklist

All applicable items use:

- No = 0
- Insufficiently = 0.5
- Yes = 1
- Not applicable = excluded from that score's denominator

Quality scores contextualize confidence and sensitivity analyses; they are not automatic exclusion thresholds and cannot make an ineligible report, genericity profile, outcome/burden record, or V&V record eligible. The A/E/C/T/P/I genericity profile and `NA`/`G0`--`G4` tier are not included in this numerical checklist and must not be averaged with it.

### Report and EPS-thread quality

1. Was the primary research published in a credible scholarly venue, identifiable institutional technical-report series, or completed degree work from an identifiable degree-granting institution/authoritative dissertation service, with report type, provenance, completion status, and reported peer/technical/degree-examination status verifiable?
2. Is the CubeSat/nanosatellite mission context and lifecycle stage described clearly enough to assess applicability?
3. Are the MBSE method, model boundary, language/toolchain, artifacts, and modeled relations described clearly enough to verify MBSE qualification?
4. Are the EPS anchor, model anchor, explicit bridge, and EPS boundary reported clearly enough to reconstruct the qualifying thread?
5. Are the model's stated purpose, intended decisions, users/roles, and lifecycle use reported?
6. Are material inputs and assumptions reported with sufficient detail about value/range, units or time basis, provenance, uncertainty/margin, and rationale?
7. Are model/tool/data availability, configurations, interfaces, and reusable assets reported sufficiently to assess reproducibility?
8. Do the authors discuss limitations, scope boundaries, uncertainty, threats to validity, or alternative explanations?

### RQ1-G genericity-evidence audit, when applicable

Apply the [A/E/C/T/P/I gates and tier rules](protocol.md#bounded-genericity-reusable-artifacts-and-tailoring) without numerical scoring. In addition to the source location and status for every gate, audit whether:

- the claim object is an EPS-linked model artifact rather than a method, tool, workflow, or generic whole-spacecraft assertion;
- artifact/version lineage and every credited tailoring application are identifiable without transferring evidence across uncertain versions or duplicate reports;
- the DAE is distinguished from demonstrated coverage and from reviewer-inferred applicability;
- retained core, variation points, actual changes, footprint, and any reuse-as-is rationale are reported;
- each context credited to G3/G4 has a post-tailoring criterion, executed check, and result relevant to intended use;
- G4 independence reflects an independently adopted/tailored and assured application corroborated by an independent-adopter/evaluator source, not merely the originator's assertion, an independent reviewer, publication, author list, or repeat evaluation of the originator's instance; and
- failed, mixed, out-of-envelope, or contradictory applications are retained in claim-concordance reporting.

A genericity tier grades the completeness and independence of evidence for bounded transfer; it is not a finding that the artifact is high quality, beneficial, broadly applicable, or superior.

### RQ2 outcome/burden quality, when applicable

9. Is the outcome or implementation burden explicitly linked to a qualifying EPS thread and a stated MBSE mechanism rather than to EPS technology choice or generic MBSE?
10. Is its reported direction or burden supported by an appropriate metric, traceable case result, comparator, stakeholder assessment, reuse, integration/test result, or operational evidence?

### RQ3 V&V quality, when applicable

11. Are the EPS target, linkage scope, model-to-V&V bridge, source terminology, normalized V&V object, method/artifact, criterion, lifecycle timing, and execution status explicitly reported?
12. When execution or closure is claimed, are the result/verdict and any downstream software, hardware, integration, test, operational, or flight link evidenced?

Items 1--3 and 8 are scored at report level; items 4--7 at EPS-thread level; items 9--10 for each direct RQ2 outcome/burden record; and items 11--12 for each EPS-linked RQ3 record. The separate genericity audit is reported at artifact-lineage/profile and tailoring-application level without a numerical roll-up. Any checklist roll-up is descriptive and retains its unit and applicable-item denominator. Linkage, lineage, and tier confidence are also retained separately from quality score.

### Appraisal meaning, reporting-bias assessment, and conclusion confidence

The checklist assesses reporting completeness, direct EPS linkage, and strength of support in heterogeneous engineering evidence; it is not presented as a validated clinical risk-of-bias instrument. Report checklist domains and record-level evidence confidence at their actual units rather than collapsing them into an unqualified “study quality” label.

No funnel plot or statistical publication-bias test is planned because there is no common effect estimate and the evidence types are heterogeneous. Instead, assess and report, for each RQ synthesis:

- coverage/interface limitations and unique yield across the fifteen operational sources/collections, thirteen interfaces, and citation routes, with OATD reported in the website/other-methods channel;
- effects of the English, date, population, publication-type, retrieval, and source-access limits, including PQDT entitlement, OATD's open-repository/participation boundary, geographic and institutional skew, embargoes, missing abstracts/metadata, degree-status uncertainty, and PQDT–OATD overlap;
- unavailable full reports and lead-only material;
- selective or missing genericity claims, applicability boundaries, tailoring failures/burdens, outcome/burden, criteria, results, and limitations;
- dependence created by shared study/implementation report families and repeated reporting of the same artifact lineage/application; and
- protocol deviations, search refinements, or review-process limitations that could change interpretation.

Assign conclusion-level confidence narratively as `higher`, `moderate`, `lower`, or `insufficient`, with a source-locatable rationale. Consider directness to a qualifying EPS thread, report and record quality, the genericity profile/tier where relevant, evidence type and comparator, maturity/independent or physical validation, consistency including null/adverse or failed-transfer evidence, report-family and tailoring-application independence, and review-process limitations. A genericity tier never maps mechanically to a conclusion-confidence label. No numerical quality cutoff or mechanical averaging determines confidence. `Higher` requires multiple materially independent, directly linked and well-supported records with no major unexplained inconsistency; `moderate` permits limited independence, maturity, or comparators but still requires directly supporting evidence; `lower` denotes sparse, weak, indirect, dependent, or materially inconsistent support; and `insufficient` denotes no eligible direct evidence for the conclusion. These labels are an engineering-review framework, not GRADE.

---

**Previous:** [Part 1 — Scope and definitions](protocol.md)  **Next:** [Part 3 — Extraction and synthesis](protocol-extraction-and-synthesis.md)
