# Query Search Plan: EPS MBSE in CubeSat/Nanosatellite Development

- **Review run:** `eps-mbse-slr-2026`
- **Protocol:** `protocol.md`, version `1.1`, pre-search freeze candidate
- **Plan status:** pre-freeze interface validation complete; final search authorization pending
- **Planned evidence window:** 2011 through the date each final search is run in 2026
- **Electronic sources:** Scopus; IEEE Xplore; Compendex on Engineering Village; Wiley Online Library; ESA Indico; NASA Technical Reports Server (NTRS)
- **Search unit:** one exact source-specific query, request body, or reproducible website-harvest/matching operation together with its fields, limits, pagination/coverage settings, date, and raw artifacts

## 1. Purpose and scope

Build a new, independently discovered candidate set for full-text retrieval. The search must support both:

- **Stream A — EPS-explicit:** population × EPS × structured-system-model/MBSE concepts; and
- **Stream B — embedded-thread recall:** population × structured-system-model/MBSE concepts without a mandatory EPS term.

Search sensitivity is broader than final scientific eligibility. Route A/Route B status and the required EPS anchor, model anchor, and explicit bridge are full-text decisions, not metadata assumptions. Generic `SmallSat`/small-satellite work is outside the population and is not a positive search concept.

The six sources are searched in full within their documented interfaces or public collections. Wiley is not restricted to INCOSE publications, ESA Indico is not restricted to ESA MBSE workshops, and NTRS is not restricted to a predetermined NASA series. INCOSE International Symposium content and ESA MBSE workshop content are coverage checks only.

### Pre-freeze interface validation completed 2026-08-06

| Source | Validated route | Diagnostic completion |
|---|---|---|
| Scopus | Elsevier Scopus Search API, `COMPLETE` view | All six exact strings accepted; count and complete-retrieval/merge checks passed |
| IEEE Xplore | IEEE JSON search interface | All six exact strings/facets accepted; count and complete JSON/CSV merge checks passed |
| Compendex | Engineering Village Expert Search, Compendex only | Field/filter/pagination behavior and final C-B1 settings validated; native Detailed CSV normalized and merged successfully |
| Wiley Online Library | Advanced Search, unrestricted `Anywhere` | All six exact strings accepted; pagination and native RIS-to-compatible-CSV merge path validated |
| ESA Indico | Root/child category and event-contribution JSON exports | Whole-instance census behavior and nested contribution response shape validated |
| NASA NTRS | Public citations JSON API; search UI retained for final cross-check | Phrase/conjunction, date, total, 100-record pagination, and normalized merge behavior validated; unreliable Boolean prohibited |

Every observation is logged as `pilot_not_candidate_search` in [`search-log.md`](search-log.md). Final discovery begins only after protocol authorization and reruns every accepted method from a clean final-run artifact set.

## 2. Anti-anchoring and provenance rules

1. Do not inspect Git history, deleted legacy search/corpus/extraction files, or retained source Markdown/PDFs while formulating or screening the independent planned-source candidate set.
2. Save every raw run, including zero-result, failed, malformed, and overbroad pilots. A failed request is not a zero-result search.
3. Read each complete saved result/export after every run; record both the source-reported total and records actually retrieved or parsed.
4. Give every artifact a new-run query/event ID and record source/database and platform, exact query/request/method, filters, run date/time/time zone, limits/pages or harvest coverage, status, assessment, and successor/predecessor refinement.
5. Do not import legacy IDs. Assign `eps-mbse-slr-2026-r####` IDs only after final merge/deduplication. A prior ID may later be recorded only as `legacy_corpus_id` after an independently rediscovered report is matched.
6. The retained `markdown/` and `pdfs/` directories are retrieval caches only. Match against them after the independently discovered six-source baseline is merged and frozen.
7. Buruso et al. (2026) is a named secondary-review seed and deferred recall benchmark. Do not use its bibliography to insert candidates into the independent baseline.

## 3. Eligibility-related search limits

