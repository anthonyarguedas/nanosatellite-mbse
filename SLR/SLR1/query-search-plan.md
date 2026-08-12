# Query Search Plan: EPS MBSE in CubeSat/Nanosatellite Development

- **Review run:** `eps-mbse-slr-2026`
- **Protocol:** `protocol.md`, version `1.6`, prospectively amended, frozen, and authorized 2026-08-10
- **Version-1.4 source amendment:** Inspec was added to every Engineering Village search alongside Compendex; Springer Nature Link, Advanced Technologies & Aerospace Index on ProQuest, and AIAA Aerospace Research Central were added as separately provenance-coded collections
- **Version-1.5 source/completeness amendment:** authorize the public IAF Digital Library as an IAC-proceedings-only collection; complete Stream A with direct-source `A3`; complete IEEE finite T2 inflections and NTRS C1 anchors; standardize finite V1/O1 probes/tags; and freeze one review-wide evidence cutoff
- **Version-1.6 thesis/dissertation amendment:** admit completed master's-level theses and doctoral dissertations/theses; add exact-database PQDT Global and whole-index OATD as mandatory, separately provenance-coded sources; retain the common cutoff and all scientific eligibility thresholds
- **V16-C Engineering Village transport amendment (2026-08-11):** fixed visible 25/page replaces the former final 100/page transport setting only; paired selection, frozen query/set semantics, and all other controls are unchanged, and a fresh complete rerun remains required
- **Protocol synchronization:** completed in version 1.6 for fourteen independently searched sources/collections through twelve interfaces, ten direct source/query families, 110 logical direct query events (99 physical source-native code blocks plus 11 normative PQDT aliases), and all permitted source adapters in `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts`
- **Plan status:** no valid final discovery has been executed. Run every version-1.6-authorized method from clean final-run storage. The completed baseline must not mix any pilot, version-1.5 artifact, or pre-authorization IAF output with final discovery.
- **Common evidence cutoff:** first formal publication/issue from 2011-01-01 through 2026-08-10, inclusive, for every source and citation route regardless of execution date
- **Authorized version-1.6 sources/collections:** Scopus; Web of Science Core Collection; IEEE Xplore; Compendex and Inspec, searched simultaneously on Engineering Village; Wiley Online Library; Springer Nature Link; Advanced Technologies & Aerospace Index on ProQuest; ProQuest Dissertations & Theses Global (PQDT Global) in a separate exact-database ProQuest event; AIAA Aerospace Research Central (ARC); IAF Digital Library (IAC proceedings only); Open Access Theses and Dissertations (OATD); ESA Indico; NASA Technical Reports Server (NTRS)
- **Search interfaces:** twelve; Engineering Village is one simultaneous two-database interface, while one ProQuest Platform interface hosts two separate database-restricted events, giving fourteen operational sources/collections
- **Search unit:** one exact source-specific query, request body, or reproducible website-harvest/matching operation together with its fields, limits, pagination/coverage settings, date, and raw artifacts

## 1. Purpose and scope

Build a new, independently discovered candidate set for full-text retrieval. The search must support both:

- **Stream A — EPS-explicit:** population × EPS × structured-system-model/MBSE concepts; and
- **Stream B — embedded-thread recall:** population combined with structured-system-model/MBSE, precise reusable-artifact (`B-G`), conservative central-asset (`B-C1`), or model-coupled tailoring (`B-T2`) concepts, without a mandatory EPS term.

For the ten full-strategy direct source/query families (covering eleven databases/collections because Engineering Village searches two together, and operated through nine physical direct interfaces because the two ProQuest sources are separate events on one platform), **Stream A is the retained union `A1 ∪ A2 ∪ A3`**: A1 is `P AND E_high-specificity AND M_high-specificity`, A2 is `P AND E_functional/analysis AND M_all`, and A3 is `P AND E_high-specificity AND M_broad-structured-model`. This partition is exactly equivalent to `P AND E_all AND M_all` without relying on B2's relation gate. **Core B is the retained union `B1 ∪ B2`**: B1 is `P AND M_high-specificity`, while B2 is `P AND M_broad-structured-model AND R` because its broader model terms need the established systems-engineering concern block. IAF exhausts a short population-only query separately for each IAC event year, retrieves public title and abstract metadata for that bounded set, and applies deterministic local `P AND M` core-B matching with a full-E Stream-A tag and separate G/C1 expansions. This avoids truncating long concept expressions at IAF's visible 500-character query ceiling, pretending that local tags were direct source queries, or assuming that its selectable search fields include abstracts. For IAF, ESA, and NTRS, deterministic core B is `P AND M` and Stream A is `P AND E AND M` within one local record/route. Thus the source-native and local Stream-A definitions are semantically aligned, while “core B” remains a provenance-coded union rather than a claim that every source-native B2 string omits R. The version-1.6 plan retains the version-1.3-defined expansion partitions as candidate-generating where source-specific no-screening pilots showed—or a structurally non-contained finite source adaptation prospectively preserves—possible IDs outside core B1∪B2. They are terminology-recall partitions inside Stream B, not additional eligibility routes and not evidence that a retrieved model is generic or tailored. G/C1/T2 words are never mandatory for core-B records, and every included artifact receives the same full-text RQ1-G assessment regardless of discovery query.

Search sensitivity is broader than final scientific eligibility. Route A/Route B status and the required EPS anchor, model anchor, and explicit bridge are full-text decisions, not metadata assumptions. Generic `SmallSat`/small-satellite work is outside the population and is not a positive search concept.

Under the authorized version-1.6 baseline, fourteen operational sources/collections are searched through twelve documented interfaces or receive a documented source failure. Every Engineering Village query searches Compendex and Inspec simultaneously and retains each database instance until record-level deduplication. Web of Science is restricted to the Core Collection database but includes all available Core Collection citation-index editions. Wiley, Springer Nature Link, and AIAA ARC are searched across their full publisher-platform scope. The ProQuest Platform is used for two separately executed, never-combined events: one selects only `Advanced Technologies & Aerospace Index`, and one selects only `ProQuest Dissertations & Theses Global`; neither may use a parent, sibling, alternative edition, institution-only subset, or all-databases scope. OATD is searched across its whole native ETD index; linked repositories are retrieval destinations, not extra discovery sources. IAF is restricted deliberately to records whose canonical event is `IAC-YYYY`; GLEX, IAF Spring Meetings, other IAF events, manuscript/full-text routes, and the robots-disallowed API are outside this source boundary. Wiley is not restricted to INCOSE publications, AIAA ARC is not restricted to a named journal or meeting, ESA Indico is not restricted to ESA MBSE workshops, and NTRS is not restricted to a predetermined NASA series. INCOSE International Symposium content and ESA MBSE workshop content are coverage checks only.

### Scripted-source completeness audit

Every permitted source-specific `search_*.py` adapter in `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts` maps to an authorized review source. Web of Science Core Collection remains an additional authorized source operated through its normal interface because that directory has no WoS search adapter. That directory currently has no PQDT Global or OATD adapter: `search_proquest_aerospace.py` is restricted to the aerospace index and must never be relabelled or run as PQDT. Any new source-specific wrapper in this review must pass offline fixtures and a live fail-closed gate before final use. Helper, retrieval, conversion, merge, and test scripts are not information sources.

| Adapter | Authorized source/collection | Version-1.6 status |
|---|---|---|
| `search_scopus.py` | Scopus | included |
| `search_ieee_xplore.py` | IEEE Xplore | included |
| `search_compendex.py` | Compendex and Inspec on Engineering Village | both included in one paired event |
| `search_wiley_online_library.py` | Wiley Online Library | included |
| `search_springer_link.py` | Springer Nature Link | included |
| `search_proquest_aerospace.py` | Advanced Technologies & Aerospace Index | included |
| `search_aiaa_arc.py` | AIAA Aerospace Research Central | included |
| `search_iaf_digital_library.py` | IAF Digital Library, IAC proceedings only | included |
| `search_esa_indico.py` | ESA Indico | included through the stricter attachment-first whole-instance method |
| `search_ntrs.py` | NASA NTRS | included through the exhaustive finite-cell method |
| `search_arxiv.py` | arXiv | forbidden; do not run |
| `search_semantic_scholar.py` | Semantic Scholar | forbidden; do not run |
| `search_google_scholar.py` | Google Scholar | forbidden; do not run |

Additional version-1.6 routes not supplied by that package are PQDT Global through its normal ProQuest product/interface and OATD through its native public interface. Their exact implemented scripts or reproducible manual-browser procedures, selectors, form values, checksums, and fixture results must be recorded in this repository and the final search log; adapter absence is not permission to omit either source. The common merger now has separately regression-tested canonical aliases `proquest_aerospace_index`, `proquest_dissertations_theses_global`, and `oatd`; source aliasing does not validate retrieval or authorize either pending wrapper.

### PRESS-corrected pre-freeze validation completed 2026-08-07

| Source | Validated route | Diagnostic completion |
|---|---|---|
| Scopus | Elsevier Scopus Search API, `COMPLETE` | All six corrected no-type-filter strings accepted; unrestricted S-B1 = 85 and completed two ordered 85-record passes over four pages with strict reconciliation and merge preflight |
| Web of Science Core Collection | Clarivate normal Basic Search `Topic`, `Editions: All` | All six corrected strings executed with English/exact dates/no Document Type (including valid WS-A2 zero); Exact Search state recorded; unrestricted WS-B1 ordinary RIS preflight succeeded |
| IEEE Xplore | IEEE JSON search interface | All six corrected no-ContentType strings accepted; unrestricted I-B2 = 47 and completed two ordered 47-record passes over two pages with strict reconciliation and merge preflight |
| Compendex | Engineering Village Expert Search, Compendex only (historical pre-amendment pilot) | All six corrected strings accepted under autostemming-off/no-type controls; counts and one-page reconciliation recorded; prior Detailed CSV normalization path remains valid |
| Wiley Online Library | Advanced Search, unrestricted `Anywhere` | All six corrected strings accepted; broad W-B2 pagination reconciled through page 6; the later deterministic two-pass/native-RIS adapter gate in Section 10 supersedes the earlier export mechanics |
| ESA Indico | Whole root/event JSON census plus local attachment-first matcher | Frozen dictionary/code/fixtures passed; 408/408 event exports and all 6,770 material associations inventoried; 5,690 document-like URLs received retrieval/parse outcomes; corrected metadata/attachment A/B routes reconciled |
| NASA NTRS | Public citations JSON API plus representative normal-UI checks | Complete corrected 6×18 P×M matrix executed 108/108; every page reconciled; full-E local tag and A⊆B invariant passed |

### Inspec coverage-amendment validation completed 2026-08-10

Engineering Village accepted all ten then-current version-1.4 `C-*` strings with **Compendex and Inspec selected together**, All/Knovel clear, Published 2011–Latest plus the literal year/English suffix, autostemming off, Relevance, 100 records/page, no document-type filter, and source deduplication off. Every query completed two identical ordered opaque-ID passes with `retrieved == combined total`; `C-B1` reconciled 100+19 records and every other query fit one page. Complete database-only `C-B1` and `C-B2` comparators exactly equaled their respective partitions of the simultaneous result sets. A subsequent mixed-source RIS/JSON/CSV/merge smoke test preserved both database provenances. Counts and execution rules are in Section 9. These are `pilot_not_candidate_search` diagnostics, not final discovery.

### Springer Nature Link and ProQuest Index pilots completed 2026-08-10

Two read-only subagents separately investigated the added interfaces without inspecting the retained corpus. Springer's direct requests were challenge-blocked, and the ProQuest subagent stopped when its owned tab unexpectedly became another agent's Engineering Village tab; neither condition was treated as zero and no unrelated tab was touched. Bounded follow-ups used explicit owned browser target IDs and closed only those targets:

| Source | Pilot controls and aggregate result | Elapsed browser work |
|---|---|---:|
| Springer Nature Link | Whole Link; complete SN-B1/SN-B2; English; 2011–2026; Relevance; no type/access/venue facet: 114/252 | both counts stabilized within 2.2 s |
| Advanced Technologies & Aerospace Index on ProQuest | Exact Index only; complete NOFT PQ-B1/PQ-B2; `YR(2011-2026)`; `LA(English)`; no type/full-text/peer-review/source-deduplication limiter: 32/30 | 1.1/1.2 s; selection, both runs, and state restoration 5.3 s |

### AIAA ARC source-addition pilots completed 2026-08-10

Five read-only subagent jobs tested direct HTTP, source-method design, normal-browser queries, a 100-per-page hard-timeout follow-up, and page-size performance. ARC remained at `arc.aiaa.org`; direct HTTP was Cloudflare-challenged, while the normal visible-browser interface accepted complete ARC-A1/B1/B2 expressions and reported dynamic month-end totals 108/308/820. A one-tab benchmark reached count state in 3.649 seconds for finite A1 at 20/page and 4.413 seconds for finite A2 at 20/page; 20/page was fastest. Larger nominal page sizes rendered partial/lazy rows, so the final contract uses 20/page plus an exact expected-row assertion rather than maximizing page size. No result metadata, identifier values, screening decisions, or candidates were inspected. Details are in [`2026-08-10-aiaa-arc-source-addition-pilots.md`](searches/subagent-logs/2026-08-10-aiaa-arc-source-addition-pilots.md).

### IAF Digital Library public-adapter gate completed 2026-08-10

Read-only reconnaissance established normal anonymous XHTML routes for `/search/`, `/index/`, and canonical `/event/IAC-YYYY/paper/<paper-id>/` landing pages, plus the 500-character visible query limit, fixed adapter page size of 50, exact positive/zero summaries, and public title/author/year/DOI/abstract metadata. A single off-strategy `6GStarLab`/IAC-2024 smoke reconciled one source record and its complete public abstract while leaving `openAccess_pdf` empty. Twenty-one offline adapter tests, Ruff checks, and a normalized merge smoke then passed. No planned `IAF-P-YYYY` cell was run, the smoke record was not evaluated for eligibility, and neither the smoke nor its aggregate may enter the review. This is `pilot_not_candidate_search`, not authorization or final discovery.

The version-1.4 added-source runs and the pre-authorization IAF gate are `pilot_not_candidate_search`: no result was assessed, retained, or used as evidence. They validate source operation and provisional syntax only. Version 1.5 authorized IAF prospectively but did not promote its smoke record or any earlier aggregate to discovery.

The version-1.6 PQDT/OATD reconnaissance and aggregate browser checks are also `pilot_not_candidate_search`. A managed challenge, entitlement failure, unverified selection, syntax/interface failure, or incomplete count is total `null`, not zero; a successful aggregate count still supplies no candidate. Exact outcomes are recorded in [`search-log.md`](search-log.md) and [`2026-08-10-thesis-dissertation-source-pilots.md`](searches/subagent-logs/2026-08-10-thesis-dissertation-source-pilots.md).

Every version-1.2 observation is logged as `pilot_not_candidate_search` in [`search-log.md`](search-log.md); the finding-by-finding closure map is [`2026-08-07-press-finding-resolution.md`](searches/subagent-logs/2026-08-07-press-finding-resolution.md). Version-1.3 genericity/tailoring, version-1.4 source-amendment, version-1.5 completion, and version-1.6 thesis-source pilots are likewise no-screening diagnostics and are recorded separately. Under the authorized version-1.6 protocol, final discovery must rerun every accepted method, including all eleven PQDT/OATD partitions, `A3`, source-applicable `B-G`, `B-C1`, and `B-T2`, and the IAF population harvest/local classification from a clean version-1.6 final-run artifact set.

## 2. Anti-anchoring and provenance rules

1. Do not inspect Git history, deleted legacy search/corpus/extraction files, or retained source Markdown/PDFs while formulating or screening the independent planned-source candidate set.
2. Save every raw run, including zero-result, failed, malformed, and overbroad pilots. A failed request is not a zero-result search.
3. Read each complete saved result/export after every run; record both the source-reported total and records actually retrieved or parsed.
4. Give every artifact a new-run query/event ID and record source/database and platform, exact query/request/method, filters, run date/time/time zone, limits/pages or harvest coverage, status, assessment, and successor/predecessor refinement.
5. Do not import legacy IDs. Assign `eps-mbse-slr-2026-r####` IDs only after final merge/deduplication. A prior ID may later be recorded only as `legacy_corpus_id` after an independently rediscovered report is matched.
6. The retained `markdown/` and `pdfs/` directories are retrieval caches only. Match against them only after the complete successful-source baseline and explicit failure register for all fourteen version-1.6 sources/collections are frozen.
7. Buruso et al. (2026) is a named secondary-review seed and deferred recall benchmark. Do not use its bibliography to insert candidates into the independent baseline.

## 3. Eligibility-related search limits

