# Web of Science Core Collection interface validation

**Status:** completed interface pilot; **`pilot_not_candidate_search` only**. None of these records or counts were screened or used as candidate-set results.

- **Validation started (local):** 2026-08-07 00:39:54 EDT (UTC−04:00)
- **Validation completed (local):** 2026-08-07 00:56:38 EDT (UTC−04:00), including the post-pilot merger source-alias fix and regression test
- **Database/interface:** Web of Science Core Collection, normal web UI in the existing local browser session
- **Scope:** inspect and retain the prior live session; do not restart the six searches. WS-A2 was already present in live search history, so no query was re-run.
- **Git:** no pilot metadata was staged or committed.

## Evidence convention

- **Observed** means directly visible in the live WoS UI/search history or in the native ordinary-export artifact.
- **Inferred** means reconstructed from timing/context or a proposed future procedure; it is explicitly marked as such.

## Live-session inventory and exact query validation

### Common observed execution settings

All six entries below were visible in the **Current session** WoS search history. The UI rendered each Boolean string as **`(Topic)`**, then appended **English (Language)** and **Article OR Book Chapter OR Proceedings Paper (Document Type)**. Each showed **Timespan: 2011-01-01 to 2026-08-06 (Publication Date)**.

Thus, the observed pilot used the required 2011–current window **as of the 2026-08-06 run date**, English, and the three eligible discovery document types. At this report's local date (2026-08-07), the end date is one day behind current; a future authorized run must rerun the strategies through its actual run date rather than relabel this pilot as current through 2026-08-07.

The history displays only a clock time, not a calendar date. The table's 2026-08-06 dates are **inferred** from the overnight transition and the prior live session; the times, query texts, settings, and counts are **observed**.

| ID | UI time (EDT; date inferred as 2026-08-06) | Observed source-native Topic query | Result count |
|---|---:|---|---:|
| WS-A1 | 9:29 PM | A1 string below | 1 |
| WS-A2 | 9:30 PM | A2 string below | 0 |
| WS-B1 | 9:31 PM | B1 string below | 43 |
| WS-B2 | 9:31 PM | B2 string below | 29 |
| WS-V1 | 9:32 PM | V1 string below | 1 |
| WS-O1 | 9:32 PM | O1 string below | 1 |

