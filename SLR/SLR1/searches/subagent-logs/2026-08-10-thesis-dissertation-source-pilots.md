# Thesis/dissertation source amendment pilots — 2026-08-10

**Review run:** `eps-mbse-slr-2026`  
**Status:** `pilot_not_candidate_search`  
**Protocol effect:** prospective version-1.6 method validation only

## Non-candidate boundary

The orchestrator delegated source/method checks to isolated internet-enabled subagents and performed bounded follow-up checks. Completed pilots were restricted to source identity, form/query syntax, controls, aggregate totals, and mechanical row/range reconciliation. Every completed report confirms that no title, author, abstract, snippet, identifier value, record URL, full text, export, relevance decision, or eligibility decision was inspected; no such content was preserved or imported. A later canceled B2-only runner returned no report, so this log makes no claim that it reached source navigation and accepts no source data from it. Dynamic aggregates below are not final discovery counts. Every version-1.6 strategy must be rerun from clean final storage or receive an explicit fail-closed final-source disposition.

## Method and source-taxonomy review

A read-only methods subagent reviewed PRISMA-S, PRISMA 2020 flow guidance, Cochrane Handbook chapters 4 and 5, first-party PQDT documentation, and the OATD site/FAQ. It recommended:

- admitting completed master's-level theses and doctoral dissertations/theses under all ordinary scientific and full-report rules;
- treating PQDT Global as a separately searched named database on the ProQuest Platform;
- treating OATD as a separately searched indexed online resource and reporting it in the PRISMA website/other-methods channel;
- using an operational baseline of 14 sources/collections through 12 interfaces, including 10 direct source/query families and 110 logical direct strategy blocks;
- retaining date provenance, retrieval/embargo state, source overlap, and thesis-to-article report-family relations without double counting; and
- carrying all incomplete earlier gates into one cumulative version-1.6 pre-final register.

This was model-assisted review, not formal PRESS peer review by a human information specialist.

Method/source references consulted:

- PRISMA-S: <https://doi.org/10.1186/s13643-020-01542-z>
- PRISMA 2020/PRISMA-S flow guidance: <https://pmc.ncbi.nlm.nih.gov/articles/PMC9014944/>
- Cochrane Handbook, chapter 4: <https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04>
- Cochrane Handbook, chapter 5: <https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-05>
- PQDT Global: <https://about.proquest.com/en/products-services/pqdtglobal/>
- OATD and FAQ: <https://oatd.org/> and <https://oatd.org/faq.html>

## PQDT Global

### Source research and isolated-browser failures

First-party source documentation confirmed the current product name, dissertation/thesis scope, `NOFT` field, Boolean/phrase/range syntax, and normal ProQuest result controls. The normal product entry is <https://www.proquest.com/pqdtglobal/advanced>.

Two isolated-profile probes were challenge-blocked before exact database-selection proof or query submission:

| Probe | UTC interval / elapsed | Disposition |
|---|---:|---|
| Fresh Playwright Chrome | 2026-08-11 00:16:23–00:16:47 / 23.555 s | `access_challenge`; total `null` |
| Separately launched fresh Chrome/profile | 2026-08-11 00:18:28–00:18:31 / 2.713 s | `access_challenge`; total `null` |

An offline A1/B1/B2 query-contract preflight verified only construction invariants: one `YR(2011-2026)`, one `LA(English)`, and planned concept blocks under `NOFT`. It was not a live syntax test. The existing ProQuest aerospace adapter's 15/15 offline tests passed as a design-pattern check only; they do not validate PQDT selectors, limits, pagination, or export.

### Normal-browser aggregate follow-up

A later owned-tab follow-up reached the licensed normal interface and verified exactly one selected source: **ProQuest Dissertations & Theses Global** (the interface appended “Full Text Included” to the database label). No all-databases, PQDT Open, institution-specific, or other ProQuest source was selected. The separate Full text limiter was unchecked.

Common observed controls were Relevance, 20 records/page, source-side duplicate exclusion off, no full-text/peer-review/source-type/document-type limiter, and automatic spelling plus plural/adjective variants on. The expansion state was recorded rather than interpreted as exact set equivalence.

| Pilot | Local start (UTC−04:00) / UTC start | Elapsed | Aggregate | Query echo |
|---|---:|---:|---:|---|
| `PQDT-A1` | 20:41:05.427 / 00:41:05.427 | 0.780 s | 1 | exact |
| `PQDT-B1` | 20:30:58.028 / 00:30:58.028 | 1.345 s | 17 | exact |
| `PQDT-B2` | 20:31:32.738 / 00:31:32.738 | 1.113 s | 9 | exact |

