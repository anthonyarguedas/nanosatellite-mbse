# Search and source-interface log

**Review run:** `eps-mbse-slr-2026`<br>
**Protocol status during entries below:** version 1.1 pre-search freeze candidate<br>
**Time zone unless stated otherwise:** EDT (UTC−04:00)

## Status boundary

Every entry dated 2026-08-06 below is `pilot_not_candidate_search`: it validates source syntax, controls, pagination, export, or normalization before protocol authorization. No pilot record establishes discovery provenance or evidence membership. Every accepted strategy must be rerun after the protocol freeze; only those later final-run artifacts may create the independent candidate set.

Aggregate behavior and checksums are retained here without importing pilot hits into screening. Raw diagnostic artifacts are retained read-only in the access-controlled, Git-ignored `.searches/eps-mbse-slr-2026/interface-pilots/2026-08-06/` work area and are indexed by `manifest.json` (88 files; manifest SHA-256 `0e5986a1cd43b8fb1cab65b00ba8863696127eadb579ac9b000e1492bfcd31b4`); they are not the SLR corpus and must not be passed to candidate merge or screening.

## Scopus interface diagnostics

- **Source/platform:** Scopus Search API, Elsevier; `https://api.elsevier.com/content/search/scopus`
- **Interface/view:** authenticated API, `COMPLETE`; API key omitted from all logs
- **Client:** `search_scopus.py`; SHA-256 `1c92dde7a62b43d8003767eb0b2c7c262d35ef12ac09da430da65b642def6d9d`
- **Limits for every accepted diagnostic:** `PUBYEAR AFT 2010`, `PUBYEAR BEF 2027`, `LANGUAGE(english)`, and `DOCTYPE(ar|cp|ch)` as written in each source-native query
- **Initial transport check:** an unauthenticated request returned HTTP 401 and was correctly treated as authentication failure, not zero results.

| Pilot ID | Time (EDT) | Exact strategy | Source total | Retrieved | Disposition |
|---|---:|---|---:|---:|---|
| `P-S-A1-count` | 19:37:48 | `S-A1` verbatim in `query-search-plan.md` plus year clauses | 3 | 1 diagnostic record | syntax/count accepted |
| `P-S-A2-count` | 19:37:50 | `S-A2` verbatim plus year clauses | 9 | 1 diagnostic record | syntax/count accepted |
| `P-S-B1-count` | 19:37:41 | `S-B1` verbatim plus year clauses | 75 | 1 diagnostic record | syntax/count accepted |
| `P-S-B2-count` | 19:37:52 | `S-B2` verbatim plus year clauses | 55 | 1 diagnostic record | syntax/count accepted |
| `P-S-V1-count` | 19:37:53 | `S-V1` verbatim plus year clauses | 1 | 1 diagnostic record | syntax/count accepted |
| `P-S-O1-count` | 19:37:55 | `S-O1` verbatim plus year clauses | 4 | 1 diagnostic record | syntax/count accepted |
| `P-S-A1-full-check` | 19:38:04 | same as `P-S-A1-count` | 3 | 3 | total reconciled; normalized JSON passed merge test |

These are dynamic interface counts, not identification or inclusion counts.

## IEEE Xplore interface diagnostics

- **Source/platform:** IEEE Xplore; `https://ieeexplore.ieee.org/rest/search`
- **Count-pilot client:** `search_ieee_xplore.py`; SHA-256 `eee08f82ab70620c70f06d09090208ece811bb9b801e6420c55b864074e0a3e9`
- **CSV-provenance revision:** SHA-256 `7d09758723b759f03d5db95264bfce4c749f43022dd6b2d9c51a1d0be033ab77`; a second complete I-A1 diagnostic still returned/reconciled 4 and its CSV preserved source, exact query, rank, and source total through the merge test
- **Limits for every diagnostic:** years 2011–2026; content types `Journals`, `Conferences`, `Books`; language `English`
- **Initial transport check:** a bare curl POST returned HTTP 418 and was treated as an access/challenge response, not zero results. The client used its validated request behavior successfully.

