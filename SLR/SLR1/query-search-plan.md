# Query Search Plan: EPS MBSE in CubeSat/Nanosatellite Development

- **Review run:** `eps-mbse-slr-2026`
- **Protocol:** `protocol.md`, version `1.2`, frozen and authorized 2026-08-07
- **Plan status:** final discovery is authorized but not yet executed; rerun every accepted method from a clean final-run artifact set
- **Planned evidence window:** 2011 through the date each final search is run in 2026
- **Electronic sources:** Scopus; Web of Science Core Collection; IEEE Xplore; Compendex on Engineering Village; Wiley Online Library; ESA Indico; NASA Technical Reports Server (NTRS)
- **Search unit:** one exact source-specific query, request body, or reproducible website-harvest/matching operation together with its fields, limits, pagination/coverage settings, date, and raw artifacts

## 1. Purpose and scope

Build a new, independently discovered candidate set for full-text retrieval. The search must support both:

- **Stream A — EPS-explicit:** population × EPS × structured-system-model/MBSE concepts; and
- **Stream B — embedded-thread recall:** population × structured-system-model/MBSE concepts without a mandatory EPS term.

Search sensitivity is broader than final scientific eligibility. Route A/Route B status and the required EPS anchor, model anchor, and explicit bridge are full-text decisions, not metadata assumptions. Generic `SmallSat`/small-satellite work is outside the population and is not a positive search concept.

The seven sources are searched in full within their documented interfaces or public collections. Web of Science is restricted to the Core Collection database but includes all available Core Collection citation-index editions. Wiley is not restricted to INCOSE publications, ESA Indico is not restricted to ESA MBSE workshops, and NTRS is not restricted to a predetermined NASA series. INCOSE International Symposium content and ESA MBSE workshop content are coverage checks only.

### PRESS-corrected pre-freeze validation completed 2026-08-07

| Source | Validated route | Diagnostic completion |
|---|---|---|
| Scopus | Elsevier Scopus Search API, `COMPLETE` | All six corrected no-type-filter strings accepted; unrestricted S-B1 = 85 and completed two ordered 85-record passes over four pages with strict reconciliation and merge preflight |
| Web of Science Core Collection | Clarivate normal Basic Search `Topic`, `Editions: All` | All six corrected strings executed with English/exact dates/no Document Type (including valid WS-A2 zero); Exact Search state recorded; unrestricted WS-B1 ordinary RIS preflight succeeded |
| IEEE Xplore | IEEE JSON search interface | All six corrected no-ContentType strings accepted; unrestricted I-B2 = 47 and completed two ordered 47-record passes over two pages with strict reconciliation and merge preflight |
| Compendex | Engineering Village Expert Search, Compendex only | All six corrected strings accepted under autostemming-off/no-type controls; counts and one-page reconciliation recorded; prior Detailed CSV normalization path remains valid |
| Wiley Online Library | Advanced Search, unrestricted `Anywhere` | All six corrected strings accepted; broad W-B2 103-record pagination reconciled through page 6; prior RIS normalization path remains valid |
| ESA Indico | Whole root/event JSON census plus local attachment-first matcher | Frozen dictionary/code/fixtures passed; 408/408 event exports and all 6,770 material associations inventoried; 5,690 document-like URLs received retrieval/parse outcomes; corrected metadata/attachment A/B routes reconciled |
| NASA NTRS | Public citations JSON API plus representative normal-UI checks | Complete corrected 6×18 P×M matrix executed 108/108; every page reconciled; full-E local tag and A⊆B invariant passed |

Every observation is logged as `pilot_not_candidate_search` in [`search-log.md`](search-log.md); the finding-by-finding closure map is [`2026-08-07-press-finding-resolution.md`](searches/subagent-logs/2026-08-07-press-finding-resolution.md). Under the authorized version 1.2 protocol, final discovery must rerun every accepted method from a clean final-run artifact set.

## 2. Anti-anchoring and provenance rules

1. Do not inspect Git history, deleted legacy search/corpus/extraction files, or retained source Markdown/PDFs while formulating or screening the independent planned-source candidate set.
2. Save every raw run, including zero-result, failed, malformed, and overbroad pilots. A failed request is not a zero-result search.
3. Read each complete saved result/export after every run; record both the source-reported total and records actually retrieved or parsed.
4. Give every artifact a new-run query/event ID and record source/database and platform, exact query/request/method, filters, run date/time/time zone, limits/pages or harvest coverage, status, assessment, and successor/predecessor refinement.
5. Do not import legacy IDs. Assign `eps-mbse-slr-2026-r####` IDs only after final merge/deduplication. A prior ID may later be recorded only as `legacy_corpus_id` after an independently rediscovered report is matched.
6. The retained `markdown/` and `pdfs/` directories are retrieval caches only. Match against them after the independently discovered seven-source baseline is merged and frozen.
7. Buruso et al. (2026) is a named secondary-review seed and deferred recall benchmark. Do not use its bibliography to insert candidates into the independent baseline.

## 3. Eligibility-related search limits

- **Years:** first formal publication from 2011 through each source's exact search date, inclusive. When source controls admit the rest of 2026 or the rest of the run month (Scopus, IEEE Xplore, Compendex `Latest`, and Wiley), preserve the unaltered source total, then apply and log an exact-day first-formal-publication cutoff with the number removed.
- **Language:** English where the source supports a reliable filter; otherwise screen language.
- **Publication types:** full primary-research journal articles, conference/proceedings or workshop papers, research chapters, and substantive institutional technical reports. Empirical comparison and experience reports are eligible. Abstract-only, poster-only, presentation/slide-only, and recording-only records may be discovery leads but are not primary evidence.
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

Broad `model-based` or `simulation` is insufficient alone. When broad model terms are used, combine them with a systems-engineering relation/concern block such as requirements, function/behavior, architecture, interfaces, traceability, parametrics, verification, or validation.

### O/V — selected, non-exhaustive outcome, burden, and V&V sensitivity probes

These lists define the broader optional tagging vocabulary. The exact `*-O1` and `*-V1` strategies below intentionally select a source-representable subset spanning the priority outcome/burden and V&V domains; they are sensitivity probes, not complete translations or baseline eligibility filters. The subset avoids making outcome reporting mandatory and keeps comparable probes across sources. Any later expansion requires a separately logged syntax/count pilot.

