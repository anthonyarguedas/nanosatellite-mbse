# Wiley Online Library diagnostic observations — S-D05-P03

**Status:** completed bounded diagnostic phase; campaign remains technically blocked for the unrun completeness gate. This attempt is diagnostic only. No screening, relevance classification, candidate import, final event, or partial-prefix import occurred.

## Scope and preflight

1. **[observed] Source-free gate passed before allocation.** The required reading was completed; the current Wiley adapter/test hashes matched the P03 plan; the focused suite passed 29 tests and 20 subtests; CLI help, exact existing query-byte checks, output safety, the shared validator, and `git diff --check` passed. No deterministic setup defect was found and no source-specific code patch was needed.
2. **[observed] Shared CfT preflight passed.** The read-only supervisor status reported epoch `5ASpPQYHIFJh_uD--zoyM7LG5u6fCcKh`, one protected inert anchor, one CfT process using the canonical shared profile, endpoint `127.0.0.1:9222`, and matching runtime/on-disk version `152.0.7977.54`. The lease was free before acquisition. See [`preflight.json`](preflight.json).
3. **[observed] The attached phase used the exact shared lease contract and process-scoped `caffeinate -dims`.** The lease receipt reports `released`, child exit `0`, and `verified-clean`; the postflight status reports one protected inert page, no surviving adapter page, no orphan child/group, and a free lease. No actual Sleep/Wake/DarkWake event was observed in the phase window. See [`live-phase-receipt.json`](live-phase-receipt.json), [`postflight.json`](postflight.json), and [`power-sleep-check.json`](power-sleep-check.json).

## Source operations

4. **[observed] OP-01 — B1, Articles & Chapters, count-only.** The existing `queries/B1.wiley-allfield.txt` was submitted through the one `AllField`/Anywhere row with the diagnostic date bound, `Earliest`, page size 20, and no language, publication-type, venue, access, or open-access convenience restriction. Wiley exposed an exact positive total of **44**, an exact query/control echo, a first page of 20 cards, and a separate Collections tab total of 1. The output retained no normalized records and is outside Git under the restricted root.
5. **[observed] OP-02 — A1, Articles & Chapters, count-only.** The existing `queries/A1.wiley-allfield.txt` passed the same route/control checks and returned an exact positive total of **13** with 13 first-page cards. The long Boolean query was accepted and echoed exactly. The separate Collections total was not parseable on this A1 page; that is unresolved, not zero, and OP-03 independently tested the declared Collections route.
6. **[observed] OP-03 — B1, Collections, count-only.** The explicit `Collections` route and target were active and returned an exact positive total of **1** with one card. Collections were treated as coverage containers only; no collection record was imported or classified.
7. **[observed] Conditional OP-04 was not run.** OP-01's total was 44, outside the predeclared 1–40 range. The plan prohibited selecting a fallback query or retrieving a convenient prefix, so the two-pass/native-RIS completeness diagnostic was correctly not enacted. See [`diagnostic-plan.json`](diagnostic-plan.json) and [`live-operation-summary.json`](live-operation-summary.json).

## Interpretation and remaining uncertainty

8. **[observed] Current route and count behavior is available only for the three executed diagnostic operations.** The adapter observed the full-platform Articles & Chapters and Collections route labels, exact totals, AllField field boundary, date-month normalization through 2026-08-31, and the `Earliest` URL control. The pilot upper bound 2026-08-25 remains a diagnostic execution-date bound only; `P-001` is unresolved.
9. **[observed] Failure/output accounting remained safe.** All three operations exited successfully with positive native totals, zero records retained by the count-only outputs, no output collision, and no retry. No explicit native zero was observed. A future access, syntax, transport, parser, pagination, identity, export, or completeness failure remains `null` with no partial prefix.
10. **[untested]** The Wiley controlled-vocabulary/indexed-term surface, descriptor hierarchy, pair/proximity semantics, full nine-cell support, two-pass stable identity, page transition, native RIS reconciliation, and complete retrieval remain untested. The A1 Collections-total parseability issue is unresolved outside the separately successful Collections operation.
11. **[protocol]** No concept, Boolean relationship, source boundary, evidence window, language/content rule, identity/capture/completeness meaning, or PRISMA accounting rule changed. The draft translation remains prohibited for final use pending the remaining required gates.

## Rights and disposition

All raw count-only JSON and commit-marker files are outside Git under `.searches/s-d05-wiley-restricted/S-D05-P03-20260825T103818-0400/`; the tracked packet contains only aggregate summaries, hashes, receipts, and safe ledgers. No screening, candidate import, final event, or relevance decision occurred. `code_issue=false` for this attempt; the historical P01 no-clobber defect and P02 stale-endpoint stop remain immutable.

**Smallest next action:** retain the P03 evidence and campaign checkpoint without retrying or choosing a fallback query; any further completeness or methodological work requires a separately authorized scope after review-owner/controller consideration.