- **Years/common cutoff:** first formal publication/issue from 2011-01-01 through the fixed review-wide cutoff 2026-08-10, inclusive, regardless of when a source or citation search is executed. When source controls admit the rest of 2026 or the rest of August 2026 (Scopus, IEEE Xplore, Engineering Village's Compendex/Inspec `Latest`, Wiley, Springer Nature Link's year-normalized dates, both ProQuest events, OATD's unrestricted native results, AIAA ARC's month-normalized dates, and IAF's event-year-only metadata), preserve the unaltered source total, then apply and log the same 2026-08-10 cutoff with the number removed or unresolved. For a degree work, retain formal issue/publication, defence, approval/award, repository deposit, public-release/embargo, and indexing dates separately; do not silently substitute deposit, harvest, indexing, or embargo-end date for the work's formal date. IAF and any 2026 thesis record exposing only a year remain unresolved until source-locatable exact-day evidence is found, never guessed. Any later evidence-window update requires a prospective protocol amendment and complete reruns of every source and citation route to one new common cutoff.
- **Language:** English where the source supports a reliable filter; otherwise screen full-report language. English translated metadata alone is insufficient.
- **Publication types:** full primary-research journal articles, conference/proceedings or workshop papers, research chapters, substantive institutional technical reports, completed master's-level theses, and completed doctoral dissertations/theses. Empirical comparison and experience reports are eligible. Undergraduate/bachelor or non-degree work, proposals/prospectuses, incomplete degree work, metadata/abstract stubs, abstract-only papers, posters, presentation/slides, and recordings may be discovery leads but are not primary evidence.
- **Population:** work that the source identifies as orbital CubeSat/nanosatellite-class. `PocketQube`, `picosatellite`, `CanSat`, generic `SmallSat`/small-satellite, and conventional/larger spacecraft are not positive concepts. A record found through another route qualifies only if a CubeSat/nanosatellite case is explicit and separable at full text.
- **Access:** do not intentionally limit discovery to open access. Source access and full-text retrieval status are logged separately.
- **Outcome and V&V terms:** optional supplementary concepts, never mandatory across the whole search.

## 4. Concept blocks

### P — population

`CubeSat`, `CubeSats`, `cube sat`, `nanosat`, `nanosatellite`, `nanosatellites`, `nano-satellite`, `nano-satellites`, `nano satellite`, `nano satellites`, and the source-supported `nanosat*` expansion. Any source-specific spelling variant added after a logged pilot must be versioned in the search dictionary and applied consistently; it cannot be added silently.

A dated pre-freeze spelling audit found additional yield after adding explicit plural forms in Compendex and Scopus, while IEEE and Wiley accepted those revisions without a displayed-count increase. The PRESS correction then added bare `nanosat` where wildcard behavior was unavailable and the ordinary spaced plural `"nano satellites"` in every translation. The final Boolean expressions below use the complete source-representable block consistently. NTRS cannot express an OR block, so every frozen NTRS form is a separate cell term. See the dated population and PRESS-fix pilot reports in `searches/subagent-logs/`. All are `pilot_not_candidate_search` checks, not recall estimates or evidence discovery.

Do not use unqualified `SmallSat` or `small satellite` in any planned population block or sensitivity probe. A source record containing those labels may still be screened if it was retrieved through a permitted population term, but the generic label does not establish eligibility.

### E — EPS

High-specificity terms:

- `electrical power system`, `electric power system`, `electrical power subsystem`, `electric power subsystem`, `EPS`, `power subsystem`, `electrical architecture`, `power architecture`, `PCDU`, `PMAD`.

Functional/analysis terms:

- `power budget`, `energy budget`, `energy balance`, `power generation`, `solar array`, `battery`, `batteries`, `energy storage`, `power conditioning`, `power distribution`, `power management`, `power interface`, `power mode`, `power modes`, `load profile`.

Bare `EPS` is always intersected with both population and model blocks in sources that support Boolean grouping, to suppress unrelated acronym senses.

### M — structured system model / MBSE

- `model-based systems engineering`, `model based systems engineering`, `model-based system engineering`, `model based system engineering`, `MBSE`, `SysML`, `systems modeling language`, `system model`, `systems model`, `system modeling`, `systems modeling`, `system modelling`, `systems modelling`, `reference model`, `digital engineering`, `Arcadia`, `Capella`, `object-oriented systems model`.

Broad `model-based` or `simulation` is insufficient alone. In EPS-free core-B retrieval, combine broad structured-model terms with a systems-engineering relation/concern block such as requirements, function/behavior, architecture, interfaces, traceability, parametrics, verification, or validation. In Stream A, the explicit EPS block supplies the additional precision, so A2/A3 intentionally retain `P AND E AND M_broad` without imposing R.

### G/C1/T2/R — bounded reusable-artifact and tailoring recall expansion

`G`, `C1`, and `T2` are conservative candidate-recall blocks, never genericity verdicts.

- **G1/G2 — precise artifacts:** generic, reusable, or configurable `model`/`system model`; `model template`; hyphenated/spaced mission-agnostic or mission-independent model/architecture; `reference architecture`; `domain model`; `metamodel`/`meta-model`; hyphenated/spaced product-line or product-family model; and complete `variation point AND model/architecture` constructs.
- **C1 — central reusable assets:** `reference model`/`system reference model`; complete model-library, model-pattern, model-profile, and `SysML profile` phrases; and a hyphenated/spaced US/UK domain-specific modeling-language phrase coupled to an MBSE/system-model anchor. Bare `library`, `pattern`, `profile`, or language is prohibited.
- **T2 — model-coupled tailoring:** the source's B2 structured-model block plus explicit reuse, tailor, customize/customise, configure, parameterize/parameterise, instantiate, variability/variation point, specialize/specialise, or adapt forms coupled to model(s) or architecture(s).

The preferred Boolean implementations are separate `P AND G1`, `P AND G2`, `P AND C1`, and `P AND M_B2 AND T2` queries, with complete provenance and a union only after each accepted partition is exhausted. No R term is required for precise G/C1 because a relation gate can suppress metadata-sparse artifact reports and can be lexically self-satisfied by `architecture`. For G/C1 expansion records, `R_ALL` (requirements, functions/US-UK behavior, architecture, interfaces, traceability, parametrics, verification, validation) may be retained as an optional precision/provenance tag; this does not remove the required R block from the retained broad-model bibliographic B2 core strategy. If an operationally necessary relation-gated fallback is prospectively piloted, use `G_M AND R_ALL` versus `G_A AND R_NO_ARCH` as separate cells and compare it against relation-free G; never use unsplit `G AND R_ALL`.

Only full-text Route A/B screening establishes MBSE qualification and an EPS bridge. C1/G/T2 retrieval is no evidence of a reusable EPS artifact, and no core-B record must contain these terms. Report each expansion's overlap and unique yield against core B and the accepted cumulative union. A source-adapted partition may be structurally tag-only—for example, T2 where local core B is already `P AND M` without R—but the term hits are still retained for RQ1-G characterization.

### O/V — selected, non-exhaustive outcome, burden, and V&V sensitivity probes

These lists define the broader optional tagging vocabulary. The exact `*-O1` and `*-V1` strategies below use one finite, source-independent subset so that probe and local-tag yields are semantically comparable without assuming wildcard, stemming, or lemmatization equivalence. They are sensitivity probes/tags, not complete translations or baseline eligibility filters. The subset avoids making outcome or V&V reporting mandatory. Any later expansion requires a separately logged syntax/count pilot.

- **Exact O1 finite subset:** `reliability`, `reliable`, `mission assurance`, `reproducibility`, `reproducible`, `reuse`, `reusable`, `integrability`, `integrable`, `interoperability`, `interoperable`, `traceability`, `traceable`, `benefit`, `benefits`, `impact`, `outcome`, `no effect`, `adverse`, `burden`, `effort`, `workload`, `overhead`, `cost`, `schedule`, `training`, `learning curve`, `licensing`, `license`, `licence`, `adoption`.
- **Exact V1 finite subset:** `verification`, `validation`, `traceability`, `traceable`, `model verification`, `model validation`, `system verification`, `system validation`, `requirements-in-the-loop`, `model checking`, `virtual integration`, `MIL`, `model-in-the-loop`, `SIL`, `software-in-the-loop`, `PIL`, `processor-in-the-loop`, `HIL`, `hardware-in-the-loop`, `test case`, `test procedure`.
- **Broader optional extraction/tag vocabulary:** `interface consistency`, `lifecycle continuity`, `time`, `skill`, `resource`, `maintenance`, `governance`, `V&V`, `design verification`, `design validation`, and `model-to-test`, together with the exact O1/V1 forms above.
Tailoring operations and footprint are additionally tagged within every retrieved record. The 2026-08-10 T1 probe was a strict subset of core B1∪B2, but the later T2 design replaces B2's relation gate with a model/architecture-coupled tailoring block and produced opaque additions; T1 therefore remains superseded and cannot justify omitting T2.

## 5. Common execution and PRISMA-S log rules

For every source, preserve the source/platform name, actual web/API/script interface and version where known, endpoint, exact source-native query or request, all limits and filters, date/time/time zone, reported total, retrieved/parsed total, pagination or event coverage, raw filenames and checksums, operator, refinement history, and final disposition (`planned`, `piloted`, `accepted_final`, `replaced`, `failed`, or `not_run`, with predecessor/successor IDs). Also record whether the interface exposes automatic stemming, lemmatization, or term expansion and its observed state/default; explicit frozen variants remain in the strategy regardless. Draft strings below are not evidence that a search ran. The final supplement must reproduce the exact strings, request bodies, matching dictionaries, and methods actually executed—not cleaned translations.

For every browser-backed source, keep the search fast and safe in a shared Chrome session: default to one source-owned browser process and tab/target with a unique run name and private temporary directory; retain and re-check its target ID and hostname before every action; and ignore unexpected unrelated tabs. A source-specific method may reuse an existing tab only when the operator explicitly authorizes its exact target ID: never select it by tab position, re-check the ID and hostname before each navigation, assert the expected page state around other actions, and leave that user-owned tab open. Otherwise never navigate, reuse, or close a tab that the run did not create. Submit frozen URLs/forms, count, paginate, and export mechanically with asserted state transitions and bounded waits rather than model decisions or fixed sleeps between records. Prefer one complete native export over page-by-page browser reading when it preserves the full set, but reconcile it to the rendered source total and ordered source IDs. Close only owned targets and restore only source state deliberately changed by the run.

Before the first valid run in each source, record the selected interface and its pagination/export behavior in the search log. Where a source changes syntax, facets, pagination, or export behavior, retain the failed attempt and pilot the correction. A source failure must be documented; it is not permission to silently omit that source. Search-source duplicates are retained as discovery events until the merged record-level deduplication stage.

Apply the official [PRISMA-S checklist](https://www.prisma-statement.org/prisma-search) as follows:

| PRISMA-S item | Execution/reporting rule for this review |
|---|---|
| 1. Database and platform | Name each source and the actual platform, interface, endpoint, and provider used. Report Advanced Technologies & Aerospace Index and PQDT Global as two separate exact-database events on the ProQuest Platform, each with independent selection proof, strategy, count, export, and provenance. |
| 2. Multi-database searching | Every Engineering Village `C-*` event searches Compendex and Inspec simultaneously. Report both database names, Engineering Village as platform, the exact paired selection, combined total, database-specific record counts, and how database instances were retained through later deduplication. The two ProQuest databases are deliberately not searched together, so Item 2 does not combine their events. |
| 3. Registries | No study registry search is planned; report this explicitly rather than treating a bibliographic source as a registry. |
| 4. Online resources/browsing | Log the full Wiley, Springer Nature Link, and AIAA ARC publisher-platform searches, the two separate exact-database ProQuest events, the whole native OATD index search and its linked-repository boundary, the authorized IAC-only IAF Digital Library population harvest/local match, whole-instance ESA harvest, full NTRS search, and every deliberate venue/website coverage audit with scope, method, date, yield, and stopping rule. Report OATD in the PRISMA website/other-methods channel. |
| 5. Citation searching | Use the complete reference list for backward chasing and both Scopus and Web of Science Core Collection for forward chasing; log seed set, direction, exact index/interface, cycles, yield, decisions, failures, and stopping outcome as an “other source.” |
| 6. Contacts | Author/expert contact is not an unlogged discovery route. If later used for retrieval or clarification, log who/what was sought, date, outcome, and resulting discovery provenance; otherwise report that no contacts were used. |
| 7. Other methods | Report Buruso and retained-file checks as deferred recall audits, not direct sources; distinguish discovery from manual retrieval. |
| 8. Full strategies | Preserve each source-native strategy/request/dictionary exactly as executed, including syntax, fields, filters, partitions, and failed/replaced runs. |
| 9. Limits/restrictions | Report and justify date, language, population, publication-type, field, pagination/harvest, and access restrictions and every source-specific exception. |
| 10. Search filters | No published search filter is currently used. If that changes, cite it, identify modifications, and preserve the exact implementation. |
| 11. Prior work | No legacy strategy is reused. Disclose and cite any later substantive adaptation of another review's strategy. |
| 12. Updates | The evidence cutoff is frozen at 2026-08-10. Any update requires a prospective protocol amendment, one new common cutoff, and complete reruns of every electronic and citation source as separate search events; do not imply an update occurred if none did. |
| 13. Search dates | Record the last-run date for every final query, ESA harvest/match, NTRS cell, citation cycle, and other source—not one global date. |
| 14. Peer review | Interface pilots and model/subagent checking are not formal information-specialist peer review. If human search peer review is later arranged, log reviewer, framework, date, feedback, and changes; otherwise report that none occurred. |
| 15. Records identified | Preserve source-reported and actually retrieved totals per run, plus source/stream unions before deduplication, and reconcile them to the PRISMA flow. For Engineering Village, preserve the simultaneous combined total and separate Compendex/Inspec record counts before cross-database deduplication. Preserve separate ATAI, PQDT, and OATD totals and their overlap; OATD remains in the website/other-methods channel. For IAF, distinguish each annual source P-query total, records retrieved, locally population-confirmed records, local core-B and G/C1 partitions, E/R/T2/V1/O1 tags, missing-abstract leads, and the final candidate union. |
| 16. Deduplication | Record software/version, normalization, matching precedence/thresholds, manual adjudication, and counts removed. Keep record deduplication separate from report-family mapping. |

For PRISMA 2020 flow arithmetic, this review makes one explicit, frozen classification decision: OATD alone is in `other_methods` / `website`; each of the other thirteen bounded structured operational collections is in `databases_and_registers` / `database`, regardless of whether its transport is a browser, API, export, or local harvest. No source appears in both channels. Engineering Village's combined total and a combined ProQuest platform total are never extra identification units; OATD-linked repositories are retrieval provenance only. The exact fourteen-source/twelve-interface crosswalk and final manifest/failure schemas are [`final-run-source-crosswalk-v1.6.json`](searches/final-run-source-crosswalk-v1.6.json), [`final-run-manifest-schema-v1.6.json`](searches/final-run-manifest-schema-v1.6.json), and [`failure-register-schema-v1.6.json`](searches/failure-register-schema-v1.6.json), with current-byte SHA-256 values `48caa54a0624630c3f2fb1b69e2dc2dec99fcb13632a7e83743263241a89b25c`, `fd6720eac1bd6e66021c4517ad94b68bd5330905b5ae75f3a1e4af24c63398f1`, and `6953266f0be7ca902638bdcf18681958391ace4eaea99e40e9e8e0d182d22658`, respectively. `final_run_governance_lint.py` (`9ef6622a0955ad647536c83e443391abf83aa6afbd5c217ef5904db4a86a8588`) validates 14 sources/12 interfaces with two positive and eight negative synthetic contracts; the two added schema-valid negatives prove that duplicate source IDs and a valid-but-wrong OATD interface/PRISMA mapping fail crosswalk binding. Its optional `--manifest PATH` schema-validates and binds any future real manifest to the exact 14 source IDs each once, exact interface/PRISMA mappings, and the current crosswalk byte hash; it creates no real manifest/root. The independent audit's medium governance issue is resolved.

Source-interface validation before freeze and all later amendment validations are diagnostic only. Preserve their exact requests and aggregate behavior, label them `pilot_not_candidate_search`, and rerun every accepted version-1.6 strategy after authorization in clean final storage. The pre-authorization IAF adapter gate remains diagnostic and cannot be relabelled as final discovery. Pilot hits cannot establish evidence membership or the independent baseline.

Preserve every source-native structured export. In addition, create one normalized JSON or CSV artifact per query/batch for `merge_search_results.py`. Compatible CSV columns are `Search source`, `Query`, `Rank`, `Paper ID`, `DOI`, `Title`, `Authors`, `Publication year`, `Abstract`, `Citation count`, `URL`, `Open access PDF`, and `Source total`; `Search source`, exact `Query`, and global result `Rank` are required for provenance even when the native export omits them. Never overwrite or mislabel the native export. Run a merge smoke test on each source's first normalized batch before final retrieval continues. For Scopus and IEEE API routes, a partial page is never a merge input: the first merge preflight is the first successful complete, reconciled normalized pass.

## 6. Scopus validated API and planned searches

Use the Elsevier Scopus Search API (`https://api.elsevier.com/content/search/scopus`, `COMPLETE` view) with Scopus `TITLE-ABS-KEY` concept blocks, explicit `PUBYEAR AFT 2010` and `PUBYEAR BEF 2027` limits, and English. Apply **no discovery document-type restriction**; verify publication type during screening so reports, secondary-review leads, and atypically indexed eligible manifestations are not silently suppressed. Never serialize an API key, cookie, or access token.

The Search API request exposes no separate automatic stemming/lemmatization parameter in the validated template. Record that absence and any changed source documentation/default at final execution; never infer singular/plural or US/UK equivalence, because the explicit variants below remain mandatory.

Pre-freeze diagnostics on 2026-08-06 accepted all six original strings. API totals were: S-A1 = 3, S-A2 = 9, S-B1 = 75, S-B2 = 55, S-V1 = 1, and S-O1 = 4. A complete diagnostic retrieval of S-A1 reconciled all 3 records and normalized JSON merged successfully. On 2026-08-07, the normal Scopus web UI accepted the revised population block and returned S-B1 = 80 versus 75 under matched web-UI controls. An initial API retry failed authentication and produced invalid empty shells, but a later institutional-network retry successfully reproduced original S-B1 = 75 and revised S-B1 = 80 in `COMPLETE` view. These are `pilot_not_candidate_search` observations; under version-1.6 authorization, confirm API authentication afresh and run the seven current core/sensitivity strategies (including new S-A3 and revised S-V1/O1) plus the four expansion partitions using only clean final-run artifacts for discovery. An initial relation-gated combined G query retrieved 12 records with 9 opaque additions over the fresh 126-ID S-B1∪S-B2 union, but that formula was superseded because architecture-bearing artifacts could self-satisfy its R block. Follow-up two-pass Scopus pilots accepted relation-free G1 (5 total; 4 additions), relation-free G2 (8; 6), C1 (24; 7), and T2 (26; 2); all had stable ordered passes and no exact-day removal/unresolved record. No title, abstract, eligibility, or evidence assessment occurred, so these are recall diagnostics only.

### Scopus request template, pagination, and acceptance rule

The versioned non-secret template is [`searches/api-pagination-request-templates.json`](searches/api-pagination-request-templates.json). Its `prospective_final_execution.scopus` object contains the corrected no-type-filter S-B1 preflight request; the separate top-level `scopus` object preserves the historical MAJOR-06 pilot descriptor only. For every final `S-*` execution, start from the prospective object, replace only `query` with the complete corresponding displayed string below—already including its year clauses—and retain every other template field:

- **GET** `https://api.elsevier.com/content/search/scopus`; `Accept: application/json`; supply `X-ELS-APIKey` only from the secure runtime environment, never in an URL, artifact, log, or command transcript.
- Query parameters: `count=25`, `start=0,25,50,…`, `view=COMPLETE`, `sort=eid`, and `httpAccept=application/json`. The historical delegated pilot observed `start=0,25,50,75` and pages of 25, 25, 25, and 5 against 80. The PRESS-corrected unrestricted S-B1 preflight then observed the same offsets and a terminal `start=75` page of 10 against 85. `start` is therefore frozen as zero-based offset pagination, not a cursor.
- Treat `search-results.opensearch:totalResults` on page 1 as the snapshot total; require it unchanged on every subsequent page. Use `entry.eid` in returned order as the page ID, `sort=eid` as the declared source ordering, and preserve ranks `start + 1` through `start + returned_count`. The corrected preflight's full 85-ID sequence was non-increasing by EID and identical across two complete passes. When the complete result fits one terminal page, Scopus may advertise `itemsPerPage` as the actual terminal count rather than requested 25; accept only requested 25 or the exactly computed terminal count, never a short nonterminal page.
- Use [`searches/tools/api_pagination_reconcile.py`](searches/tools/api_pagination_reconcile.py), not an arbitrary `max-pages` limit, to retrieve computed pages to exhaustion. It uses a 30-second timeout; retries network/408/425/429/5xx failures three times after the initial attempt with `Retry-After` or capped exponential backoff; stops on redirects, access/authentication responses, malformed JSON, unexpected offsets, short/nonterminal pages, duplicated page-ID sequences/IDs, or a changed total. One changed-total snapshot is restarted from page 1; a repeated change is a source failure. It writes ordered page-ID/global-rank reconciliation, detects missing pages, and fails unless `retrieved == source total` and a second complete pass has the same ordered IDs.
- Retain raw pages and normalized/merge-preflight outputs only in the access-controlled, Git-ignored run directory. Do not merge or screen a failed snapshot; a `pilot_not_candidate_search` snapshot is superseded and never a review candidate. After a successful **final** snapshot, run the normalizer/`merge_search_results.py` only on its successful normalized pass and retain the source total and global ranks.

The 2026-08-07 S-B1 multi-page pilot, tool/runtime checksums, retry/stop rules, and no-screening archive manifests are recorded in [`2026-08-07-scopus-ieee-multipage-api-validation.md`](searches/subagent-logs/2026-08-07-scopus-ieee-multipage-api-validation.md). This resolves API-page behavior only; it does not substitute pilot results for a post-authorization final execution.

### S-A1 — explicit EPS names × explicit MBSE/language

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-A2 — EPS analyses/interfaces × structured system model

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model") AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-A3 — explicit EPS names × broad structured system model

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-B1 — embedded-thread baseline with explicit MBSE/languages

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-B2 — embedded-thread structured-model expansion

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-BG1 — relation-free precise reusable-model/template artifacts

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture") AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-BG2 — relation-free structural reusable artifacts

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture))) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-BC1 — conservative central reusable assets

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model"))) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-BT2 — model/architecture-coupled tailoring

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY(((reuse OR reuses OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures))) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