The B1/B2 echoes exactly matched their planned `NOFT(...)`, `YR(2011-2026)`, and `LA(English)` bodies. Counts came only from the dedicated aggregate control. Exact source selection remained unchanged after the runs. No result card was inspected.

**Pilot conclusion:** the exact-PQDT-only normal interface and three representative complete strings are viable for prospective use. Final readiness remains open because complete pagination/ordered stable IDs, exact-day accounting, native RIS limits/content, normalization, and two-pass reconciliation were not tested. A future adapter must be PQDT-specific and fail closed; it must not expose arbitrary database selection or inherit aerospace-Index limits/selectors without a live gate.

## OATD

### Interface and syntax checks

The normal interface loaded at <https://oatd.org/> without a challenge in an owned browser tab. The basic form uses GET `https://oatd.org/oatd/search` with one `q` value. The advanced composer exposed four Boolean rows (`AND`, `OR`, `PHRASE`, `NOT`), any-field/title/author/abstract/publisher/subject/discipline choices, `earliest`/`latest` year boxes, language/country selectors, Relevance, 30/60/100 page sizes, and a Creative-Commons-only control. No degree-type control was observed.

| Check | Local start / UTC start | Elapsed | Aggregate and mechanical reconciliation |
|---|---:|---:|---|
| Basic exact phrase `"cube sat"` | 20:35:37.429 / 00:35:37.429 | observation loop 21.751 s | 12; 12/12 first-page containers |
| Basic grouped Boolean `("CubeSat" OR "CubeSats") AND ("MBSE" OR "SysML")` | 20:37:08.301 / 00:37:08.301 | 2.251 s | 18; 18/18 first-page containers |

Both responses displayed an exact query echo. No container content was read.

At 20:38:23.834 local / 00:38:23.834 UTC, an advanced-composer baseline returned `Server Too Busy - Please slow down` after 20.180 s. Its total is `null`, not zero. Direct HTTP/fresh-browser orchestrator probes were separately blocked by Cloudflare. An archived OATD home/form snapshot was used only to corroborate visible form structure, not to obtain records or aggregates.

### Cooldown retry

A separate rate-limited owned-tab retry submitted the complete finite planned `OATD-B1` expression through the validated basic interface:

| Pilot | Local / UTC interval | Elapsed | Aggregate | Query/range result |
|---|---:|---:|---:|---|
| `OATD-B1` | 20:49:08.203–20:49:10.857 / 00:49:08.203–00:49:10.857 | 2.654 s | 23 | exact echo; “1–23 of 23”; 23 mechanical rows; no pagination |

`OATD-B2` was not run: the owned tab failed its state assertion because it had closed before wait/navigation. Its pilot total remains `null`; this is not a zero or evidence of source rejection. A1 was not attempted in that retry. A later focused B2-only internet subagent produced no stdout, stderr, or source-state report within 15 minutes and was canceled by the orchestrator. The timeout supplies no source result or syntax evidence; B2 remains `null`, no partial state is imported, and no claim is made about whether a source navigation occurred.

**Pilot conclusion:** the basic GET route supports quoted phrases, grouped uppercase Boolean logic, the complete finite B1 expression, exact query echo, and aggregate/range reconciliation. The version-1.6 plan therefore uses explicit finite forms with no assumed wildcard semantics and local date/language screening. Final readiness remains open pending full B2 re-proof, all eleven expressions, source-total/30-row/pagination/stable-identity checks, two complete passes, exact-day handling, repository-link provenance, and normalization/merge reconciliation. A busy/challenge/hidden-cap/unstable-identity state fails closed with total `null` and no partial import.

## Preserved artifacts

Non-secret pilot artifacts are retained, owner-restricted and Git-ignored, under:

`.searches/eps-mbse-slr-2026/theses-dissertations-amendment-pilots/2026-08-10/`

The deterministic manifest indexes 71 files; its SHA-256 is `3a60a106975f125dc1effc4769e67f6663b7f306b86be4344c955d098bb17210`. It includes subagent prompts/stdout, PQDT source-research captures and bounded probes, OATD interface research, and orchestrator follow-up provenance. It contains no candidate corpus and must not be supplied to screening. A separate read-only consistency subagent then found no material version-1.6 contradiction or omission; its report is preserved in the same non-candidate archive.