- **Years:** 2011 through each source's search date, inclusive.
- **Language:** English where the source supports a reliable filter; otherwise screen language.
- **Publication types:** full primary-research journal articles, conference/proceedings or workshop papers, research chapters, and substantive institutional technical reports. Empirical comparison and experience reports are eligible. Abstract-only, poster-only, presentation/slide-only, and recording-only records may be discovery leads but are not primary evidence.
- **Population:** work that the source identifies as orbital CubeSat/nanosatellite-class. `PocketQube`, `picosatellite`, `CanSat`, generic `SmallSat`/small-satellite, and conventional/larger spacecraft are not positive concepts. A record found through another route qualifies only if a CubeSat/nanosatellite case is explicit and separable at full text.
- **Access:** do not intentionally limit discovery to open access. Source access and full-text retrieval status are logged separately.
- **Outcome and V&V terms:** optional supplementary concepts, never mandatory across the whole search.

## 4. Concept blocks

### P — population

`CubeSat`, `CubeSats`, `cube sat`, `nanosatellite`, `nanosatellites`, `nano-satellite`, `nano-satellites`, `nano satellite`, and `nanosat*`. Any source-specific spelling variant added after a logged pilot must be versioned in the search dictionary and applied consistently; it cannot be added silently.

Do not use unqualified `SmallSat` or `small satellite` in any planned population block or sensitivity probe. A source record containing those labels may still be screened if it was retrieved through a permitted population term, but the generic label does not establish eligibility.

### E — EPS

High-specificity terms:

- `electrical power system`, `electric power system`, `electrical power subsystem`, `electric power subsystem`, `EPS`, `power subsystem`, `electrical architecture`, `power architecture`, `PCDU`, `PMAD`.

Functional/analysis terms:

- `power budget`, `energy budget`, `energy balance`, `power generation`, `solar array`, `battery`, `energy storage`, `power conditioning`, `power distribution`, `power management`, `power interface`, `power mode`, `load profile`.

Bare `EPS` is always intersected with both population and model blocks in sources that support Boolean grouping, to suppress unrelated acronym senses.

### M — structured system model / MBSE

- `model-based systems engineering`, `model based systems engineering`, `model-based system engineering`, `model based system engineering`, `MBSE`, `SysML`, `systems modeling language`, `system model`, `systems model`, `system modeling`, `systems modelling`, `reference model`, `digital engineering`, `Arcadia`, `Capella`, `object-oriented systems model`.

Broad `model-based` or `simulation` is insufficient alone. When broad model terms are used, combine them with a systems-engineering relation/concern block such as requirements, function/behavior, architecture, interfaces, traceability, parametrics, verification, or validation.

### O/V — optional outcome, burden, and V&V probes

- **Outcomes:** `reliab*`, `mission assurance`, `reproduc*`, `reuse`, `reusable`, `integrab*`, `interoperab*`, `traceab*`, `interface consistency`, `lifecycle continuity`, `benefit`, `impact`, `outcome`, `no effect`, `adverse`.
- **Implementation burdens:** `burden`, `effort`, `workload`, `overhead`, `cost`, `schedule`, `time`, `training`, `skill`, `learning curve`, `licen*`, `resource`, `maintenance`, `governance`, `adoption`.
- **V&V:** `verification`, `validation`, `V&V`, `model verification`, `model validation`, `system verification`, `system validation`, `design verification`, `design validation`, `requirements-in-the-loop`, `model checking`, `virtual integration`, `MIL`, `model-in-the-loop`, `SIL`, `software-in-the-loop`, `PIL`, `processor-in-the-loop`, `HIL`, `hardware-in-the-loop`, `test case`, `test procedure`, `model-to-test`.

## 5. Common execution and PRISMA-S log rules

For every source, preserve the source/platform name, actual web/API/script interface and version where known, endpoint, exact source-native query or request, all limits and filters, date/time/time zone, reported total, retrieved/parsed total, pagination or event coverage, raw filenames and checksums, operator, refinement history, and final disposition (`planned`, `piloted`, `accepted_final`, `replaced`, `failed`, or `not_run`, with predecessor/successor IDs). Draft strings below are not evidence that a search ran. The final supplement must reproduce the exact strings, request bodies, matching dictionaries, and methods actually executed—not cleaned translations.

Before the first valid run in each source, record the selected interface and its pagination/export behavior in the search log. Where a source changes syntax, facets, pagination, or export behavior, retain the failed attempt and pilot the correction. A source failure must be documented; it is not permission to silently omit that source. Search-source duplicates are retained as discovery events until the merged record-level deduplication stage.

