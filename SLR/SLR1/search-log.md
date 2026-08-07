# Search and source-interface log

**Review run:** `eps-mbse-slr-2026`<br>
**Protocol status during entries below:** version 1.1 pre-search freeze candidate<br>
**Current protocol status:** version 1.2 frozen and authorized 2026-08-07; no final discovery run is recorded below<br>
**Time zone unless stated otherwise:** EDT (UTC−04:00)

## Status boundary

Every entry dated 2026-08-06 or 2026-08-07 below is `pilot_not_candidate_search`: it validates source syntax, controls, pagination, export, or normalization before protocol authorization. No pilot record establishes discovery provenance or evidence membership. Every accepted strategy must be rerun after the protocol freeze; only those later final-run artifacts may create the independent candidate set.

Aggregate behavior and checksums are retained here without importing pilot hits into screening. The 2026-08-06 raw diagnostics are retained read-only in the access-controlled, Git-ignored `.searches/eps-mbse-slr-2026/interface-pilots/2026-08-06/` work area and indexed by `manifest.json` (88 files; manifest SHA-256 `0e5986a1cd43b8fb1cab65b00ba8863696127eadb579ac9b000e1492bfcd31b4`). The Web of Science export and merge diagnostics are retained under `.searches/eps-mbse-slr-2026/interface-pilots/2026-08-07/` (6 files; manifest SHA-256 `c137b96f8e5406cdbc04783bf1d2ada45446e43959e11c1ad76b0884d2bb80eb`). The population-term API/count pilots are retained under `.searches/eps-mbse-slr-2026/term-variant-pilots/2026-08-07/` (85 files; manifest SHA-256 `12b249a440bda72b4ba2a74b82e90ff3e74f23aeb9aea63a8e3dd4f37e9a8f68`). The two-pass Scopus/IEEE API pilots are under `.searches/eps-mbse-slr-2026/multipage-api-pilots/2026-08-07/`, with source manifests SHA-256 `b0b395fdd388533912511cc296300c30657dd22fc70a341687fe37b1a6f70619` (Scopus) and `c18c2c3d558be6fa8b9c7a931dfd4e40e9765d65fbecdb0ca60254278c97bd25` (IEEE).

PRESS-fix pilots are under `.searches/eps-mbse-slr-2026/press-fix-pilots/2026-08-07/`. Key manifests are: API count/strict artifacts `fda7a1ab5a373b4ab8cd25835fe2f5f5a1d1cda31ea66378ab0a8318844f2217`; browser sources `5c98bffe52e4aaa46ea15437aad538fa9dbcf0414c0a29c8eb9d77a714f086e5`; WoS follow-up `0e516843d2e40bf4aae949e94f641de442613f79cd08c6577c483a5f03f7c3bc`; revised NTRS matrix `6a39421df2e5797e47b3b34e67be71330afd7ebf851c02d88862c228a89b1a9a`; and active post-purge/corrected-rematch ESA artifacts `ae1aba9681d63237ae33b0896cefb94787c24bc4086aeb40d8fe501ecde3f8e8`. These artifacts are not the SLR corpus and must not be passed to candidate screening or represented as final-run discovery output.

## Scopus interface diagnostics

- **Source/platform:** Scopus Search API, Elsevier; `https://api.elsevier.com/content/search/scopus`
- **Interface/view:** authenticated API, `COMPLETE`; API key omitted from all logs
- **Client:** `search_scopus.py`; SHA-256 `1c92dde7a62b43d8003767eb0b2c7c262d35ef12ac09da430da65b642def6d9d`
- **Original diagnostic limits (superseded for type):** `PUBYEAR AFT 2010`, `PUBYEAR BEF 2027`, `LANGUAGE(english)`, and `DOCTYPE(ar|cp|ch)`. PRESS revision removes `DOCTYPE` from discovery; the original restricted counts remain only as comparators.
- **Initial transport check:** an unauthenticated request returned HTTP 401 and was correctly treated as authentication failure, not zero results.

