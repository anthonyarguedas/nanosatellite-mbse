# Browser-search acceleration and execution-interface policy

**Date:** 2026-08-10  
**Scope:** implementation and aggregate-only speed diagnostics  
**Classification:** `pilot_not_candidate_search`; no screening or candidate creation

The work used parallel architecture, API-feasibility, historical-interface, live Wiley, live Web of Science, Compendex implementation, and code-review subagents. Live diagnostics inspected controls, aggregate totals/cardinality, timings, and transient IDs only where needed for reconciliation. No title, abstract, author, full text, eligibility, relevance, or scientific content was inspected. These speed tests were not added as formal search events in `search-log.md`.

## Outcome

| Source | Acceleration outcome | Acceptance boundary |
|---|---|---|
| Wiley Online Library | Added a deterministic browser-harness helper and website contract. One process/tab performs direct documented GET pagination and two complete ordered passes without model decisions between pages. | Accepted for aggregate/DOI enumeration. Native page-scoped RIS export, exact-day filtering, normalization, and export-to-ledger reconciliation remain separate final-run steps. |
| Compendex | Restored the missing `search_compendex.py` source with a fixed Expert-mode state machine, 100/page verification, normal same-origin RIS retrieval, strict ID/export checks, and offline fixtures. | Accepted as a live-smoked generic bounded client; defaults may intentionally return `partial`. It is not yet the review-specific exhaustive two-pass/native-export runner. |
| Web of Science Core Collection | Recovered a current semantic selector bundle and fast control/page state machine. Page navigation itself is now cheap. | Do not accept deterministic record enumeration yet: cards lazy-load 20→40→50 and no uniform stable DOM accession attribute was validated. Use the playbook for fast controlled submission/counts; retain normal RIS/range reconciliation or manual operation for final export. |

The main speed gain is architectural: keep one browser-harness/Playwright process and one dedicated tab alive for the whole source job, navigate pages mechanically, and make every state transition an assertion. Repeated LLM reasoning was slower and less reproducible than source retrieval. The integrated reusable-tool state is agent-tools commit `f6bd33a` (following the Wiley helper and Compendex restoration commits `a5c783e` and `7e346f2`).

## Wiley implementation and benchmark

Reusable code is in the browser package:

- `internet/skills/browser/site_search_helpers.py`
- `internet/skills/browser/agent_helpers.py`
- `internet/skills/browser/domain-skills/academic-publishers/wiley-online-library-search.md`
- `internet/tests/test_site_search_helpers.py`

`wiley_collect_search(...)` freezes `AllField`, month-granular dates, Articles & Chapters, 20/page, native page identity, and an explicit sort. It rejects access/challenge/syntax states, parameter rewrites, wrong tab/page, missing IDs, short nonterminal pages, duplicate/repeated IDs, changed totals, and disagreement between two ordered passes. A verified zero requires Wiley's native no-result element. Concurrent jobs must use distinct `BH_NAME` values.

Live aggregate-only diagnostics:

| Diagnostic | Complete work | Elapsed |
|---|---:|---:|
| Verified zero | two one-page passes | 5.36 s |
| Six-result one-page set | two passes, 6/6 unique | 5.23 s |
| 125-result multipage set, explicit `sortBy=Earliest` | 7 pages × 2 passes; 125/125; identical order | 56.99 s |

A useful failure was found: default Relevance retained aggregate total 125 but shifted records over page boundaries, producing repeated DOI IDs and only 122–124 unique IDs in diagnostic crawls. The helper failed rather than silently accepting the short set. Wiley's Date link is the documented `sortBy=Earliest` route; it yielded 125 unique IDs in one pass and two identical 125-ID passes in the full benchmark. Use explicit Earliest for deterministic enumeration and record it as the changed source sort. If a run must retain Relevance, the same strict checks should be allowed to fail.

The helper deliberately leaves native citation export separate. Wiley exports the visible page (tested safe at 20); preserve each native RIS privately, normalize with the cumulative page-ledger rank, and apply/log the exact run-day cutoff because Wiley's source upper date is month-end.

### Follow-up Wiley latency iteration