- **Outcomes:** `reliab*`, `mission assurance`, `reproduc*`, `reuse`, `reusable`, `integrab*`, `interoperab*`, `traceab*`, `interface consistency`, `lifecycle continuity`, `benefit`, `impact`, `outcome`, `no effect`, `adverse`.
- **Implementation burdens:** `burden`, `effort`, `workload`, `overhead`, `cost`, `schedule`, `time`, `training`, `skill`, `learning curve`, `licen*`, `resource`, `maintenance`, `governance`, `adoption`.
- **V&V:** `verification`, `validation`, `V&V`, `model verification`, `model validation`, `system verification`, `system validation`, `design verification`, `design validation`, `requirements-in-the-loop`, `model checking`, `virtual integration`, `MIL`, `model-in-the-loop`, `SIL`, `software-in-the-loop`, `PIL`, `processor-in-the-loop`, `HIL`, `hardware-in-the-loop`, `test case`, `test procedure`, `model-to-test`.

## 5. Common execution and PRISMA-S log rules

For every source, preserve the source/platform name, actual web/API/script interface and version where known, endpoint, exact source-native query or request, all limits and filters, date/time/time zone, reported total, retrieved/parsed total, pagination or event coverage, raw filenames and checksums, operator, refinement history, and final disposition (`planned`, `piloted`, `accepted_final`, `replaced`, `failed`, or `not_run`, with predecessor/successor IDs). Also record whether the interface exposes automatic stemming, lemmatization, or term expansion and its observed state/default; explicit frozen variants remain in the strategy regardless. Draft strings below are not evidence that a search ran. The final supplement must reproduce the exact strings, request bodies, matching dictionaries, and methods actually executed—not cleaned translations.

Before the first valid run in each source, record the selected interface and its pagination/export behavior in the search log. Where a source changes syntax, facets, pagination, or export behavior, retain the failed attempt and pilot the correction. A source failure must be documented; it is not permission to silently omit that source. Search-source duplicates are retained as discovery events until the merged record-level deduplication stage.

