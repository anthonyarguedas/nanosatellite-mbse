# PRESS-fix browser-source validation — WoS, Compendex, and Wiley

**Classification:** `pilot_not_candidate_search` only.
**Run date/time zone:** 2026-08-07, EDT (UTC−04:00).
**Scope:** fresh no-screening browser diagnostics for MAJOR-01, MAJOR-02, MAJOR-04, MAJOR-07, and MINOR-02 only.

No record was opened, selected, exported, screened, retained, or used as a candidate. No protocol, plan, search log, dictionary, tool, or final-search artifact was changed.

## Exact inputs and artifact boundary

All `WS-*`, `C-*`, and `W-*` strings were byte-for-byte extracted from the current fenced blocks in [`../../query-search-plan.md`](../../query-search-plan.md). The ignored raw input artifact is `queries-final-and-variants.json` (SHA-256 `ea6c504bf74b9cd86c8d0d2410ef5896cc82d99257b1c5d42bd6fcea4d067845`), with per-query lengths/SHA-256 values.

For each matched population check, the comparator was the corresponding **final B1** text with only this substring removed:

```text
 OR "nano satellites"
```

Thus the comparisons retain the other corrected population, M, E, relation, date, language, and source controls. They are count comparisons only; no result-set or record-level comparison was made.

Raw aggregate diagnostics are exclusively in the Git-ignored, owner-only directory:

```text
.searches/eps-mbse-slr-2026/press-fix-pilots/2026-08-07/browser-sources/
```

The directory is mode `0700`; artifacts are mode `0600`. `manifest.json` indexes 27 payload files and has SHA-256 **`5c98bffe52e4aaa46ea15437aad538fa9dbcf0414c0a29c8eb9d77a714f086e5`**. Its sanitization checks found no raw HTML, Engineering Village session ID, resolver payload, record list, or native record export.

## Controls observed

### Web of Science Core Collection

- Normal browser **Basic Document Search**, one complete Boolean expression in **Topic**.
- `Search in: Web of Science Core Collection`; `Editions: All`. The picker showed all ten available editions selected: SCI-EXPANDED, SSCI, AHCI, CPCI-S, CPCI-SSH, BKCI-S, BKCI-SSH, ESCI, CCR-EXPANDED, and IC.
- Publication Date `2011-01-01` through `2026-08-07`; Language = `English`; Relevance; page size 50.
- Final runs had **no Document Type field/restriction**. The old-control comparator alone used `Article OR Book Chapter OR Proceedings Paper`.
- At **11:21:39 EDT**, Advanced Search → **More options** exposed **Exact search** as a `switch` with observed `aria-checked="false"`. It was left unchanged. No UI semantics for lemmatization, stemming, or automatic term expansion were stated or inferred from that state.

### Compendex on Engineering Village

- Normal browser **Expert Search**; Compendex checked; All, Inspec, and Knovel clear.
- Published UI control = `2011–Latest`; Relevance; visibly selected **100/page**.
- The checkbox labelled **Turn autostemming off** was checked throughout (autostemming OFF per the visible control label).
- Every successful result echo contained the literal suffix:

```text
AND (2011-* WN YR) AND (({English}) WN LA)
```

- No document-type filter was selected and no `WN DT` clause was echoed.

### Wiley Online Library

- Normal browser Advanced Search across the whole Wiley platform, one non-empty `Anywhere`/`AllField` row (`field1=AllField`, complete query in `text1`); rows 2–3 empty.
- `AfterMonth=1&AfterYear=2011&BeforeMonth=8&BeforeYear=2026`; Wiley rendered the upper date as 2026-08-31. No venue, `PubType`, OA, subject, or language facet was supplied.
- `Articles & Chapters` and `Collections` were kept separate. With no explicit sort parameter, the rendered sort control said `Date`.

## Observed final-string counts

### WoS Core Collection