| Pilot ID | Time (EDT) | Exact strategy | Source total | Retrieved | Disposition |
|---|---:|---|---:|---:|---|
| `P-S-A1-count` | 19:37:48 | original pre-spelling-audit `S-A1` plus year clauses; exact query in raw artifact | 3 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-A2-count` | 19:37:50 | original pre-spelling-audit `S-A2` plus year clauses; exact query in raw artifact | 9 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-B1-count` | 19:37:41 | original pre-spelling-audit `S-B1` plus year clauses; exact query in raw artifact | 75 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-B2-count` | 19:37:52 | original pre-spelling-audit `S-B2` plus year clauses; exact query in raw artifact | 55 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-V1-count` | 19:37:53 | original pre-spelling-audit `S-V1` plus year clauses; exact query in raw artifact | 1 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-O1-count` | 19:37:55 | original pre-spelling-audit `S-O1` plus year clauses; exact query in raw artifact | 4 | 1 diagnostic record | syntax/count accepted; superseded P block |
| `P-S-A1-full-check` | 19:38:04 | same as `P-S-A1-count` | 3 | 3 | total reconciled; normalized JSON passed merge test |

These are dynamic interface counts, not identification or inclusion counts.

## Web of Science Core Collection browser diagnostics

- **Source/platform:** Clarivate Web of Science, **Web of Science Core Collection**; <https://www.webofscience.com/wos/woscc/basic-search>
- **Interface:** normal browser Basic Document Search, one complete Boolean expression in the `Topic` field; Advanced Search was inspected as a documented fallback but was not substituted for the six Basic Search pilots
- **Browser report:** [`2026-08-07-wos-interface-validation.md`](searches/subagent-logs/2026-08-07-wos-interface-validation.md)
- **Original common settings (superseded for type):** Publication Date 2011-01-01 through 2026-08-06; Language `English`; Document Type `Article OR Book Chapter OR Proceedings Paper`; Relevance sort; observed page size 50. PRESS revision removes the Document Type restriction and reruns through 2026-08-07.
- **Database/edition state:** `Search in: Web of Science Core Collection`; `Editions: All`, with SCI-EXPANDED, SSCI, AHCI/A&HCI, CPCI-S, CPCI-SSH, BKCI-S, BKCI-SSH, ESCI, CCR-EXPANDED, and IC all visible and selected
- **Timing caveat:** live Search History displayed the exact query, controls, total, and time of day but not the calendar date. The six 21:29–21:32 EDT entries are dated 2026-08-06 from the preserved overnight session context; the history/export validation occurred 2026-08-07.

| Pilot ID | Time (EDT) | Exact strategy | Source total | Diagnostic handling | Disposition |
|---|---:|---|---:|---|---|
| `P-WS-A1` | 21:29 | pre-PRESS WS-A1 preserved in the dated browser report | 1 | one-record ordinary RIS export and merge preflight | syntax/controls/count accepted; strategy superseded |
| `P-WS-A2` | 21:30 | pre-PRESS WS-A2 preserved in the dated browser report | 0 | zero-result history entry | valid zero; strategy superseded |
| `P-WS-B1` | 21:31 | pre-PRESS WS-B1 preserved in the dated browser report | 43 | result page/count only | syntax/controls/count accepted; strategy superseded |
| `P-WS-B2` | 21:31 | pre-PRESS WS-B2 preserved in the dated browser report | 29 | result page/count only | syntax/controls/count accepted; strategy superseded |
| `P-WS-V1` | 21:32 | pre-PRESS WS-V1 preserved in the dated browser report | 1 | result page/count only | syntax/controls/count accepted; strategy superseded |
| `P-WS-O1` | 21:32 | pre-PRESS WS-O1 preserved in the dated browser report | 1 | result page/count only | syntax/controls/count accepted; strategy superseded |

Ordinary page-level **Export → RIS (other reference software)** succeeded without credentials on 2026-08-07. The dialog supported explicit record ranges of no more than 1,000 records per export. The validated one-record route used range 1–1 and Custom selection (30), including accession number, DOI, abstract, editions, and cited references; it produced one native RIS record with 31 `CR` tags. The untouched native RIS has SHA-256 `08008465e75f29fda995d58057ed8f818a442f598aa07aa9d2d172c2f0508263`. A separate earlier Full Record RIS has SHA-256 `c7cde3b602e50515b3f9c9caea803dc46a072ae2ff5306e0f4742dc585dede39`. Fast 5000 opened a Clarivate-login route in the prior session and is prohibited as the planned export path; this did not block ordinary RIS export.

`ris_to_merge_csv.py` converted the native RIS to the common one-row CSV schema while preserving exact query, global rank 1, source total 1, WoS accession in `Paper ID`, DOI, title, authors, year, and abstract (normalized CSV SHA-256 `2c5845d9a0b75bb18b0d58c31c24e6ccf46f703ca50b7af8f0d1f158c6a1c3a5`). A reproducible sidecar retained all 31 cited-reference strings (SHA-256 `fbd8f9807a82590b21e989b8b9bd2c0c9b092132f2d6296aedcf04b4d21791f1`). After adding explicit Web of Science aliases, `merge_search_results.py` canonicalized the source as `web_of_science_core_collection` and reconciled 1 raw/1 unique/0 removed (merged JSON SHA-256 `dd8ea3597ff593f51fc83ee945d74e7b4cadfa0193af7fa639e4cab21e3a5bc8`). The post-fix merger SHA-256 is `fcf0168dd25480dc882de6e53c505fb47eebc3839d772bd96fdfc1b1c921dde4`; all seven offline regression tests passed.

All WoS counts, records, and exports above are dynamic interface diagnostics, not identification, screening, or inclusion evidence. Rerun all six exact Topic strategies and the one-record export/merge preflight after authorization.

## IEEE Xplore interface diagnostics

- **Source/platform:** IEEE Xplore; `https://ieeexplore.ieee.org/rest/search`
- **Count-pilot client:** `search_ieee_xplore.py`; SHA-256 `eee08f82ab70620c70f06d09090208ece811bb9b801e6420c55b864074e0a3e9`
- **CSV-provenance revision:** SHA-256 `7d09758723b759f03d5db95264bfce4c749f43022dd6b2d9c51a1d0be033ab77`; a second complete I-A1 diagnostic still returned/reconciled 4 and its CSV preserved source, exact query, rank, and source total through the merge test
- **Original diagnostic limits (superseded for type):** years 2011–2026; content types `Journals`, `Conferences`, `Books`; language `English`. PRESS revision retains years/language but omits every Content Type refinement.
- **Initial transport check:** a bare curl POST returned HTTP 418 and was treated as an access/challenge response, not zero results. The client used its validated request behavior successfully.

