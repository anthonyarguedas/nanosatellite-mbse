# IEEE Xplore diagnostic pilot observations

- **Pilot:** `S-D03-P01-20260821T003654-0400`
- **Task/source:** `S-D03` / IEEE Xplore
- **Protocol commit:** `ad77460df82764312fb701f6be4ebf7eb5051c41`
- **Status:** **blocked**; diagnostic only; not accepted.
- **Scope guard:** no IEEE source query, source page, result card, record, title, abstract, stable ID, DOI, export, screening, relevance assessment, candidate construction/import, full-text retrieval, PDF download, final event, or final-event write occurred.

**Claim labels:** **observed**, **official_documentation**, **inferred**, and **untested**. Every source-interface behavior that was not visible in a normal owned IEEE tab is labelled untested.

## Browser/access disposition

- **observed — blocked:** At `2026-08-21T00:36:54-04:00`, the local browser harness doctor found Chrome and its daemon running but reported **`[FAIL] active browser connections — 0`**. The safe ignored diagnostic is `E-001` in [evidence-index.json](evidence-index.json); SHA-256: `c94afc450dd14a81303b2b089d59a627300b02108173f05ef71d0e97262ab5f9`.
- **observed:** No source tab or request was made after that access finding. No retry, login, credential entry, cookie access, CAPTCHA/challenge action, direct endpoint call, fresh/headless browser, target ID, existing-tab inspection, saved-result URL, or full-text action occurred.
- **inferred:** The academic-search adapter documentation says it is intended to create an owned tab and use the normal rendered IEEE UI. That tool description is recorded as `E-002`; it is not proof of a current IEEE interface or access state.
- **untested:** Whether the user’s reported institutional sign-in is active or relevant; no rendered IEEE source evidence was obtained.

## Boundary, grammar, controls, and capture

- **official_documentation — review protocol:** The protocol designates IEEE Xplore as a bibliographic and full-text database. This does not prove the live platform/database boundary or the default search scope.
- **untested:** Normal default field/scope; visible database/source controls; query entry/echo/rewrite; Boolean/phrase/grouping; punctuation/hyphens; case/acronyms; expansion/stemming/lemmatization; wildcard behavior including `nanosat*`; term/query limits; visible Year/date precision; language; no-restriction state; totals/explicit zero; page size/ranges/pagination/order; document route/article number/DOI; duplicate behavior; capture/export; caps; and two-pass completeness.
- **observed:** The local draft deliberately uses no field wrapper, no wildcard, no `SmallSat`, no date syntax, no language filter, and no content-type/access/peer-review/venue/subject/publication-type restriction. This is local text construction, not source behavior.
- **untested:** `P-001` has not supplied a common upper cutoff. The pilot did not test the required 2011 lower bound, a diagnostic future sentinel, unbounded comparison, or whether IEEE date controls are year-only or exact-day.

## Local translation and partition coverage

- **observed:** `translation-integrity.json` verifies all eleven UTF-8/BOM-free/LF-terminated local files against the normative dictionary checksum and finds no missing required literals, no wildcard, no prohibited `SmallSat`, balanced parentheses, and matching SHA-256 values.
- **inferred:** The normal-input text uses explicit `AND`/`OR`/parentheses and same-query Boolean conjunctions for dictionary pair rules. It preserves the protocol terms and Boolean schedule locally but does not establish IEEE’s source grammar, pairing semantics, or default field scope.

| Partition | Cell | Local structural status | IEEE source validation | Source total |
|---|---|---|---|---:|
| A1 | `A1-C1` / `queries/A1.txt` | observed pass | blocked / untested | null |
| A2 | `A2-C1` / `queries/A2.txt` | observed pass | blocked / untested | null |
| A3 | `A3-C1` / `queries/A3.txt` | observed pass | blocked / untested | null |
| B1 | `B1-C1` / `queries/B1.txt` | observed pass | blocked / untested | null |
| B2 | `B2-C1` / `queries/B2.txt` | observed pass | blocked / untested | null |
| BG1 | `BG1-C1` / `queries/BG1.txt` | observed pass | blocked / untested | null |
| BG2 | `BG2-C1` / `queries/BG2.txt` | observed pass | blocked / untested | null |
| BC1 | `BC1-C1` / `queries/BC1.txt` | observed pass | blocked / untested | null |
| BT2 | `BT2-C1` / `queries/BT2.txt` | observed pass | blocked / untested | null |
| V1 | `V1-C1` / `queries/V1.txt` | observed pass | blocked / untested | null |
| O1 | `O1-C1` / `queries/O1.txt` | observed pass | blocked / untested | null |

## Required focused follow-up

1. Restore the authorized loopback Chrome connection without sharing credentials, cookies, existing-tab URLs, or session/search URLs. Stop again if login, entitlement, challenge, CAPTCHA, unusual traffic, or inaccessible-browser state appears.
2. In one new adapter-owned normal IEEE tab, prove the platform/default scope, visible controls, exact query echo, exact total/range, and explicit-zero behavior with count-only diagnostics.
3. Test Boolean/phrase/grouping, punctuation/hyphen, case/acronym, expansion, wildcard, source limits, date precision, and language controls before changing any translation. Keep finite P forms unless an exhaustive fixed-scope stable-ID comparison establishes that `nanosat*` is lossless and adds no unapproved meaning.
4. Run every complete partition count-only. If a demonstrated source limit requires cells, predefine every cell and reconcile a lossless stable-article-ID union; do not narrow or drop a cell.
5. Only if needed for identity/capture proof, make one tiny retained-record `--skip-full-abstracts` diagnostic under the ignored S-D03 worklog, then validate page/range/order/article-number/detail/DOI/export behavior and two full source-ID passes before a future final event.

No protocol semantics changed. The future final run remains blocked on `P-001`, `R-002`, a successful current-interface preflight, and supervisor approval.