**WS-A1 — Topic**

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("electrical power system" OR "electric power system" OR "electrical power subsystem" OR "electric power subsystem" OR "power subsystem" OR "electrical architecture" OR "power architecture" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

**WS-A2 — Topic**

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("power budget" OR "energy budget" OR "energy balance" OR "power generation" OR "solar array" OR batter* OR "energy storage" OR "power conditioning" OR "power distribution" OR "power management" OR "power interface" OR "load profile") AND ("model-based systems engineering" OR "model based systems engineering" OR MBSE OR SysML OR "system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR Arcadia OR Capella)
```

**WS-B1 — Topic**

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("model-based systems engineering" OR "model based systems engineering" OR "model-based system engineering" OR "model based system engineering" OR MBSE OR SysML OR "systems modeling language" OR Arcadia OR Capella)
```

**WS-B2 — Topic**

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("system model" OR "systems model" OR "system modeling" OR "systems modelling" OR "reference model" OR "digital engineering" OR "object-oriented systems model") AND (requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)
```

**WS-V1 — Topic**

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (verification OR validation OR traceab* OR "model verification" OR "model validation" OR "system verification" OR "system validation" OR "model checking" OR "virtual integration" OR "requirements-in-the-loop" OR MIL OR "model-in-the-loop" OR SIL OR "software-in-the-loop" OR PIL OR "processor-in-the-loop" OR HIL OR "hardware-in-the-loop" OR "test case" OR "test procedure")
```

**WS-O1 — Topic**

```text
(CubeSat OR CubeSats OR "cube sat" OR nanosatellite OR nanosatellites OR nanosat* OR "nano-satellite" OR "nano-satellites" OR "nano satellite") AND ("electrical power system" OR "electric power system" OR "power subsystem" OR "power budget" OR "energy budget" OR PCDU OR PMAD OR EPS) AND ("model-based systems engineering" OR MBSE OR SysML OR "system model" OR "reference model" OR "digital engineering") AND (reliab* OR "mission assurance" OR reproduc* OR reuse OR reusable OR integrab* OR interoperab* OR traceab* OR benefit* OR impact OR outcome OR burden OR effort OR workload OR overhead OR cost OR schedule OR training OR "learning curve" OR licen* OR adoption)
```

## Observed interface behavior

### Core Collection and citation-index selection

On the Basic Document Search form, **Search in: Web of Science Core Collection** and **Editions: All** were visible. Opening the edition picker showed **Select All** checked plus all ten available listed indexes checked. The A1 history entry's **Show editions** control displayed the same selected set.

| Available and selected in this session | Picker coverage shown |
|---|---|
| Science Citation Index Expanded (**SCI-EXPANDED**) | 1900–present |
| Social Sciences Citation Index (**SSCI**) | 1900–present |
| Arts & Humanities Citation Index (**AHCI**; history rendered `A&HCI`) | 1975–present |
| Conference Proceedings Citation Index – Science (**CPCI-S**) | 1990–present |
| Conference Proceedings Citation Index – Social Science & Humanities (**CPCI-SSH**) | 1990–present |
| Book Citation Index – Science (**BKCI-S**) | 2005–present |
| Book Citation Index – Social Sciences & Humanities (**BKCI-SSH**) | 2005–present |
| Emerging Sources Citation Index (**ESCI**) | 2005–present |
| Current Chemical Reactions (**CCR-EXPANDED**) | 1985–present |
| Index Chemicus (**IC**) | 1993–present |

This confirms that **CPCI-S, CPCI-SSH, BKCI-S, and BKCI-SSH were both available and selected**, not silently excluded. The one-record export also contained `WE  - Conference Proceedings Citation Index - Science (CPCI-S)`.

### Basic Search controls and syntax

**Observed:** Basic Document Search exposed `FIELDED SEARCH`, `QUERY BUILDER`, `CITED REFERENCES`, and `STRUCTURE`; its default field was **Topic**, with **Add row** and **Add date range** controls. The live history/result heading is the evidence that the six strings were submitted in the Topic field and that English, the three document types, and Publication Date range were applied.

**Observed handling to retain for a final run:** enter one complete parenthesized Boolean string in Topic; use explicit `AND`/`OR`, quotes, parentheses, and the existing wildcard forms; set Publication Date from 2011-01-01 through the actual run date; apply English plus Article, Book Chapter, and Proceedings Paper. Do not infer a broader eligible type set from this pilot.

### Advanced Search controls and syntax

**Observed:** Advanced Search exposed a field/query builder, **Query editor**, **Query Preview**, **Exact search**, `Publication Date`, `Search Help`, and the direct instruction `Booleans: AND, OR, NOT`. Its visible field-tag list includes `TS=Topic`, `PY=Year Published`, `UT=Accession Number`, `DO=DOI`, and `ALL=All Fields` (plus title, abstract, author, source, conference, address, funding, category, and date tags). An earlier live syntax probe remains in session as `TS=(CubeSat AND MBSE) AND PY=(2011-2026)`.

The six validated pilots used Basic/Topic UI rendering rather than being newly re-executed in Advanced Search. For a controlled final Advanced equivalent, preserve the literal Topic blocks and log any `TS=`/`PY=` translation as a distinct source-native execution rather than treating it as identical by assumption.

### Sort, pagination, and session/search-history behavior

- **Observed:** A1 and B1 result pages displayed **Sort by Relevance** and **Page size 50**. B1 displayed 43 results and `of 1`; no multi-page traversal was needed or tested. All six pilot totals are at most 43, so page-boundary behavior and a final large-set pagination reconciliation remain unvalidated.
- **Observed:** normal result pages expose next-page controls, a per-page record selection count (for example, `0/43`), Add To Marked List, and Export.
- **Observed:** Search History labels these rows as **Current session**, provides a date-range filter, `Clear all history`, and an Export control. Advanced Search showed **Session Queries 0/9**, `Combine Sets`, `Export`, and `Clear History`. The same live session was visible across the pre-existing Basic, Advanced, result, and history tabs.
- **Observed:** the UI advertised saved-search management on the Alerts page and showed Sign In/Register, but no account, saved search, alert, or credential entry was used. Session persistence beyond the displayed live browser session was not validated.

## One-record ordinary metadata export and merge smoke test

### Ordinary export procedure — observed success

At approximately **2026-08-07 00:44–00:50 EDT**, an existing WS-A1 one-result page was used. No full text was opened.

1. Opened the normal page-level **Export** menu only. The ordinary menu offered Plain text file, **RIS (other reference software)**, BibTeX, Excel, Tab delimited file, Printable HTML file, Email, and other destinations; **Fast 5000** appeared as a separate menu item and was not selected.
2. Selected ordinary **RIS (other reference software)**. Its dialog offered **All records on page** or **Records from/to** and stated **“No more than 1000 records at a time.”**
3. Selected range **1 to 1**. The direct content choices were Author/Title/Source; Author/Title/Source/Abstract; **Full Record**; and Custom selection (10). A direct Full Record RIS completed first (2,527 bytes) and was retained unchanged as a comparison artifact.
4. There was no direct named **“Full Record and Cited References”** option. However, the Custom selection **Edit** dialog explicitly exposed **Cited References** and reported that RIS does not support every listed field. All selectable custom fields were selected; the dialog then displayed **Custom selection (30)**, including Cited References, Abstract, addresses/affiliations, document type, keywords, editions, citation/use fields, and funding/publisher/access/language fields.
5. Selected range **1 to 1** again with Custom selection (30) and submitted ordinary RIS Export. Download events completed a 4,576-byte RIS to `/tmp/savedrecs.ris`; it contains **31 individual `CR` tags**. This is the richest available normal-UI structured export observed here. No login redirect occurred, and no credential was requested or entered.

The pre-existing browser tab at `access.clarivate.com` had a URL ending in `overlay:export/fast5k`, an **observed prior-session Fast 5000/login path**. It was not used in this validation. Ordinary RIS export therefore has no observed authentication blocker in this session.

### Native artifact preservation and contents

- **Primary native untouched copy:** `/tmp/slr1-wos-a1-custom-30-including-cited-references-1-1.ris` (the browser's completion path was `/tmp/savedrecs.ris`; both have identical bytes).
- **Durable access-controlled pilot copy:** `.searches/eps-mbse-slr-2026/interface-pilots/2026-08-07/web-of-science/`; its six diagnostic files are indexed by the parent `manifest.json` (manifest SHA-256 `c137b96f8e5406cdbc04783bf1d2ada45446e43959e11c1ad76b0884d2bb80eb`). The directory is Git-ignored and prohibited from candidate use.
- **Format:** RIS, ordinary normal UI, WS-A1, range 1–1, **Custom selection (30) including Cited References**.
- **Size:** 4,576 bytes; **records:** 1.
- **SHA-256:** `08008465e75f29fda995d58057ed8f818a442f598aa07aa9d2d172c2f0508263`.
- **Tag counts:** `A1:1, AB:1, AD:1, AN:1, AU:3, C3:4, CP:1, CR:31, DO:1, ER:1, J9:1, KW:5, LA:1, N1:1, PA:1, PI:1, PU:1, PY:1, SN:2, T2:1, TI:1, TY:1, WE:1`.
- **Initial direct Full Record comparison artifact:** `/tmp/slr1-wos-a1-full-record-1-1.ris`, 2,527 bytes, SHA-256 `c7cde3b602e50515b3f9c9caea803dc46a072ae2ff5306e0f4742dc585dede39`; it had the same metadata tags but no individual `CR` tags.
- **Native identifiers/content facts:** `AN` is `WOS:001027247800008`; `DO` and `AB` are present; `CR` has 31 values; `UR` is absent. Thus URL is genuinely blank in the normalized artifact rather than fabricated.

### Reproducible normalization and merge

The supplied RIS converter already maps RIS `AN` to `Paper ID` (`AN`, then `ID`, then `M1`), so no custom converter was needed for the WoS accession ID. Its common merge CSV schema has no cited-references column, however. A separate reproducible `/tmp/wos_ris_cited_refs_sidecar.py` reads the native RIS through the supplied converter's parser and writes the 31 `CR` values unchanged to a JSON sidecar; no bibliographic values or native RIS bytes were hand-edited.

```bash
python3 /Users/antho/agent-tools/academic-research/skills/academic-search/scripts/ris_to_merge_csv.py \
  --input /tmp/slr1-wos-a1-custom-30-including-cited-references-1-1.ris \
  --output-path /tmp/slr1-wos-a1-cited-refs-normalized.csv \
  --source 'Web of Science Core Collection' \
  --query '<exact WS-A1 Topic Boolean shown above>' \
  --rank-offset 0 \
  --source-total 1

python3 /tmp/wos_ris_cited_refs_sidecar.py \
  --input /tmp/slr1-wos-a1-custom-30-including-cited-references-1-1.ris \
  --output-path /tmp/slr1-wos-a1-cited-refs-sidecar.json \
  --source 'Web of Science Core Collection' \
  --query '<exact WS-A1 Topic Boolean shown above>' \
  --rank-offset 0 \
  --source-total 1

python3 /Users/antho/agent-tools/academic-research/skills/academic-search/scripts/merge_search_results.py \
  --input /tmp/slr1-wos-a1-cited-refs-normalized.csv \
  --output-path /tmp/slr1-wos-a1-cited-refs-merged-with-alias.json
```

- **Normalized CSV:** `/tmp/slr1-wos-a1-cited-refs-normalized.csv`; 1 row; SHA-256 `2c5845d9a0b75bb18b0d58c31c24e6ccf46f703ca50b7af8f0d1f158c6a1c3a5`.
- **Headers:** `Search source, Query, Rank, Paper ID, DOI, Title, Authors, Publication year, Abstract, Citation count, URL, Open access PDF, Source total`.
- **Cited-reference sidecar:** `/tmp/slr1-wos-a1-cited-refs-sidecar.json`; one record, `paper_id=WOS:001027247800008`, 31 cited-reference strings, SHA-256 `fbd8f9807a82590b21e989b8b9bd2c0c9b092132f2d6296aedcf04b4d21791f1`. Script SHA-256: `ab9b0e16509adc1d46061ffe228110866b3f129ce0e375145a7bd19b457cb1cc`.
- **Merged JSON after the source-alias fix:** `/tmp/slr1-wos-a1-cited-refs-merged-with-alias.json`; SHA-256 `dd8ea3597ff593f51fc83ee945d74e7b4cadfa0193af7fa639e4cab21e3a5bc8`; merge result **1 raw / 1 unique / 0 removed**.
- **Merger update:** `merge_search_results.py` now recognizes `Web of Science`, `Web of Science Core Collection`, `WoS`, and `WoS Core Collection` as `web_of_science_core_collection`; filename inference also recognizes `web_of_science` and tokenized `wos`. Its seven offline regression tests passed, including a new normalized-WoS CSV test. Post-fix SHA-256: merger `fcf0168dd25480dc882de6e53c505fb47eebc3839d772bd96fdfc1b1c921dde4`; test file `917e547c5f49125a1796f6881d83640b2dcaffee2b6c37a079e936451b0e0540`.

| Required provenance/metadata item | Normalized CSV result | Merge result |
|---|---|---|
| Search source | `Web of Science Core Collection` preserved verbatim | canonicalized to `web_of_science_core_collection` after the explicit alias update |
| Query | exact WS-A1 Topic Boolean preserved | preserved in record provenance |
| Rank | `1` | provenance rank `1` |
| WoS UT/accession ID | `Paper ID=WOS:001027247800008` from RIS `AN` | preserved as `paperId` |
| DOI | `10.1109/SysCon53073.2023.10131054` | preserved canonically lowercased by merger |
| Title, authors, year, abstract | present (`TI`, `AU`, `PY`, `AB`) | preserved (authors normalized to name objects) |
| URL | blank: native RIS has no `UR` | blank; not fabricated |
| Source total | `1` | input total `1` |
| Individual cited references | 31 native `CR` values retained in the sidecar (the common CSV has no such column) | not represented by the merger schema; retain native RIS/sidecar |
| Raw / unique counts | 1 exported row | 1 / 1 |

The smoke test is therefore successful for rich native RIS export, cited-reference preservation, record/metadata conversion, canonical WoS source attribution, and deduplication. Native RIS plus the sidecar retain the individual cited references outside the common merger schema.

## Operational procedure for a later authorized final run

1. Start in Web of Science Core Collection Basic Search and confirm **Editions: All** still has the ten indexes listed above selected, including CPCI-S/CPCI-SSH and BKCI-S/BKCI-SSH.
2. Re-enter all six exact Topic strings; set Publication Date 2011-01-01 through the actual run date, English, and Article/Book Chapter/Proceedings Paper. Preserve each History entry, UI time/date/time zone, count, and selected editions.
3. Declare a sort (the pilot observed Relevance) and page size; enumerate all pages and reconcile result ranks to the source total before export.
4. Before a large export, use ordinary Export — never Fast 5000 — and perform a one-record preflight: RIS, range 1–1, then Full Record plus Custom selection with Cited References where the direct combined option is absent; enable download events to a controlled directory, preserve native RIS/CR sidecar and checksum, then convert and merge-smoke-test.
5. If ordinary export later redirects to login, stop without credentials and record the URL/status. An authorized operator should verify institutional WoS export entitlement, use normal Export rather than Fast 5000, confirm range/content settings and a real browser download event, then preserve the native artifact before conversion. That contingency was **not** reached here.

## Limitations and blockers

- All six are dynamic, session-bound **pilot_not_candidate_search** observations. They must be rerun after protocol authorization and must not be screened.
- WS-A2 is an observed zero-result history entry; it was found rather than re-run.
- History showed time-of-day but no calendar date; 2026-08-06 is inferred for the six 9:29–9:32 PM entries. The exact query/settings/counts are UI-observed.
- The observed pilot end date is 2026-08-06, not the report date 2026-08-07.
- Multi-page result processing and a hard export ceiling beyond the dialog's 1,000-record statement were not validated. Individual cited-reference export **was** validated for one record through Custom selection (30), but only as source-native RIS/sidecar data because the common merge CSV schema has no cited-references field.
- Native Full Record RIS omitted `UR`; URL cannot be recovered without a separate documented source action and was left empty.
- The common merge schema does not carry individual cited references; retain the native RIS and reproducible sidecar when those references are needed for backward citation chasing.
- No ordinary-export access blocker occurred. The existing Fast 5000 Clarivate-login tab is not evidence that normal export is blocked.

## Insertion-ready text for `query-search-plan.md`

```markdown
### Web of Science Core Collection interface validation (2026-08-06/07)

A live normal-UI pilot used Web of Science Core Collection Basic Search with
`Editions: All`. The visible selected set was SCI-EXPANDED, SSCI, AHCI/A&HCI,
CPCI-S, CPCI-SSH, BKCI-S, BKCI-SSH, ESCI, CCR-EXPANDED, and IC; retain all of
these selections, especially the conference- and book-citation indexes, in a
final run. The six exact Topic-field Boolean strings and their live
`pilot_not_candidate_search` counts are preserved in
`searches/subagent-logs/2026-08-07-wos-interface-validation.md`: WS-A1=1,
WS-A2=0, WS-B1=43, WS-B2=29, WS-V1=1, and WS-O1=1. The pilot applied
Publication Date 2011-01-01–2026-08-06, English, and Article OR Book Chapter
OR Proceedings Paper. Rerun through the actual final-run date after
authorization; pilot hits must not be screened.

Use ordinary Export, not Fast 5000. The tested one-record procedure is RIS,
range 1–1, with the direct Full Record choice followed by Custom selection
(30) including Cited References because no direct named `Full Record and Cited
References` option appeared. The normal UI download succeeded without login;
the rich native RIS preserved `AN`/WoS accession, DOI, title, authors, year,
abstract, and 31 individual `CR` values. Preserve native RIS unchanged,
normalize its common metadata with `ris_to_merge_csv.py` using source `Web of
Science Core Collection`, exact query, global rank offset, and source total,
and retain a reproducible CR sidecar because the merge schema has no cited-
references column. Then smoke-test with `merge_search_results.py`. The merger now recognizes
`Web of Science Core Collection` as canonical source
`web_of_science_core_collection`; preserve that regression-tested alias in the
final-run software version.
```

## Insertion-ready entry for `search-log.md`

```markdown
### Web of Science Core Collection — interface pilot (`pilot_not_candidate_search`)

- **Interface/date:** normal Web of Science Core Collection Basic/Advanced UI;
  observations made 2026-08-07 EDT from a live prior-session history. The
  six history times were 2026-08-06 (date inferred; UI showed time only):
  A1 21:29, A2 21:30, B1/B2 21:31, V1/O1 21:32 EDT.
- **Scope/settings:** Basic Search Topic field; Editions All with
  SCI-EXPANDED, SSCI, AHCI/A&HCI, CPCI-S, CPCI-SSH, BKCI-S, BKCI-SSH, ESCI,
  CCR-EXPANDED, and IC selected; Publication Date 2011-01-01–2026-08-06;
  English; Article, Book Chapter, Proceedings Paper; observed sort Relevance
  and page size 50. Exact Topic strings are in
  `searches/subagent-logs/2026-08-07-wos-interface-validation.md`.
- **Reported totals:** WS-A1 1; WS-A2 0; WS-B1 43; WS-B2 29; WS-V1 1;
  WS-O1 1. Do not use as candidates or inclusion counts; rerun all six after
  authorization.
- **Normal-export preflight:** ordinary RIS, WS-A1 range 1–1, direct Full
  Record followed by Custom selection (30) including Cited References. Native
  `/tmp/slr1-wos-a1-custom-30-including-cited-references-1-1.ris` has one RIS
  record, 31 `CR` tags, and SHA-256
  `08008465e75f29fda995d58057ed8f818a442f598aa07aa9d2d172c2f0508263`.
  Normalized `/tmp/slr1-wos-a1-cited-refs-normalized.csv` had one row and
  post-fix merge output `/tmp/slr1-wos-a1-cited-refs-merged-with-alias.json`
  reconciled 1 raw/1 unique; `/tmp/slr1-wos-a1-cited-refs-sidecar.json`
  retains the 31 `CR` values. `AN` mapped to `WOS:001027247800008`, and the
  regression-tested merger alias canonicalized the source as
  `web_of_science_core_collection`. No credentials, Fast 5000 action, full
  text, screening, staging, or commit occurred.
```