| Pilot ID | Time (UTC) | Exact strategy | Source total | Retrieved | Disposition |
|---|---:|---|---:|---:|---|
| `P-I-A1-count` | 23:36:41 | original pre-spelling-audit `I-A1`; exact query in raw artifact | 4 | count-only | syntax/facets accepted; superseded P block |
| `P-I-A2-count` | 23:36:44 | original pre-spelling-audit `I-A2`; exact query in raw artifact | 2 | count-only | syntax/facets accepted; superseded P block |
| `P-I-B1-count` | 23:36:24 | original pre-spelling-audit `I-B1`; exact query in raw artifact | 38 | count-only | syntax/facets accepted; superseded P block |
| `P-I-B2-count` | 23:36:45 | original pre-spelling-audit `I-B2`; exact query in raw artifact | 42 | count-only | syntax/facets accepted; superseded P block |
| `P-I-V1-count` | 23:36:49 | original pre-spelling-audit `I-V1`; exact query in raw artifact | 1 | count-only | syntax/facets accepted; superseded P block |
| `P-I-O1-count` | 23:36:51 | original pre-spelling-audit `I-O1`; exact query in raw artifact | 4 | count-only | syntax/facets accepted; superseded P block |
| `P-I-A1-full-check` | 23:37:11 | same as `P-I-A1-count` | 4 | 4 | total reconciled; normalized JSON and CSV each passed merge test |

Count-only runs deliberately discarded the one response record. These are dynamic interface counts, not identification or inclusion counts.

## Scopus and IEEE Xplore multi-page API validation

**Status:** completed `pilot_not_candidate_search`; no record was screened, retained as a candidate, or used as evidence. The full reproducibility report is [`2026-08-07-scopus-ieee-multipage-api-validation.md`](searches/subagent-logs/2026-08-07-scopus-ieee-multipage-api-validation.md); non-secret request templates and the reusable reconciler are [`searches/api-pagination-request-templates.json`](searches/api-pagination-request-templates.json) and [`searches/tools/api_pagination_reconcile.py`](searches/tools/api_pagination_reconcile.py).