These four separately reconciled queries are required terminology partitions, not genericity/tailoring classifications. Do not replace them with the rejected combined X1 shortcut or the superseded unsplit G×R query.

### S-V1 — EPS-linked V&V sensitivity probe

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND TITLE-ABS-KEY(verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure") AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-O1 — outcome and implementation-burden sensitivity probe

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND TITLE-ABS-KEY(reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

## 7. Web of Science Core Collection validated browser interface and planned searches

Search **Web of Science Core Collection**, not All Databases, through Clarivate's normal browser interface at <https://www.webofscience.com/wos/woscc/basic-search>. Use Basic Document Search with one complete Boolean expression in the **Topic** field. Before every final run, confirm `Search in: Web of Science Core Collection` and `Editions: All`, with all available Core Collection editions selected: SCI-EXPANDED, SSCI, AHCI/A&HCI, CPCI-S, CPCI-SSH, BKCI-S, BKCI-SSH, ESCI, CCR-EXPANDED, and IC. Preserve the edition list because entitlements and available coverage may change.

Apply source-native controls for Publication Date from `2011-01-01` through the common evidence cutoff `2026-08-10` and Language = `English`. Select **no Document Type restriction** at discovery; verify publication type during screening. Do not restrict by organization, research area, source title, open-access status, citation count, or individual Core Collection edition. Preserve the Basic Search history entry, exact Topic string, controls, selected editions, run date/time/time zone, source total, declared sort, page size, and complete result/export reconciliation. If Advanced Search is used as a fallback, log its `TS=`/`PY=` strategy as a distinct source-native implementation and demonstrate set equivalence rather than assuming it.

Before each final run, open the current WoS Search Settings and record the observed **Exact Search/lemmatization** control and state. Use the same documented state for all final runs and retain every explicit spelling/number variant regardless; equal counts never establish expansion equivalence. If the Basic Search route no longer exposes or reports the control, record the source default as observed rather than guessing.

A 2026-08-07 PRESS-corrected Basic/Topic pilot used Publication Date `2011-01-01`–`2026-08-07`, English, Editions All, and no Document Type restriction. Dynamic totals were WS-A1 = 1, WS-A2 = 0 (the clean follow-up displayed `Your search found no results`), WS-B1 = 43, WS-B2 = 34, WS-V1 = 1, and WS-O1 = 1. Final B1 versus the same query minus only `"nano satellites"` was 43 versus 43; unrestricted versus the old three-type restriction was also 43 versus 43, with no set-equivalence inference. The Advanced `Exact search` switch was observed unchanged at `aria-checked=false`; no expansion semantics were inferred. Corrected unrestricted WS-B1 also completed an ordinary non-Fast-5000 one-record RIS export. These are `pilot_not_candidate_search` observations; rerun every strategy and export preflight after authorization. Full observations are in [`2026-08-07-press-browser-source-validation.md`](searches/subagent-logs/2026-08-07-press-browser-source-validation.md). A later relation-free G1/G2 follow-up displayed diagnostic totals 2/4 but could not execute the required English refinement, so both runs are failures rather than accepted sets. C1/T2 follow-ups were likewise provisional only. The clean version-1.6 run must execute all eleven WS strategies, including new WS-A3, revised WS-V1/O1, and English-controlled WS-BG1/2, WS-BC1, and WS-BT2, or report a source failure; pilot diagnostics cannot substitute.

Use Relevance sort and a declared page size (50 was observed). Read and reconcile every results page, retaining global rank. Use **ordinary Export**, never Fast 5000, in source-supported ranges no larger than 1,000 records. A one-record pilot validated RIS with Custom selection (30), including the WoS accession number, DOI, title, authors, publication year, abstract, editions, and cited references; preserve native RIS unchanged. Normalize each batch with `academic-search/scripts/ris_to_merge_csv.py`, supplying source `Web of Science Core Collection`, the exact query, zero-based rank offset, and source total. Preserve cited references in the native RIS and a reproducible sidecar because the common merge schema does not carry them. Then run `merge_search_results.py`, whose regression-tested alias canonicalizes this source as `web_of_science_core_collection`. Repeat a one-record export/normalization/merge preflight after authorization before bulk export. If ordinary export redirects to authentication or fails, log the failure and obtain an authorized manual export; do not use the Fast 5000 login path as an undocumented substitute.

### WS-A1 — explicit EPS names × explicit MBSE/language

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### WS-A2 — EPS analyses/interfaces × structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### WS-A3 — explicit EPS names × broad structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")
```

### WS-B1 — embedded-thread baseline with explicit MBSE/languages

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### WS-B2 — embedded-thread structured-model expansion

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)
```

### WS-BG1 — relation-free precise reusable-model/template artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture")
```

### WS-BG2 — relation-free structural reusable artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))
```

### WS-BC1 — conservative central reusable assets

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model")))
```

### WS-BT2 — model/architecture-coupled tailoring

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND ((((reuse OR reuses OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures))))
```

These four expansions use the same Topic field and common controls as WS-B1/B2 and are reconciled separately before union.

### WS-V1 — EPS-linked V&V sensitivity probe

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### WS-O1 — outcome and implementation-burden sensitivity probe

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption)
```

## 8. IEEE Xplore validated interface and planned searches

Use IEEE Xplore's JSON search interface at `https://ieeexplore.ieee.org/rest/search` through the source-native pagination reconciler, with unfielded Boolean metadata search, inclusive years 2011–2026, and language `English`. Apply **no Content Type refinement** at discovery; verify publication type during screening. Obtain the source total from the reconciler's first page and retrieve the complete result set under the fixed request template; do not treat a count-only response as complete retrieval.

The validated JSON request exposes no separate automatic stemming, lemmatization, or term-expansion parameter. Record that absence and any interface-default statement observed at final execution; the explicit singular/plural and US/UK forms below remain mandatory.

Pre-freeze diagnostics on 2026-08-06 accepted all six original strings and all intended facets. Displayed/API totals were: I-A1 = 4, I-A2 = 2, I-B1 = 38, I-B2 = 42, I-V1 = 1, and I-O1 = 4. A complete diagnostic retrieval of I-A1 reconciled all 4 records and normalized JSON merged successfully. On 2026-08-07, the revised complete population block was accepted; I-B1 remained 38, I-V1 remained 1, and I-O1 remained 4. Equal counts do not prove identical sets. These counts and records are `pilot_not_candidate_search`; run the seven current core/sensitivity queries (including new I-A3 and revised I-V1/O1) plus the four expansion partitions under version-1.6 authorization, preserve fresh count/full retrieval, and use only those final reruns for discovery. An initial relation-gated G query retrieved 7 records and six confirmed-date additions, but its unsplit architecture relation was superseded. Follow-up two-pass relation-free pilots found G1 = 0; G2 = 7 raw/6 exact-day-confirmed with six additions; C1 = 22 raw/21 confirmed with six additions; and T2 = 22 raw/19 confirmed with six additions. Unresolved dates remained separate and no record was screened.

### IEEE Xplore request template, pagination, and acceptance rule

The versioned non-secret template is [`searches/api-pagination-request-templates.json`](searches/api-pagination-request-templates.json). Start from `prospective_final_execution.ieee_xplore` (not the preserved historical top-level `ieee_xplore` pilot descriptor). For every final `I-*` execution, replace only `queryText` with the corresponding displayed query below and retain the observed request fields: `action=search`, `newsearch=true`, `matchBoolean=true`, `matchPubs=true`, `highlight=false`, `returnType=SEARCH`, `rowsPerPage=25`, `sortType=newest`, `ranges=["2011_2026_Year"]`, and the sole refinement `Language:English`. Do not add a `ContentType` refinement. The fixed non-secret HTTP headers are in that template; never persist `userInfo`, cookies, or any access context.

The historical delegated I-B2 pilot observed one-based `pageNumber=1,2`, with `startRecord/endRecord` 0/25 then 25/42. The PRESS-corrected no-type-filter I-B2 preflight observed 0/25 then 25/47, 25 and 22 records, and `totalPages=2`; `pageNumber=0` aliased the first page during a separate probe and is prohibited. `sortType=newest` changed the first-page ordered-ID sequence from the default/relevance sequence; the corrected preflight's full 47 `articleNumber` IDs were identical across two complete passes. Preserve source response order as global ranks 1–47; do not invent a cursor or an unobserved sort field.

Use [`searches/tools/api_pagination_reconcile.py`](searches/tools/api_pagination_reconcile.py) with the common retry, total-change, missing-page, duplicate-ID/page, and strict `retrieved == source total` rules in the template. IEEE may report `totalPages=1` for a valid zero-record response; the reconciler accepts that convention only while fetching one empty page in each pass and requiring source total, retrieved count, and unique-ID count all to equal zero. It retries network/408/425/429/5xx failures three times after the initial request with `Retry-After` or capped exponential backoff, treats redirect/access/challenge/non-JSON responses as failures, reruns one whole snapshot after a changed total, and requires an identical second full ordered-ID pass. Do not merge or screen failed snapshots; pilot outputs remain superseded `pilot_not_candidate_search` artifacts. The empirical run, checksums, archive manifests, and merge preflights are in [`2026-08-07-scopus-ieee-multipage-api-validation.md`](searches/subagent-logs/2026-08-07-scopus-ieee-multipage-api-validation.md).

### I-A1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### I-A2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR batteries OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### I-A3 — explicit EPS names × broad structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")
```

### I-B1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### I-B2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation)
```

### I-BG1 — relation-free precise reusable-model/template artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture")
```

### I-BG2 — relation-free structural reusable artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))
```

### I-BC1 — conservative central reusable assets

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model")))
```

### I-BT2 — model/architecture-coupled tailoring

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (((reuse OR reuses OR reused OR reusable OR reusing OR tailor OR tailors OR tailored OR tailoring OR customize OR customizes OR customized OR customizing OR customization OR customise OR customises OR customised OR customising OR customisation OR configure OR configures OR configured OR configuring OR configuration OR parameterize OR parameterizes OR parameterized OR parameterizing OR parameterization OR parameterise OR parameterises OR parameterised OR parameterising OR parameterisation OR instantiate OR instantiates OR instantiated OR instantiating OR instantiation OR variability OR "variation point" OR specialize OR specializes OR specialized OR specializing OR specialization OR specialise OR specialises OR specialised OR specialising OR specialisation) AND (model OR models OR architecture OR architectures)) OR ((adapt OR adapts OR adapted OR adapting OR adaptation) AND (model OR models OR architecture OR architectures)))
```

These four separately reconciled queries are required terminology partitions, not genericity/tailoring classifications.

### I-V1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### I-O1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption)
```

## 9. Engineering Village (Compendex + Inspec) validated interface and planned searches

Search **Compendex and Inspec simultaneously on Elsevier Engineering Village** through Expert Search at <https://www.engineeringvillage.com/search/expert.url?database=1>. The URL initializes the validated Expert form; it is not evidence of the final database scope. In the database control select **both Compendex and Inspec**, leave **All and Knovel clear**, and preserve the paired selection and the source summary `Compendex & Inspec` for every run. Do not add `(cpx WN DB)`: besides being absent from the current displayed code table, it would suppress the required Inspec records. The historical `C-*` prefix is retained as a stable query ID, but every final `C-*` event now means one paired Engineering Village search, not a Compendex-only run or two separately translated searches.

Use `KY` (`Subject/Title/Abstract`) for concept blocks in the paired search, uppercase Boolean, double-quoted phrases, and explicit wildcards. Use the literal suffix `AND (2011-* WN YR) AND (({English}) WN LA)` and also display/log Published = 2011–Latest in the UI. Set **Turn autostemming off** to checked, because the strategy already prespecifies variants and wildcards and the pilot showed that changing this control materially changes retrieval. Use Relevance sort and set and verify **fixed visible 25 records/page**. Fixed visible page size is enumeration transport only, not search-set semantics: it changes neither the paired database selection nor the frozen query or other controls. For every pass, retrieve all pages, require exactly 25 visible rows on every nonterminal page, and require terminal arithmetic against a source total that remains stable on every page and across both passes. Do not apply a document-type filter at discovery: the databases expose journal, conference, chapter, article-in-press, book, report-related, dissertation, and other values, and filtering could suppress an eligible or useful lead. Apply the protocol's publication-type rule during screening.

Leave Engineering Village's **Remove duplicates** function unapplied. Preserve the simultaneous source total, each row's displayed `Database: Compendex` or `Database: Inspec` provenance, the separate database counts, global source order/rank, and every database instance. Require the database counts and retrieved rows to reconcile to the combined total. For every `C-*` query, complete two fresh, independent, value-blind passes with identical ordered `(global rank, database label, source-prefixed opaque handle)` ledgers. Reconcile complete native RIS against the complete paired ledger before normalization and merge, retaining database labels/handles and all native artifacts; only the complete reconciled set may be normalized or merged. A record indexed in both databases remains two discovery instances until the review's documented record-level deduplication stage. A missing/unselected database, non-paired selection, missing row-level database label or handle, conflicting total, short/nonterminal page, terminal-arithmetic failure, order mismatch, incomplete RIS reconciliation, or unreconciled page is a failed paired run, not permission to accept a Compendex-only fallback or a partial prefix. Database-only searches may be used for logged troubleshooting or partition verification but do not replace the required simultaneous final event.

### C-A1

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-A2

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model") WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-A3 — explicit EPS names × broad structured system model

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) WN KY) AND (("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-B1

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-B2

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") WN KY) AND ((requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-BG1 — relation-free precise reusable-model/template artifacts

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture") WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-BG2 — relation-free structural reusable artifacts

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture))) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-BC1 — conservative central reusable assets

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model"))) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-BT2 — model/architecture-coupled tailoring

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") WN KY) AND ((((reuse OR reuses OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures))) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

These four expansions retain paired Compendex-and-Inspec, autostemming-off, no-type, year, and language controls and are reconciled separately.

### C-V1

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure") WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-O1

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

The first browser diagnostic validated the original expressions under controls later superseded. A 2026-08-07 PRESS-corrected pilot used the then-current six version-1.2 strings with Compendex only, Published 2011–Latest, the literal year/language suffix, autostemming off, Relevance, 100/page, and no type filter: C-A1 = 3, C-A2 = 6, C-B1 = 76, C-B2 = 58, C-V1 = 1, and C-O1 = 1. Final B1 versus the same text minus only `"nano satellites"` was 76 versus 76; equal totals do not prove equal sets. A 2026-08-10 relation-free Compendex-only follow-up reconciled C-BG1 = 4 and C-BG2 = 8, union 12, with eight opaque IDs outside a fresh 111-ID B1∪B2 set; C1/T2 attempts failed and were not zeros. These historical pilots do not validate omission of Inspec.

### 2026-08-10 paired-database amendment pilot

All ten then-current version-1.4 strings (before A3 and the revised V1/O1 forms) were rerun with Compendex and Inspec selected together under the complete planned controls. Totals are live **database-record** diagnostics before cross-database deduplication:

| Query | Compendex records | Inspec records | Combined total | Reconciled pages at 100/page |
|---|---:|---:|---:|---|
| C-A1 | 3 | 2 | 5 | 5 |
| C-A2 | 6 | 2 | 8 | 8 |
| C-B1 | 77 | 42 | 119 | 100 + 19 |
| C-B2 | 59 | 35 | 94 | 94 |
| C-BG1 | 4 | 1 | 5 | 5 |
| C-BG2 | 8 | 2 | 10 | 10 |
| C-BC1 | 23 | 17 | 40 | 40 |
| C-BT2 | 23 | 16 | 39 | 39 |
| C-V1 | 1 | 1 | 2 | 2 |
| C-O1 | 1 | 1 | 2 | 2 |

Every paired query completed two identical complete ordered-ID passes; database labels agreed with the source-prefixed opaque row handles, IDs were unique within each combined pass, database counts summed to the combined total, and `retrieved == total`. Separate complete database-only comparators confirmed that the 77-record Compendex and 42-record Inspec `C-B1` sets exactly equaled the corresponding partitions of the 119-record paired set; the analogous `C-B2` comparison was 59 + 35 = 94 with exact partition equality. This verifies the simultaneous implementation and material Inspec yield, not relevance, eligibility, recall, or final counts. No record was screened or admitted to the corpus. The private aggregate is under `.searches/eps-mbse-slr-2026/inspec-amendment-pilots/2026-08-10/`; its manifest SHA-256 is `9891d9987925579548cf097e05229bcaf8e0b3cd666202d28b68fbb950cd0f20`. All eleven current C strategies, including new C-A3 and revised C-V1/O1, must be run in clean version-1.6 final storage.

### V16-C prospective 25/page transport amendment — 2026-08-11

All earlier 100/page observations above, including the `Reconciled pages at 100/page` table, remain historical `pilot_not_candidate_search` diagnostics. The 2026-08-11 V16-C 100/page pilot remains failed (`total: null`): its two-row control snapshot was rejected, and no query result, RIS, normalized/merge output, or partial prefix was imported. The prospective 25/page successor does not retroactively accept that failed pilot.

A later existing-CDP control probe stopped before mutation or query submission because the current shared selection had All+Knovel selected. Its fixed result was `NULL_CURRENT_SELECTION_NOT_PAIRED_NO_MUTATION`, with `total: null` and evidence SHA-256 `640f625c2000b94ba6ae33e622e2b393519a00354fec2c06892f13f39816834c`; it supplies no page-size result. A canceled pre-execution draft that would have launched fresh Chrome supplied no source evidence.

The fixed-visible-25/page successor is authorized for implementation only, not accepted. It requires a fresh complete rerun under the Section 9 paired-control, pagination, two-pass, RIS-reconciliation, normalization, and merge contract; no partial prefix may be accepted.

The source summary can retain a broad coverage label despite the literal year clause, so retain both the `YR` clause and UI Published control, audit every exported publication date from both databases, preserve the source and database totals, and log removals after the common 2026-08-10 cutoff.

Engineering Village exposed EndNote/RIS, BibTeX, ASCII, CSV, Excel, PDF, and RTF, with Current page, Citation, Abstract, and Detailed record options and a session basket labelled to 5,000 selected records. A historical Compendex-only one-record **CSV Detailed record** pilot produced a native file with 29 columns; because it omitted exact query and rank, a normalized CSV added the common provenance columns and passed `merge_search_results.py`.

A 2026-08-10 post-amendment live smoke test updated `search_compendex.py` with explicit `--databases compendex`, `--databases inspec`, and paired `--databases compendex inspec` modes. The paired `C-V1` route reconciled and exported two records in one normal same-origin RIS request with database mask `3`, one row from each database. Normalized JSON and CSV retained distinct row sources and database-specific record URLs; the updated `merge_search_results.py` deduplicated the shared DOI to one record while preserving separate `inspec` and `compendex` provenance events. Separate one-record Inspec-only (mask `2`) and backward-compatible default Compendex-only (mask `1`) live runs also passed. The aggregate-only private artifact is `.searches/eps-mbse-slr-2026/inspec-amendment-pilots/2026-08-10/tool-smoke.json` (SHA-256 `73a15643ba3455c0348280f572d80cb777487b4c25cb9274bd5f099133506340`). This resolves the prior mixed-source tooling blocker for pilot use, but the clean final run must repeat the export/normalization/merge preflight and preserve its artifacts.

In normalized output, set `Search source` to the row's actual database (`Compendex` or `Inspec`), retain the shared `C-*` query event, combined total, and combined global rank, and preserve database-specific totals in a sidecar or manifest. Preserve native and normalized files separately, export the complete paired set in logged batches, save the Search Summary, and reconcile totals, pages, database labels, selections, and export batches.

Official platform documentation checked on 2026-08-06, with the Inspec product page checked on 2026-08-10:

- <https://www.elsevier.com/products/engineering-village/databases/compendex>
- <https://www.elsevier.com/products/engineering-village/databases/inspec>
- <https://www.elsevier.support/engineering-village/answer/how-can-i-improve-my-expert-search>
- <https://www.elsevier.support/engineering-village/answer/what-are-the-expert-search-field-codes>
- <https://www.elsevier.support/engineering-village/answer/what-are-the-search-fields-in-the-compendex-database>

## 10. Wiley Online Library validated interface and planned searches

Search the **entire Wiley Online Library publisher database**, not a selected journal or proceedings series. The validated interface is Wiley Online Library Advanced Search, <https://onlinelibrary.wiley.com/search/advanced>, submitting GET requests to `https://onlinelibrary.wiley.com/action/doSearch`. Use one `Anywhere` row (`field1=AllField`) containing the complete parenthesized query in `text1`. Uppercase Boolean `AND`/`OR`/`NOT`, quoted phrases, parenthesized groups, hyphenated phrases, and non-leading unquoted wildcards such as `nanosat*` were accepted on 2026-08-06; unseparated terms default to `AND`, but explicit operators and parentheses are retained.

Use `AfterMonth=1`, `AfterYear=2011`, `BeforeMonth=8`, and `BeforeYear=2026`. Wiley normalizes the upper bound to 2026-08-31, so screen out any record after the common 2026-08-10 evidence cutoff. No reliable language or pre-search content-type control was exposed. Do not apply `PubType`, INCOSE, journal, ISSN, subject, access-status, or other venue facets to the baseline. Preserve and process the individual `Articles & Chapters` results (`content=articlesChapters&target=default`); separately log and inspect the `Collections` tab as a container/coverage route rather than counting a collection as a primary-evidence report.

For final enumeration, freeze Wiley's source Date order as `sortBy=Earliest` and `pageSize=20`; do not use the default Relevance order. A 125-record off-strategy benchmark retained the same total under Relevance but shifted records across page boundaries and produced only 122–124 unique DOI IDs, whereas explicit Earliest produced 125 unique IDs and two identical complete ordered passes. Preserve the source label as `Date (sortBy=Earliest)`, not as an inferred publication-date semantic. Preserve the exact query, generated URL/parameters, server-normalized query/date display, active tab, source total, sort, and every page. The `Anywhere` label does not document its precise metadata/full-text coverage, so make no claim that it is equivalent to Scopus `TITLE-ABS-KEY`; it is nevertheless the platform's validated unrestricted field. The benchmark and challenge policy are recorded in [`2026-08-10-browser-search-acceleration-and-interface-policy.md`](searches/subagent-logs/2026-08-10-browser-search-acceleration-and-interface-policy.md).

### Wiley deterministic browser execution and acceptance rule

Use `~/agent-tools/academic-research/skills/academic-search/scripts/search_wiley_online_library.py`. Precompile each exact `W-*` expression and normal-form GET URL before opening Wiley. First save a `--count-only --passes 2` artifact with a prospective `--max-source-total` safety bound. For a positive accepted count `N`, use that immediately observed value as `--expected-source-total`, set `--limit` to at least `N`, set `--max-pages` to at least `ceil(N/20)`, provide a clean `--native-export-dir`, retain exact `--date-start`/`--date-end`, and invoke `--passes 2 --require-complete`. The bounded non-complete mode is diagnostic/prefix retrieval only. Complete mode is acceptable only when Articles & Chapters retrieval exhausts the source total, exact-day accounting closes, native RIS succeeds, and both complete DOI passes agree.

Use an authorized visible browser session; direct unauthenticated HTTP is not a retrieval fallback. Without `--target-id`, the adapter's isolated/default or loopback-CDP mode opens and closes only an adapter-owned page. When an already authorized Wiley tab must be retained, loopback `--cdp-url` plus an operator-supplied exact hexadecimal `--target-id` may reuse only that Wiley target; the adapter re-checks target identity and hostname before navigation, never selects a tab by position, and deliberately leaves the target open. Never automate login, CAPTCHA, Cloudflare, or another access-control step, and never serialize cookies, challenge state, or access tokens.

For every navigation, require the exact `field1=AllField`, query text, empty unused rows, content/target, `pageSize=20`, zero-based `startPage`, month controls, and `sortBy=Earliest`; require the server-normalized title/date display, exact source total, intended active tab, requested active page, and complete terminal/nonterminal row arithmetic. Inspect the preserved server-normalized title before final acceptance for any silent expression rewrite. A challenge, login wall, access error, missing or conflicting total, changed control, stale or short page, timeout, silent rewrite, impossible page, duplicate DOI, DOI-less/ambiguous Articles & Chapters card, or changed total fails with `total: null`, never zero. Preserve a DOI-less/ambiguous card rather than fabricating or silently omitting an identifier; any fallback identifier/export route requires prospective validation before rerun. Preserve every failure and do not retry an access challenge. Before any clean manual restart after a changed snapshot, obtain and record a fresh count and expected-total guard.

For Articles & Chapters, require exactly `min(20, N - 20*startPage)` rendered cards and one unambiguous normalized DOI per card. Preserve page and global order/rank, reject duplicate IDs within or across pages, exhaust every computed page, and require the second complete pass to reproduce the first pass's ordered DOI ledger exactly. A valid zero requires the first-page native no-result element together with Wiley's explicit zero marker and no result list/cards; an absent total, fallback page, or challenge is not zero. Run `content=collections&target=default` separately as two-observation count-only coverage for every `W-*` query. Collections are container evidence, never bibliographic candidates or merge input; a route that falls back to Articles & Chapters or lacks an exact active-tab count is unresolved/failure, not zero.

### W-A1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### W-A2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR batteries OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### W-A3 — explicit EPS names × broad structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")
```

### W-B1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### W-B2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)
```

### W-BG1 — relation-free precise reusable-model/template artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture")
```

### W-BG2 — relation-free structural reusable artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))
```

### W-BC1 — conservative central reusable assets

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model")))
```

### W-BT2 — model/architecture-coupled tailoring

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND ((((reuse OR reuses OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures))))
```

These four expansions use the same Anywhere/date/result-tab controls as W-B1/B2 and are reconciled separately before union.

### W-V1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### W-O1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption)
```

Outcome/burden and V&V terms remain optional probes, not baseline restrictions.

A 2026-08-07 PRESS-corrected whole-platform pilot accepted all six exact strings. Articles & Chapters totals were W-A1 = 7, W-A2 = 46, W-B1 = 44, W-B2 = 103, W-V1 = 17, and W-O1 = 21; Collections were respectively unresolvable (the direct route fell back and is not a zero), 2, 1, 4, 1, and 1. Final W-B1 versus the same query minus only `"nano satellites"` remained 44 Articles & Chapters and 1 Collection; equal totals do not establish identical sets. W-B2 pagination reached active page 6 with 3 cards at `pageSize=20`, reconciling 103. Wiley rendered its Date control as `sortBy=Earliest`; the later deterministic benchmark above established it as the required final enumeration sort. These observations are `pilot_not_candidate_search`; run the seven current core/sensitivity strategies (including new W-A3 and revised W-V1/O1) and all four expansion strategies after version-1.6 authorization. Full details are in [`2026-08-07-press-browser-source-validation.md`](searches/subagent-logs/2026-08-07-press-browser-source-validation.md). A relation-free follow-up reconciled W-BG1 = 5 and W-BG2 = 13, union 16, with nine opaque additions over the fresh 124-ID B1∪B2 set; its G union was identical to the superseded gated union. W-BC1 reconciled 32 records with six additions, while W-BT2 failed changing-total/pagination controls and is not an accepted set. No record was screened; every expansion must run anew.

A 2026-08-10 deterministic-adapter gate then reran W-A1 only as a diagnostic with exact dates 2011-01-01–2026-08-10, explicit Earliest, expected total 7, and maximum total 20. It reconciled 7/7 Articles & Chapters, two identical ordered seven-DOI passes, a visible one-record RIS-with-abstract preflight, a complete seven-record page export, two exact-byte native RIS files, zero exact-day exclusions or unresolved dates, normalized JSON/CSV, and a 7-raw-to-7-unique merge. A direct W-B1 Collections run accepted one container in two observations; W-A1 Collections again fell back and remained unresolved rather than zero. A synthetic native zero page was structurally accepted only after Wiley's normal automatic verification; the preceding challenge attempt wrote an error with `total: null` and was not bypassed. Thirty Wiley unit tests and the 171-test academic/browser regression set passed. All outputs remain `pilot_not_candidate_search` interface evidence and must not enter discovery or screening.

If Wiley rejects or silently rewrites a final expression, first use its validated multi-row equivalent: P, E, and M OR-blocks in three `AllField` rows for Stream A, or P and M in two rows for Stream B; Wiley AND-combines non-empty rows. Confirm source-equivalent counts/sets before acceptance. If needed, partition into finite population-term × model-term cells and, for Stream A, population-term × EPS-term × model-term cells; save each partition and union all complete sets. If no reproducible route works, record a source failure and obtain prospective approval rather than substituting an external index.

For every authorized final `W-*` Articles & Chapters run, perform a fresh one-record export preflight in clean storage. Open the visible page-scoped **Export Citations** wizard, reconcile its `bulkDownload` DOI controls exactly and in order to the rendered page DOI ledger, select the first DOI through its visible label, select RIS and abstract inclusion through the visible controls, and accept only the browser download. Reconcile the preflight RIS DOI exactly to the selected DOI, prove that abstract inclusion was selected, and audit abstract/date preservation; retain genuinely absent source metadata as missing or date-unresolved rather than inventing it. Reset any retained wizard step only through Wiley's visible **Go back** control; do not mutate hidden form state or call a private export endpoint.

After the preflight, export every complete rendered page as one tested-safe batch of at most 20 using the same visible wizard. Require each RIS batch to contain exactly one record per selected page DOI, with no missing, duplicate, foreign, or reordered DOI, and require the parsed aggregate DOI ledger to equal the first rendered pass. Preserve every native RIS byte-for-byte. The adapter directly writes normalized JSON and optional merge-compatible CSV with source `Wiley Online Library`, exact query, global rank, DOI/stable ID, title, authors, publication date/year, abstract, URL, and source total; retain native and normalized artifacts separately and test the normalized output with `merge_search_results.py`. Wiley does not expose native CSV, so never describe the normalized CSV as a Wiley export or substitute Crossref/another index for Wiley metadata reconciliation.

Preserve result-page HTML/PDF where permitted, count and failure artifacts, generated URLs, server-normalized query/date display, target mode/ID where applicable, both pass ledgers and hashes, native RIS checksums, export reconciliation, DOI/title/author/exact-date/source metadata, access status, exact-day exclusions/unresolved dates, and normalized merge results. Keep the unaltered Wiley source total separate from the post-cutoff retained count. INCOSE International Symposium (online ISSN `2334-5837`) is a coverage audit after the unrestricted Wiley baseline: verify that unrestricted searches recover relevant known symposium records and log any targeted audit query separately; never use the series as the Wiley source boundary.

## 11. Springer Nature Link browser interface and planned searches

Search the **entire Springer Nature Link** portfolio through <https://link.springer.com/search> or its Advanced Search page at <https://link.springer.com/advanced-search/>. Do not restrict the source to a journal, book series, subject, discipline, brand, access state, or content type. The platform describes this route as searching Link content across journals, books, chapters, reference works, protocols, and other hosted content from Springer Nature brands. Use the unrestricted **Keywords** search; it covers title, abstract, and body text but not supplementary files, so report it as a whole-platform full-text-capable publisher search rather than as a title/abstract/keyword field.

Use uppercase, case-sensitive `AND`/`OR`/`NOT`, parentheses, quoted phrases, and non-leading `*` wildcards. These operators and wildcards are documented by Springer Nature and the complete B1/B2 strings were accepted in the rendered interface. Retain all explicit number, spelling, and US/UK variants; do not infer stemming or lemmatization. Apply `date=custom`, `dateFrom=2011`, `dateTo=2026`, `language=En`, and `sortBy=relevance`; apply no `content-type`, taxonomy, discipline, subdiscipline, open-access, or journal facet. The live date controls normalized ISO-looking values to years `2011` and `2026`, so preserve the source total and remove/log first-formal-publication dates after the common 2026-08-10 cutoff.

A delegated 2026-08-10 direct-HTTP pilot received a 3,038-byte `Client Challenge` document for SN-B1 and SN-B2; those responses are failures, not zeroes. A bounded browser follow-up created only owned targets, ignored unrelated tabs, and accepted the complete controlled strings in 2.2 seconds total: **SN-B1 = 114** and **SN-B2 = 252**, with English, 2011–2026, Relevance, and no content-type restriction. The page reported 20 records per page; page 1 omits `page`, and later pages use one-based `page=2,3,...`. These observations are `pilot_not_candidate_search`: no result was assessed, saved as a candidate, or used as evidence. Every Springer query below, including new SN-A3 and revised SN-V1/O1, must be run under version-1.6 authorization in clean final storage.

### SN-A1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### SN-A2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR batteries OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### SN-A3 — explicit EPS names × broad structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")
```

### SN-B1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### SN-B2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)
```

### SN-BG1 — relation-free precise reusable-model/template artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture")
```

### SN-BG2 — relation-free structural reusable artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))
```

### SN-BC1 — conservative central reusable assets

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model")))
```

### SN-BT2 — model/architecture-coupled tailoring

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND ((((reuse OR reuses OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures))))
```

These four expansions use the same unrestricted Keywords/date/language/sort controls as SN-B1/B2 and are reconciled separately before union.

### SN-V1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### SN-O1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption)
```

Outcome/burden and V&V terms remain optional probes.

For fast final execution, use `~/agent-tools/academic-research/skills/academic-search/scripts/search_springer_link.py`: its isolated-Chrome default and loopback-CDP mode both create and close only one owned page, while `--count-only` validates the rendered query, date/language filters, sort, exact total, 20-row arithmetic, and canonical paths without returning card bibliographic text. Its generic record mode is a bounded one-pass adapter, not a substitute for the final two-identical-pass and native-CSV row reconciliation required here. Submit each generated GET URL mechanically in one source-owned browser process/tab and assert the target ID, Link hostname, rendered query, controls, total, and sort after every navigation. Direct unauthenticated HTTP is only a quick challenge check; it cannot replace rendered results. The result-page control exposes **Download results (.csv)** only to a signed-in personal Link account and limits it to the first 1,000 records. When a run is at most 1,000, use the native CSV rather than model-driven page clicking, reconcile its ordered DOI/canonical-URL rows to the displayed total, and repeat the count/export pass. When a run exceeds 1,000, partition prospectively into disjoint publication years and, only where one year still exceeds 1,000, disjoint months; retain all cells and reconcile their union. Do not narrow concepts, use a venue filter, or silently accept the first 1,000.

Preserve the exact query URL, normalized control display, source total, page/export coverage, native CSV, and DOI/canonical Link URL. Normalize a copy with source `Springer Nature Link`, exact query, source total, and global rank, but do not call the CSV RIS. If personal-login export is unavailable, log the export failure and retrieve every normal result page with the same strict count/ID checks; do not silently substitute the Springer Metadata or Open Access APIs, whose scope and terms differ from the Link search interface. Official interface documentation checked on 2026-08-10:

- <https://support.springernature.com/en/support/solutions/articles/6000271990-search-options-on-springer-nature-link>
- <https://support.springernature.com/en/support/solutions/articles/6000079741-boolean-operators-search-function-results-and-wildcard-searches>
- <https://support.springernature.com/en/support/solutions/articles/6000134488-download-export-a-list-of-search-results-in-springer-nature-link>

## 12. Advanced Technologies & Aerospace Index on ProQuest and planned searches

Search **Advanced Technologies & Aerospace Index — ProQuest Platform**, the current name of the ProQuest aerospace index formerly labeled Aerospace Database. Enter through <https://www.proquest.com/advancedtechaerospace/advanced> or the corresponding Command Line Search, then use **Change databases**, clear the parent/child selection, and select only `Advanced Technologies & Aerospace Index`. Do not silently substitute `Advanced Technologies & Aerospace Database`, the parent `Advanced Technologies & Computer Science Collection`, `Computer Science Database`, or all ProQuest databases. The page title remains the broader collection name even during an Index-only search, so title/URL alone is not proof of scope; preserve the exact checked database list before every run.

Use ProQuest Command Line Search with every concept block scoped to `NOFT` (`Anywhere except full text`), uppercase Boolean, parentheses, quoted phrases, and non-leading truncation. ProQuest `*` expands at most five characters, so retain explicit `nanosat`, `nanosatellite`, and `nanosatellites` as well as `nanosat*`. Keep the literal suffix `AND YR(2011-2026) AND LA(English)`. Apply no Full text, Peer reviewed, Source type, Document type, or access limiter, and leave **Exclude duplicate documents** off. Record and, where exposed, disable automatic spelling/form variants; if they cannot be disabled, preserve their observed state and do not remove explicit variants. Use Relevance sort and the source's displayed page size.

The delegated 2026-08-10 pilot reached the licensed Advanced Search form but its owned tab was later attached to another agent's Engineering Village target; it stopped without touching that tab, and the intended totals remained unavailable rather than zero. An explicit-target follow-up then verified the exact Index checkbox independently of the three broader checked entries and executed the complete controlled Command Line strings. With only the Index selected, **PQ-B1 = 32** and **PQ-B2 = 30**; each result count stabilized in about 1.2 seconds, and database selection, both searches, and restoration of the pre-existing collection state completed in 5.3 seconds. The pilot did not inspect the automatic spelling/form-expansion state. Results used 20 records on the first page and a one-based result-page ordinal. These runs are `pilot_not_candidate_search`: no result was assessed, exported as a candidate, or used as evidence. Every aerospace-Index ProQuest query below, including new PQ-A3 and revised PQ-V1/O1, must be run under version-1.6 authorization in clean final storage.

### PQ-A1

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS)) AND NOFT(("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)) AND YR(2011-2026) AND LA(English)
```

### PQ-A2

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR batteries OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile")) AND NOFT(("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")) AND YR(2011-2026) AND LA(English)
```

### PQ-A3 — explicit EPS names × broad structured system model

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS)) AND NOFT(("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")) AND YR(2011-2026) AND LA(English)
```

### PQ-B1

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)) AND YR(2011-2026) AND LA(English)
```