| ID | Observed EDT completion | Source total | Result |
|---|---:|---:|---|
| WS-A1 | 11:52:02 | 1 | Topic, English, exact dates, All editions, no type restriction rendered |
| WS-A2 | initial attempts 11:52:35/11:56:45; clean follow-up 12:13:38 | 0 | Initial harness route failed; the clean Basic/Topic follow-up below displayed `Your search found no results`, establishing a valid source zero |
| WS-B1 | 11:53:08 | 43 | final unrestricted form rendered |
| WS-B2 | 11:53:41 | 34 | final unrestricted form rendered |
| WS-V1 | 11:54:14 | 1 | final unrestricted form rendered |
| WS-O1 | 11:54:47 | 1 | final unrestricted form rendered |

The initial WS-A2 harness attempts remain logged failures, not zeros. The later clean Basic/Topic execution below supersedes only their unresolved status and establishes the valid zero without a fallback translation.

### Compendex

| ID | Observed EDT completion | Source total | Page reconciliation |
|---|---:|---:|---|
| C-A1 | 11:41:29 | 3 | 3 current-page controls at 100/page; 1/1 page |
| C-A2 | 11:38:25 | 6 | 6 at 100/page; 1/1 page |
| C-B1 | 11:38:47 | 76 | 76 at 100/page; 1/1 page |
| C-B2 | 11:39:09 | 58 | 58 at 100/page; 1/1 page |
| C-V1 | 11:43:42 | 1 | 1 at 100/page; 1/1 page |
| C-O1 | 11:44:01 | 1 | 1 at 100/page; 1/1 page |

All six accepted their current corrected exact text under the controls above. `2011-latest` is the server summary range; both the UI Published control and literal `YR` suffix were retained.

### Wiley Online Library

| ID | EDT interval | Articles & Chapters | Collections |
|---|---:|---:|---:|
| W-A1 | 11:22:25–11:22:52 | 7 | tab not exposed; direct Collections route fell back to Articles & Chapters (not asserted as zero) |
| W-A2 | 11:22:52–11:23:31 | 46 | 2 |
| W-B1 | 11:23:31–11:24:03 | 44 | 1 |
| W-B2 | 11:24:03–11:24:40 | 103 | 4 |
| W-V1 | 11:24:40–11:25:16 | 17 | 1 |
| W-O1 | 11:25:16–11:25:49 | 21 | 1 |

## Required matched checks

### Added spaced plural only

| Source/B1 control set | Final text | Final minus only `"nano satellites"` | Difference |
|---|---:|---:|---:|
| WoS, unrestricted, English, exact dates, Editions All | 43 | 43 (11:55:20 EDT) | 0 |
| Compendex, final Expert controls | 76 | 76 (11:40:00 EDT; 100/page recheck 11:36:30) | 0 |
| Wiley Articles & Chapters | 44 | 44 (11:26:05 EDT) | 0 |
| Wiley Collections | 1 | 1 (11:26:13 EDT) | 0 |

Equal dynamic totals do **not** establish identical sets or expansion equivalence.

### WoS MAJOR-07 type-control comparison

Under the same final WS-B1 Topic text, Core Collection/All editions, English, and Publication Date `2011-01-01`–`2026-08-07`:

| B1 form | EDT | Total |
|---|---:|---:|
| Final unrestricted — **no Document Type restriction** | 11:53:08 | 43 |
| Old restriction — `Article OR Book Chapter OR Proceedings Paper` | 11:58:22 | 43 |

The restricted form visibly rendered the three document types; the final form did not. The observed count difference is 0, but no set equivalence or eligibility inference follows.

## Pagination/export diagnostics

- **Wiley broad set:** W-B2 Articles & Chapters reported 103. A direct normal-browser request with `pageSize=20&startPage=5` at 11:26:42–11:26:56 EDT rendered Page 6 active and 3 result-card controls, consistent with the final partial page. No record content was assessed.
- **Compendex:** the broad successful C-B1/C-B2 sets fit on one visible 100-record page (76/76 and 58/58).
- **WoS:** the broad successful unrestricted B1 set was 43 at the observed 50/page, so no multi-page traversal was needed.
- **Fresh ordinary record export:** unrun in the initial count phase; the WoS follow-up below subsequently completed ordinary unrestricted WS-B1 RIS range 1–1. Prior validations still supply the richer cited-reference export procedure for final execution.