| Pilot | Run (EDT) | Observed native pagination/order | Source total; retrieved in pass 1/pass 2 | Reconciliation and merge preflight |
|---|---|---|---:|---|
| `P-S-B1-multipage-historical-type-filter` | 10:49:48–10:49:57 | Scopus `count=25`, zero-based `start=0,25,50,75`; `COMPLETE`; `sort=eid`; 25/25/25/5 records; historical `DOCTYPE` clause | 80; 80/80 | all four `startIndex` values matched; 80 unique EIDs; no duplicate/missing page; ordered passes identical; 80 raw/80 unique merge; request superseded for type |
| `P-I-B2-multipage-historical-type-filter` | 10:49:48–10:49:54 | IEEE `rowsPerPage=25`, one-based `pageNumber=1,2`; `sortType=newest`; 25/17 records; historical ContentType facets | 42; 42/42 | 42 unique articleNumbers; no duplicate/missing page; ordered passes identical; 42 raw/42 unique merge; request superseded for type |
| `P-S-B1-multipage-PRESS-unrestricted` | 11:27:45–11:27:56 | corrected final S-B1; no `DOCTYPE`; `start=0,25,50,75`; 25/25/25/10 records | 85; 85/85 | 85 unique EIDs; two ordered passes identical; no retry/missing/duplicate page or ID; 85 raw/84 bibliographically unique merge |
| `P-I-B2-multipage-PRESS-unrestricted` | 11:27:45–11:27:53 | corrected final I-B2; sole facet `Language:English`; `pageNumber=1,2`; 25/22 records | 47; 47/47 | 47 unique article numbers; two ordered passes identical; no retry/missing/duplicate page or ID; 47 raw/47 unique merge |

The delegated historical pilots used the then-current type filters. After MAJOR-01/02/07 corrections, the same audited driver completed fresh broad pilots with spaced-plural/crossed-model variants and no publication/content-type filter; exact prospective request shapes and both generations of pilot descriptors are separated in `api-pagination-request-templates.json`. Both used a 30-second timeout, three retries after the initial attempt for network/408/425/429/5xx failures, `Retry-After` or capped exponential backoff, one permitted clean restart after a changed total, and a hard failure unless all expected pages, unique ordered IDs, matching two-pass order, and `retrieved == source total` hold. Redirect, access/challenge, non-JSON, offset, short-page, duplicate-page/ID, or repeated-total-change conditions are failures, not zero results or partial candidates. The driver strips credential-like fields and IEEE `userInfo`; credentials/cookies/tokens were not written.

The current template SHA-256 is `15087ec37cf4c510fae78583df248c28703a3257365e8e1dea6d73cd4b48a66a`; driver SHA-256 is `be9fd8a5202ddb8ef5fec96855d119d840a8c9fbcbbb1f8393836df594d6801e`. Corrected broad-pilot manifests are `e89596345c9da44c09807b71ba205dd6a350e7de515251b443fdaad045c0a3f9` (Scopus) and `1d475b5e8fd562459c011fc8fc678f8d374b9dc87435b6c50e1a0e0b8b998934` (IEEE). Rerun every final query post-authorization in a clean final-run directory; these pilot records remain superseded and are never candidates.

## PRESS-corrected Scopus and IEEE syntax/count pilots

**Run:** 2026-08-07 11:13–11:28 EDT; all outputs are `pilot_not_candidate_search`. The exact final strings are the displayed blocks in `query-search-plan.md`. No record was screened or retained.

| Source | A1 | A2 | B1 | B2 | V1 | O1 | Final B1 versus old type-restricted B1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Scopus `COMPLETE` | 3 | 10 | 85 | 68 | 1 | 4 | 85 versus 80 (+5) |
| IEEE Xplore | 4 | 6 | 39 | 47 | 1 | 4 | 39 versus 38 (+1) |

Scopus queries retained `LANGUAGE(english)` and explicit `PUBYEAR AFT 2010 AND PUBYEAR BEF 2027` but no `DOCTYPE`; IEEE retained years 2011–2026 and `Language:English` but no ContentType facet. A matched B1 population comparison found no displayed-count change from adding `"nano satellites"` in Scopus (85→85) or adding standalone `nanosat` plus `"nano satellites"` in IEEE (39→39); equal counts do not prove set identity. Both APIs expose no separate automatic stemming/lemmatization request parameter in the frozen route, so no equivalence is inferred and all explicit variants remain.

