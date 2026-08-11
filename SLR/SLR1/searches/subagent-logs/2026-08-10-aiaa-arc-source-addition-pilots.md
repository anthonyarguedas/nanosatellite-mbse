# AIAA ARC source-addition and fast-browser pilots

**Date:** 2026-08-10  
**Classification:** `pilot_not_candidate_search`; prospective source/interface and aggregate-speed validation only  
**Protocol boundary at pilot time:** protocol version 1.3 still named the original seven sources; these pilots supported the prospective AIAA source amendment before any valid final discovery  
**Current disposition:** version 1.4 now authorizes the eleven-database/collection, ten-interface plan; these original pilots remain non-candidate diagnostics

## Guardrails and delegation

Five read-only subagent jobs were used: direct-HTTP reconnaissance, source-method design, a normal-browser query pilot, a focused `pageSize=100` follow-up, and an adaptive page-size benchmark. They did not edit the checkout. No result title, author, abstract, snippet, identifier value, URL, full text, relevance, eligibility, or prior corpus was inspected. Only source controls, exact submitted expressions, aggregate totals, page/cardinality state, timing, and the existence—not values—of identifiers/export controls were observed. Nothing below is a candidate or final discovery event.

Prompts, stdout, empty stderr files, and exit statuses are retained in the Git-ignored `.searches/eps-mbse-slr-2026/aiaa-arc-pilots/2026-08-10/subagents/` archive. Its 20-file `manifest.json` has SHA-256 `c1449a468949a3ab4c35d0f072170207c5370a48d09f945b3a24e5d6d600252b`.

## Source/interface observations

- Current source: **AIAA Aerospace Research Central (ARC)**, <https://arc.aiaa.org/>; no successor-host redirect was observed.
- Normal Advanced Search: <https://arc.aiaa.org/search/advanced>; browser-generated endpoint: `https://arc.aiaa.org/action/doSearch`.
- Broad field: **Anywhere** / `AllField`; other visible fields included Title, Author, Keywords, Abstract, and Affiliation.
- Accepted in the normal browser: uppercase `AND`/`OR`, parentheses, quoted phrases, and trailing wildcards. Acceptance does not establish wildcard or stemming semantics.
- Common pilot controls: January 2011 through August 2026; default **All content** (`access=on`); no language, publication-type, venue, topic, author, or OA restriction.
- The month-granular upper bound rendered as 2026-08-31. A final run must preserve the source total and separately remove/log first-formal-publication dates after the exact run day.
- Default sort was Relevance. Source-exposed page sizes were 20, 50, and 100; pagination was zero-based `startPage`.
- Result rows exposed nonempty `doi` selection fields without identifier values being read. A native **Export Citations** control was visible but was not invoked; format and batch limits remain unknown.
- A direct non-browser `GET https://arc.aiaa.org/` at 2026-08-10T19:53:36Z returned a Cloudflare-mitigated HTTP 403 in 0.034 seconds. This was an access failure, not zero. Static HTTP is not an accepted ARC route.

## Initial normal-browser aggregate pilot

The exact strings are the `ARC-A1`, `ARC-B1`, and `ARC-B2` expressions recorded in `query-search-plan.md`; the pilot used the same terms, with Boolean-equivalent OR-term ordering.

| Pilot | Timestamp (EDT) | Status | Source total | Pages at 20 | Timing evidence |
|---|---|---|---:|---:|---|
| `P-ARC-B1` | 15:54:45 | accepted normal result state | 308 | 16 | form-dispatch timing invalid for end-to-end use |
| `P-ARC-B2` | 15:56:55 | accepted normal result state | 820 | 41 | form-dispatch timing invalid for end-to-end use |
| `P-ARC-A1` | 15:58:56 | accepted normal result state | 108 | 6 | direct GET to semantic readiness: 7.750 s |

The totals cover the source's month-end date range and are dynamic pilot aggregates only. No page was enumerated for candidate creation.

## Focused 100-per-page follow-up

At 2026-08-10T16:08:18.924-04:00, the exact finite `I-A2` expression was submitted unchanged as `ARC-A2-finite` with `pageSize=100`. It reached the prespecified 20-second semantic-readiness deadline at 20.002 seconds. Total and card count are `null`; this is a failed pilot, not zero. The planned finite B2 and BT2 follow-ups, page 2, sort inspection, and export inspection were not run after the hard stop.

## Page-size benchmark

A final browser subagent reused one tab and precompiled normal-interface GET URLs. All four count states completed under the 20-second deadline:

| Query | Timestamp (EDT) | Page size | Count-ready | Source total | Provisionally rendered cards |
|---|---|---:|---:|---:|---:|
| `ARC-A1-finite` | 16:16:07.874 | 20 | 3.649 s | 108 | 20 |
| `ARC-A1-finite` | 16:16:11.562 | 50 | 5.117 s | 108 | 22 |
| `ARC-A1-finite` | 16:16:16.703 | 100 | 5.948 s | 108 | 24 |
| `ARC-A2-finite` | 16:16:22.661 | 20 | 4.413 s | 699 | 15 |

`pageSize=20` was the fastest measured count route. Only the A1/20 state rendered its full expected 20 rows at the first asserted state; 50/100 were visibly partial/lazy, and the provisional A2 row selector returned 15 rather than 20. Therefore 50/100 are rejected for final enumeration unless a later logged hydration contract proves every expected row, and count readiness alone is not page-completeness evidence. Final pagination starts at 20/page and must additionally poll/assert exactly `min(20, total - 20*startPage)` stable row/DOI selectors. A short nonterminal page is a failure, not a speed optimization. Equal A1 totals for finite and wildcard-bearing pilots do not establish set equivalence.

## Accepted fast execution architecture

1. Use the normal browser route, one named process, and one persistent ARC tab; do not use curl/static HTTP or parallel ARC tabs.
2. Precompile exact query/control URLs. Once selector state is established, use deterministic navigation and DOM assertions with no model turn, screenshot, or fixed sleep per page.
3. Require a new page matching the requested query/control plus `.search-result__nav`, `.search-result__body`, `Search Results (N)`, and the expected stable row/DOI-selector count. A challenge, access wall, stale or short page, absent state, query rewrite, or timeout is failure with total `null`.
4. Use the measured page-size policy above rather than assuming the nominal maximum is fastest. Preserve page size and timing per query.
5. Mechanically paginate from `startPage=0`, preserve global rank and stable IDs in final execution, enforce a stable source total, and perform a second ordered pass. Pilot aggregates cannot be reused.
6. First validate one-record native citation export, normalization, and merge. Never substitute an external index for ARC discovery.

## Remaining gates at pilot close and later disposition

- Protocol synchronization is complete in version 1.4, but every final `ARC-*` strategy still requires a clean authorized run.
- Later off-topic adapter gates validated the per-record RIS route and complete three-page/two-pass retrieval mechanics; see `search-log.md`. Unpiloted final expressions, any actually encountered DOI-less fallback, and final exact-day/language screening remain final-run gates.
- Treat any future Cloudflare/access state, malformed/rewritten query, unavailable total, incomplete pagination, or changing snapshot as a source failure, never zero.