Apply the official [PRISMA-S checklist](https://www.prisma-statement.org/prisma-search) as follows:

| PRISMA-S item | Execution/reporting rule for this review |
|---|---|
| 1. Database and platform | Name each source and the actual platform, interface, endpoint, and provider used. |
| 2. Multi-database searching | No simultaneous multi-database platform search is planned; report this as not applicable if true at completion. |
| 3. Registries | No study registry search is planned; report this explicitly rather than treating a bibliographic source as a registry. |
| 4. Online resources/browsing | Log the full Wiley search, whole-instance ESA harvest, full NTRS search, and every deliberate venue/website coverage audit with scope, method, date, yield, and stopping rule. |
| 5. Citation searching | Use the complete reference list for backward chasing and both Scopus and Web of Science Core Collection for forward chasing; log seed set, direction, exact index/interface, cycles, yield, decisions, failures, and stopping outcome as an “other source.” |
| 6. Contacts | Author/expert contact is not an unlogged discovery route. If later used for retrieval or clarification, log who/what was sought, date, outcome, and resulting discovery provenance; otherwise report that no contacts were used. |
| 7. Other methods | Report Buruso and retained-file checks as deferred recall audits, not direct sources; distinguish discovery from manual retrieval. |
| 8. Full strategies | Preserve each source-native strategy/request/dictionary exactly as executed, including syntax, fields, filters, partitions, and failed/replaced runs. |
| 9. Limits/restrictions | Report and justify date, language, population, publication-type, field, pagination/harvest, and access restrictions and every source-specific exception. |
| 10. Search filters | No published search filter is currently used. If that changes, cite it, identify modifications, and preserve the exact implementation. |
| 11. Prior work | No legacy strategy is reused. Disclose and cite any later substantive adaptation of another review's strategy. |
| 12. Updates | The final search-update policy is deferred. Once decided, record it prospectively and preserve every rerun as a separate search event; do not imply an update occurred if none did. |
| 13. Search dates | Record the last-run date for every final query, ESA harvest/match, NTRS cell, citation cycle, and other source—not one global date. |
| 14. Peer review | Interface pilots and model/subagent checking are not formal information-specialist peer review. If human search peer review is later arranged, log reviewer, framework, date, feedback, and changes; otherwise report that none occurred. |
| 15. Records identified | Preserve source-reported and actually retrieved totals per run, plus source/stream unions before deduplication, and reconcile them to the PRISMA flow. |
| 16. Deduplication | Record software/version, normalization, matching precedence/thresholds, manual adjudication, and counts removed. Keep record deduplication separate from report-family mapping. |

Source-interface validation before freeze is diagnostic only. Preserve its exact requests and aggregate behavior in `search-log.md`, label it `pilot_not_candidate_search`, and rerun every accepted strategy after protocol authorization. Pilot hits cannot establish evidence membership or the independent baseline.

Preserve every source-native structured export. In addition, create one normalized JSON or CSV artifact per query/batch for `merge_search_results.py`. Compatible CSV columns are `Search source`, `Query`, `Rank`, `Paper ID`, `DOI`, `Title`, `Authors`, `Publication year`, `Abstract`, `Citation count`, `URL`, `Open access PDF`, and `Source total`; `Search source`, exact `Query`, and global result `Rank` are required for provenance even when the native export omits them. Never overwrite or mislabel the native export. Run a merge smoke test on each source's first normalized batch before final retrieval continues. For Scopus and IEEE API routes, a partial page is never a merge input: the first merge preflight is the first successful complete, reconciled normalized pass.

## 6. Scopus validated API and planned searches

Use the Elsevier Scopus Search API (`https://api.elsevier.com/content/search/scopus`, `COMPLETE` view) with Scopus `TITLE-ABS-KEY` concept blocks, explicit `PUBYEAR AFT 2010` and `PUBYEAR BEF 2027` limits, and English. Apply **no discovery document-type restriction**; verify publication type during screening so reports, secondary-review leads, and atypically indexed eligible manifestations are not silently suppressed. Never serialize an API key, cookie, or access token.

The Search API request exposes no separate automatic stemming/lemmatization parameter in the validated template. Record that absence and any changed source documentation/default at final execution; never infer singular/plural or US/UK equivalence, because the explicit variants below remain mandatory.

Pre-freeze diagnostics on 2026-08-06 accepted all six original strings. API totals were: S-A1 = 3, S-A2 = 9, S-B1 = 75, S-B2 = 55, S-V1 = 1, and S-O1 = 4. A complete diagnostic retrieval of S-A1 reconciled all 3 records and normalized JSON merged successfully. On 2026-08-07, the normal Scopus web UI accepted the revised population block and returned S-B1 = 80 versus 75 under matched web-UI controls. An initial API retry failed authentication and produced invalid empty shells, but a later institutional-network retry successfully reproduced original S-B1 = 75 and revised S-B1 = 80 in `COMPLETE` view. These are `pilot_not_candidate_search` observations; after authorization, confirm API authentication afresh and rerun all six revised strategies using only final-run artifacts for discovery.

### Scopus request template, pagination, and acceptance rule

The versioned non-secret template is [`searches/api-pagination-request-templates.json`](searches/api-pagination-request-templates.json). Its `prospective_final_execution.scopus` object contains the corrected no-type-filter S-B1 preflight request; the separate top-level `scopus` object preserves the historical MAJOR-06 pilot descriptor only. For every final `S-*` execution, start from the prospective object, replace only `query` with the complete corresponding displayed string below—already including its year clauses—and retain every other template field:

- **GET** `https://api.elsevier.com/content/search/scopus`; `Accept: application/json`; supply `X-ELS-APIKey` only from the secure runtime environment, never in an URL, artifact, log, or command transcript.
- Query parameters: `count=25`, `start=0,25,50,…`, `view=COMPLETE`, `sort=eid`, and `httpAccept=application/json`. The historical delegated pilot observed `start=0,25,50,75` and pages of 25, 25, 25, and 5 against 80. The PRESS-corrected unrestricted S-B1 preflight then observed the same offsets and a terminal `start=75` page of 10 against 85. `start` is therefore frozen as zero-based offset pagination, not a cursor.
- Treat `search-results.opensearch:totalResults` on page 1 as the snapshot total; require it unchanged on every subsequent page. Use `entry.eid` in returned order as the page ID, `sort=eid` as the declared source ordering, and preserve ranks `start + 1` through `start + returned_count`. The corrected preflight's full 85-ID sequence was non-increasing by EID and identical across two complete passes.
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

### S-B1 — embedded-thread baseline with explicit MBSE/languages

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-B2 — embedded-thread structured-model expansion

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-V1 — EPS-linked V&V sensitivity probe

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND TITLE-ABS-KEY(verification OR validation OR traceab* OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure") AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

### S-O1 — outcome and implementation-burden sensitivity probe

```text
TITLE-ABS-KEY(cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND TITLE-ABS-KEY(reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab* OR benefit* OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licen* OR adoption) AND LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027
```

## 7. Web of Science Core Collection validated browser interface and planned searches

Search **Web of Science Core Collection**, not All Databases, through Clarivate's normal browser interface at <https://www.webofscience.com/wos/woscc/basic-search>. Use Basic Document Search with one complete Boolean expression in the **Topic** field. Before every final run, confirm `Search in: Web of Science Core Collection` and `Editions: All`, with all available Core Collection editions selected: SCI-EXPANDED, SSCI, AHCI/A&HCI, CPCI-S, CPCI-SSH, BKCI-S, BKCI-SSH, ESCI, CCR-EXPANDED, and IC. Preserve the edition list because entitlements and available coverage may change.

Apply source-native controls for Publication Date from `2011-01-01` through the actual run date and Language = `English`. Select **no Document Type restriction** at discovery; verify publication type during screening. Do not restrict by organization, research area, source title, open-access status, citation count, or individual Core Collection edition. Preserve the Basic Search history entry, exact Topic string, controls, selected editions, run date/time/time zone, source total, declared sort, page size, and complete result/export reconciliation. If Advanced Search is used as a fallback, log its `TS=`/`PY=` strategy as a distinct source-native implementation and demonstrate set equivalence rather than assuming it.

Before each final run, open the current WoS Search Settings and record the observed **Exact Search/lemmatization** control and state. Use the same documented state for all six runs and retain every explicit spelling/number variant regardless; equal counts never establish expansion equivalence. If the Basic Search route no longer exposes or reports the control, record the source default as observed rather than guessing.

A 2026-08-07 PRESS-corrected Basic/Topic pilot used Publication Date `2011-01-01`–`2026-08-07`, English, Editions All, and no Document Type restriction. Dynamic totals were WS-A1 = 1, WS-A2 = 0 (the clean follow-up displayed `Your search found no results`), WS-B1 = 43, WS-B2 = 34, WS-V1 = 1, and WS-O1 = 1. Final B1 versus the same query minus only `"nano satellites"` was 43 versus 43; unrestricted versus the old three-type restriction was also 43 versus 43, with no set-equivalence inference. The Advanced `Exact search` switch was observed unchanged at `aria-checked=false`; no expansion semantics were inferred. Corrected unrestricted WS-B1 also completed an ordinary non-Fast-5000 one-record RIS export. These are `pilot_not_candidate_search` observations; rerun every strategy and export preflight after authorization. Full observations are in [`2026-08-07-press-browser-source-validation.md`](searches/subagent-logs/2026-08-07-press-browser-source-validation.md).

Use Relevance sort and a declared page size (50 was observed). Read and reconcile every results page, retaining global rank. Use **ordinary Export**, never Fast 5000, in source-supported ranges no larger than 1,000 records. A one-record pilot validated RIS with Custom selection (30), including the WoS accession number, DOI, title, authors, publication year, abstract, editions, and cited references; preserve native RIS unchanged. Normalize each batch with `academic-search/scripts/ris_to_merge_csv.py`, supplying source `Web of Science Core Collection`, the exact query, zero-based rank offset, and source total. Preserve cited references in the native RIS and a reproducible sidecar because the common merge schema does not carry them. Then run `merge_search_results.py`, whose regression-tested alias canonicalizes this source as `web_of_science_core_collection`. Repeat a one-record export/normalization/merge preflight after authorization before bulk export. If ordinary export redirects to authentication or fails, log the failure and obtain an authorized manual export; do not use the Fast 5000 login path as an undocumented substitute.

### WS-A1 — explicit EPS names × explicit MBSE/language

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### WS-A2 — EPS analyses/interfaces × structured system model

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### WS-B1 — embedded-thread baseline with explicit MBSE/languages

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### WS-B2 — embedded-thread structured-model expansion

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)
```

### WS-V1 — EPS-linked V&V sensitivity probe

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceab* OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### WS-O1 — outcome and implementation-burden sensitivity probe

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab* OR benefit* OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licen* OR adoption)
```

## 8. IEEE Xplore validated interface and planned searches

Use IEEE Xplore's JSON search interface at `https://ieeexplore.ieee.org/rest/search` through the source-native pagination reconciler, with unfielded Boolean metadata search, inclusive years 2011–2026, and language `English`. Apply **no Content Type refinement** at discovery; verify publication type during screening. Obtain the source total from the reconciler's first page and retrieve the complete result set under the fixed request template; do not treat a count-only response as complete retrieval.

The validated JSON request exposes no separate automatic stemming, lemmatization, or term-expansion parameter. Record that absence and any interface-default statement observed at final execution; the explicit singular/plural and US/UK forms below remain mandatory.

Pre-freeze diagnostics on 2026-08-06 accepted all six original strings and all intended facets. Displayed/API totals were: I-A1 = 4, I-A2 = 2, I-B1 = 38, I-B2 = 42, I-V1 = 1, and I-O1 = 4. A complete diagnostic retrieval of I-A1 reconciled all 4 records and normalized JSON merged successfully. On 2026-08-07, the revised complete population block was accepted; I-B1 remained 38, I-V1 remained 1, and I-O1 remained 4. Equal counts do not prove identical sets. These counts and records are `pilot_not_candidate_search`; rerun every revised query after authorization, preserve fresh count and full-retrieval events, and use only those final reruns for discovery.

### IEEE Xplore request template, pagination, and acceptance rule

The versioned non-secret template is [`searches/api-pagination-request-templates.json`](searches/api-pagination-request-templates.json). Start from `prospective_final_execution.ieee_xplore` (not the preserved historical top-level `ieee_xplore` pilot descriptor). For every final `I-*` execution, replace only `queryText` with the corresponding displayed query below and retain the observed request fields: `action=search`, `newsearch=true`, `matchBoolean=true`, `matchPubs=true`, `highlight=false`, `returnType=SEARCH`, `rowsPerPage=25`, `sortType=newest`, `ranges=["2011_2026_Year"]`, and the sole refinement `Language:English`. Do not add a `ContentType` refinement. The fixed non-secret HTTP headers are in that template; never persist `userInfo`, cookies, or any access context.

The historical delegated I-B2 pilot observed one-based `pageNumber=1,2`, with `startRecord/endRecord` 0/25 then 25/42. The PRESS-corrected no-type-filter I-B2 preflight observed 0/25 then 25/47, 25 and 22 records, and `totalPages=2`; `pageNumber=0` aliased the first page during a separate probe and is prohibited. `sortType=newest` changed the first-page ordered-ID sequence from the default/relevance sequence; the corrected preflight's full 47 `articleNumber` IDs were identical across two complete passes. Preserve source response order as global ranks 1–47; do not invent a cursor or an unobserved sort field.

Use [`searches/tools/api_pagination_reconcile.py`](searches/tools/api_pagination_reconcile.py) with the common retry, total-change, missing-page, duplicate-ID/page, and strict `retrieved == source total` rules in the template. It retries network/408/425/429/5xx failures three times after the initial request with `Retry-After` or capped exponential backoff, treats redirect/access/challenge/non-JSON responses as failures, reruns one whole snapshot after a changed total, and requires an identical second full ordered-ID pass. Do not merge or screen failed snapshots; pilot outputs remain superseded `pilot_not_candidate_search` artifacts. The empirical run, checksums, archive manifests, and merge preflights are in [`2026-08-07-scopus-ieee-multipage-api-validation.md`](searches/subagent-logs/2026-08-07-scopus-ieee-multipage-api-validation.md).

### I-A1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### I-A2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR batteries OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### I-B1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### I-B2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation)
```

### I-V1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### I-O1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR "mission assurance" OR reproducibility OR reuse OR reusable OR integrability OR interoperability OR traceability OR benefit OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR adoption)
```

## 9. Compendex validated interface and planned searches

Search **Compendex on Elsevier Engineering Village** through Expert Search at <https://www.engineeringvillage.com/search/expert.url?database=1>. Select **Compendex only** in the database control and preserve that selection in the Search Summary; do not rely on the accepted but currently undocumented `(cpx WN DB)` expression. Use `KY` (`Subject/Title/Abstract`) for concept blocks, uppercase Boolean, double-quoted phrases, and explicit wildcards. Use the literal suffix `AND (2011-* WN YR) AND (({English}) WN LA)` and also display/log Published = 2011–Latest in the UI.

Set **Turn autostemming off** to checked, because the strategy already prespecifies variants and wildcards and the pilot showed that changing this control materially changes retrieval. Use Relevance sort and 100 records per page; retrieve all pages. Do not apply a document-type filter at discovery: the current index distinguishes journal, conference, chapter, article-in-press, book, and report-related values, and the small gain from filtering does not justify suppressing potentially eligible online-first or institutional-report records. Apply the protocol's publication-type rule during screening.

### C-A1

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-A2

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model") WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-B1

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-B2

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") WN KY) AND ((requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-V1

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((verification OR validation OR traceab* OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure") WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-O1

```text
((cubesat OR cubesats OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab* OR benefit* OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licen* OR adoption) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

The first browser diagnostic validated the original expressions under controls later superseded. A 2026-08-07 PRESS-corrected pilot used the exact final strings above with Compendex only, Published 2011–Latest, the literal year/language suffix, autostemming off, Relevance, 100/page, and no type filter: C-A1 = 3, C-A2 = 6, C-B1 = 76, C-B2 = 58, C-V1 = 1, and C-O1 = 1. Final B1 versus the same text minus only `"nano satellites"` was 76 versus 76; equal totals do not prove equal sets. The server summary can retain a broad coverage label despite the literal year clause, so retain both the `YR` clause and UI Published control, audit every exported publication date, preserve the source total, and log removals after the exact run-day cutoff. These are syntax/interface observations, not candidate searches; rerun all six exact strings after authorization. Full details are in [`2026-08-07-press-browser-source-validation.md`](searches/subagent-logs/2026-08-07-press-browser-source-validation.md).

Engineering Village exposed EndNote/RIS, BibTeX, ASCII, CSV, Excel, PDF, and RTF, with Current page, Citation, Abstract, and Detailed record options and a session basket labelled to 5,000 selected records. A normal one-record **CSV Detailed record** pilot produced a native file with 29 columns; because it omitted exact query and rank, a normalized CSV added the common provenance columns and passed `merge_search_results.py` with source, query, rank, and 1/1 raw/unique counts preserved. Repeat this preflight after authorization, preserve native and normalized files separately, and then export the complete set in logged batches. Save the Search Summary and reconcile source totals, pages, selections, and export batches.

Official platform documentation checked on 2026-08-06:

- <https://www.elsevier.com/products/engineering-village/databases/compendex>
- <https://www.elsevier.support/engineering-village/answer/how-can-i-improve-my-expert-search>
- <https://www.elsevier.support/engineering-village/answer/what-are-the-expert-search-field-codes>
- <https://www.elsevier.support/engineering-village/answer/what-are-the-search-fields-in-the-compendex-database>

## 10. Wiley Online Library validated interface and planned searches

Search the **entire Wiley Online Library publisher database**, not a selected journal or proceedings series. The validated interface is Wiley Online Library Advanced Search, <https://onlinelibrary.wiley.com/search/advanced>, submitting GET requests to `https://onlinelibrary.wiley.com/action/doSearch`. Use one `Anywhere` row (`field1=AllField`) containing the complete parenthesized query in `text1`. Uppercase Boolean `AND`/`OR`/`NOT`, quoted phrases, parenthesized groups, hyphenated phrases, and non-leading unquoted wildcards such as `nanosat*` were accepted on 2026-08-06; unseparated terms default to `AND`, but explicit operators and parentheses are retained.

Use `AfterMonth=1`, `AfterYear=2011`, `BeforeMonth=<run month>`, and `BeforeYear=<run year>`. Wiley normalizes the upper bound to the last day of that month, so screen out any record after the actual run date. No reliable language or pre-search content-type control was exposed. Do not apply `PubType`, INCOSE, journal, ISSN, subject, access-status, or other venue facets to the baseline. Preserve and process the individual `Articles & Chapters` results (`content=articlesChapters&target=default`); separately log and inspect the `Collections` tab as a container/coverage route rather than counting a collection as a primary-evidence report.

For each run, preserve the exact query, generated URL/parameters, server-normalized query/date display, active tab, default sort (`Relevance`) or any changed sort, reported total, and every page. The `Anywhere` label does not document its precise metadata/full-text coverage, so make no claim that it is equivalent to Scopus `TITLE-ABS-KEY`; it is nevertheless the platform's validated unrestricted field.

### W-A1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### W-A2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR battery OR batteries OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "power mode" OR "power modes" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR "system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella OR "object-oriented systems model")
```

### W-B1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### W-B2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("system model" OR "systems model" OR "system modeling" OR "systems modeling" OR "system modelling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)
```

### W-V1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### W-O1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano-satellites" OR "nano satellite" OR "nano satellites") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR "mission assurance" OR reproducibility OR reuse OR reusable OR integrability OR interoperability OR traceability OR benefit OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR adoption)
```

Outcome/burden and V&V terms remain optional probes, not baseline restrictions.

A 2026-08-07 PRESS-corrected whole-platform pilot accepted all six exact strings. Articles & Chapters totals were W-A1 = 7, W-A2 = 46, W-B1 = 44, W-B2 = 103, W-V1 = 17, and W-O1 = 21; Collections were respectively unresolvable (the direct route fell back and is not a zero), 2, 1, 4, 1, and 1. Final W-B1 versus the same query minus only `"nano satellites"` remained 44 Articles & Chapters and 1 Collection; equal totals do not establish identical sets. W-B2 pagination reached active page 6 with 3 cards at `pageSize=20`, reconciling 103. Wiley rendered its sort control as `Date` in this dated pilot, so preserve the actual declared sort rather than assuming an earlier default. These observations are `pilot_not_candidate_search`; rerun all six exact strategies after authorization. Full details are in [`2026-08-07-press-browser-source-validation.md`](searches/subagent-logs/2026-08-07-press-browser-source-validation.md).

If Wiley rejects or silently rewrites a final expression, first use its validated multi-row equivalent: P, E, and M OR-blocks in three `AllField` rows for Stream A, or P and M in two rows for Stream B; Wiley AND-combines non-empty rows. Confirm source-equivalent counts/sets before acceptance. If needed, partition into finite population-term × model-term cells and, for Stream A, population-term × EPS-term × model-term cells; save each partition and union all complete sets. If no reproducible route works, record a source failure and obtain prospective approval rather than substituting an external index.

Retrieve every active-tab page with `pageSize=20` and zero-indexed `startPage=0,1,...`; verify rendered page identity because an AJAX URL change can leave stale DOM, and reconcile page counts to the active-tab total. Export page-scoped selections in tested-safe batches of 20. Wiley exposed Plain Text, RIS, EndNote, BibTeX, Medlars, and RefWorks—not native CSV—and its citation form supports `include=abs`. Preserve each native RIS batch and transform it with `academic-search/scripts/ris_to_merge_csv.py` to a merge-compatible CSV containing `Search source`, `Query`, `Rank`, `Paper ID`, `DOI`, `Title`, `Authors`, `Publication year`, `Abstract`, `Citation count`, `URL`, `Open access PDF`, and `Source total`; retain both forms and test every normalized CSV with `merge_search_results.py`. A one-record normal-UI RIS pilot preserved its `N2` abstract and the normalized source, exact query, global rank, source total, and 1/1 merge counts. Never describe normalized CSV as a Wiley-native export.

Preserve result-page HTML/PDF where permitted, citation exports, DOI/title/author/year/source metadata, access status, and count reconciliation. INCOSE International Symposium (online ISSN `2334-5837`) is a coverage audit after the unrestricted Wiley baseline: verify that unrestricted searches recover relevant known symposium records and log any targeted audit query separately; never use the series as the Wiley source boundary.

## 11. ESA Indico whole-instance harvest and search

Search **the entire public ESA Indico instance**, not only events labeled MBSE. A pre-freeze diagnostic on 2026-08-06 found 437 unique events in the root export; its event-ID set exactly equaled the union of public top-level category exports 5, 6, and 7, and nested category 9 was a subset of category 6. All root events had parseable dates, 408 were dated 2011-01-01 through the diagnostic date, and all five known MBSE coverage-event IDs were present. This validates the root endpoint's recursive census behavior at pilot time only. Repeat and save the root/child set comparison at every final harvest so a later category or visibility change is detected. At every harvest:

1. save the official root inventory from <https://indico.esa.int/export/categ/0.json> and any child-category exports needed by the validation;
2. reconcile reported event counts with returned unique event IDs and document duplicate/category-path handling;
3. retain every event dated from 2011-01-01 through the harvest date, logging missing/unparseable dates as exceptions; and
4. for every in-window event, irrespective of apparent topic, retrieve and save `https://indico.esa.int/export/event/{id}.json?detail=contributions`.

Record HTTP status, retrieval time, access/protection outcome, retries, checksum, and parsed contribution count for every event. The validated response shape is one event object in `results[0]`, with contributions in `results[0].contributions`; top-level `count` is therefore not the contribution count. An unavailable or malformed export is a source-access failure, not a zero-contribution event.

Use the frozen dictionary [`searches/search-concept-dictionary.json`](searches/search-concept-dictionary.json), deterministic matcher [`searches/tools/concept_matcher.py`](searches/tools/concept_matcher.py), attachment-first harvester [`searches/tools/esa_indico_harvest_match.py`](searches/tools/esa_indico_harvest_match.py), and field-level positive/negative fixtures [`searches/fixtures/esa-matcher-regression.json`](searches/fixtures/esa-matcher-regression.json). Freeze and record their versions and SHA-256 checksums at each execution. The dictionary specifies the exact P/E/M forms, explicit wildcard expansions, standalone boundaries for acronyms, HTML/entity handling, Unicode NFKC case-folding, Unicode-dash and hyphen/space normalization, phrase behavior, and the absence of implicit stemming or lemmatization.

Create one provenance-preserving joined metadata record per contribution from the exact dictionary-listed event, contribution, author, session/track, and material-metadata fields. **Before any P/M candidate gate**, inventory `folders[].attachments` and legacy `material[].resources` for every in-window event and every contribution. Deduplicate duplicate representations by public attachment URL/ID while preserving all event/contribution associations. Attempt anonymous retrieval of every accessible document-like attachment, including PDF, text/HTML, office/open-document, spreadsheet, and slide/poster formats; normalize and match every successfully extracted text. Record protected, inaccessible, failed, malformed, encrypted, scanned/no-text, and otherwise unparseable materials as coverage failures rather than zero hits. Images, audio, and video remain inventoried even when no text extractor applies.

Match two independently preserved routes; do not create a hit merely by combining a P term from one route with an M term from the other:

- **joined-metadata route:** all frozen metadata fields for one contribution (or one event-level material record);
- **attachment-text route:** the normalized extractable text of each individual attachment.

For each route:

- **ESA-A1:** `P AND E AND M`, reported as an EPS-explicit tag;
- **ESA-B1:** `P AND M`, without a mandatory EPS term.

Union the metadata and attachment-text ESA-B1 candidates and retain field/attachment-level term hits and route provenance. By construction ESA-A1 is a subset of ESA-B1: report `A∩B`, `B-only`, and the union, require `A-only = 0` as an invariant, and do not interpret the structural zero as poor Stream-A performance. Generic `SmallSat`/small-satellite does not satisfy P. Event date controls source harvesting only; report-level first formal publication date is checked again during eligibility screening.

Only after this attachment-first union is complete may screening classify an attachment. Abstracts, posters, slide decks, presentations, and recordings remain lead-only unless a distinct substantive full report is located; they are never discarded solely because surrounding metadata fails P/M. Log every lead-to-report route and screen the distinct report separately. A complete pre-freeze no-screening dry run must reconcile root/child events, in-window exports, contributions, all materials, retrieval/parse failures, metadata/attachment route yield, A/B overlap, and union counts; its records remain `pilot_not_candidate_search` and must not be reused as final discovery output.

A complete 2026-08-07 no-screening dry run validated this implementation: 437 root events; 408 in-window event exports retrieved out of 408; 8,394 contributions; 6,770 material associations; 5,690 unique document-like attachments, of which 5,686 were retrieved, 5,664 yielded extractable text, four failed retrieval, and 22 were unparseable/no-text. After correcting an event-material association over-attribution and rerunning a no-network match over the same complete census, the metadata route produced 17 B subjects, attachment text 62, overlap 5, and the union 74, including 57 attachment-only subjects; A∩B was 23, B-only 51, and A-only 0. These are aggregate `pilot_not_candidate_search` matcher diagnostics—not candidates, screening, or evidence—and may not be reused. Checksums and coverage details are in [`2026-08-07-esa-attachment-first-validation.md`](searches/subagent-logs/2026-08-07-esa-attachment-first-validation.md).

Known ESA MBSE event IDs `161`, `329`, `386`, `407`, and `472` are a dated 2026-08-06 coverage set only. After the whole-instance harvest, verify that each was enumerated and its contributions processed. Discover and process any later or differently titled MBSE events through the same unrestricted root inventory; do not limit the source to this list.

Report root events returned; in-window events; contribution exports attempted/retrieved/inaccessible/malformed; contributions parsed; all material attachments inventoried; document-like attachments retrieved, text-parsed, inaccessible, and unparseable; metadata-only, attachment-only, and overlapping candidate routes; `A∩B`, `B-only`, and union candidates; attachments classified; lead-only records; distinct full reports found; and included reports. A later protocol-approved search update reruns the full root census, all in-window event exports, and the complete attachment inventory/text match so retrospective changes are detectable.

## 12. NASA NTRS whole-database search

Search the public **NASA Technical Reports Server** through <https://ntrs.nasa.gov/search> and the source's JSON endpoint, `POST https://ntrs.nasa.gov/api/citations/search`. Pre-freeze API diagnostics on 2026-08-06 confirmed that the `published` date object, `page.size: 100`, and zero-based `page.from` pagination are accepted; simple space-delimited terms behave as conjunctions in the tested sets, and quotation marks materially restrict phrases. Explicit `AND` returned the same tested record set but changed ordering, while `OR` and parenthesized Boolean tests unexpectedly returned zero. Therefore, final cells use only space-delimited terms and quoted phrases—no Boolean operators or parentheses—and pagination uses fixed 100-record pages. Cross-check representative cells in the UI at final execution and retain the diagnostic and final logs; these observations are interface validation, not candidate-search results.

Use these query-cell term sets; every quoted phrase remains one source cell term:

- `P_N = {CubeSat, CubeSats, "cube sat", nanosatellite, "nano-satellite", nanosat, "nano satellites"}`;
- `M_N = {MBSE, "model-based systems engineering", "model based systems engineering", "model-based system engineering", "model based system engineering", SysML, "systems modeling language", "system model", "systems model", "system modeling", "systems modeling", "system modelling", "systems modelling", "reference model", "digital engineering", Arcadia, Capella, "object-oriented systems model"}`.

The complete mandatory discovery baseline is **108 N-B cells** (`6 P_N × 18 M_N`). Run and log every cell separately to exhaustion; a dated zero does not establish source equivalence and is not grounds to omit a frozen cell later. This complete `P_N × M_N` union implements Stream B and secures candidate discovery before any EPS tagging.

Do not run a redundant mandatory N-A discovery matrix. Instead, after deduplicating the complete N-B union, deterministically apply the full corrected E dictionary in [`searches/search-concept-dictionary.json`](searches/search-concept-dictionary.json) to every returned record's complete available NTRS metadata. This local **N-A EPS-explicit tag** includes both electrical/electric subsystem phrases, all functional terms, `power mode`/`power modes`, and `battery`/`batteries`; it is necessarily a subset of N-B and cannot add candidates. Preserve field-level E hits, report `A∩B`, `B-only`, and the union, require structural `A-only = 0`, and do not interpret that zero as poor Stream-A performance. A small source-query-versus-local-tag equivalence pilot may append one E term to representative P×M parent cells, but those checks are not mandatory discovery cells and cannot compensate for an incomplete N-B matrix.

**N-V/N-O** remain optional one-at-a-time terms appended only to a logged, already mandatory P×M parent cell when a prespecified concept-coverage audit or named recall miss triggers them. Record the trigger, parent cell, added term, and result; these probes do not replace or alter the 108-cell baseline.

A 2026-08-07 `pilot_not_candidate_search` executed and reopened all 108 corrected P×M cells: 108/108 reconciled in one page each, with 39 overlapping source events and a six-ID unscreened union, no retry/failure/total change, and representative normal-UI syntax checks. The unchanged full-E matcher passed 25/25 term-form self-tests and tagged one of the six metadata records (`A∩B=1`, `B-only=5`, `A-only=0`). These aggregates validate syntax, arithmetic, and tagging only; they are not candidates and all 108 cells must be rerun after authorization. Full details are in [`2026-08-07-ntrs-revised-matrix-validation.md`](searches/subagent-logs/2026-08-07-ntrs-revised-matrix-validation.md).

Do not use `SmallSat` or `small satellite`. Example request body:

```json
{
  "q": "CubeSat \"model-based systems engineering\"",
  "published": {
    "gte": "2011-01-01",
    "lte": "<YYYY-MM-DD run date>"
  },
  "page": {
    "size": 100,
    "from": 0
  }
}
```

For a non-discovery source-equivalence check only, an example EPS-appended `q` is `nanosatellite "electrical power system" MBSE`. Every mandatory P×M discovery cell begins at `from: 0` and increments by 100 until returned pages reconcile with `stats.total`. Archive the exact request body, UTC timestamp, status, raw JSON for every page, checksums, API-reported total, returned records, and representative UI cross-checks. If totals change during pagination, preserve the invalid snapshot and rerun the complete logical cell.

Screen all unique returned records under the protocol's complete date, language, publication-type, population, MBSE, EPS-route, and retrieval rules, and inspect available attachments. Potentially eligible NTRS evidence includes a substantive full primary report—such as a technical publication/memorandum, contractor or grantee report, or conference paper—with methods/results and stable provenance; accessibility alone neither establishes nor defeats scientific eligibility. Preserve NTRS ID, report numbers, STI/document type, technical/peer-review metadata when reported, distribution, version, identifiers, attachment type, and availability. A scientifically plausible report that cannot be obtained follows the protocol's `not_retrieved` route. Abstracts, posters, and presentation-only records are discovery leads only.

Deduplicate NTRS deposits by source ID, report number, DOI, normalized title/author/year, and attachment identity, while retaining all discovery events. Link technical-report, conference, abstract, and presentation manifestations through the protocol's study/implementation report-family mapping; do not erase a substantively distinct report merely because it shares a family.

Report the total and retrieved count for every one of the 108 logical cells, the simple sum across cells with overlap explicitly acknowledged, the separately deduplicated NTRS union, full-E tag hits and `A∩B`/`B-only`/union counts, full reports sought/retrieved, lead-only records, report families, exclusions, and inclusions. Any later protocol-approved update reruns the complete 108-cell matrix and reapplies the versioned E matcher because NTRS may add older records retrospectively.

## 13. Citation searching and Buruso recall benchmark

Citation chasing is an `other source`, separate from the independent seven-source baseline. The prespecified platforms are **Scopus** and **Web of Science Core Collection (WoSCC)**. Use the normal Scopus record/citation interface for `Cited by` results and the normal WoSCC `Citing Articles`/Cited Reference Search interfaces with all available Core Collection editions. Google Scholar and Semantic Scholar are not fallback citation indexes.

For every full-text-included report and relevant secondary review:

1. Assign a citation seed/event ID and record the seed DOI, normalized title, year, Scopus EID/source ID and WoS accession when available, report-family ID where applicable, cycle, operator, and search date/time/time zone.
2. **Backward chasing:** inspect the seed's complete full-text reference list. Record the total references inspected and every bibliographically identifiable report taken forward under the normal title/abstract criteria. WoS exported cited references or Scopus indexed references may assist transfer and reconciliation, but they do not replace the source report's reference list.
3. **Forward chasing:** search both Scopus and WoSCC for every seed. Prefer the indexed record/DOI; when a seed is not indexed, use the platform's DOI/title/cited-reference route where supported and retain the exact source-native request. A zero result or indexing failure in one platform does not waive the other platform.
4. Export every forward-citation result available through each platform, preserve its native artifact and source total, normalize it with exact seed/direction/cycle provenance and global rank, and union/deduplicate the two platform sets without erasing duplicate discovery events.
5. Apply the review's date, language, publication-type, population, MBSE, and EPS-thread rules normally. Citation provenance never bypasses eligibility or full-text screening.

Newly included reports become seeds in the next numbered cycle. Repeat complete backward and dual-platform forward chasing until one full cycle produces no new eligible report. Log, for every seed/direction/platform/cycle, source total, retrieved/parsed total, candidates taken forward, duplicates, reports sought, eligibility decisions, included reports, unavailable indexing/export, and stopping result. Citation searches use the common evidence cutoff; if the review search is updated, rerun forward chasing for every seed and backward chasing for any newly included seed. The machine-readable citation-event table is kept under `searches/citation-chasing/`; PRISMA counts remain at record/report level and citation records retain `discovery_route=citation_chasing` separately from their bibliographic database source.

After the independent seven-source candidate set is merged and frozen, use this named secondary review:

> Buruso, R. B., Himmiche, S., Tejumola, T., Alemayehu, Y., & Rose, B. (2026). Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review. *Systems Engineering*. https://doi.org/10.1002/sys.70051

Create a read-only benchmark register of its cited reports that appear potentially relevant to CubeSat/nanosatellite MBSE, EPS, outcome/burden, or V&V. Match normalized DOI/title metadata against the independent set and report found/missed status and discovery source. A miss may trigger a logged concept-level recall probe or a citation-chasing event; it cannot be inserted directly. Merge and deduplicate every resulting candidate, then rerun the Buruso and retained-file audits against the expanded set. Repeat this supplementary-search/audit cycle until a full cycle produces no new eligible report; preserve each baseline/audit version rather than silently moving the original freeze point. Record the final eligibility reason for every apparently relevant benchmark report without importing Buruso's classifications.

The use of arXiv, Semantic Scholar, and Google Scholar is forbidden for discovery or citation searching.

## 14. Iteration and count rules

1. Run two or three pilots at a time for query-based sources; do not treat ESA event pagination/harvest requests as separate conceptual searches.
2. Count before full retrieval where supported, then retrieve and inspect every record for each accepted final query or matching operation.
3. A query around 30–70 hits is normally manageable. Do not narrow solely to meet that heuristic if doing so removes a prespecified concept; partition terms and retrieve all partitions instead.
4. If a query is overbroad, inspect a sample and refine using fields or structured-model relations—not outcome direction, open-access status, generic SmallSat terms, or legacy titles.
5. If a query is too narrow, relax one concept variant at a time and log the effect.
6. Retrieve all records available for every accepted final query or source harvest, subject only to documented source/API limits and failures.
7. Compare Stream A and Stream B unique yield after deduplication. A broad Stream B route cannot be dropped merely because most records lack EPS terms in metadata.
8. Keep source-reported totals, actually retrieved totals, unique records, reports, report families, EPS threads, outcome/burden records, and V&V records as distinct counts.

## 15. Merge, deduplication, and screening

- Merge final accepted runs by normalized DOI, then stable source/report ID, then manually confirmed normalized title–author–year.
- Preserve every discovery event: source/platform, query/event ID, exact method, raw artifact, rank when available, and search stream.
- Keep conflicting metadata and document how the preferred value was selected.
- Deduplicate multiple database/source records at record/report level before PRISMA screening counts; separately map substantively distinct companion reports to study/implementation report families.
- Title/abstract tiers follow the protocol:
  - `core`: clear EPS-primary MBSE or likely explicit EPS thread;
  - `supporting`: plausible CubeSat/nanosatellite structured-system MBSE requiring full text to test for an embedded EPS thread;
  - `rejected`: clearly fails population, publication/date/language, or structured-system-model scope.
- Do not reject a Stream B record solely because EPS/power is absent from its title or abstract.
- Reject generic SmallSat/small-satellite-only records unless the source identifies a separable CubeSat/nanosatellite case.
- Report secondary reviews and lead-only records separately; do not place them in the primary-evidence corpus.

### PRISMA 2020 flow reconciliation

Use the official new-review template for databases and other sources, backed by a machine-readable count table:

1. retain identification totals separately for all seven electronic sources and for each permitted citation/other-source route;
2. distinguish source-reported/harvested totals from records actually retrieved or parsed;
3. count duplicate removals before screening separately from records excluded during screening;
4. reconcile records screened, records excluded, reports sought, reports not retrieved, full reports assessed, and full reports excluded with one primary reason;
5. make included **reports** the flow endpoint and report report families, EPS threads, outcome/burden records, and V&V records only in separate analytic-denominator tables; and
6. do not count a retained legacy file as identification unless it is independently rediscovered or reached through a permitted logged citation route.

## 16. Coverage audit and deferred retained-file recall check

Audit at least these concept/source clusters without using old screening decisions:

- EPS-primary structured models and power/electrical architecture;
- parametric power/energy budgets bound to system models;
- whole-spacecraft SysML/MBSE with possible embedded EPS allocation/interface threads;
- reference/template/domain models and the full range of reported reuse/tailoring approaches;
- digital-engineering/toolchain transformations, interoperability, and implementation burdens;
- beneficial, null, mixed, and adverse EPS-attributed outcomes;
- model versus system/design verification and validation;
- EPS-specific versus system-wide EPS-linked V&V;
- executable pre-physical checks, virtual integration, MIL/SIL/PIL/HIL, and model-to-test continuity;
- substantive institutional technical reports and conference/workshop papers that may be weakly indexed;
- Web of Science Core Collection Topic retrieval with all available citation-index editions, including CPCI-S/CPCI-SSH and BKCI-S/BKCI-SSH;
- unrestricted Wiley retrieval, with INCOSE International Symposium as a coverage check;
- unrestricted ESA Indico harvest, with the known ESA MBSE workshops as a coverage check;
- NTRS technical-report and conference-paper coverage; and
- Buruso et al. (2026) benchmark recall.

Only after the independent seven-source candidate set is frozen, compare its normalized DOI/title/source-ID metadata with the retained `markdown/` and `pdfs/` cache. Record found/not-found status and the independent discovery event for matches. Use misses only to design logged concept-level recall probes; a retained file cannot enter the corpus without a valid discovery or protocol-compliant citation-chasing event.

## 17. Planned artifacts

```text
SLR/SLR1/
  protocol.md
  query-search-plan.md
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
    compendex/
    wiley-online-library/
    esa-indico/
    nasa-ntrs/
    citation-chasing/
    worklogs/
    merged_candidates.json
    search-manifest.json
    search-concept-dictionary.json
    deduplication-report.json
    report-family-registry.json
    buruso-recall-audit.json
    retained-file-recall-audit.json
    subagent-logs/
  prisma-flow-data.*
  prisma-s-checklist.*
  prisma-2020-checklist.*
```

Raw licensed exports or copyrighted full text may remain non-public where required, but exact strategies/methods, dates, manifests, counts, derived decisions, and rights-aware availability restrictions must be preserved under the integrated PRISMA-S/PRISMA 2020 requirements in this plan and the protocol.

## 18. Search-stage stopping rule

The independent electronic-source and title/abstract corpus stage is complete only when:

- both streams have final accepted runs in Scopus, Web of Science Core Collection, IEEE Xplore, Compendex, and Wiley, or a documented source failure;
- every 2011-current ESA Indico event has an export/access outcome; every event/contribution material is inventoried; every accessible document-like attachment has a retrieval/text-extraction outcome; and the complete metadata plus extractable attachment text has been matched with the frozen dictionary;
- all 108 mandatory NTRS P×M baseline cells have been paginated to exhaustion or have a documented source failure, and the complete versioned E matcher has tagged the deduplicated union;
- all final-query/source records available within documented limits have been saved, read, and reconciled to source totals;
- required concept clusters, publication types, technical-report routes, and source-specific coverage checks have been audited;
- Stream A/Stream B and source-unique yields are known;
- additional query refinements are predominantly duplicates or irrelevant records rather than merely inconvenient to search;
- the merged candidate set, screening log, and retrieval corpus pass provenance and count checks;
- the independent candidate set and every supplementary expansion have undergone the deferred Buruso and retained-file recall audits, with one complete audit cycle yielding no new eligible report; and
- every unresolved source access failure, lead-only record, and count discrepancy is explicitly logged.

Citation chasing remains a later search phase tied to full-text inclusions and relevant secondary reviews. It is complete only after one full cycle of complete backward-reference inspection and forward searching in both Scopus and WoSCC yields no new eligible report; it must not be falsely reported as complete at the independent corpus-construction stage.