IEEE's academic client retrieved the complete unrestricted I-B2 set in two pages (25/22; 47/47) and its merge smoke test reconciled 47 raw/47 unique. The generic Scopus academic client reached the source but failed normalization on a null author given-name; this is a client error, not a source failure or zero. The audited reconciler safely handled that value and completed the corrected unrestricted Scopus two-pass 85/85 preflight recorded above. Both source controls include the rest of 2026, so final execution preserves the source total and separately logs records removed after the exact run-day first-formal-publication cutoff.

## ESA Indico interface diagnostics

- **Source/interface:** full public ESA Indico instance; `https://indico.esa.int/export/categ/0.json`
- **Root run:** 2026-08-06 19:23:31 EDT; HTTP 200; 2,512,942 bytes; SHA-256 `cd981bbfbd5e9fac036f790805bb6ea5a0dfab3a77d9b09d063e6262cad30312`
- **Observed root total:** 437 unique events. The root event-ID set exactly equaled the union of child exports 5, 6, and 7; category 9 was a subset of category 6. Child counts were 3, 377, 57, and 1 respectively.
- **Date check:** all 437 root events had parseable start dates; 408 fell from 2011-01-01 through 2026-08-06.
- **Coverage IDs:** 161, 329, 386, 407, and 472 were all present.
- **Contribution-shape checks:** each tested `export/event/{id}.json?detail=contributions` request returned HTTP 200 and one event in `results[0]`; contribution counts must be read from `results[0].contributions`, not top-level `count`. Diagnostic nested counts for the five coverage events were 15, 35, 46, 62, and 15.

This validates the original census and response shape only. The full root/child comparison and all in-window contribution exports must be rerun after authorization.

### PRESS-corrected attachment-first dry run

A complete `pilot_not_candidate_search` ran 2026-08-07 11:05:23–12:11:29 EDT with the frozen dictionary/matcher/fixtures and no metadata gate. It retrieved all 408/408 in-window event exports and parsed 8,394 contributions. Before matching, it inventoried 6,770 material associations and attempted all 5,690 unique document-like URLs: 5,686 retrieved, 5,664 text-parsed, four retrieval failures, and 22 unparseable/no-text coverage failures.

The first matcher pass revealed that event-level attachment text was being inherited by every contribution at the event; those inflated route counts are superseded and were never screened. After correcting the prospective harvester and re-matching the same complete saved census with zero network requests, joined metadata yielded 17 Stream-B subjects; attachment text yielded 62; five overlapped; the union was 74, including **57 attachment-only** subjects. The EPS-explicit tag reconciled as `A∩B=23`, `B-only=51`, and `A-only=0`. These are aggregate matcher diagnostics only and no item was screened or retained. Root IDs again equaled category 5∪6∪7, category 9 remained a subset of 6, and all five known coverage IDs were present.

- Dictionary SHA-256 `1b2416c22840bd780d9b47f3ff81c6fd6466f13d52ee9d2ca7b429161a4232ab`
- Matcher SHA-256 `895d7e8fb333d1ce684cda02e6ca795f6fbc29ee70a16cc894c5d8eaaa0203eb`; fixtures 10/10 passed
- Corrected harvester SHA-256 `78ff39c67371b4948bbae14b9cdbdf2b9b92f54bcd67858a8c35b5ef41e04d2b`; no-network rematcher SHA-256 `ff2d71659089b18c935c636c6ce09bd3b5ae5c6887c247b2dc864e01ff1ada39`
- Corrected rematch output SHA-256 `8d54a4e17f6e2c8e2922ef8a4beae29f87838c664e4e581a55036ba2ea7173b4`
- Active private retained-artifact manifest SHA-256 `ae1aba9681d63237ae33b0896cefb94787c24bc4086aeb40d8fe501ecde3f8e8`
- Detailed report: [`2026-08-07-esa-attachment-first-validation.md`](searches/subagent-logs/2026-08-07-esa-attachment-first-validation.md)