| Pilot ID | Time (UTC) | Exact strategy | Source total | Retrieved | Disposition |
|---|---:|---|---:|---:|---|
| `P-I-A1-count` | 23:36:41 | `I-A1` verbatim in `query-search-plan.md` | 4 | count-only | syntax/facets accepted |
| `P-I-A2-count` | 23:36:44 | `I-A2` verbatim | 2 | count-only | syntax/facets accepted |
| `P-I-B1-count` | 23:36:24 | `I-B1` verbatim | 38 | count-only | syntax/facets accepted |
| `P-I-B2-count` | 23:36:45 | `I-B2` verbatim | 42 | count-only | syntax/facets accepted |
| `P-I-V1-count` | 23:36:49 | `I-V1` verbatim | 1 | count-only | syntax/facets accepted |
| `P-I-O1-count` | 23:36:51 | `I-O1` verbatim | 4 | count-only | syntax/facets accepted |
| `P-I-A1-full-check` | 23:37:11 | same as `P-I-A1-count` | 4 | 4 | total reconciled; normalized JSON and CSV each passed merge test |

Count-only runs deliberately discarded the one response record. These are dynamic interface counts, not identification or inclusion counts.

## ESA Indico interface diagnostics

- **Source/interface:** full public ESA Indico instance; `https://indico.esa.int/export/categ/0.json`
- **Root run:** 2026-08-06 19:23:31 EDT; HTTP 200; 2,512,942 bytes; SHA-256 `cd981bbfbd5e9fac036f790805bb6ea5a0dfab3a77d9b09d063e6262cad30312`
- **Observed root total:** 437 unique events. The root event-ID set exactly equaled the union of child exports 5, 6, and 7; category 9 was a subset of category 6. Child counts were 3, 377, 57, and 1 respectively.
- **Date check:** all 437 root events had parseable start dates; 408 fell from 2011-01-01 through 2026-08-06.
- **Coverage IDs:** 161, 329, 386, 407, and 472 were all present.
- **Contribution-shape checks:** each tested `export/event/{id}.json?detail=contributions` request returned HTTP 200 and one event in `results[0]`; contribution counts must be read from `results[0].contributions`, not top-level `count`. Diagnostic nested counts for the five coverage events were 15, 35, 46, 62, and 15.

This validates census and response shape only. The full root/child comparison and all in-window contribution exports must be rerun after authorization.

## NASA NTRS interface diagnostics

- **Source/UI:** `https://ntrs.nasa.gov/search`
- **Endpoint:** `POST https://ntrs.nasa.gov/api/citations/search`
- **Common body controls:** `published.gte=2011-01-01`, `published.lte=2026-08-06`, `page.size` as shown, zero-based `page.from`
- **Normalized-client check:** `search_ntrs.py` SHA-256 `b2a51f682fecd5acf19dc8730fb636cdaba3957372f331ead67ae96b0a115f4d` retrieved/reconciled all 4 records for diagnostic `CubeSat MBSE`; its JSON passed `merge_search_results.py`

| Pilot ID | Exact `q` | Total | Observation |
|---|---|---:|---|
| `P-N-T01` | `CubeSat MBSE` | 4 | simple spaces accepted |
| `P-N-T02` | `CubeSat AND MBSE` | 4 | same complete ID set as T01, different order |
| `P-N-T03` | `CubeSat OR MBSE` | 0 | Boolean OR unreliable; prohibit |
| `P-N-T04` | `(CubeSat OR nanosatellite) AND MBSE` | 0 | grouped Boolean unreliable; prohibit |
| `P-N-T05` | `CubeSat "model-based systems engineering"` | 2 | phrase quoting materially restrictive |
| `P-N-T06` | `CubeSat model-based systems engineering` | 7 | unquoted words differ from exact phrase |
| `P-N-T07` | `CubeSat SysML` | 0 | valid zero-result diagnostic |
| `P-N-T08` | `nanosatellite "electrical power system" MBSE` | 0 | valid zero-result diagnostic |
| `P-N-T09` | `"nano-satellite" "system model"` | 0 | valid zero-result diagnostic |

Further controls confirmed `page.size=100`; two `CubeSat` pages at `from=0` and `from=5` returned nonoverlapping five-record samples with stable total 841. The publication-date filter changed the broad `CubeSat` total from 857 (1900 start) to 841 (2011 start) and 161 (2020 start). Final cells therefore use only spaces and quoted phrases, fixed pages of 100, no Boolean operators/parentheses, and complete reconciliation to `stats.total`.

## Wiley Online Library browser diagnostics