### PQ-B2

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")) AND NOFT((requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)) AND YR(2011-2026) AND LA(English)
```

### PQ-BG1 — relation-free precise reusable-model/template artifacts

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture")) AND YR(2011-2026) AND LA(English)
```

### PQ-BG2 — relation-free structural reusable artifacts

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))) AND YR(2011-2026) AND LA(English)
```

### PQ-BC1 — conservative central reusable assets

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model")))) AND YR(2011-2026) AND LA(English)
```

### PQ-BT2 — model/architecture-coupled tailoring

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")) AND NOFT(((((reuse OR reuses OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures))))) AND YR(2011-2026) AND LA(English)
```

These four expansions retain Index-only, NOFT, English, 2011–2026, no-type/no-access-limiter, no-source-deduplication, and Relevance controls and are reconciled separately.

### PQ-V1

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS)) AND NOFT(("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering")) AND NOFT((verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")) AND YR(2011-2026) AND LA(English)
```

### PQ-O1

```text
NOFT((CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")) AND NOFT(("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS)) AND NOFT(("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering")) AND NOFT((reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption)) AND YR(2011-2026) AND LA(English)
```

Outcome/burden and V&V terms remain optional probes.

For fast final execution, use `~/agent-tools/academic-research/skills/academic-search/scripts/search_proquest_aerospace.py`: it expands the parent list, selects only the exact Index, freezes Relevance/20-per-page/source-deduplication-off/spelling-and-form-expansion-off, and provides a metadata-free `--count-only` path. Its isolated-Chrome default avoids shared source state; loopback CDP opens one owned page and restores an explicit pre-run database selection only when conflict checks pass. Its generic card mode remains a bounded one-pass adapter and does not replace the final two-pass ledger or native RIS preflight/batch reconciliation. Use one owned browser target in one process with a unique harness name and private temporary directory. Select the Index once, verify the four relevant states as parent=false, Aerospace Database=false, Index=true, and Computer Science Database=false before each submission, then submit all frozen strings mechanically through Command Line Search. Read the count from the dedicated result-count element instead of waiting on or interpreting result cards. Ignore unrelated tabs and never use the globally current tab as identity. Restore only source state that this run deliberately changed, and close only the owned target.

