# S-D11-X01 arXiv Advanced Search diagnostic

**Receipt:** released / `cleanup=verified-clean`  
**Mode:** X diagnostic only; not an evidence, pilot, final-search, screening, import, gate, or final event.

## One bounded operation

- One normal rendered arXiv Advanced Search GET was issued; start was zero and no pagination or `More` action was used.
- The exact simple-sentinel check passed (7 UTF-8 bytes; SHA-256 `f4d8581ea796810254a292e207a7e3f680c3b60f6d41ca16d9ec7f5a68225023`).
- The rendered route/query booleans were true. Visible controls were reconciled as All fields, submitted-date range 2011–2026, submitted-date type, classification all, cross-list include, Show abstracts, page size 25, and empty-order Relevance.
- No challenge, login, bad-request, busy, or access category was observed.

## Restricted aggregate observation

- State: positive parser-reconciled snapshot.
- Total: 470; null: false; zero: false.
- Native heading aggregate: one range heading; displayed range 1–25; rendered row count 25.
- Identity-candidate count: 25; malformed: false; duplicate: false.
- Next was enabled with one target count. No next-page operation occurred.
- No row fields, identifiers, versions, titles, authors, abstracts, DOI/PDF/abstract routes, URL/query string, DOM, cookies, or session data were retained outside the mandated restricted viewport screenshots.

## Boundary and cleanup

- Exactly one fresh Playwright-owned page was created in the sole context, then closed; owned-page closure was verified.
- Baseline preservation was verified by non-interference: no baseline page was inspected, navigated, or closed.
- No records were retained; no screening, import, gate, final event, campaign/P/shared edit, or agent-tools patch occurred.
- Pinned agent-tools commit: `aa10b5f885a20603f3fef0c77bbb9cf2ab45b6a7`. The adapter was not invoked. Only `build_search_url`, `ARXIV_SEARCH_STATE_SCRIPT`, and `parse_arxiv_page` were imported from `search_arxiv.py` (SHA-256 `c794026802ab00365214f5dcf470ef848ec97ffa4a0750de777f083849a2356c`).

## Freeze and later review

One simple-sentinel health-capability diagnostic operation is frozen, limited solely to this observed control-and-parser reconciliation. It creates no acceptance decision and is not campaign evidence, a pilot, or a final search.

| Review cell | Status |
| --- | --- |
| Field semantics | Deferred to later X→P |
| Exact date/version | Deferred to later X→P |
| Metadata/abstract | Deferred to later X→P |
| Identity | Deferred to later X→P |
| Pagination/completeness | Deferred to later X→P |
| Controlled vocabulary | Deferred to later X→P |
| Pairs | Deferred to later X→P |

The canonical lease receipt SHA-256 is `b2b47cb37180f3b40223018c3af29fc554d0b93fd1e38cb4736a1490e1fdfb49`; one inert anchor remained, no orphan survived, and exact-window checks found no Sleep/Wake/DarkWake or System Information/About This Mac launch. Restricted artifact hashes and byte counts are indexed in `restricted-evidence-index.json`.