A second subagent round examined the 56.99 s broad-run latency without changing the accepted helper. Static profiling attributed at least 8.4 s of that run to known local sleeps: 4.9 s from the 0.35 s two-observation stabilization interval and 3.5 s from the 0.25 s page delay. The remaining approximately 48.6 s includes source navigation/rendering plus load and IPC polling. Removing duplicate `readyState` waiting could reduce serial latency, but ordinary server rendering remains the dominant component.

A reproducibility review conditionally accepted bounded regular visible Chrome tabs, but only when each pass independently starts at page zero, discovers its own extent, visits every normal UI page, disposes pass-one tabs before pass two, and preserves exact ordered reconciliation. It rejected same-origin detached `fetch()`, cached-response replay, or reparsing pass-one HTML as substitutes for independent source observations. With three tabs, seven pages have a theoretical scheduling ceiling near 2.33× versus fourteen serial navigations; this is a model, not a measured speedup.

Two isolated, unmerged prototypes were produced: serial semantic-readiness commit `4649a08` (17 offline tests) and bounded visible-tab commit `0bc3726` (15 offline tests). Independent reviews blocked both from integration. The serial prototype changed pacing to zero, lacked owned-tab/pass cleanup, and did not enforce one hard navigation deadline. The parallel prototype became an unvalidated three-tab default, needed transient execution-context handling, interacted incorrectly with the harness daemon's global title/session handoff, and retained selector assumptions not proved for zero/single-page states. Both branches remain reversible prototypes; agent-tools `main` remains at the previously live-validated `f6bd33a` state.

The sole follow-up live profiler encountered Wiley's access/challenge signal before collecting timing or page-size evidence. It stopped immediately, closed its tab, stopped its named daemon, and made no retry, fetch, page-size request, or repository edit. No result content was inspected. Consequently no faster timing is claimed. After a user restores normal browser access, acceptance requires conservative serial revalidation first, followed by opt-in cap-2/cap-3 comparison against the same 125/125 two-pass Earliest tuple; any challenge, selector drift, total change, or ordered-ID mismatch stops the attempt.

After normal results were reported in a browser, one conservative retry in the automation-attached Chrome failed with `BrowserSearchError` after 0.512 s and returned no total, pages, IDs, or timing evidence; it was not retried. A no-navigation follow-up then found no already-open Wiley target in that CDP profile, so it could not distinguish a genuine challenge from the known over-broad body-text challenge detector or another contract failure. The next live gate requires leaving a normal Wiley result tab open in the dedicated local automation Chrome (`127.0.0.1:9222`) before any search navigation. A local-evidence audit also found no visible Wiley control or UI-generated capture for `pageSize=50` or `100`; manually forcing those parameters is therefore not an accepted `web_ui` acceleration route.

Second-generation isolated commits `3efb5a5` (serial lifecycle/deadline prototype; 28 offline tests) and `ceb7aaf` (opt-in bounded prototype while preserving the parent serial entry point; 26 offline tests) addressed several first-review findings but remain unmerged. Independent reviews still blocked live use on final-target handoff/schema compatibility, structural challenge detection, selector ambiguity, confirmed target cleanup, hard IPC deadlines, daemon session/marker edge cases, and positive single-page tab handling. The validated agent-tools `main` remains unchanged at `f6bd33a`.

A later no-navigation check against a user-left Wiley result tab proved that the automation profile could render a normal page: total/cardinality 7/7, one active Articles & Chapters tab, no missing DOI cards, and no legacy or structural challenge/syntax signal. The next benchmark command nevertheless contained a diagnostic error: it passed unquoted `test test test`, not the literal phrase `"test test test"` used by the historical 125-result benchmark. Wiley reported 3,667,752 hits; one isolated page-zero profile rendered 20/20 in 5.964 s, but the accidentally broad full helper spent 425.210 s before an unclassified failure and produced no accepted output. That attempt is invalid and supplies no benchmark evidence. A single corrected quoted-phrase page-zero request then returned a terminal signal with no total/cards and was stopped immediately without retry. The user's original normal result tab was not altered. Further live work is blocked until normal access is restored again; future runners must assert the literal frozen query fingerprint and expected bounded total before allowing pagination.