ProQuest documented a 10,000-record pageable ceiling. Count first; if an accepted query approaches any paging/export ceiling, partition it into disjoint publication-year cells before retrieval and subdivide a year only as needed. Do not narrow the concepts or switch to the broader full-text database. Run a one-record native **RIS** preflight after authorization with citation, abstract, indexing, DOI/stable ProQuest ID, and permalink where available; record the actual per-export limit, then export in safe source-supported ranges. Preserve native batches, the selected-database proof, exact command, controls, total, sort, page/rank ledger, and source IDs. Normalize copies with source `Advanced Technologies & Aerospace Index`, exact query, source total, and global rank; leave source-side duplicate exclusion off and deduplicate only during the common merge.

Official platform documentation checked on 2026-08-10:

- <https://www.proquest.com/help/academic/Advanced_Search.html>
- <https://www.proquest.com/help/academic/Command_Line_Search.html>
- <https://www.proquest.com/help/academic/Search_Tips.html>
- <https://www.proquest.com/help/academic/View_Field_Codes.html>

## 13. ProQuest Dissertations & Theses Global and planned searches

Search **ProQuest Dissertations & Theses Global (PQDT Global)** through the ProQuest Platform as a separate exact-database event. Enter through <https://www.proquest.com/pqdtglobal/advanced> or the corresponding Command Line Search, open **Change databases**, and require the selected semantic source to be exactly `ProQuest Dissertations & Theses Global` before every query. The 2026-08-10 browser gate displayed the exact source as `ProQuest Dissertations & Theses Global Full Text Included`; this product-label suffix does not activate the separate Full text limiter, which remained unchecked. Do not substitute an all-ProQuest search, PQDT Open, an institution-specific `Dissertations & Theses @` product, Advanced Technologies & Aerospace Index, or another parent/sibling/edition. The PQDT and aerospace-index events share one platform interface but have separate query IDs, selection proofs, totals, exports, and provenance and are never searched simultaneously.

Use the same eleven semantic partitions as the aerospace Index because the thesis/dissertation source boundary replaces—not supplements—the publication-type concept. Do not add `thesis`, `dissertation`, degree, institution, manuscript-type, full-text, peer-review, or access terms/filters. Use ProQuest Command Line Search with each concept block scoped to `NOFT` (`Anywhere except full text`), uppercase Boolean, parentheses, quoted phrases, and source-supported non-leading truncation. Retain the literal suffix `AND YR(2011-2026) AND LA(English)`; full-report language screening remains authoritative. Use Relevance, 20/page, source-side duplicate exclusion off, and the observed automatic spelling plus plural/adjective-variant expansion **on**, recording and re-verifying rather than treating that expansion as equivalence to any explicit term. Preserve the source total before applying the common 2026-08-10 exact-day cutoff.

The exact PQDT source-native strings are the verbatim corresponding `PQ-*` code blocks in Section 12; only the query/event ID and exact selected database differ. This table is normative and creates eleven separately executed logical queries rather than a combined ProQuest search:

| PQDT query/event ID | Verbatim source-native query body |
|---|---|
| `PQDT-A1` | `PQ-A1` |
| `PQDT-A2` | `PQ-A2` |
| `PQDT-A3` | `PQ-A3` |
| `PQDT-B1` | `PQ-B1` |
| `PQDT-B2` | `PQ-B2` |
| `PQDT-BG1` | `PQ-BG1` |
| `PQDT-BG2` | `PQ-BG2` |
| `PQDT-BC1` | `PQ-BC1` |
| `PQDT-BT2` | `PQ-BT2` |
| `PQDT-V1` | `PQ-V1` |
| `PQDT-O1` | `PQ-O1` |

The initial fresh isolated-browser probes on 2026-08-10/11 UTC rollover reached a managed `Just a moment…` challenge before database selection and correctly recorded totals `null`. A later authorized normal-browser follow-up proved the exact PQDT-only source state, `/pqdtglobal/advanced` and `/pqdtglobal/commandline` routes, exact query echoes, Relevance, 20/page, source duplicate exclusion off, Full text off, and expansion on. Aggregate-only diagnostic totals were **PQDT-A1 = 1, PQDT-B1 = 17, and PQDT-B2 = 9**; count states stabilized in 0.780/1.345/1.113 seconds. A later impossible-string native-zero/control attempt reached the normal database-selection page but stopped on a local browser-automation command error before checkbox-state inspection; selection, controls, sentinel submission, query echo, and zero were therefore not established, and its total is `null`. No result card, title, author, abstract, identifier, export, full text, or candidate was inspected. All runs are `pilot_not_candidate_search`; every final `PQDT-*` query must run anew in clean version-1.6 storage.

The four expansion queries remain separately reconciled terminology partitions, not evidence that a thesis reports reuse, genericity, or tailoring. V1/O1 remain optional sensitivity probes.

The review-local [`search_proquest_pqdt_global.py`](searches/tools/search_proquest_pqdt_global.py) is implemented and hash-pinned in the current validation state as an **aggregate-only validation wrapper**, not a production retrieval adapter. It accepts only a frozen query ID and loopback CDP target, makes two semantic PQDT-only selector assertions in the same owned page, and before submission requires exactly one visible **Full text** control that is unchecked. It serializes no cards/records/IDs, can never create merge input, deliberately rejects native zero, and exposes no arbitrary database/query option. It reads the pinned manifest once as bytes, hashes and decodes those same bytes, maps ordinary runtime failures to fixed-code artifacts with `source_total: null`, and publishes no-clobber owner-only `0600` JSON artifacts. Its visible Full text assertion does not prove absent/hidden/type/degree/access limiter state, and its cooperative lock cannot eliminate external ABA; both are explicit `V16-PQDT-02` live residuals. Its offline fixtures advance only the implementation part of the gate; all live retrieval/export gates remain open. Before final execution, extend or replace it with a source-specific fail-closed PQDT retrieval adapter or fully reproducible manual procedure; do not relabel `search_proquest_aerospace.py` or expose an unrestricted arbitrary-database option. The live gate must re-prove the exact semantic database/product label, `pqdtglobal` route, exact query echo, Relevance, 20/page, duplicate exclusion off, expansion on, all required limiter states, stable rank/source-ID semantics, native zero, pagination cap, and RIS export limit. Do not inherit the aerospace Index's 10,000-record cap or export ceiling without PQDT-specific evidence.

Count first, then retrieve every accepted query through two identical complete ordered source-ID/rank passes and require `retrieved == source total`. If a PQDT-verified paging/export ceiling could truncate a set, partition prospectively into disjoint publication-year cells and subdivide a year only as needed without narrowing concepts. Run a fresh one-record native RIS preflight, preserve source-supported safe batches and exact bytes, and normalize copies with canonical source `proquest_dissertations_theses_global`, exact query, source total, and global rank. Strip session/search/account parameters from stable record URLs. A challenge, entitlement/selection ambiguity, query rewrite, changed total, missing ID, cap, export mismatch, or restoration failure yields total `null` and no partial import.

Record degree level/name, institution, manuscript type, every source date label, access/embargo state, and reported review/examination status during screening/extraction rather than filtering at discovery. `NOFT` is a metadata-field choice, not an availability restriction. A PQDT record without retrievable substantive full text is a lead or `not_retrieved`, not primary evidence.

Source-method references:

- <https://proquest.libguides.com/pqdt>
- <https://proquest.libguides.com/pqdt/content>
- <https://proquest.libguides.com/pqdt/features>
- <https://about.proquest.com/en/products-services/pqdtglobal/>

## 14. Open Access Theses and Dissertations (OATD) and planned searches

Search the whole public **Open Access Theses and Dissertations (OATD)** index at <https://oatd.org/> as one separately provenance-coded online resource. OATD states that it aggregates records for graduate electronic theses/dissertations intended to be freely available from contributing repositories; the substantive full text remains at the originating repository. OATD may index metadata and, for some records, text from approximately the first 30 pages for hit display, so its native any-field search is broader and unevenly populated relative to title/abstract fields. Preserve that source limitation; never treat an OATD hit, open-access label, or partial-text match as full-report eligibility evidence. A linked repository is a retrieval location, not another discovery event.

The normal basic interface is GET `https://oatd.org/oatd/search` with one `q` value. A 2026-08-10 aggregate-only browser pilot accepted a quoted exact phrase and grouped uppercase `AND`/`OR` query with an exact query echo. The advanced composer exposes four rows (`AND`, `OR`, `PHRASE`, `NOT`), any-field/title/author/abstract/publisher/subject/discipline fields, `earliest`/`latest` year boxes, language/country, Relevance, 30/60/100 page sizes, and a Creative-Commons-only control. A later composer request returned `Server Too Busy - Please slow down`; it is an interface/access failure with total `null`, not zero. After a cooldown, a separate owned-tab retry submitted the complete finite **OATD-B1** below through the basic interface and accepted its exact query echo and **23**-record aggregate in 2.654 seconds, with a mechanical 23/23 first-page row/range reconciliation and no card content inspection. OATD-B2 was not run because the owned tab then failed its state assertion before navigation; its pilot total remains `null`, and A1 was not attempted. A later focused B2-only subagent produced no stdout, stderr, or source-state report within 15 minutes and was canceled by the orchestrator. A subsequent retry at 2026-08-10 21:34:53.822 EDT stopped after 5.089 seconds on a browser/runtime timeout before it confirmed an owned target or inspected source state. A later browser doctor showed a pilot-owned tab at the exact B2 URL, but because the actor had not asserted its identity or returned page evidence, the orchestrator closed that and the other known pilot-owned OATD tabs without inspecting result state. These attempts add no aggregate or syntax evidence; B2 remains `null`, not zero. Consequently, the frozen initial implementation uses the validated basic `q` grammar, complete finite concept forms with no wildcard assumptions, default native Relevance/30-page controls as re-verified at execution, no native date or language limit, and local date/language screening. The composer year/language controls may replace local screening only after a separately logged set-equivalence and metadata-quality gate.

Run the eleven source-native expressions below exactly as the `q` value with `form=basic`. Do not append `thesis`, `dissertation`, degree, institution, country, language, Creative-Commons, or access terms/filters: OATD's source boundary already identifies graduate ETDs, while the protocol—not source metadata—determines eligible degree type and English full-report language. Retrieve all years returned, preserve the unaltered source total, and apply 2011-01-01 through 2026-08-10 locally from source-locatable formal dates; a 2026 year-only record remains unresolved. Finite forms replace every wildcard because OATD wildcard expansion was not validated.

### OATD-A1 — explicit EPS names × explicit MBSE/language

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### OATD-A2 — EPS analyses/interfaces × structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR batteries OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### OATD-A3 — explicit EPS names × broad structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")
```

### OATD-B1 — embedded-thread baseline with explicit MBSE/languages

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### OATD-B2 — embedded-thread structured-model expansion

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation)
```

### OATD-BG1 — relation-free precise reusable-model/template artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture")
```

### OATD-BG2 — relation-free structural reusable artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))
```

### OATD-BC1 — conservative central reusable assets

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model")))
```

### OATD-BT2 — model/architecture-coupled tailoring

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND ((((reuse OR reuses OR reused OR reusable OR reusing OR tailor OR tailors OR tailored OR tailoring OR customize OR customizes OR customized OR customizing OR customization OR customise OR customises OR customised OR customising OR customisation OR configure OR configures OR configured OR configuring OR configuration OR parameterize OR parameterizes OR parameterized OR parameterizing OR parameterization OR parameterise OR parameterises OR parameterised OR parameterising OR parameterisation OR instantiate OR instantiates OR instantiated OR instantiating OR instantiation OR variability OR "variation point" OR specialize OR specializes OR specialized OR specializing OR specialization OR specialise OR specialises OR specialised OR specialising OR specialisation) AND (model OR models OR architecture OR architectures)) OR ((adapt OR adapts OR adapted OR adapting OR adaptation) AND (model OR models OR architecture OR architectures))))
```

### OATD-V1 — EPS-linked V&V sensitivity probe

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### OATD-O1 — outcome and implementation-burden sensitivity probe

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption)
```

The expansion queries are independent recall partitions, never evidence of genericity or tailoring; V1/O1 remain optional sensitivity probes. The complete accepted OATD union is deduplicated within source before common cross-source deduplication, with every query discovery event retained.

### OATD execution, pagination, and failure contract

The review-local [`oatd_basic_count_gate.py`](searches/tools/oatd_basic_count_gate.py) is implemented and hash-pinned in the current validation state as an **aggregate-only validation wrapper**, not a production retrieval adapter, pinned to the eleven finite `OATD-*` bodies in [`thesis-source-query-manifest-v1.6.json`](searches/thesis-source-query-manifest-v1.6.json). It permits one frozen query ID, one loopback CDP target, one navigation, and no retries; it emits only aggregate/control evidence and is never merge eligible. Its page-state script does not scan broad headings (`h1`/`h2`) or card content. Like the PQDT wrapper, it reads the pinned manifest once as bytes, hashes and decodes those same bytes, maps ordinary runtime failures to fixed-code artifacts with `source_total: null`, and publishes no-clobber owner-only `0600` JSON artifacts. It deliberately rejects native zero. Its synthetic fixtures do not validate native zero, pagination, source-record identity, record capture, normalization, or date/language screening.

Use one owned normal-browser target and no concurrent OATD actor. Submit one mechanically precompiled query at a time, retain the exact URL/query echo and dedicated source total, and respect source load signals; on `Server Too Busy`, challenge, or another access state, stop without immediate retry and log total `null`. Before final discovery, a no-screening gate must establish the exact native-zero state, 30-row page contract, pagination parameter and terminal-page arithmetic, stable result order, one unique `record` identifier/canonical OATD URL per row, changed-total behavior, and any source cap. It must re-prove B1 and establish that the full frozen B2 expression is accepted without rewrite; otherwise partition a logical query into complete, prospectively defined source-representable cells and union all cells without narrowing concepts.

For each successful final expression, require every expected page, contiguous global ranks, unique stable OATD record identifiers, `retrieved == source total`, and a second identical complete ordered-ID pass. Preserve source records or rights-permitted field captures and checksums, the source-supplied stable OATD record identifier/canonical URL established by the gate, originating repository URLs, date/language/degree fields as supplied, missing-field counts, and exact query/rank/total provenance. OATD exposes no validated native bibliographic export in this plan; source-derived normalized JSON/CSV must be labelled as derived, not native. A missing stable ID, busy/challenge state, query rewrite, short/stale page, hidden cap, changed total, pass mismatch, parse failure, or rights/interface block fails the whole logical query with no partial import.

Normalize with canonical source `oatd`, while retaining the repository host/identifier separately. Broken or embargoed repository links are retrieval outcomes. OATD and PQDT records for one thesis are duplicate discovery records/manifestations of one report when identity is confirmed; a substantively distinct derivative article remains a separate report linked through the report-family registry.

Source-method references:

- <https://oatd.org/>
- <https://oatd.org/faq.html>

## 15. AIAA Aerospace Research Central (ARC) browser interface and planned searches

Search **AIAA Aerospace Research Central (ARC)** at <https://arc.aiaa.org/search/advanced> as a publisher-hosted, source-wide platform, not as an independent bibliographic index. Use the normal Advanced Search **Anywhere** field (`AllField`) over ARC's default **All content** scope. Do not restrict discovery by AIAA journal, meeting, book, topic, author, publication type, open-access status, or known venue. Describe the boundary as all content indexed by ARC under the observed source-wide control; do not claim it represents every AIAA publication outside ARC or that Anywhere is equivalent to another source's title/abstract/keyword field. Preserve overlap with every other planned source as separate discovery events and deduplicate only after source retrieval.

The validated normal-interface request is a browser navigation to `https://arc.aiaa.org/action/doSearch` with `field1=AllField`, the complete expression in `text1`, `AfterMonth=1`, `AfterYear=2011`, `BeforeMonth=8`, `BeforeYear=2026`, and `access=on`. Preserve all other normal-form parameters exactly as generated. ARC renders the upper month through 2026-08-31, so retain the unaltered source total and then apply/log the common 2026-08-10 first-formal-publication cutoff. No reliable language control was observed; screen language. Apply no discovery publication-type facet and screen type later.