- **Source/platform:** full Wiley Online Library; <https://onlinelibrary.wiley.com/search/advanced>
- **Endpoint:** `https://onlinelibrary.wiley.com/action/doSearch`
- **Browser reports:** [`2026-08-06-wiley-interface-validation.md`](searches/subagent-logs/2026-08-06-wiley-interface-validation.md) and [`2026-08-06-wiley-export-followup.md`](searches/subagent-logs/2026-08-06-wiley-export-followup.md)
- **Observed field:** `Anywhere` / `AllField`; exact uppercase Boolean, groups, phrases, and non-leading wildcards accepted
- **Date controls:** January 2011 through August 2026; source normalizes through month-end, requiring report-level run-date screening

| Pilot ID | Time (EDT) | Exact strategy | Articles & Chapters | Collections | Disposition |
|---|---:|---|---:|---:|---|
| `P-W-A1` | 19:25:08 | `W-A1` verbatim in `query-search-plan.md` | 7 | not recorded | accepted |
| `P-W-A2` | 20:23:50 | `W-A2` verbatim | 40 | 2 | accepted |
| `P-W-B1` | 19:27:59–19:28:20 | `W-B1` verbatim | 44 | 1 | accepted; three pages |
| `P-W-B2` | 20:24:21 | `W-B2` verbatim | 105 | 4 | accepted |
| `P-W-V1` | 19:33:32–19:33:52 | `W-V1` verbatim | 17 | 1 | accepted at 690 characters |
| `P-W-O1` | 19:34:23–19:34:43 | `W-O1` verbatim | 21 | 1 | accepted |

Pagination is 20 records with zero-based `startPage`. Export is page-scoped; 20 was a tested-safe selection size. Wiley exposed RIS and other citation formats but no native CSV. A normal one-record W-A1 RIS export with abstracts succeeded (SHA-256 `159debf96aeaa0768f578e4cdbee5b804c2342dd2abe8747668337b937f103e9`) and contained one `N2` abstract. `ris_to_merge_csv.py` (SHA-256 `9099bff33f49f4ac27b91ae0ea711825b01d81cd139aed1be9c1682ab98575c1`) produced a 1-row normalized CSV, and `merge_search_results.py` (SHA-256 `ea1098e54f176aae98e75da7f1b4174b5ad138ccbbdd555360c64831e57e6cd4`) preserved Wiley source, exact query, source total, global rank, and 1/1 raw/unique counts. Repeat this export/merge preflight after authorization and never label normalized CSV as native Wiley output.

## Compendex/Engineering Village browser diagnostics

- **Source/platform:** Compendex on Elsevier Engineering Village Expert Search; <https://www.engineeringvillage.com/search/expert.url?database=1>
- **Browser reports:** [`2026-08-06-compendex-interface-validation.md`](searches/subagent-logs/2026-08-06-compendex-interface-validation.md) and [`2026-08-06-compendex-export-followup.md`](searches/subagent-logs/2026-08-06-compendex-export-followup.md)
- **Validated fields/syntax:** `KY` Subject/Title/Abstract, `YR`, `LA`, uppercase Boolean, parentheses, quoted phrases, and explicit wildcards; Compendex-only selected in the UI
- **Final-setting diagnostic:** C-B1 with `AND (2011-* WN YR) AND (({English}) WN LA)`, Relevance, 100/page, autostemming off, no document-type or `WN DB` clause returned 72 at 2026-08-06 20:12:09 EDT. The server summary retained a broad `1884–2026` coverage label, so the final run must also set the UI Published range and audit exported years.

Earlier syntax pilots with autostemming on and `JA|CA|CP|CH` returned C-A1 = 3, C-A2 = 4, C-B1 = 68, C-B2 = 42, C-V1 = 1, and C-O1 = 1. Those settings were superseded by the higher-recall plan and the counts are not identification counts.

A normal one-record CSV Detailed export succeeded after setting Chrome's download behavior. The untouched 29-column native file had SHA-256 `bd5e879e4d13841a7c8a877b8d64d93eebfde628d3ef77ea5af6d22f5145775f`; it omitted exact query and rank. A normalized CSV (SHA-256 `99108152649565600f4794c495ea358549b3845a12f2118aeb83024d1c73c7de`) added common provenance and passed `merge_search_results.py`, preserving Compendex source, exact query, rank 1, and 1/1 raw/unique counts. Pilot record metadata is not retained in the review workspace and must be re-exported after authorization.