Downloaded pilot binaries were purged after text/checksum derivation for storage/rights minimization; per-attachment status and SHA-256 remain private. The complete final census/match must be rerun after authorization and this pilot union cannot become candidates.

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

## NTRS PRESS-corrected matrix validation

- **Run:** 2026-08-07 11:24:17–11:30:15 EDT; `pilot_not_candidate_search`; no screening, full-text retrieval, candidate classification, or evidence use
- **Specification:** six exact P terms × eighteen exact M terms = **108 mandatory P×M cells**; no Boolean operators, parentheses, fields, or wildcards
- **Date/page body:** `published.gte=2011-01-01`, `published.lte=2026-08-07`, `page.size=100`, zero-based `page.from`
- **Completion:** 108 attempted / 108 HTTP-200 complete / 0 failed; 108 pages reopened and reconciled; 0 retries or total changes
- **Aggregate diagnostic only:** simple overlapping sum 39/39; six unique NTRS IDs; no record screened
- **Normal UI:** representative `CubeSat MBSE`, `nanosat MBSE`, `"nano satellites" "systems modeling language"`, and `CubeSat "object-oriented systems model"` forms were accepted; UI totals are not equated to date-limited API totals
- **Full-E local tag:** dictionary 25/25 E forms and fixtures 10/10 passed; over the six-ID metadata union, `A∩B=1`, `B-only=5`, `A-only=0`, union=6. A is a structural tag, not an additional discovery stream.
- **Artifacts:** detailed report [`2026-08-07-ntrs-revised-matrix-validation.md`](searches/subagent-logs/2026-08-07-ntrs-revised-matrix-validation.md); private 458-entry raw manifest SHA-256 `6a39421df2e5797e47b3b34e67be71330afd7ebf851c02d88862c228a89b1a9a`

The prior 136-cell design and selected nine-term E_N matrix are superseded. After authorization, rerun all 108 complete P×M cells to exhaustion, deduplicate their union, and reapply the frozen full-E matcher.

## Wiley Online Library browser diagnostics

- **Source/platform:** full Wiley Online Library; <https://onlinelibrary.wiley.com/search/advanced>
- **Endpoint:** `https://onlinelibrary.wiley.com/action/doSearch`
- **Browser reports:** [`2026-08-06-wiley-interface-validation.md`](searches/subagent-logs/2026-08-06-wiley-interface-validation.md) and [`2026-08-06-wiley-export-followup.md`](searches/subagent-logs/2026-08-06-wiley-export-followup.md)
- **Observed field:** `Anywhere` / `AllField`; exact uppercase Boolean, groups, phrases, and non-leading wildcards accepted
- **Date controls:** January 2011 through August 2026; source normalizes through month-end, requiring report-level run-date screening

| Pilot ID | Time (EDT) | Exact strategy | Articles & Chapters | Collections | Disposition |
|---|---:|---|---:|---:|---|
| `P-W-A1` | 19:25:08 | original pre-spelling-audit `W-A1`; exact query in browser report | 7 | not recorded | accepted; superseded P block |
| `P-W-A2` | 20:23:50 | original pre-spelling-audit `W-A2`; exact query in browser report | 40 | 2 | accepted; superseded P block |
| `P-W-B1` | 19:27:59–19:28:20 | original pre-spelling-audit `W-B1`; exact query in browser report | 44 | 1 | accepted; three pages; superseded P block |
| `P-W-B2` | 20:24:21 | original pre-spelling-audit `W-B2`; exact query in browser report | 105 | 4 | accepted; superseded P block |
| `P-W-V1` | 19:33:32–19:33:52 | original pre-spelling-audit `W-V1`; exact query in browser report | 17 | 1 | accepted at 690 characters; superseded P block |
| `P-W-O1` | 19:34:23–19:34:43 | original pre-spelling-audit `W-O1`; exact query in browser report | 21 | 1 | accepted; superseded P block |