## Failures and unrun checks

- **Initial harness/source-route failure:** the first WS-A2 attempts as described above were not zeros; the clean follow-up below subsequently resolved WS-A2 as a valid source zero.
- **Not inferred:** WoS Exact Search `false` was not interpreted as a statement about lemmatization/term expansion; equal plural-check counts were not interpreted as equivalence.
- **Unrun in the initial phase:** no Advanced-Search fallback and no record export. The clean follow-up required no fallback and completed ordinary WS-B1 RIS; no result-set comparison or screening was performed.
- A few local harness-selector/extraction missteps are retained in the ignored raw archive and explicitly distinguished there from source failures; successful aggregate-only follow-ups supplied the reported Compendex and WoS observations.

## Disposition

This is pre-freeze interface/count evidence only. All pilot observations remain superseded for discovery purposes and must be rerun after authorization. No commit was made.

## Follow-up — 2026-08-07 12:08–12:19 EDT (UTC−04:00)

**Classification:** `pilot_not_candidate_search` only. This follow-up resolves only the previously unrun WoS checks below. No result was screened, selected as a candidate, retained for discovery, or used as evidence.

### WS-A2 clean Basic-Search retry

- A new normal **Basic Document Search → Fielded Search → Topic** form was cleared and used; no Advanced-Search fallback was used. The submitted Topic value exactly matched the current `WS-A2` fenced string in `query-search-plan.md` (SHA-256 `4dcd58f550fb3ecd82f67249c6a378a80bfe799a85f0c05580c968c1beb5ad9b`).
- The observed form had `Search in: Web of Science Core Collection`; `Editions: All`, with Select All and all ten available editions checked: SCI-EXPANDED, SSCI, AHCI, CPCI-S, CPCI-SSH, BKCI-S, BKCI-SSH, ESCI, CCR-EXPANDED, and IC. It had Language = English, Publication Date `2011-01-01`–`2026-08-07`, and **no Document Type row/restriction**.
- Submitted at 12:13:27 EDT; at 12:13:38 EDT the source itself displayed **“Your search found no results.”** This is a valid observed source total of **0**, not a UI/navigation failure.
- A zero-result page exposes no results-grid sort or page-size control, so none was inferred for WS-A2. The fresh unrestricted WS-B1 result page used below visibly displayed **Sort by Relevance** and **Page size 50** (43 results, page 1 of 1).

### WS-B1 ordinary RIS follow-up

- A separate clean Basic/Topic execution used the current exact corrected `WS-B1` string (SHA-256 `d7df1054f693e9b7f073206cefd0bcdf936e1ea55af0da0cf6478c37eef5e3cb`) under the same Core Collection/All-ten-editions, English, exact-date, and no-document-type controls. Its source total was **43**.
- The normal page **Export → RIS (other reference software)** route was available and used; **Fast 5000 was not selected**. The ordinary dialog used `Records from/to` = `1`–`1` and its visible default content label was `Author, Title, Source`. A browser download-completed event occurred without a login redirect.
- The untouched native one-record RIS is retained only in the ignored raw archive (391 bytes; SHA-256 `cc7bf2061a2f9181d25a86008a1182da46c132f51b6aec83cf30103fe378de75`; one end-record marker). No exported-record metadata is reproduced here.

### Exact Search observation and raw archive

- In Advanced Search, the observed **Exact search** switch had `aria-checked="false"` and was left unchanged. No lemmatization, stemming, or term-expansion meaning was inferred from that state.
- Raw, access-controlled diagnostics (including the native RIS and download event) are only in `.searches/eps-mbse-slr-2026/press-fix-pilots/2026-08-07/wos-followup/` (directory `0700`, payloads `0600`). `manifest.json` indexes 16 payload artifacts; its SHA-256 is **`0e516843d2e40bf4aae949e94f641de442613f79cd08c6577c483a5f03f7c3bc`**. The current plan's WS-A2/WS-B1 bytes were rechecked against the archived inputs before closing this follow-up.