Direct unauthenticated HTTP was Cloudflare-challenged and is not the planned transport. Use an authorized visible browser and classify the run as `web_ui`, even when it navigates directly to a URL generated by ARC's normal form. Never serialize cookies, challenge state, or access tokens. ARC accepted uppercase Boolean operators, parentheses, quoted phrases, and trailing wildcards in the pilot, but no stemming or wildcard-expansion semantics were inferred; the explicit population, number, and US/UK variants remain in every strategy.

### ARC fast browser execution and acceptance rule

Precompile exact `ARC-*` expressions and URLs before opening ARC. Use one named browser process and one persistent dedicated result tab for a batch of two or three queries; retain and assert the owned target ID before every action. The adapter may create one transient source-owned record-export tab per bounded batch and must close only that tab after reconciliation. After the selector/control contract is established, a deterministic helper—not a model turn—navigates and reads each page. Poll with no fixed sleeps or screenshots for a new page carrying the exact query/controls, `.search-result__nav`, `.search-result__body`, ARC's `Search Results (N)`, and the expected rendered-row/DOI-selector count. Use the measured `pageSize=20`, zero-based `startPage=0,1,...`, and the fixed recorded Relevance sort; mechanically compute and exhaust every page. Although ARC exposes 50 and 100, the speed pilot rendered only 22/50 and 24/100 provisional cards at its first count-ready state, so those sizes are prohibited unless a later logged hydration contract proves every expected row. A 20-second semantic-and-row-readiness deadline applies per navigation. A challenge, login wall, access error, stale/short page, absent count/body, silent query rewrite, or deadline is a failure with total `null`, never zero; do not retry an access challenge. An explicit accepted `Search Results (0)` is required for a valid zero.

The reusable adapter is `~/agent-tools/academic-research/skills/academic-search/scripts/search_aiaa_arc.py`. Its bounded default is diagnostic/prefix retrieval; invoke final cells with exact `--date-start`/`--date-end`, `--passes 2`, `--require-complete`, and `--limit`/`--max-pages` high enough to exhaust the source total. Complete mode additionally requires visible Relevance/20-page controls, strict repeat ordering, and full retrieval or writes a failure with total `null`. `--count-only` remains aggregate-only. Off-topic live calibrations validated the normal per-record RIS path, exact-byte preservation, and a complete 44-record/three-page/two-pass run under `--require-complete`; these implementation gates are not substitute runs for any `ARC-*` strategy.

Each result row exposed a nonempty `doi` selection value in the pilots and all 44 rows in the complete live gate exposed exactly one DOI. For final retrieval, require exactly `min(20, total - 20*startPage)` stable row/DOI selectors before a page is ready, preserve source order and global rank, require the displayed total unchanged on every page, reject short nonterminal pages and duplicate/missing DOI sequences, and run a second complete ordered pass. One clean restart is allowed after a changed total; a repeated change or ordered-pass mismatch is a source failure. The accepted automated contract is DOI-based: if a row lacks a DOI, stop with total `null`, preserve the failed page, and do not discard the row. Before rerunning, prospectively preflight a source-generated canonical record URL or displayed ARC paper/article number as the stable fallback plus its source-native metadata route; never fabricate a DOI, silently omit the row, or substitute another index.

The live calibration established that result-page **Export Citations** offers formatted text styles, not RIS. Use the source-native per-record route instead: from the first rendered DOI in each bounded batch, visibly follow **Tools → Download citation**, poll the newly opened controlled menu without a fixed sleep until the visible link is stable, assert the exact `/action/showCitFormats?doi=...` route and the POST form to `/action/downloadCitation`, retain `include=abs`, select visible RIS plus checked Direct import, and accept only a browser `.ris` download that reconciles to that DOI. After this visible route proof, the adapter may navigate the same exact normal citation-format route for the remaining rendered DOIs in batches of at most 20, while reasserting form DOI/action/controls and preserving every native file byte-for-byte. The first off-topic calibration reconciled one preflight plus 20 distinct first-page RIS records; the later complete gate reconciled all 44 records across three pages, 45 native files including the duplicate preflight, two ordered result-page passes, and a 44/44 normalized merge. Every authorized final cell must still perform its own one-record preflight in clean storage. Normalize to the common merge schema with source `AIAA Aerospace Research Central (ARC)`, exact query, global rank, stable ID, DOI, and source total, then run `merge_search_results.py`; do not substitute Crossref or another index for ARC discovery or metadata reconciliation.

### ARC-A1 — explicit EPS names × explicit MBSE/language

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### ARC-A2 — EPS analyses/interfaces × structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR batteries OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### ARC-A3 — explicit EPS names × broad structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model")
```

### ARC-B1 — embedded-thread baseline with explicit MBSE/languages

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### ARC-B2 — embedded-thread structured-model expansion

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)
```

### ARC-BG1 — relation-free precise reusable-model/template artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("generic model" OR "generic system model" OR "reusable model" OR "reusable system model" OR "configurable model" OR "configurable system model" OR "model template" OR "mission-agnostic model" OR "mission agnostic model" OR "mission-independent model" OR "mission independent model" OR "mission-agnostic architecture" OR "mission agnostic architecture" OR "mission-independent architecture" OR "mission independent architecture")
```

### ARC-BG2 — relation-free structural reusable artifacts

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference architecture" OR "domain model" OR metamodel OR "meta-model" OR "product-line model" OR "product line model" OR "product-family model" OR "product family model" OR ("variation point" AND (model OR architecture)))
```