Pagination is 20 records with zero-based `startPage`. Export is page-scoped; 20 was a tested-safe selection size. Wiley exposed RIS and other citation formats but no native CSV. A normal one-record W-A1 RIS export with abstracts succeeded (SHA-256 `159debf96aeaa0768f578e4cdbee5b804c2342dd2abe8747668337b937f103e9`) and contained one `N2` abstract. `ris_to_merge_csv.py` (SHA-256 `9099bff33f49f4ac27b91ae0ea711825b01d81cd139aed1be9c1682ab98575c1`) produced a 1-row normalized CSV, and `merge_search_results.py` (SHA-256 `ea1098e54f176aae98e75da7f1b4174b5ad138ccbbdd555360c64831e57e6cd4`) preserved Wiley source, exact query, source total, global rank, and 1/1 raw/unique counts. Repeat this export/merge preflight after authorization and never label normalized CSV as native Wiley output.

## Compendex/Engineering Village browser diagnostics

- **Source/platform:** Compendex on Elsevier Engineering Village Expert Search; <https://www.engineeringvillage.com/search/expert.url?database=1>
- **Browser reports:** [`2026-08-06-compendex-interface-validation.md`](searches/subagent-logs/2026-08-06-compendex-interface-validation.md) and [`2026-08-06-compendex-export-followup.md`](searches/subagent-logs/2026-08-06-compendex-export-followup.md)
- **Validated fields/syntax:** `KY` Subject/Title/Abstract, `YR`, `LA`, uppercase Boolean, parentheses, quoted phrases, and explicit wildcards; Compendex-only selected in the UI
- **Final-setting diagnostic:** C-B1 with `AND (2011-* WN YR) AND (({English}) WN LA)`, Relevance, 100/page, autostemming off, no document-type or `WN DB` clause returned 72 at 2026-08-06 20:12:09 EDT. The server summary retained a broad `1884–2026` coverage label, so the final run must also set the UI Published range and audit exported years.

Earlier syntax pilots with autostemming on and `JA|CA|CP|CH` returned C-A1 = 3, C-A2 = 4, C-B1 = 68, C-B2 = 42, C-V1 = 1, and C-O1 = 1. Those settings were superseded by the higher-recall plan and the counts are not identification counts.

A normal one-record CSV Detailed export succeeded after setting Chrome's download behavior. The untouched 29-column native file had SHA-256 `bd5e879e4d13841a7c8a877b8d64d93eebfde628d3ef77ea5af6d22f5145775f`; it omitted exact query and rank. A normalized CSV (SHA-256 `99108152649565600f4794c495ea358549b3845a12f2118aeb83024d1c73c7de`) added common provenance and passed `merge_search_results.py`, preserving Compendex source, exact query, rank 1, and 1/1 raw/unique counts. Pilot record metadata is not retained in the review workspace and must be re-exported after authorization.

## Population-spelling pre-freeze audit

Two detailed reports preserve the 2026-08-07 audit: [`2026-08-07-population-term-audit.md`](searches/subagent-logs/2026-08-07-population-term-audit.md) for browser sources and [`2026-08-07-api-population-term-audit.md`](searches/subagent-logs/2026-08-07-api-population-term-audit.md) for IEEE/NTRS and the initial-failure/successful-retry Scopus API checks. No record was screened, exported from the browser sources, retained as a candidate, or used as evidence.

- **Compendex:** under matched final controls with autostemming off, original C-B1 = 72 and revised C-B1 = 76 (+4). Revised C-V1 = 1 and C-O1 = 1. The revised block explicitly adds `cubesats` and `"nano-satellites"` and supersedes the original P block.
- **Wiley:** original versus revised W-B1 remained 44 Articles & Chapters and 1 Collection; revised W-V1 = 17 plus 1 Collection and W-O1 = 21 plus 1 Collection. The added phrase was accepted; equal totals do not establish set equivalence.
- **Scopus:** under matched normal-web-UI controls, original S-B1 = 75 and revised S-B1 = 80 (+5). The initial API recheck failed authentication; empty shells written with `total: 0` are invalid and are not source results. After institutional network access became available, the `COMPLETE`-view API retry successfully reproduced 75 and 80. Final Scopus execution still requires a fresh post-authorization authentication preflight.
- **IEEE Xplore:** original and revised I-B1 both returned 38; revised I-V1 = 1 and I-O1 = 4. The complete revised population block was accepted; equal totals do not establish set equivalence.
- **NTRS (superseded matrix decision):** the first 56-cell diagnostic tested eight population spellings against seven then-planned `M_N` terms and found source-unique yield for `CubeSats`. PRESS review subsequently identified omitted frozen P/M terms. The 136-cell P/E/M design is retired; the corrected mandatory baseline is 108 complete P×M cells (six P × eighteen M), followed by a full-E local tag over the deduplicated union.