An isolated serial-safety patch at agent-tools branch commit `796e725` now replaces body-text challenge/syntax scans with sanitized structural signals and adds `expected_source_total` plus a default 5,000-record ceiling. It validates every page against an immutable pass total and every later pass against pass one, so a broad/mistyped query or changed total stops before another page is scheduled. Default callers retain the prior output schema; explicit guards add only sanitized safety metadata. Twenty-six offline tests, JavaScript syntax checks, Python compilation, Ruff formatting/checks, and diff checks pass. The patch remains unmerged and has no speed claim. A no-navigation live check of that branch was attempted only after all source requests had stopped, but the local CDP WebSocket handshake returned HTTP 404 and requested browser approval before any page evaluation; no retry or source request followed.

## Compendex implementation

The restored generic client is:

- `academic-research/skills/academic-search/scripts/search_compendex.py`
- `academic-research/skills/academic-search/scripts/test_search_compendex.py`
- `academic-research/skills/academic-search/scripts/fixtures/compendex/`

Its deterministic path uses one dedicated local Chrome tab, loopback-only CDP, Expert Search by default, Compendex only, autostemming off, Relevance, and 100/page. Current live result controls are `#results-per-page-select`/`#results-per-page-select-bottom` (Select2), not hidden selected-basket `#ev-selectedrecords-tools-pagesize`; current Next is `a#next-page-top`. It keeps row request handles from `input[name="cbresult"][docid]` separate from stable row accessions in `span[an]`, then reconciles those accessions one-to-one to RIS `U1` without positional fallback. It collapses equal nested totals, rejects conflicting totals, detects a selected-100/rendered-25 trap, and verifies page ordinals/cardinality/global ID uniqueness before writing an allowlisted schema. Access, login, CAPTCHA, syntax, stale control, malformed export, and local browser failures produce an error artifact with `total: null`, never a zero shell. The `--result-url` fallback is restricted to an already-authorized Engineering Village URL with loopback CDP.

Twenty-one offline Compendex test methods pass, covering the seven synthetic state fixtures, current U1/accession mapping, strict RIS reconciliation, exact scoped query confirmation, Expert-only mode, URL/CDP restrictions, redaction, and normalized CSV provenance. Python 3.13 compilation and Ruff formatting pass. Live aggregate-only smoke tests then completed: a verified synthetic zero in 2 s; one 100-row result page plus one reconciled RIS record in 3 s; and two 100-row pages plus 101 reconciled RIS records in 5–6 s. Bibliographic output was redirected, not inspected, and immediately deleted; only aggregate telemetry was retained in this report.

An independent read-only code review initially blocked integration on five issues: whole-body substring query confirmation, an insufficiently bound export database, Quick-mode bypass of Expert controls, an unbounded browser-side export fetch, and stale count-semantics documentation. The integrated revision uses exact dedicated field/query-bar comparison, requires database value `1` plus Compendex-only controls, rejects Quick mode, aborts export fetches at the run timeout, and updates the academic-search skill. It also verifies the visible autostemming-off label rather than interpreting checkbox state alone.

Important scope limit: the academic-search CLI preserves its generic `--limit` and `--max-pages` behavior and labels bounded output `partial`. It performs one retrieval/export pass and retains normalized output rather than a private native export. The SLR final adapter must instead compute every page from the source total, require two identical ordered ID passes, set/log the UI Published control as well as the frozen literal year/language clauses, preserve licensed native export separately, reconcile source ranks, and emit merge-ready output only after manifests and exact-day handling pass.

## Web of Science live contract

Current selectors and stop rules are in:

- `internet/skills/browser/domain-skills/webofscience/search.md`

The live contract now covers Core Collection, Editions All with every current edition checked, Topic, exact date inputs, a true Language=English search row (distinct from UI locale), absence of Document Type, submit, native verified zero, active friendly-display controls, Relevance, 50/page, current page, and visible Next. Exact Search is found semantically by label plus `button[role="switch"]`; its observed `false` state was recorded but not interpreted.

Warm aggregate-only timings were 0.281 s to a synthetic verified zero, 1.057 s to a bounded generic nonzero result route, and 0.053/0.068 s for ordinary page 1→2 and 2→3 transitions before full lazy-card hydration. This is much faster than historical model-driven attempts; the remaining issue is correctness, not navigation latency.