Apply the official [PRISMA-S checklist](https://www.prisma-statement.org/prisma-search) as follows:

| PRISMA-S item | Execution/reporting rule for this review |
|---|---|
| 1. Database and platform | Name each source and the actual platform, interface, endpoint, and provider used. |
| 2. Multi-database searching | No simultaneous multi-database platform search is planned; report this as not applicable if true at completion. |
| 3. Registries | No study registry search is planned; report this explicitly rather than treating a bibliographic source as a registry. |
| 4. Online resources/browsing | Log the full Wiley search, whole-instance ESA harvest, full NTRS search, and every deliberate venue/website coverage audit with scope, method, date, yield, and stopping rule. |
| 5. Citation searching | Log seed set, backward/forward direction, citation index/interface, cycles, yield, decisions, and stopping outcome as an “other source.” |
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

Preserve every source-native structured export. In addition, create one normalized JSON or CSV artifact per query/batch for `merge_search_results.py`. Compatible CSV columns are `Search source`, `Query`, `Rank`, `Paper ID`, `DOI`, `Title`, `Authors`, `Publication year`, `Abstract`, `Citation count`, `URL`, `Open access PDF`, and `Source total`; `Search source`, exact `Query`, and global result `Rank` are required for provenance even when the native export omits them. Never overwrite or mislabel the native export. Run a merge smoke test on each source's first normalized batch before final retrieval continues.

## 6. Scopus validated API and planned searches

Use the Elsevier Scopus Search API (`https://api.elsevier.com/content/search/scopus`, `COMPLETE` view) with Scopus `TITLE-ABS-KEY` concept blocks, explicit `PUBYEAR AFT 2010` and `PUBYEAR BEF 2027` limits, English, and document types `ar`, `cp`, and `ch`. Preserve the key-free request URL/parameters, executed query including year clauses, API response, entitlement/view, pagination, and client script checksum; never log the API key.

Pre-freeze diagnostics on 2026-08-06 accepted all six strings. API totals were: S-A1 = 3, S-A2 = 9, S-B1 = 75, S-B2 = 55, S-V1 = 1, and S-O1 = 4. A complete diagnostic retrieval of S-A1 reconciled all 3 records and normalized JSON merged successfully. These are `pilot_not_candidate_search` observations; rerun all strategies after authorization and use only those final artifacts for discovery.

### S-A1 — explicit EPS names × explicit MBSE/language

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-A2 — EPS analyses/interfaces × structured system model

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-B1 — embedded-thread baseline with explicit MBSE/languages

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-B2 — embedded-thread structured-model expansion

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND TITLE-ABS-KEY(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-V1 — EPS-linked V&V sensitivity probe

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND TITLE-ABS-KEY(verification OR validation OR traceab* OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure") AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

### S-O1 — outcome and implementation-burden sensitivity probe

```text
TITLE-ABS-KEY(cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") AND TITLE-ABS-KEY("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND TITLE-ABS-KEY("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND TITLE-ABS-KEY(reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab* OR benefit* OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licen* OR adoption) AND LANGUAGE(english) AND (DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))
```

## 7. IEEE Xplore validated interface and planned searches

Use IEEE Xplore's JSON search interface at `https://ieeexplore.ieee.org/rest/search` through the normalized local search client, with unfielded Boolean metadata search, inclusive years 2011–2026, language `English`, and content types `Journals`, `Conferences`, and `Books`. First run `--count-only`; retrieve the complete result set for each accepted query up to its reported total. Confirm that the endpoint parsed Boolean syntax by inspecting full result lists.

Pre-freeze diagnostics on 2026-08-06 accepted all six strings and all intended facets. Displayed/API totals were: I-A1 = 4, I-A2 = 2, I-B1 = 38, I-B2 = 42, I-V1 = 1, and I-O1 = 4. A complete diagnostic retrieval of I-A1 reconciled all 4 records and normalized JSON merged successfully. These counts and records are `pilot_not_candidate_search`; rerun every query after authorization, preserve fresh count and full-retrieval events, and use only those final reruns for discovery.

### I-A1

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### I-A2

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("power budget" OR "energy budget" OR "energy balance" OR "solar array" OR battery OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

### I-B1

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### I-B2

```text
(CubeSat OR CubeSats OR nanosatellite OR nanosatellites OR "nano-satellite") AND ("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering") AND (requirements OR functions OR behavior OR behaviour OR architecture OR interfaces OR traceability OR parametric OR verification OR validation)
```

### I-V1

```text
(CubeSat OR nanosatellite OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### I-O1

```text
(CubeSat OR nanosatellite OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR "mission assurance" OR reproducibility OR reuse OR reusable OR integrability OR interoperability OR traceability OR benefit OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR adoption)
```

## 8. Compendex validated interface and planned searches

Search **Compendex on Elsevier Engineering Village** through Expert Search at <https://www.engineeringvillage.com/search/expert.url?database=1>. Select **Compendex only** in the database control and preserve that selection in the Search Summary; do not rely on the accepted but currently undocumented `(cpx WN DB)` expression. Use `KY` (`Subject/Title/Abstract`) for concept blocks, uppercase Boolean, double-quoted phrases, and explicit wildcards. Use the literal suffix `AND (2011-* WN YR) AND (({English}) WN LA)` and also display/log Published = 2011–Latest in the UI.

Set **Turn autostemming off** to checked, because the strategy already prespecifies variants and wildcards and the pilot showed that changing this control materially changes retrieval. Use Relevance sort and 100 records per page; retrieve all pages. Do not apply a document-type filter at discovery: the current index distinguishes journal, conference, chapter, article-in-press, book, and report-related values, and the small gain from filtering does not justify suppressing potentially eligible online-first or institutional-report records. Apply the protocol's publication-type rule during screening.

### C-A1

```text
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-A2

```text
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-B1

```text
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-B2

```text
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") WN KY) AND ((requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-V1

```text
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((verification OR validation OR traceab* OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure") WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

### C-O1

```text
((cubesat OR "cube sat" OR nanosat* OR "nano-satellite" OR "nano satellite") WN KY) AND (("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) WN KY) AND (("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") WN KY) AND ((reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab* OR benefit* OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licen* OR adoption) WN KY) AND (2011-* WN YR) AND (({English}) WN LA)
```

The first browser diagnostic validated every core expression with the documented year/language/database syntax; counts with autostemming on and a `JA|CA|CP|CH` filter were C-A1 = 3, C-A2 = 4, C-B1 = 68, C-B2 = 42, C-V1 = 1, and C-O1 = 1. A follow-up using the final C-B1 expression and settings above returned 72 at 2026-08-06 20:12 EDT. The server summary still displayed its broad `1884–2026` coverage label, so retain both the literal `YR` clause and UI Published control and audit every exported publication year rather than inferring that the summary label proves the limit. These are syntax/interface observations, not candidate searches; rerun all six exact strings after authorization.

Engineering Village exposed EndNote/RIS, BibTeX, ASCII, CSV, Excel, PDF, and RTF, with Current page, Citation, Abstract, and Detailed record options and a session basket labelled to 5,000 selected records. A normal one-record **CSV Detailed record** pilot produced a native file with 29 columns; because it omitted exact query and rank, a normalized CSV added the common provenance columns and passed `merge_search_results.py` with source, query, rank, and 1/1 raw/unique counts preserved. Repeat this preflight after authorization, preserve native and normalized files separately, and then export the complete set in logged batches. Save the Search Summary and reconcile source totals, pages, selections, and export batches.

Official platform documentation checked on 2026-08-06:

- <https://www.elsevier.com/products/engineering-village/databases/compendex>
- <https://www.elsevier.support/engineering-village/answer/how-can-i-improve-my-expert-search>
- <https://www.elsevier.support/engineering-village/answer/what-are-the-expert-search-field-codes>
- <https://www.elsevier.support/engineering-village/answer/what-are-the-search-fields-in-the-compendex-database>

## 9. Wiley Online Library validated interface and planned searches

Search the **entire Wiley Online Library publisher database**, not a selected journal or proceedings series. The validated interface is Wiley Online Library Advanced Search, <https://onlinelibrary.wiley.com/search/advanced>, submitting GET requests to `https://onlinelibrary.wiley.com/action/doSearch`. Use one `Anywhere` row (`field1=AllField`) containing the complete parenthesized query in `text1`. Uppercase Boolean `AND`/`OR`/`NOT`, quoted phrases, parenthesized groups, hyphenated phrases, and non-leading unquoted wildcards such as `nanosat*` were accepted on 2026-08-06; unseparated terms default to `AND`, but explicit operators and parentheses are retained.

Use `AfterMonth=1`, `AfterYear=2011`, `BeforeMonth=<run month>`, and `BeforeYear=<run year>`. Wiley normalizes the upper bound to the last day of that month, so screen out any record after the actual run date. No reliable language or pre-search content-type control was exposed. Do not apply `PubType`, INCOSE, journal, ISSN, subject, access-status, or other venue facets to the baseline. Preserve and process the individual `Articles & Chapters` results (`content=articlesChapters&target=default`); separately log and inspect the `Collections` tab as a container/coverage route rather than counting a collection as a primary-evidence report.

For each run, preserve the exact query, generated URL/parameters, server-normalized query/date display, active tab, default sort (`Relevance`) or any changed sort, reported total, and every page. The `Anywhere` label does not document its precise metadata/full-text coverage, so make no claim that it is equivalent to Scopus `TITLE-ABS-KEY`; it is nevertheless the platform's validated unrestricted field.

### W-A1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### W-A2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR "nano-satellite" OR "nano satellite") AND ("power budget" OR "energy budget" OR "energy balance" OR "solar array" OR battery OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

### W-B1

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR nanosatellites OR "nano-satellite" OR "nano satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

### W-B2

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosat* OR nanosatellite OR "nano-satellite" OR "nano satellite") AND ("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering") AND (requirement OR function OR behavior OR behaviour OR architecture OR interface OR traceability OR parametric OR verification OR validation)
```

### W-V1

```text
(CubeSat OR nanosatellite OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceability OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

### W-O1

```text
(CubeSat OR nanosatellite OR "nano-satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliability OR "mission assurance" OR reproducibility OR reuse OR reusable OR integrability OR interoperability OR traceability OR benefit OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licensing OR adoption)
```

Outcome/burden and V&V terms remain optional probes, not baseline restrictions.

Pre-freeze browser diagnostics on 2026-08-06 returned W-A1 = 7 Articles & Chapters; W-A2 = 40 Articles & Chapters plus 2 Collections; W-B1 = 44 Articles & Chapters plus 1 Collection; W-B2 = 105 Articles & Chapters plus 4 Collections; W-V1 = 17 Articles & Chapters plus 1 Collection; and W-O1 = 21 Articles & Chapters plus 1 Collection. All six exact strings were accepted without partitioning, including the 690-character W-V1. These counts are `pilot_not_candidate_search`; rerun all six strategies after authorization.

If Wiley rejects or silently rewrites a final expression, first use its validated multi-row equivalent: P, E, and M OR-blocks in three `AllField` rows for Stream A, or P and M in two rows for Stream B; Wiley AND-combines non-empty rows. Confirm source-equivalent counts/sets before acceptance. If needed, partition into finite population-term × model-term cells and, for Stream A, population-term × EPS-term × model-term cells; save each partition and union all complete sets. If no reproducible route works, record a source failure and obtain prospective approval rather than substituting an external index.

Retrieve every active-tab page with `pageSize=20` and zero-indexed `startPage=0,1,...`; verify rendered page identity because an AJAX URL change can leave stale DOM, and reconcile page counts to the active-tab total. Export page-scoped selections in tested-safe batches of 20. Wiley exposed Plain Text, RIS, EndNote, BibTeX, Medlars, and RefWorks—not native CSV—and its citation form supports `include=abs`. Preserve each native RIS batch and transform it with `academic-search/scripts/ris_to_merge_csv.py` to a merge-compatible CSV containing `Search source`, `Query`, `Rank`, `Paper ID`, `DOI`, `Title`, `Authors`, `Publication year`, `Abstract`, `Citation count`, `URL`, `Open access PDF`, and `Source total`; retain both forms and test every normalized CSV with `merge_search_results.py`. A one-record normal-UI RIS pilot preserved its `N2` abstract and the normalized source, exact query, global rank, source total, and 1/1 merge counts. Never describe normalized CSV as a Wiley-native export.

Preserve result-page HTML/PDF where permitted, citation exports, DOI/title/author/year/source metadata, access status, and count reconciliation. INCOSE International Symposium (online ISSN `2334-5837`) is a coverage audit after the unrestricted Wiley baseline: verify that unrestricted searches recover relevant known symposium records and log any targeted audit query separately; never use the series as the Wiley source boundary.

## 10. ESA Indico whole-instance harvest and search

Search **the entire public ESA Indico instance**, not only events labeled MBSE. A pre-freeze diagnostic on 2026-08-06 found 437 unique events in the root export; its event-ID set exactly equaled the union of public top-level category exports 5, 6, and 7, and nested category 9 was a subset of category 6. All root events had parseable dates, 408 were dated 2011-01-01 through the diagnostic date, and all five known MBSE coverage-event IDs were present. This validates the root endpoint's recursive census behavior at pilot time only. Repeat and save the root/child set comparison at every final harvest so a later category or visibility change is detected. At every harvest:

1. save the official root inventory from <https://indico.esa.int/export/categ/0.json> and any child-category exports needed by the validation;
2. reconcile reported event counts with returned unique event IDs and document duplicate/category-path handling;
3. retain every event dated from 2011-01-01 through the harvest date, logging missing/unparseable dates as exceptions; and
4. for every in-window event, irrespective of apparent topic, retrieve and save `https://indico.esa.int/export/event/{id}.json?detail=contributions`.

Record HTTP status, retrieval time, access/protection outcome, retries, checksum, and parsed contribution count for every event. The validated response shape is one event object in `results[0]`, with contributions in `results[0].contributions`; top-level `count` is therefore not the contribution count. An unavailable or malformed export is a source-access failure, not a zero-contribution event.

Create one provenance-preserving joined record per contribution using combined event and contribution metadata: event title/description/category/date/keywords/materials plus contribution title/abstract/description/session/track/keywords/authors/material metadata. Preserve raw JSON/HTML and produce a versioned normalized-text derivative. Before the valid harvest, materialize the Section 4 P/E/M terms in a machine-readable `search-concept-dictionary.json` and freeze the dictionary together with documented case-folding, HTML stripping, Unicode/hyphen normalization, phrase matching, wildcard/stemming behavior, fields searched, and matcher tests. Apply that exact dictionary and matcher to the combined metadata:

- **ESA-A1:** `P AND E AND M`;
- **ESA-B1:** `P AND M`, without a mandatory EPS term.

Save the normalization and matching code/version, dictionary checksum/version, field-level hits, Stream A/B overlap, and candidate IDs. Generic `SmallSat`/small-satellite does not satisfy P. Event date controls source harvesting only; the report-level first-formal-publication date is checked again during eligibility screening.

For every candidate, inventory and retrieve accessible attachments/materials, then screen for an identifiable full report under the normal criteria. Abstracts, posters, slide decks, presentations, and recordings are lead records only. If a lead identifies a distinct full report, log the lead-to-report route and screen the full report separately; the lead cannot itself supply evidence.

Known ESA MBSE event IDs `161`, `329`, `386`, `407`, and `472` are a dated 2026-08-06 coverage set only. After the whole-instance harvest, verify that each was enumerated and its contributions processed. Discover and process any later or differently titled MBSE events through the same unrestricted root inventory; do not limit the source to this list.

Report root events returned; in-window events; contribution exports attempted/retrieved/inaccessible/malformed; contributions parsed; Stream A, Stream B, overlap, and union candidates; attachments classified; lead-only records; distinct full reports found; and included reports. A later protocol-approved search update reruns the full root census and all in-window event exports so retrospective changes are detectable.

## 11. NASA NTRS whole-database search

Search the public **NASA Technical Reports Server** through <https://ntrs.nasa.gov/search> and the source's JSON endpoint, `POST https://ntrs.nasa.gov/api/citations/search`. Pre-freeze API diagnostics on 2026-08-06 confirmed that the `published` date object, `page.size: 100`, and zero-based `page.from` pagination are accepted; simple space-delimited terms behave as conjunctions in the tested sets, and quotation marks materially restrict phrases. Explicit `AND` returned the same tested record set but changed ordering, while `OR` and parenthesized Boolean tests unexpectedly returned zero. Therefore, final cells use only space-delimited terms and quoted phrases—no Boolean operators or parentheses—and pagination uses fixed 100-record pages. Cross-check representative cells in the UI at final execution and retain the diagnostic and final logs; these observations are interface validation, not candidate-search results.

Use these query-cell term sets:

- `P_N = {CubeSat, nanosatellite, "nano-satellite"}`;
- `M_N = {MBSE, "model-based systems engineering", "model based systems engineering", SysML, "system model", "reference model", "digital engineering"}`;
- `E_N = {EPS, "electrical power system", "electric power system", "electrical power subsystem", "power subsystem", "power budget", "energy budget", PCDU, PMAD}`.

The finite mandatory baseline contains 21 N-B cells (`3 P_N × 7 M_N`) and 81 N-A cells (`3 P_N × 9 E_N × 3` high-specificity model terms), before deduplication. Run and log every baseline cell separately unless a documented syntax pilot proves two cells source-equivalent and the consolidation is approved before retrieval:

- **N-B:** one `P_N` term plus one `M_N` term;
- **N-A:** one `P_N` term plus one `E_N` term plus one high-specificity model term (`MBSE`, `SysML`, or `"system model"`);
- **N-V/N-O:** optional one-at-a-time V&V or outcome/burden terms appended only when a prespecified concept-coverage audit or a named recall miss is not represented by the baseline. The trigger, selected parent cell, added term, and result are logged; optional cells are not needed merely to duplicate the mandatory V/O probes already run in the query-based bibliographic sources.

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

For Stream A, an example `q` is `nanosatellite "electrical power system" MBSE`. Begin at `from: 0` and increment by 100 until returned pages reconcile with `stats.total`. Archive the exact request body, UTC timestamp, status, raw JSON for every page, checksums, API-reported total, returned records, and any UI cross-check. If totals change during pagination, preserve the snapshot and rerun the logical query.

Screen all unique returned records under the protocol's complete date, language, publication-type, population, MBSE, EPS-route, and retrieval rules, and inspect available attachments. Potentially eligible NTRS evidence includes a substantive full primary report—such as a technical publication/memorandum, contractor or grantee report, or conference paper—with methods/results and stable provenance; accessibility alone neither establishes nor defeats scientific eligibility. Preserve NTRS ID, report numbers, STI/document type, technical/peer-review metadata when reported, distribution, version, identifiers, attachment type, and availability. A scientifically plausible report that cannot be obtained follows the protocol's `not_retrieved` route. Abstracts, posters, and presentation-only records are discovery leads only.

Deduplicate NTRS deposits by source ID, report number, DOI, normalized title/author/year, and attachment identity, while retaining all discovery events. Link technical-report, conference, abstract, and presentation manifestations through the protocol's study/implementation report-family mapping; do not erase a substantively distinct report merely because it shares a family.

Report the total and retrieved count for every logical cell, the simple sum across cells with overlap explicitly acknowledged, the separately deduplicated NTRS union, full reports sought/retrieved, lead-only records, report families, exclusions, and inclusions. Any later protocol-approved update reruns the complete matrix because NTRS may add older records retrospectively.

## 12. Citation searching and Buruso recall benchmark

Backward/forward citation chasing is not part of the independent six-source baseline. After full-text screening begins, chase every included report and relevant secondary review iteratively as required by the protocol, with new candidates rescreened and newly included reports chased. For every cycle, log seed reports, direction, citation index/platform, date, candidates, duplicates, decisions, and stopping outcome.

After the independent six-source candidate set is merged and frozen, use this named secondary review:

> Buruso, R. B., Himmiche, S., Tejumola, T., Alemayehu, Y., & Rose, B. (2026). Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review. *Systems Engineering*. https://doi.org/10.1002/sys.70051

Create a read-only benchmark register of its cited reports that appear potentially relevant to CubeSat/nanosatellite MBSE, EPS, outcome/burden, or V&V. Match normalized DOI/title metadata against the independent set and report found/missed status and discovery source. A miss may trigger a logged concept-level recall probe or a citation-chasing event; it cannot be inserted directly. Merge and deduplicate every resulting candidate, then rerun the Buruso and retained-file audits against the expanded set. Repeat this supplementary-search/audit cycle until a full cycle produces no new eligible report; preserve each baseline/audit version rather than silently moving the original freeze point. Record the final eligibility reason for every apparently relevant benchmark report without importing Buruso's classifications.

The use of arXiv, Semantic Scholar, and Google Scholar is forbidden for discovery or citation searching.

## 13. Iteration and count rules

1. Run two or three pilots at a time for query-based sources; do not treat ESA event pagination/harvest requests as separate conceptual searches.
2. Count before full retrieval where supported, then retrieve and inspect every record for each accepted final query or matching operation.
3. A query around 30–70 hits is normally manageable. Do not narrow solely to meet that heuristic if doing so removes a prespecified concept; partition terms and retrieve all partitions instead.
4. If a query is overbroad, inspect a sample and refine using fields or structured-model relations—not outcome direction, open-access status, generic SmallSat terms, or legacy titles.
5. If a query is too narrow, relax one concept variant at a time and log the effect.
6. Retrieve all records available for every accepted final query or source harvest, subject only to documented source/API limits and failures.
7. Compare Stream A and Stream B unique yield after deduplication. A broad Stream B route cannot be dropped merely because most records lack EPS terms in metadata.
8. Keep source-reported totals, actually retrieved totals, unique records, reports, report families, EPS threads, outcome/burden records, and V&V records as distinct counts.

## 14. Merge, deduplication, and screening

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

1. retain identification totals separately for all six electronic sources and for each permitted citation/other-source route;
2. distinguish source-reported/harvested totals from records actually retrieved or parsed;
3. count duplicate removals before screening separately from records excluded during screening;
4. reconcile records screened, records excluded, reports sought, reports not retrieved, full reports assessed, and full reports excluded with one primary reason;
5. make included **reports** the flow endpoint and report report families, EPS threads, outcome/burden records, and V&V records only in separate analytic-denominator tables; and
6. do not count a retained legacy file as identification unless it is independently rediscovered or reached through a permitted logged citation route.

## 15. Coverage audit and deferred retained-file recall check

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
- unrestricted Wiley retrieval, with INCOSE International Symposium as a coverage check;
- unrestricted ESA Indico harvest, with the known ESA MBSE workshops as a coverage check;
- NTRS technical-report and conference-paper coverage; and
- Buruso et al. (2026) benchmark recall.

Only after the independent six-source candidate set is frozen, compare its normalized DOI/title/source-ID metadata with the retained `markdown/` and `pdfs/` cache. Record found/not-found status and the independent discovery event for matches. Use misses only to design logged concept-level recall probes; a retained file cannot enter the corpus without a valid discovery or protocol-compliant citation-chasing event.

## 16. Planned artifacts

```text
SLR/SLR1/
  protocol.md
  query-search-plan.md
  search-log.md
  screening.md
  corpus.json
  searches/
    scopus/
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

## 17. Search-stage stopping rule

The independent electronic-source and title/abstract corpus stage is complete only when:

- both streams have final accepted runs in Scopus, IEEE Xplore, Compendex, and Wiley, or a documented source failure;
- every 2011-current ESA Indico event has an export/access outcome and the complete harvested metadata has been matched with the frozen concept dictionaries;
- all 102 mandatory NTRS baseline cells, subject only to prospectively documented source-equivalent consolidations, have been paginated to exhaustion or have a documented source failure;
- all final-query/source records available within documented limits have been saved, read, and reconciled to source totals;
- required concept clusters, publication types, technical-report routes, and source-specific coverage checks have been audited;
- Stream A/Stream B and source-unique yields are known;
- additional query refinements are predominantly duplicates or irrelevant records rather than merely inconvenient to search;
- the merged candidate set, screening log, and retrieval corpus pass provenance and count checks;
- the independent candidate set and every supplementary expansion have undergone the deferred Buruso and retained-file recall audits, with one complete audit cycle yielding no new eligible report; and
- every unresolved source access failure, lead-only record, and count discrepancy is explicitly logged.

Citation chasing remains a later search phase tied to full-text inclusions and relevant secondary reviews. It is complete only after one full backward/forward cycle yields no new eligible report and must not be falsely reported as complete at the independent corpus-construction stage.