Those population-audit expressions were later superseded by the PRESS corrections adding bare IEEE `nanosat`, spaced plural `"nano satellites"` everywhere, and the complete NTRS P/M matrix. The exact corrected implementations and fresh pilots are logged below; every strategy must still be rerun after authorization.

## PRESS-corrected browser-source pilots

**Runs:** 2026-08-07 11:21–12:19 EDT; all are `pilot_not_candidate_search`. Exact strings were byte-for-byte extracted from the final WS/C/W blocks. No record was screened, retained, or used as evidence.

| Source | A1 | A2 | B1 | B2 | V1 | O1 |
|---|---:|---:|---:|---:|---:|---:|
| WoS Core Collection | 1 | 0 | 43 | 34 | 1 | 1 |
| Compendex | 3 | 6 | 76 | 58 | 1 | 1 |
| Wiley Articles & Chapters | 7 | 46 | 44 | 103 | 17 | 21 |
| Wiley Collections | unresolved/not zero | 2 | 1 | 4 | 1 | 1 |

**WoS controls:** Basic/Topic; Core Collection; Editions All with all ten available indexes; Publication Date 2011-01-01–2026-08-07; English; no Document Type; Relevance and 50/page where results existed. The clean WS-A2 execution displayed `Your search found no results`, validating zero after two earlier navigation failures. Final unrestricted WS-B1 and the old three-type-restricted comparator both returned 43; no equivalence is inferred. Final B1 versus removal only of `"nano satellites"` was also 43→43. Advanced `Exact search` was observed unchanged at `aria-checked=false`; no stemming/lemmatization meaning was inferred. A fresh ordinary non-Fast-5000 unrestricted WS-B1 RIS range 1–1 completed (391 bytes; SHA-256 `cc7bf2061a2f9181d25a86008a1182da46c132f51b6aec83cf30103fe378de75`).

**Compendex controls:** Compendex only; Published 2011–Latest plus the literal `YR`/English suffix; autostemming OFF; Relevance; 100/page; no type filter. Final B1 versus removal only of `"nano satellites"` was 76→76. C-B1/B2 fit one page. Preserve the source total and apply the exact run-day publication cutoff after export.

**Wiley controls:** whole platform; one AllField row; January 2011–August 2026; no type/language/venue/OA facet. Final B1 versus removal only of `"nano satellites"` remained 44 Articles & Chapters and one Collection. W-B2 reconciled page 6 with three cards at 20/page against 103. The source rendered sort `Date`; final execution records the actual declared sort and separately removes records after the exact run day because the source range extends through month-end.

Detailed report: [`2026-08-07-press-browser-source-validation.md`](searches/subagent-logs/2026-08-07-press-browser-source-validation.md). Private manifests: `5c98bffe52e4aaa46ea15437aad538fa9dbcf0414c0a29c8eb9d77a714f086e5` (27-file main browser pilot) and `0e516843d2e40bf4aae949e94f641de442613f79cd08c6577c483a5f03f7c3bc` (16-file WoS follow-up).

## Prospective citation-chasing platform decision

**Decision date:** 2026-08-07, before freeze and before any valid citation search. No citation-chasing event was executed for this decision.

- Backward chasing will inspect each seed report's complete full-text reference list; indexed reference exports are aids, not substitutes.
- Forward chasing will search **both Scopus and Web of Science Core Collection** for every included report and relevant secondary-review seed. Scopus uses its normal record/`Cited by` interface; WoSCC uses `Citing Articles` and Cited Reference Search with all available Core Collection editions.
- If a seed is not indexed, use DOI/title/cited-reference searching where the platform supports it and log the exact route. A zero result or failure in one platform never waives the other.
- Log seed, direction, platform, exact route, cycle, dates, source/retrieved totals, candidates, duplicates, decisions, failures, and stopping result. Retain `discovery_route=citation_chasing` separately from bibliographic source.
- Newly included reports become next-cycle seeds. Stop only after a complete backward and dual-platform forward cycle yields no new eligible report. Google Scholar and Semantic Scholar are not fallback citation indexes.