### ARC-BC1 — conservative central reusable assets

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("reference model" OR "system reference model" OR "model library" OR "model libraries" OR "system model library" OR "system model libraries" OR "model pattern" OR "modeling pattern" OR "modelling pattern" OR "system model pattern" OR "systems model pattern" OR "model profile" OR "system model profile" OR "systems model profile" OR "SysML profile" OR (("domain-specific modeling language" OR "domain specific modeling language" OR "domain-specific modelling language" OR "domain specific modelling language") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model")))
```

### ARC-BT2 — model/architecture-coupled tailoring

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND ((((reuse OR reuses OR reused OR reusable OR reusing OR tailor* OR customiz* OR customis* OR configur* OR parameteriz* OR parameteris* OR instantiat* OR variability OR "variation point" OR specializ* OR specialis*) AND (model OR models OR architecture OR architectures)) OR (adapt* AND (model OR models OR architecture OR architectures))))
```

These four expansions use the same ARC Anywhere/date/All-content controls as ARC-B1/B2 and are reconciled separately before union.

### ARC-V1 — EPS-linked V&V sensitivity probe

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR traceable OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### ARC-O1 — outcome and implementation-burden sensitivity probe

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR reliable OR "mission assurance" OR reproducibility OR reproducible OR reuse OR reusable OR integrability OR integrable OR interoperability OR interoperable OR traceability OR traceable OR benefit OR benefits OR impact OR outcome OR "no effect" OR adverse OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR license OR licence OR adoption)
```

A 2026-08-10 aggregate-only browser pilot accepted ARC-A1, ARC-B1, and ARC-B2 with the common month-granular controls and no language/type/venue/OA restriction. Dynamic totals were ARC-A1 = 108, ARC-B1 = 308, and ARC-B2 = 820; at 20/page these implied 6, 16, and 41 pages. Direct normal-interface GET navigation reached a semantically asserted ARC-A1 count in 7.750 seconds; the earlier form-submit dispatch timings for B1/B2 were not end-to-end measurements and are not used as speed evidence. A focused ARC-A2-finite request at 100/page hit its 20.002-second deadline and was a failure, not zero. A clean one-tab benchmark then reached count state for ARC-A1-finite at 20/50/100 in 3.649/5.117/5.948 seconds and ARC-A2-finite at 20/page in 4.413 seconds (total 699). Twenty per page was fastest; only A1/20 immediately rendered the full requested row count, so larger sizes are not accepted for enumeration and the provisional A2 row selector still requires a hydration/identity preflight. Equal A1 totals do not prove finite/wildcard set equivalence. No result metadata or candidates were inspected. A separate direct-HTTP subagent received a Cloudflare 403 in 0.034 seconds before search and correctly classified it as access failure, not zero. Full observations are in [`2026-08-10-aiaa-arc-source-addition-pilots.md`](searches/subagent-logs/2026-08-10-aiaa-arc-source-addition-pilots.md).

The later off-topic gate tests validated the per-record RIS contract and complete three-page ordered retrieval mechanics, but not exact wildcard expansion, every `ARC-*` query, a complete non-A1 row-hydration contract, or any final discovery result. An attempted broader two-pass DOI census over an 856-row off-topic control stopped on a visible access challenge at zero-based `startPage=11`; it was not retried, is not a zero, and does not prove that DOI-less rows cannot occur elsewhere. Run all eleven strategies under version-1.6 authorization, including new ARC-A3 and revised ARC-V1/O1, first repeat the one-record export/normalization/merge preflight, and use only clean final-run artifacts for discovery. If ARC rejects or rewrites a final string, try the Advanced Search multi-row equivalent with P/E/M or P/M/R in separate Anywhere rows and prove count/set equivalence. Otherwise partition into finite source-representable terms, save and union every cell, or record a source failure; never substitute an external index.

## 16. IAF Digital Library authorized IAC-proceedings search

Version 1.5 first authorized, and version 1.6 retains, the public **IAF Digital Library** at <https://dl.iafastro.directory/> as an IAC-proceedings collection, not as a claim of coverage of all astronautics literature or all IAF events. No pre-authorization pilot output may be relabelled as a final search. Include only canonical `IAC-YYYY` events from 2011 through 2026 and apply the common 2026-08-10 first-formal-publication cutoff during screening. Snapshot the public `/index/` page at each final execution and reconcile its in-window `IAC-YYYY` event codes; missing, duplicated, malformed, or unexpectedly absent event years are coverage exceptions rather than implicit zero-result years.

The normal source route is server-rendered XHTML `GET https://dl.iafastro.directory/search/?q=...&o=<offset>&l=50`, followed only for retained rows by the canonical public landing page `/event/IAC-YYYY/paper/<paper-id>/`. The visible search box is capped at 500 characters, cards do not contain abstracts, no abstract-specific field was validated, and no native bulk bibliographic export or declared sort was observed. Therefore the final source adaptation is deliberately a **year-partitioned population harvest followed by deterministic local title/abstract classification**, not silently shortened Boolean translations. This broader bounded adaptation preserves every source record reached by the complete P block before applying local core-B/G/C1 candidate logic and E/R/T2/V1/O1 tags, and avoids assuming that IAF's default search index is equivalent to another source's title/abstract/keyword field.

### IAF-P-YYYY — exact annual population harvest

Use this exact user query for every event year `YYYY` from 2011 through the cutoff year—16 annual cells (`IAF-P-2011` through `IAF-P-2026`):

```text
CubeSat OR CubeSats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites"
```

The adapter must generate and verify exactly:

```text
event:IAC-* AND year:(YYYY) AND (CubeSat OR CubeSats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites")
```

The scoped form is 161 characters for a four-digit year, safely below the observed 500-character ceiling while retaining every explicit source-representable population spelling plus the supported suffix wildcard. Do not add `SmallSat`, other events, language, publication-type, access, topic, country, affiliation, author, or known-venue constraints. IAF exposes a `language` search field, but no value/coverage contract was validated; screen language rather than guessing a filter. Treat IAC cards as proceedings leads and verify eligible full-report type later—an abstract and a manuscript control do not themselves prove an eligible full paper.

Use the production adapter and one year per artifact, for example:

```bash
year=2024
total=123  # Replace with this year's positive count-only total.
pages=$(( (total + 49) / 50 ))
uv run ~/agent-tools/academic-research/skills/academic-search/scripts/search_iaf_digital_library.py \
  --query 'CubeSat OR CubeSats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites"' \
  --year-start "$year" \
  --year-end "$year" \
  --limit "$total" \
  --max-pages "$pages" \
  --timeout 20 \
  --request-delay-seconds 0.25 \
  --retries 2 \
  --output-path "SLR/SLR1/searches/iaf-digital-library-iac/pass-1/IAF-P-${year}.json"
```

First save a separate `--count-only` artifact for each year. Accept a count only when the native positive summary or explicit no-results summary echoes the exact scoped query and reconciles its range/table state. Repeat a valid zero count independently; no detail pass is needed for a twice-reconciled zero. For each positive total `N`, set `--limit N` and `--max-pages ceil(N/50)`, then execute two independent complete metadata passes into separate directories. Fixed page size is 50; a pass is acceptable only when `output_metadata.status` is `success`, `output_metadata.retrieval_complete` is true, `results_retrieved == total == N`, and every expected page and detail page reconciles. Require identical ordered `(eventCode, paperNumber, rank, canonical URL)` ledgers across passes and unchanged reconciled title, year, DOI, and abstract-availability metadata. IAF exposes no controlled sort, so rank remains opaque source order rather than a relevance claim; that uncertainty does not permit sorting away an order mismatch. One complete restart may follow a changing snapshot; a repeated total, order, set, or detail-metadata mismatch is a source failure.

The adapter's operational ceiling is 5,000 records/100 pages per annual query. If a count exceeds that ceiling, do not accept or merge a prefix: record a source failure. An atom-by-atom population union is only a possible future fallback; it requires a separately logged no-screening equivalence pilot, prospective protocol/search-plan authorization, complete two-pass cell retrieval, preserved overlap, and exact union reconciliation before use. It cannot be improvised during a final run, and an over-ceiling atom without a validated source-equivalent partition remains a source failure.

### Deterministic IAF title/abstract classification

For every unique harvested landing-page record, create one `iaf_title_abstract` route from the title and complete public abstract, preserving field boundaries and field-level hits. Exclude author, affiliation, country, publication-title boilerplate, event name, DOI, and URL from concept matching. Require P to occur locally in that route even though the source query was population scoped; this prevents a hit in another indexed field from establishing the review population. Terms may combine across title and abstract for the same record, but never across records, authors, events, or a missing abstract. Preserve every title-only/missing-abstract record in a separate `abstract_not_available` lead ledger for retrieval/manual assessment; missing metadata is a recall limitation and never an automatic concept-negative rejection.

Before final execution, version and checksum a deterministic IAF wrapper and positive/negative fixtures around [`searches/search-concept-dictionary.json`](searches/search-concept-dictionary.json). Do not silently reuse ESA route labels: verify the version-1.6 dictionary's declared IAF/OATD scope and record dictionary, matcher, wrapper, and fixture-result checksums under the distinct `iaf_title_abstract` route. Apply the complete Section 4 blocks exactly within each route:

- **IAF-A tag:** `P AND E AND M`, a structural subset of local core B rather than a separate source query.
- **IAF-B-core:** `P AND M`, using the full structured-model/MBSE block without requiring R. Preserve high-specificity-M and broad-M-plus-R subtype tags for comparison with the direct-query sources, but do not mislabel those tags as IAF B1/B2 searches.
- **IAF-BG1 and IAF-BG2:** `P AND` one complete relation-free G1 or G2 artifact, with all multi-component artifact terms in the same route.
- **IAF-BC1:** `P AND` one complete conservative C1 asset; bare library, pattern, profile, or language terms do not qualify.
- **IAF independent-R tag:** identify an R occurrence independent of every required artifact span; an artifact's own `architecture` token cannot self-satisfy it.
- **IAF-T2 tag:** apply the exact model/architecture-coupled T2 operation to IAF-B-core. Because local core already uses `P AND M`, this is a structural tag, not an additional candidate route.
- **IAF-V1 and IAF-O1 tags:** deterministic tags using the exact finite cross-source V1/O1 subsets. They do not become eligibility requirements or candidate routes.

Retain Stream A as the E-explicit tag within IAF-B-core. Retain total Stream B as IAF-B-core union the separately provenance-coded BG1, BG2, and BC1 expansions; T2 remains a tag. Report every partition total, all intersections and exclusive yields, the complete P-harvest denominator, unmatched P-harvest records, `abstract_not_available` leads, A∩core-B, core-B-only, E-explicit expansion records, independent-R/T2/V1/O1 tags, and the final candidate union; require structural `A-only = 0`. Local metadata classification is candidate generation only: it does not establish eligibility, a qualifying EPS bridge, genericity, tailoring, outcome attribution, or V&V evidence.

### Reconciliation, provenance, access, and rights

Preserve the annual count artifacts, both complete-pass JSON files, exact user and executed queries, `/index/` snapshot, request timestamps/time zone, adapter/version checksum, source total, page/detail counters, ordered and set reconciliation, canonical event code, literal paper number, DOI when present, title, authors, year, complete available abstract, landing URL, missing-field counters, matcher/fixture checksums, and local-route decisions. Use canonical source `IAF Digital Library (IAC Proceedings)` and merge key `iaf_digital_library_iac`. The source-derived JSON is normalized output, not a native IAF export; preserve rights-permitted response material or response checksums/request ledgers required by Section 5 in access-controlled final-run storage, and never describe normalized JSON as source-native. DOI is optional, citation counts are unavailable rather than observed zero, source order is opaque, and `total` is the exact annual P-query total before local candidate classification.

Use anonymous public metadata access only. Never request or follow `/api/`, `/f/` or `/f/manuscript/`, `/u/`, `/m/`, `/a/cart/`, authentication, DOI targets, manuscript/full-text controls, or links discovered inside abstracts. `openAccess_pdf` must remain `{}`. Do not inject credentials, cookies, proxies, custom headers, or inherited authenticated session state. Redirects, access/challenge/login pages, malformed XHTML, changed query/range/pagination controls, foreign or non-IAC card routes, event/year/detail mismatches, duplicate IDs, changed totals, or exhausted bounded retries fail with `total: null`; only IAF's explicit reconciled no-results state is zero.

Before bulk final execution, record the current public `robots.txt`, applicable IAF Digital Library/parent-site terms, and any permission or storage/redistribution restriction. Public readability does not itself authorize republication of abstracts or full text. Keep rights-restricted raw pages or abstract-bearing artifacts in access-controlled storage, publish only permitted derived metadata and methods, and document a rights/access failure if the preservation needed for an auditable review cannot be performed lawfully. Full-text retrieval is a separate later review stage under lawful source access; this metadata adapter must never perform it.

Local title/abstract matching is not claimed to be set-equivalent to IAF's undisclosed default index. Before promotion from this appendix, use only cap-fitting, no-screening sentinel queries to test the local implementation and document mismatches, without importing pilot IDs or replacing the population harvest. Missing abstracts and concepts searchable only in other source fields remain explicit recall limitations.

Version-1.6 final execution requires the cumulative pre-final gates in [`pilots-to-run-v1.6.md`](pilots-to-run-v1.6.md), synchronized matcher fixtures and lint, and clean final-run artifacts. The earlier `6GStarLab` smoke and every pre-authorization aggregate remain permanently excluded from candidates and final counts.

## 17. ESA Indico whole-instance harvest and search

Search **the entire public ESA Indico instance**, not only events labeled MBSE. A pre-freeze diagnostic on 2026-08-06 found 437 unique events in the root export; its event-ID set exactly equaled the union of public top-level category exports 5, 6, and 7, and nested category 9 was a subset of category 6. All root events had parseable dates, 408 were dated 2011-01-01 through the diagnostic date, and all five known MBSE coverage-event IDs were present. This validates the root endpoint's recursive census behavior at pilot time only. Repeat and save the root/child set comparison at every final harvest so a later category or visibility change is detected. At every harvest:

1. save the official root inventory from <https://indico.esa.int/export/categ/0.json> and any child-category exports needed by the validation;
2. reconcile reported event counts with returned unique event IDs and document duplicate/category-path handling;
3. retain every event dated from 2011-01-01 through the harvest date, logging missing/unparseable dates as exceptions; and
4. for every in-window event, irrespective of apparent topic, retrieve and save `https://indico.esa.int/export/event/{id}.json?detail=contributions`.

Record HTTP status, retrieval time, access/protection outcome, retries, checksum, and parsed contribution count for every event. The validated response shape is one event object in `results[0]`, with contributions in `results[0].contributions`; top-level `count` is therefore not the contribution count. An unavailable or malformed export is a source-access failure, not a zero-contribution event.

Use the frozen dictionary [`searches/search-concept-dictionary.json`](searches/search-concept-dictionary.json), deterministic matcher [`searches/tools/concept_matcher.py`](searches/tools/concept_matcher.py), attachment-first harvester [`searches/tools/esa_indico_harvest_match.py`](searches/tools/esa_indico_harvest_match.py), and field-level positive/negative fixtures [`searches/fixtures/esa-matcher-regression.json`](searches/fixtures/esa-matcher-regression.json). Freeze and record their versions and SHA-256 checksums at each execution. The dictionary specifies the exact P/E/M/G/R forms, complete G artifacts (including two-component variation-point artifacts), independent-R span rule, explicit wildcard expansions, standalone boundaries for acronyms, HTML/entity handling, Unicode NFKC case-folding, Unicode-dash and hyphen/space normalization, phrase behavior, and the absence of implicit stemming or lemmatization.

Create one provenance-preserving joined metadata record per contribution from the exact dictionary-listed event, contribution, author, session/track, and material-metadata fields. **Before any P/M candidate gate**, inventory `folders[].attachments` and legacy `material[].resources` for every in-window event and every contribution. Deduplicate duplicate representations by public attachment URL/ID while preserving all event/contribution associations. Attempt anonymous retrieval of every accessible document-like attachment, including PDF, text/HTML, office/open-document, spreadsheet, and slide/poster formats; normalize and match every successfully extracted text. Record protected, inaccessible, failed, malformed, encrypted, scanned/no-text, and otherwise unparseable materials as coverage failures rather than zero hits. Images, audio, and video remain inventoried even when no text extractor applies.

Match two independently preserved routes; do not create a hit by combining P, M, G, R, or E evidence across routes or across separate attachments:

- **joined-metadata route:** all frozen metadata fields for one contribution (or one event-level material record);
- **attachment-text route:** the normalized extractable text of each individual attachment.

For each route:

- **ESA-A1:** `P AND E AND M`, the unchanged EPS-explicit tag within core B;
- **ESA-B1:** `P AND M`, without a mandatory EPS term; and
- **ESA-BG1/ESA-BC1:** `P AND a complete G1/G2 or C1 artifact`, relation-free within the route. Every all-of component (including variation point + model/architecture and domain-specific language + model anchor) must occur in that same route. No bare library/pattern/profile/language term qualifies.
- **ESA-R-tag:** optionally identify the subset with at least one independent R occurrence whose span does not overlap any required artifact-component occurrence; `reference architecture` cannot self-qualify this tag. R is not a candidate or MBSE-evidence requirement.
- **ESA-T2 tag:** apply model-coupled tailoring terms to ESA-B1. Because local core B is already `P AND M` without an R gate, `P AND M_B2 AND T2` is structurally contained and cannot be a separate ESA discovery route.
- **ESA-V1 and ESA-O1 tags:** apply the exact finite cross-source V1/O1 subsets to every candidate route. These are non-candidate sensitivity tags and terms may not combine across metadata and attachment routes.

Union metadata and individual-attachment candidates separately for ESA-B1 and relation-free ESA-BG1/BC1, then union those partitions with complete route and field/attachment/span provenance. Also report separate E-explicit G/C1, R-qualified, T2, V1, and O1 tags; do not relabel expansion-only records as ESA-A1. By construction ESA-A1 is a subset of ESA-B1: report `A∩core-B`, core-B-only, all core/G/C1 and G/C1 intersections/exclusive yields, E-explicit G/C1, independent-R/T2/V1/O1 tags, and total B, require `A-only = 0` as an invariant, and do not interpret the structural zero as poor Stream-A performance. Generic `SmallSat`/small-satellite does not satisfy P. Event date controls source harvesting only; report-level first formal publication date is checked against the common 2026-08-10 cutoff during eligibility screening.

Only after this attachment-first union is complete may screening classify an attachment. Abstracts, posters, slide decks, presentations, and recordings remain lead-only unless a distinct substantive full report is located; they are never discarded solely because surrounding metadata fails P/M. Log every lead-to-report route and screen the distinct report separately. The clean final run must reconcile root/child events, in-window exports, contributions, all materials, retrieval/parse failures, metadata/attachment route yield, A/core-B and core-B/G/C1 overlap, relation-qualified/T2/V1/O1 tags, and the total union. Every diagnostic record remains `pilot_not_candidate_search` and must not be reused as final discovery output.

A complete 2026-08-07 no-screening dry run validated the core implementation: 437 root events; 408 in-window event exports retrieved out of 408; 8,394 contributions; 6,770 material associations; 5,690 unique document-like attachments, of which 5,686 were retrieved, 5,664 yielded extractable text, four failed retrieval, and 22 were unparseable/no-text. After correcting an event-material association over-attribution and rerunning a no-network match over the same complete census, the metadata route produced 17 core-B subjects, attachment text 62, overlap 5, and the union 74, including 57 attachment-only subjects; A∩core-B was 23, core-B-only 51, and A-only 0. Version-1.3 synthetic tests historically passed 19/19 base/concept cases and 13/13 route/individual-attachment cases. The current version-1.6-retained recorded suites pass 21/21 [base/concept cases](searches/fixtures/esa-matcher-regression-results.json) and 9/9 [genericity-route fixtures](searches/fixtures/esa-genericity-route-regression-results.json), including finite T2 and V1/O1 positives plus relation-free G/C1, architecture self-satisfaction, incomplete all-of, cross-route, and cross-attachment negatives. The latter suite is executed by the tracked aggregation regression driver against separate route and attachment fixture documents; route labels are not assertions made by the base matcher alone. A superseding zero-network rematch over the preserved complete 2026-08-07 census evaluated 8,584 subjects and reused 5,664 extracted attachment texts with complete relation-free G/C1 artifacts: core B 74; G 32; C1 15; G∩C1 6; expansion union 41; core∩G 18; core∩C1 14; core∩expansion 26; core-only 48; expansion-only 15 (14 G-only versus core/C1 and 1 C1-only versus core/G); total B 89; unchanged A 23 with A-only 0; E-explicit expansion 16; independent-R tag 41; and local T2 tag 55. Metadata and attachment routes yielded 20 and 75 total-B subjects with overlap 6. These are aggregate `pilot_not_candidate_search` diagnostics—not candidates, screening, eligibility, or evidence—and may not be reused; final validation still requires the complete fresh census. Checksums and coverage details are logged separately.

Known ESA MBSE event IDs `161`, `329`, `386`, `407`, and `472` are a dated 2026-08-06 coverage set only. After the whole-instance harvest, verify that each was enumerated and its contributions processed. Discover and process any later or differently titled MBSE events through the same unrestricted root inventory; do not limit the source to this list.

Report root events returned; events through the common cutoff; contribution exports attempted/retrieved/inaccessible/malformed; contributions parsed; all material attachments inventoried; document-like attachments retrieved, text-parsed, inaccessible, and unparseable; metadata-only, attachment-only, and overlapping routes for core B and relation-free G/C1; `A∩core-B`, partition intersections/exclusive yields, E-explicit expansion, independent-R/T2/V1/O1 tags, and total-union candidates; attachments classified; lead-only records; distinct full reports found; and included reports. A later protocol-approved evidence-window update reruns the full root census, all events through the new common cutoff, and the complete attachment inventory/text match so retrospective changes are detectable.

## 18. NASA NTRS whole-database search

Search the public **NASA Technical Reports Server** through <https://ntrs.nasa.gov/search> and the source's JSON endpoint, `POST https://ntrs.nasa.gov/api/citations/search`. Pre-freeze API diagnostics on 2026-08-06 confirmed that the `published` date object, `page.size: 100`, and zero-based `page.from` pagination are accepted; simple space-delimited terms behave as conjunctions in the tested sets, and quotation marks materially restrict phrases. Explicit `AND` returned the same tested record set but changed ordering, while `OR` and parenthesized Boolean tests unexpectedly returned zero. Therefore, final cells use only space-delimited terms and quoted phrases—no Boolean operators or parentheses—and pagination uses fixed 100-record pages. Cross-check representative cells in the UI at final execution and retain the diagnostic and final logs; these observations are interface validation, not candidate-search results.

Use these query-cell term sets; every quoted phrase remains one source cell term:

- `P_N = {CubeSat, CubeSats, "cube sat", nanosat, nanosatellite, nanosatellites, "nano-satellite", "nano-satellites", "nano satellite", "nano satellites"}`;
- `M_N = {MBSE, "model-based systems engineering", "model based systems engineering", "model-based system engineering", "model based system engineering", SysML, "systems modeling language", "system model", "systems model", "system modeling", "systems modeling", "system modelling", "systems modelling", "reference model", "digital engineering", Arcadia, Capella, "object-oriented systems model"}`; and
- `G_N = {"generic model", "reusable model", "configurable model", "generic system model", "reusable system model", "configurable system model", "model template", "mission-agnostic model", "mission agnostic model", "mission-independent model", "mission independent model", "mission-agnostic architecture", "mission agnostic architecture", "mission-independent architecture", "mission independent architecture", "reference architecture", "domain model", metamodel, "meta-model", "product-line model", "product line model", "product-family model", "product family model", '"variation point" model', '"variation point" architecture'}`; and
- `C_N = {"reference model", "system reference model", "model library", "model libraries", "system model library", "system model libraries", "model pattern", "modeling pattern", "modelling pattern", "system model pattern", "systems model pattern", "model profile", "system model profile", "systems model profile", "SysML profile", '"domain-specific modeling language" MBSE', '"domain-specific modeling language" "model-based systems engineering"', '"domain-specific modeling language" "model based systems engineering"', '"domain-specific modeling language" "model-based system engineering"', '"domain-specific modeling language" "model based system engineering"', '"domain-specific modeling language" SysML', '"domain-specific modeling language" "systems modeling language"', '"domain-specific modeling language" "system model"', '"domain-specific modeling language" "systems model"', '"domain specific modeling language" MBSE', '"domain specific modeling language" "model-based systems engineering"', '"domain specific modeling language" "model based systems engineering"', '"domain specific modeling language" "model-based system engineering"', '"domain specific modeling language" "model based system engineering"', '"domain specific modeling language" SysML', '"domain specific modeling language" "systems modeling language"', '"domain specific modeling language" "system model"', '"domain specific modeling language" "systems model"', '"domain-specific modelling language" MBSE', '"domain-specific modelling language" "model-based systems engineering"', '"domain-specific modelling language" "model based systems engineering"', '"domain-specific modelling language" "model-based system engineering"', '"domain-specific modelling language" "model based system engineering"', '"domain-specific modelling language" SysML', '"domain-specific modelling language" "systems modeling language"', '"domain-specific modelling language" "system model"', '"domain-specific modelling language" "systems model"', '"domain specific modelling language" MBSE', '"domain specific modelling language" "model-based systems engineering"', '"domain specific modelling language" "model based systems engineering"', '"domain specific modelling language" "model-based system engineering"', '"domain specific modelling language" "model based system engineering"', '"domain specific modelling language" SysML', '"domain specific modelling language" "systems modeling language"', '"domain specific modelling language" "system model"', '"domain specific modelling language" "systems model"'}`.

The governing version-1.6 protocol retains the complete Stream-B implementation of **940 cells**: **180 N-B-core cells** (`10 P_N × 18 M_N`), **250 N-BG cells** (`10 P_N × 25 G_N`), and **510 N-BC1 cells** (`10 P_N × 51 C_N`). The 51 C1 atoms comprise 15 direct asset phrases plus every combination of four source-representable domain-specific modeling/modelling-language spellings with all nine frozen MBSE/system-model anchors. Run and log every cell separately to exhaustion; a dated zero or observed subset does not establish source equivalence and is not grounds to omit a frozen cell later. Deduplicate each partition and their union, then report all core/G/C1 intersections, exclusive yields, and total Stream B. The quoted single-string notation above is documentary; each actual `q` is one population atom followed by one complete M, G, or C atom. Variation-point and domain-specific-language atoms contain the shown space-delimited conjunction.

This corrects three pre-final cardinality defects: version 1.2 prose/pilots used six P terms while displaying seven; an early version-1.3 draft compressed three source-representable population forms; and version 1.4 paired each domain-specific-language spelling with only `MBSE` and `SysML` despite NTRS supporting all nine frozen anchors through quoted phrases and space-delimited conjunction. Because no valid final search occurred, no record is affected. Version 1.6 retains all ten explicit population forms and all three complete partitions; wildcard behavior or pilot overlap/zeros cannot authorize omission.

Do not run a redundant mandatory N-A discovery matrix. Instead, after deduplicating the complete N-B-core∪N-BG∪N-BC1 union, deterministically apply the full corrected E/T dictionaries and exact finite V1/O1 subsets in [`searches/search-concept-dictionary.json`](searches/search-concept-dictionary.json) to every returned record's complete available NTRS metadata. Within N-B-core, this is the unchanged **N-A EPS-explicit tag**; within N-BG/N-BC1, report separate expansion-E tags rather than relabeling an expansion-only record as Stream A. The E dictionary includes both electrical/electric subsystem phrases, all functional terms, `power mode`/`power modes`, and `battery`/`batteries`; local tags cannot add candidates. Preserve field-level E hits, report `A∩B-core`, core-B-only, expansion-E, all partition overlaps, and the total union; require structural `A-only = 0` relative to core B and do not interpret that zero as poor Stream-A performance. A small source-query-versus-local-tag equivalence pilot may append one E term to representative parent cells, but those checks are not mandatory discovery cells and cannot compensate for an incomplete matrix.

**N-V1/N-O1** are mandatory deterministic local tags using the exact finite cross-source subsets on the deduplicated N-B-core∪N-BG∪N-BC1 union; they cannot add a source record. Optional source-query equivalence probes may append one V1/O1 term to a logged mandatory parent cell, but are not discovery cells. N-T2 is likewise a deterministic local tag on the core P×M union because `P AND M AND T2` is structurally contained in that union. Record every optional source-query trigger, parent cell, added term, and result; probes/tags do not replace or alter the 940-cell baseline.

The 2026-08-07 `pilot_not_candidate_search` executed its then-specified six-term 108-cell P×M matrix (which omitted `"cube sat"`) and found a six-ID unscreened union. A model-assisted no-screening pilot on 2026-08-10 first reconstructed a different explicit six-term 108-cell core plus 150 P×G cells, then executed the omitted seventh listed population phrase against all 18 M and 25 G atoms. Across the resulting full seven-term core/G design, all **301/301** cells reconciled with no retry or failure: core simple sum 39/deduplicated opaque union 6; G simple sum 1/opaque union 1; core∩G 1, G-only 0. A separate C1 pilot then reconciled all **161/161** seven-form P×C1 cells with valid zero results. A separate exact `"cube sat"` 43-cell repeat also completed 43/43 with valid zero results. Together these runs covered 462 cells. A focused no-screening pilot then reconciled the remaining **198/198** cells for `nanosatellites`, `"nano satellite"`, and `"nano-satellites"` against all 18 M, 25 G, and the then-current 23 C1 atoms; all were valid zeros, so the superseded 660-cell interface design was exercised. Version 1.5 adds **280 unpiloted C1 cells** (`10 P_N × 28 newly restored language-anchor combinations`). No metadata was inspected and no record was screened. Zeros and overlap do not establish source equivalence or authorize cell omission; the added 280-cell syntax/reconciliation pilot is required, and all 940 cells must later be rerun in a clean final directory. The historical 108-cell details remain in [`2026-08-07-ntrs-revised-matrix-validation.md`](searches/subagent-logs/2026-08-07-ntrs-revised-matrix-validation.md), and the version-1.3/1.4 pilots are logged separately.

Do not use `SmallSat` or `small satellite`. Example request body:

```json
{
  "q": "CubeSat \"model-based systems engineering\"",
  "published": {
    "gte": "2011-01-01",
    "lte": "2026-08-10"
  },
  "page": {
    "size": 100,
    "from": 0
  }
}
```

For a non-discovery source-equivalence check only, an example EPS-appended `q` is `nanosatellite "electrical power system" MBSE`. Every mandatory P×M, P×G, or P×C1 discovery cell begins at `from: 0` and increments by 100 until returned pages reconcile with `stats.total`. Archive the exact request body, UTC timestamp, status, raw JSON for every page, checksums, API-reported total, returned records, and representative UI cross-checks. If totals change during pagination, preserve the invalid snapshot and rerun the complete logical cell.

Screen all unique returned records under the protocol's complete date, language, publication-type, population, MBSE, EPS-route, and retrieval rules, and inspect available attachments. Potentially eligible NTRS evidence includes a substantive full primary report—such as a technical publication/memorandum, contractor or grantee report, or conference paper—with methods/results and stable provenance; accessibility alone neither establishes nor defeats scientific eligibility. Preserve NTRS ID, report numbers, STI/document type, technical/peer-review metadata when reported, distribution, version, identifiers, attachment type, and availability. A scientifically plausible report that cannot be obtained follows the protocol's `not_retrieved` route. Abstracts, posters, and presentation-only records are discovery leads only.

Deduplicate NTRS deposits by source ID, report number, DOI, normalized title/author/year, and attachment identity, while retaining all discovery events. Link technical-report, conference, abstract, and presentation manifestations through the protocol's study/implementation report-family mapping; do not erase a substantively distinct report merely because it shares a family.

Report the total and retrieved count for every one of the 940 logical cells, simple sums for core, G, and C1 with overlap explicitly acknowledged, all partition intersections/exclusive yields/total Stream B, the separately deduplicated NTRS union, full-E tag hits with unchanged A/core-B and separate expansion-E counts, T2/V1/O1 tag counts, full reports sought/retrieved, lead-only records, report families, exclusions, and inclusions. Any later protocol-approved evidence-window update reruns the complete 940-cell matrix and reapplies the versioned E/T/V1/O1 matcher because NTRS may add older records retrospectively.

## 19. Citation searching and Buruso recall benchmark

Citation chasing is an `other source`, separate from the authorized version-1.6 operational baseline of fourteen sources/collections through twelve interfaces. OATD is already reported separately in the website/other-methods channel and is not citation chasing. The prespecified platforms are **Scopus** and **Web of Science Core Collection (WoSCC)**. Use the normal Scopus record/citation interface for `Cited by` results and the normal WoSCC `Citing Articles`/Cited Reference Search interfaces with all available Core Collection editions. Google Scholar and Semantic Scholar are not fallback citation indexes.

For every full-text-included report and relevant secondary review:

1. Assign a citation seed/event ID and record the seed DOI, normalized title, year, Scopus EID/source ID and WoS accession when available, report-family ID where applicable, cycle, operator, and search date/time/time zone.
2. **Backward chasing:** inspect the seed's complete full-text reference list. Record the total references inspected and every bibliographically identifiable report taken forward under the normal title/abstract criteria. WoS exported cited references or Scopus indexed references may assist transfer and reconciliation, but they do not replace the source report's reference list.
3. **Forward chasing:** search both Scopus and WoSCC for every seed. Prefer the indexed record/DOI; when a seed is not indexed, use the platform's DOI/title/cited-reference route where supported and retain the exact source-native request. A zero result or indexing failure in one platform does not waive the other platform.
4. Export every forward-citation result available through each platform, preserve its native artifact and source total, normalize it with exact seed/direction/cycle provenance and global rank, and union/deduplicate the two platform sets without erasing duplicate discovery events.
5. Apply the review's date, language, publication-type, population, MBSE, and EPS-thread rules normally. Citation provenance never bypasses eligibility or full-text screening.

Newly included reports become seeds in the next numbered cycle. Repeat complete backward and dual-platform forward chasing until one full cycle produces no new eligible report. Log, for every seed/direction/platform/cycle, source total, retrieved/parsed total, candidates taken forward, duplicates, reports sought, eligibility decisions, included reports, unavailable indexing/export, and stopping result. Citation searches use the common evidence cutoff; if the review search is updated, rerun forward chasing for every seed and backward chasing for any newly included seed. The machine-readable citation-event table is kept under `searches/citation-chasing/`; PRISMA counts remain at record/report level and citation records retain `discovery_route=citation_chasing` separately from their bibliographic database source.

After the independent successful-source candidate set and the explicit failure register covering all fourteen authorized version-1.6 sources/collections are frozen, use this named secondary review:

> Buruso, R. B., Himmiche, S., Tejumola, T., Alemayehu, Y., & Rose, B. (2026). Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review. *Systems Engineering*. https://doi.org/10.1002/sys.70051

Create a read-only benchmark register of its cited reports that appear potentially relevant to CubeSat/nanosatellite MBSE, EPS, outcome/burden, or V&V. Match normalized DOI/title metadata against the independent set and report found/missed status and discovery source. A miss may trigger a logged concept-level recall probe or a citation-chasing event; it cannot be inserted directly. Merge and deduplicate every resulting candidate, then rerun the Buruso and retained-file audits against the expanded set. Repeat this supplementary-search/audit cycle until a full cycle produces no new eligible report; preserve each baseline/audit version rather than silently moving the original freeze point. Record the final eligibility reason for every apparently relevant benchmark report without importing Buruso's classifications.

The use of arXiv, Semantic Scholar, and Google Scholar is forbidden for discovery or citation searching.

## 20. Iteration and count rules

1. Run two or three pilots at a time for query-based sources; do not treat ESA event pagination/harvest requests as separate conceptual searches.
2. Count before full retrieval where supported, then retrieve and inspect every record for each accepted final query or matching operation.
3. A query around 30–70 hits is normally manageable. Do not narrow solely to meet that heuristic if doing so removes a prespecified concept; partition terms and retrieve all partitions instead.
4. If a query is overbroad, inspect a sample and refine using fields or structured-model relations—not outcome direction, open-access status, generic SmallSat terms, or legacy titles.
5. If a query is too narrow, relax one concept variant at a time and log the effect.
6. Retrieve all records available for every accepted final query or source harvest, subject only to documented source/API limits and failures.
7. Compare Stream A and total Stream B unique yield after deduplication; within Stream B report intersections and exclusive yields for core B, B-G, B-C1, and B-T2 where candidate-generating. A broad Stream B route or expansion cannot be dropped merely because most records lack EPS terms in metadata or later fail eligibility.
8. Keep source-reported totals, actually retrieved totals, unique records, reports, report families, EPS threads, reusable-artifact lineages/profiles, tailoring applications, outcome/burden records, and V&V records as distinct counts.

## 21. Merge, deduplication, and screening

- Merge final accepted runs by normalized DOI, then stable source/report ID, then manually confirmed normalized title–author–year.
- Preserve every discovery event: source/platform, query/event ID, exact method, raw artifact, rank when available, and search stream.
- Keep conflicting metadata and document how the preferred value was selected.
- Deduplicate multiple database/source records at record/report level before PRISMA screening counts; separately map substantively distinct companion reports to study/implementation report families.
- Title/abstract tiers follow the protocol:
  - `core`: clear EPS-primary MBSE or likely explicit EPS thread;
  - `supporting`: plausible CubeSat/nanosatellite structured-system MBSE requiring full text to test for an embedded EPS thread;
  - `rejected`: clearly fails population, publication/date/language, or structured-system-model scope.
- Do not reject a Stream B record solely because EPS/power is absent from its title or abstract.
- Discovery through B-G, B-C1, or B-T2 does not establish genericity, tailoring, MBSE qualification, or an EPS thread; screen it under the same rules as every other record and assign RQ1-G dispositions only after inclusion.
- Reject generic SmallSat/small-satellite-only records unless the source identifies a separable CubeSat/nanosatellite case.
- Report secondary reviews and lead-only records separately; do not place them in the primary-evidence corpus.

### PRISMA 2020 flow reconciliation

Use the official new-review template for databases and other sources, backed by a machine-readable count table:

1. retain identification totals separately for all fourteen authorized operational sources/collections, including separate Compendex and Inspec counts from their simultaneous Engineering Village events, separate ATAI and PQDT database events on ProQuest, OATD in the website/other-methods channel, and annual IAF population-harvest plus local-candidate counts; retain each permitted citation/other-source route separately;
2. distinguish source-reported/harvested totals from records actually retrieved or parsed;
3. count duplicate removals before screening separately from records excluded during screening;
4. reconcile records screened, records excluded, reports sought, reports not retrieved, full reports assessed, and full reports excluded with one primary reason;
5. make included **reports** the flow endpoint and report report families, EPS threads, reusable-artifact lineages/profiles, tailoring applications, outcome/burden records, and V&V records only in separate analytic-denominator tables; and
6. do not count a retained legacy file as identification unless it is independently rediscovered or reached through a permitted logged citation route.

## 22. Coverage audit and deferred retained-file recall check

Audit at least these concept/source clusters without using old screening decisions:

- EPS-primary structured models and power/electrical architecture;
- parametric power/energy budgets bound to system models;
- whole-spacecraft SysML/MBSE with possible embedded EPS allocation/interface threads;
- reference/template/domain models and the full range of reported reuse/tailoring approaches;
- generic/reusable/configurable model artifacts, model templates, reference architectures, metamodels, product-line/family models, central reusable assets, variation points, declared applicability envelopes, and source-located tailoring operations;
- digital-engineering/toolchain transformations, interoperability, and implementation burdens;
- beneficial, null, mixed, and adverse EPS-attributed outcomes;
- model versus system/design verification and validation;
- EPS-specific versus system-wide EPS-linked V&V;
- executable pre-physical checks, virtual integration, MIL/SIL/PIL/HIL, and model-to-test continuity;
- substantive institutional technical reports, completed master's-level theses, doctoral dissertations/theses, and conference/workshop papers that may be weakly indexed;
- Web of Science Core Collection Topic retrieval with all available citation-index editions, including CPCI-S/CPCI-SSH and BKCI-S/BKCI-SSH;
- paired Engineering Village retrieval with both Compendex and Inspec selected, including database-specific and cross-database unique yield;
- unrestricted Wiley Articles & Chapters retrieval with deterministic Earliest/two-pass/native-RIS reconciliation, a separate Collections count-only coverage route, and INCOSE International Symposium as a coverage check;
- unrestricted whole-platform Springer Nature Link retrieval, including articles, chapters, conference papers, and reference entries without a brand/venue/access facet;
- ProQuest retrieval with only Advanced Technologies & Aerospace Index selected, `NOFT` concept fields, source-side duplicate exclusion off, and no substitution of its broader parent/full-text databases;
- a separate exact-PQDT-only ProQuest event with all eleven mapped `PQDT-*` queries, observed expansion state, no manuscript/degree/full-text/access limiter, and thesis-to-article/report-family overlap audited;
- whole-index OATD retrieval with all eleven finite `OATD-*` queries, its partial-text/metadata and repository-participation limits, busy/access outcomes, stable-record/pagination reconciliation, linked-repository boundary, and overlap with PQDT retained;
- unrestricted AIAA ARC All-content retrieval across its source-indexed journal, meeting-paper, and book/chapter scope, with no named-venue boundary;
- authorized IAF Digital Library coverage restricted exactly to all 2011–2026 IAC proceedings subject to the common cutoff, with annual population-query totals, public abstract coverage, deterministic local core-B/G/C1 candidate classification, and E/R/T2/V1/O1 tags—not GLEX or other IAF events;
- unrestricted ESA Indico harvest, with the known ESA MBSE workshops as a coverage check;
- NTRS technical-report and conference-paper coverage; and
- Buruso et al. (2026) benchmark recall.

Only after the independent successful-source candidate set and the explicit failure register covering all fourteen authorized version-1.6 sources/collections are frozen, compare normalized DOI/title/source-ID metadata with the retained `markdown/` and `pdfs/` cache. Record found/not-found status and the independent discovery event for matches. Use misses only to design logged concept-level recall probes; a retained file cannot enter the corpus without a valid discovery or protocol-compliant citation-chasing event.

## 23. Planned artifacts

```text
SLR/SLR1/
  protocol.md
  query-search-plan.md
  pilots-to-run-v1.6.md
  search-log.md
  screening.md
  corpus.json
  searches/
    api-pagination-request-templates.json
    tools/
      api_pagination_reconcile.py
      concept_matcher.py
      esa_indico_harvest_match.py
      esa_indico_rematch.py
      search_strategy_lint.py
    fixtures/
      esa-matcher-regression.json
      esa-matcher-regression-results.json
    scopus/
    web-of-science/
    ieee-xplore/
    engineering-village/
      compendex/
      inspec/
    wiley-online-library/
    springer-nature-link/
    proquest-aerospace-index/
    proquest-dissertations-theses-global/
      selection-proof/
      native-exports/
      pass-1/
      pass-2/
      reconciliation/
    oatd/
      interface-snapshots/
      pass-1/
      pass-2/
      reconciliation/
      repository-link-map.json
    aiaa-arc/
    iaf-digital-library-iac/
      counts/
      pass-1/
      pass-2/
      reconciliation/
      matcher-fixtures/
      abstract-not-available.json
    esa-indico/
    nasa-ntrs/
    citation-chasing/
    worklogs/
    merged_candidates.json
    search-manifest.json
    search-concept-dictionary.json
    deduplication-report.json
    report-family-registry.json
    reusable-artifact-lineage-registry.json
    tailoring-applications.json
    genericity-claim-evidence-table.json
    buruso-recall-audit.json
    retained-file-recall-audit.json
    subagent-logs/
  prisma-flow-data.*
  prisma-s-checklist.*
  prisma-2020-checklist.*
```

Raw licensed exports or copyrighted full text may remain non-public where required, but exact strategies/methods, dates, manifests, counts, derived decisions, and rights-aware availability restrictions must be preserved under the integrated PRISMA-S/PRISMA 2020 requirements in this plan and the protocol.

## 24. Search-stage stopping rule

The independent electronic-source and title/abstract corpus stage is complete only when:

- every cumulative mandatory pre-final amendment gate in [`pilots-to-run-v1.6.md`](pilots-to-run-v1.6.md) has an accepted outcome or an explicit fail-closed disposition, without importing pilot records;
- all eleven strategies (`A1`, `A2`, `A3`, `B1`, `B2`, `BG1`, `BG2`, `BC1`, `BT2`, `V1`, and `O1`) have final accepted runs in every version-1.6-authorized direct source/query family—Scopus, Web of Science Core Collection, IEEE Xplore, the paired Compendex-and-Inspec Engineering Village route, Wiley, Springer Nature Link, Advanced Technologies & Aerospace Index on ProQuest, PQDT Global in a separate exact-database ProQuest event, OATD, and AIAA ARC—or a separately documented database/interface failure;
- every `PQDT-*` query has exact PQDT-only selection proof, frozen expansion/dedup/sort/page controls, two complete identical ordered source-ID passes, a native RIS preflight and safe-batch reconciliation, exact-day accounting, and normalized merge provenance—or a documented entitlement/selection/pagination/export failure with no partial candidate import;
- every `OATD-*` query has an exact query echo, complete finite-query acceptance, source-total/30-row/pagination/stable-record-ID validation, two complete identical ordered passes, local date/language accounting, repository-link provenance, and normalized merge reconciliation—or a documented busy/access/syntax/cap/identifier failure with no partial candidate import;
- the paired Engineering Village mixed-database export/normalization preflight has passed, with row-level Compendex/Inspec provenance retained and `merge_search_results.py` regression-tested not to relabel Inspec records;
- all eleven `W-*` Articles & Chapters strategies have exhausted the stable source total at 20/page under explicit Earliest and `--require-complete`, two identical ordered DOI passes, a fresh visible one-record RIS-with-abstract preflight, page-batch DOI/RIS reconciliation, exact-byte native preservation, exact-day cutoff accounting, and normalized merge reconciliation—or have a documented Articles & Chapters access/control/identifier/export failure with no partial candidate import; for each `W-*` query, the separate two-observation Collections route also has either an accepted exact container count or an explicit unresolved/failure status that is not treated as zero and does not enter the bibliographic merge;
- all eleven `ARC-*` strategies have exhausted the stable source total at 20/page under `--require-complete`, two identical ordered DOI passes, a fresh visible per-record RIS preflight, exact-byte native preservation, exact-day cutoff accounting, and normalized merge reconciliation—or have a documented access/identifier failure with no partial candidate import;
- every authorized `IAF-P-2011` through `IAF-P-2026` count and two-pass public-metadata harvest has exhausted and reconciled its exact total, the annual ID sets agree, every detail route has an outcome, missing abstracts and 2026 date precision are accounted for against the common cutoff, deterministic route fixtures pass, every local core-B/G/C1 partition, overlap, and E/R/T2/V1/O1 tag is reported, and no manuscript/full-text/disallowed route was requested—or IAF has a documented source/rights failure with no partial candidate import;
- every ESA Indico event from 2011 through the common 2026-08-10 cutoff has an export/access outcome; every event/contribution material is inventoried; every accessible document-like attachment has a retrieval/text-extraction outcome; and the complete metadata plus extractable attachment text has been matched with the frozen dictionary;
- all 940 mandatory NTRS cells (180 P×M core, 250 P×G, and 510 P×C1) have been paginated to exhaustion or have a documented source failure, partition overlap has been reconciled, and the complete versioned E/T/V1/O1 matcher has tagged the deduplicated union;
- all final-query/source records available within documented limits have been saved, read, and reconciled to source totals;
- required concept clusters, publication types, technical-report routes, and source-specific coverage checks have been audited;
- A1/A2/A3/full-Stream-A, total-Stream-B, core-B/B-G/B-C1/B-T2, V1/O1 tag, and database/source-unique yields are known;
- additional query refinements are predominantly duplicates or irrelevant records rather than merely inconvenient to search;
- the merged candidate set, screening log, and retrieval corpus pass provenance and count checks;
- the independent candidate set and every supplementary expansion have undergone the deferred Buruso and retained-file recall audits, with one complete audit cycle yielding no new eligible report; and
- every unresolved source access failure, lead-only record, and count discrepancy is explicitly logged.

Citation chasing remains a later search phase tied to full-text inclusions and relevant secondary reviews. It applies the same 2026-08-10 evidence cutoff and is complete only after one full cycle of complete backward-reference inspection and forward searching in both Scopus and WoSCC yields no new eligible report; it must not be falsely reported as complete at the independent corpus-construction stage.