Result cards are lazy: a selected page size of 50 initially rendered 20 `app-record` elements, then 40 and 50 after repeated ordinary scroll-to-bottom cycles. A deterministic page step must hydrate exactly `min(50, total - 50*(page-1))`. More importantly, `data-wos-id`/`docid` attribute names were not uniformly present, and values were not inspected. Until a stable accession strategy is validated, a card-count pass cannot support ordered-ID reconciliation. Never synthesize or replay the opaque session summary route. Normal ordinary RIS export (not Fast 5000) remains the authoritative route; reconcile its `AN` accessions to explicit ranges and retain cited references in native RIS/sidecar.

## API versus browser decision

PRISMA-S requires the exact source, platform/interface, strategy, limits, date, and records identified. It does **not** make a volatile UI intrinsically more reproducible than a deterministic API. Keep the current canonical methods:

| Source | Canonical interface | Browser role | Decision |
|---|---|---|---|
| Scopus | Official Elsevier Scopus Search API, `COMPLETE`, strict reconciler | Separately logged UI validation or recovery only | Do not browserize. Preserve redacted request/page manifests, fixed `sort=eid`, two passes, raw checksums, and tool/runtime hashes. |
| IEEE Xplore | Same-host JSON search through the validated strict reconciler | Browser-context JSON only if direct transport fails; label it `browser_context_api`, not `web_ui` | Keep direct JSON canonical. Browser context adds session/WAF coupling without stronger PRISMA evidence. |
| NTRS | Public citations JSON API plus deterministic finite-cell matrix | Representative normal-UI syntax/display checks only | Do not browserize. The 660-cell final matrix is materially more complete and reproducible through API pagination. |
| ESA Indico | Whole-instance public export/attachment harvest and local deterministic matcher | UI coverage diagnostics only | Do not browserize. UI keyword search is not equivalent to the required event/material census and attachment extraction. |

For every canonical API/harvest run, preserve an evidence chain
`strategy → execution → request/page → restricted raw response → normalization → discovery event`, with interface type, endpoint/method, redacted exact request, UTC timestamps, source total, ordered page/ID digests, retries/restarts, hashes, and failures. Never persist keys, cookies, `userInfo`, IP context, or session identifiers. If a browser fallback is actually used, give it a new execution ID and interface type; do not merge or relabel it as the API run.

Offline support checks completed during this work: 11 IEEE tests, 4 NTRS tests, 5 ESA search tests, 7 merge tests, 9 Wiley helper tests, 21 Compendex tests, and the 50-query version-1.3 strategy lint all pass.

## Recommended final-run architecture

1. Extract exact frozen query blocks by query ID; do not retype or let a model reformulate them.
2. Run one dedicated process/tab per browser source, with a unique local harness name and private temporary IPC directory.
3. Perform two complete metadata-free ordered-ID passes; one changed-total restart is allowed, then stop.
4. Verify the full control fingerprint, source total, sort, native page identity, expected page cardinality, global uniqueness, and identical ordered sequences.
5. Perform ordinary source export separately, reconcile native stable IDs/ranges to the pass-2 ledger, preserve native and normalized artifacts privately, then apply exact-day filtering.
6. Create merge-ready output only after record counts, ranks, IDs, checksums, permissions, and manifest validation all pass. A source/access/selector/export failure is reported, never converted to zero or silently omitted.

## Residual gates

- **Wiley:** first restore normal browser access manually and revalidate the conservative serial contract; only then benchmark a fixed opt-in bounded-tab prototype. Separately automate or manually execute page-scoped native RIS export and prove export-to-ledger ordering; keep Collections as a separately logged coverage route.
- **Compendex:** live zero, one-page/export, and two-page/export smoke tests now pass; add review-specific exhaustive two-pass/native-export orchestration before final discovery.
- **WoS:** validate a uniform accession identity (or a rigorous RIS range-to-page map), final partial-page lazy hydration, and the ordinary export sequence. Until then, do not claim deterministic bulk enumeration.
- **All sources:** use clean ignored final-run directories; pilot/speed artifacts cannot become candidates.
