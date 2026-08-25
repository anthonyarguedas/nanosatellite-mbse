# Wiley Online Library diagnostic observations — S-D05-P01-20260824T124916-0400

**Status:** blocked; diagnostic only; `code_issue=true`. No Wiley source request, browser-owned adapter page, source result, record, DOI, RIS, screenshot, page text, screening decision, candidate import, final event, retry, code patch, or commit occurred.

## Stop rule and timeline

1. **[observed] 2026-08-24T12:45:05-04:00 to 12:49:16-04:00 — controller gate inspected before source use.** `preflight.ok` existed for the dedicated `http://127.0.0.1:9236` / `wiley-pilot-9236` context. The controller had passed runtime/on-disk Chrome matching and retained one `chrome://newtab/` anchor. AC power, a charged battery, all four `caffeinate -dims` assertions for this process, and the physical-lid limitation were recorded. See [`environment-preflight.json`](environment-preflight.json).
2. **[observed] 2026-08-24T12:49:16-04:00 — candidate implementation verified offline.** The controller-provided adapter and direct-helper SHA-256 values matched exactly; the relevant external worktree was clean; the named adapter-touch commit was an ancestor of the observed external head; `--help` exited 0; and the focused offline suite passed 3 tests. See [`adapter-verification.json`](adapter-verification.json).
3. **[observed] 2026-08-24T12:49:16-04:00 — terminal offline safety gate failed.** A source-free temporary-directory check gave the adapter's normal JSON and CSV writers pre-existing sentinel files. Both were replaced. The adapter's normal save path has no existing-output guard, although its native-RIS path has one. This is a demonstrated normal-output no-clobber defect: `code_issue=true`. See [`offline-adapter-safety-check.json`](offline-adapter-safety-check.json).
4. **[observed] 2026-08-24T12:49:16-04:00 onward — no live Wiley work started.** Per the pilot stop rule, the planned current-interface, documentation, parser/field, pair, zero, date/control, export, and completeness phases were not started. The prospectively listed phases are retained in [`diagnostic-plan.json`](diagnostic-plan.json); they are not a retry authorization.
5. **[observed] 2026-08-24T12:51:00-04:00 — draft construction completed locally.** The renderer regenerated all nine v4 partitions with all finite literals and pair cross-products, no wildcard compression and no `S-C01` candidates. Query hashes, lengths, and terminal-LF checks passed. This validates construction only; it does not validate Wiley syntax, AllField, phrase/token behavior, source length, pair semantics, or totals. See [`query-construction-audit.json`](query-construction-audit.json) and [`../../translation-spec.json`](../../translation-spec.json).
6. **[observed] 2026-08-24T13:07:29-04:00 — final postflight passed.** The exact dedicated read-only launcher check passed. Chrome remained `151.0.7922.174`; the original anchor remained; there was one page target, no non-anchor/adaptor page, AC power and all four process-scoped assertions remained active, and the actual P01 window filter had no Sleep/Wake/DarkWake event. The lid limitation remains explicit. See [`postflight-receipt.json`](postflight-receipt.json).

## Requirement disposition

| Area | Status | Basis | Evidence / consequence |
|---|---|---|---|
| Controller gate, dedicated endpoint, anchor preservation, AC/battery, caffeinate, physical-lid limitation, and Sleep/Wake check | verified | observed | `environment-preflight.json`; `postflight-receipt.json` |
| Exact adapter/helper bytes, relevant external worktree, ancestry, CLI help, focused offline behavior | verified | observed | `adapter-verification.json`; `offline-adapter-safety-check.json` |
| Normal JSON/CSV no-clobber behavior | failed | observed | `offline-adapter-safety-check.json`; `code_issue=true` |
| Full platform boundary; Articles & Chapters vs Collections behavior | blocked | untested | No Wiley page was requested. |
| Current Advanced Search fields, Anywhere/AllField eligibility, and same-field operands | blocked | untested | The adapter's one-row claim is a hypothesis only. |
| AND/OR/NOT; precedence; phrase; punctuation/hyphen; case; acronym; wildcard; expansion; echo/rewrite; proximity; length | blocked | untested | The entire prospectively listed contrast phase stopped before source use. |
| All nine literal query cells, pair cross-products, hashes, lengths, terminal LF | verified narrowly | observed | Offline only: `query-construction-audit.json`. |
| Unordered <=5-token pair implementation or broader lossless same-field fallback | blocked | untested | BG1/BG2/BC1/BT2 remain final-use-prohibited. |
| Count-only cells and totals | blocked | untested | No query was submitted; null is not zero. |
| Controlled vocabulary/indexed term, hierarchy, scope, explosion, record descriptor | blocked | untested | No Wiley interface or record was inspected; no descriptor accepted. |
| Month/date precision, language, sort, page size, active tab, total semantics, prohibited limits | blocked | untested | P01's 2026-08-24 label is diagnostic only; `P-001` remains unresolved. |
| Native explicit zero; two-pass stable identity, page transition, RIS export, completeness | blocked | untested | No positive/zero source result or source record exists. |
| First-party Wiley documentation | blocked | untested | The terminal defect stopped all live source activity before documentation discovery/retrieval. |
| No screening/import/final event and no restricted source capture | verified | observed | `manifest.json`; `restricted-capture-ledger.json`. |

## Translation and pair decision

- **[observed]** The exact UTF-8 files cover A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2. They retain every v4 literal, use no wildcard compression, and add no candidate terminology.
- **[blocked]** The pair-bearing drafts use exhaustive Boolean left/right cross-products, not a validated proximity relation. Because no current Wiley field behavior was observed, aggregate Anywhere co-occurrence might cross underlying fields. This cannot be represented as exact or lossless pair equivalence. It is explicitly blocked in [`translation-spec.json`](../../translation-spec.json).
- **[inferred]** A future pilot must validate a Wiley-native unordered <=5-intervening-token operator or prove a broader same-field construction cannot lose exact pairs, then apply exact matching locally wherever retained fields allow it.

## Controlled vocabulary and source documentation

- **[untested]** No claim is made that Wiley has, lacks, or exposes a usable controlled vocabulary or indexed-term field. Visible author keywords, if later observed, must not automatically be called a controlled vocabulary.
- **[untested]** No current first-party Wiley documentation was retrieved. A future pilot must find and retain only concise rights-safe documentation receipts after the adapter safety gate has been corrected.

## Rights, record, and protocol separation

- **[observed]** The prospective restricted root is `.searches/s-d05-wiley-restricted/S-D05-P01-20260824T124916-0400/`. It contains no P01 capture because no Wiley request occurred; the zero-capture ledger is [`restricted-capture-ledger.json`](restricted-capture-ledger.json).
- **[protocol]** Wiley remains a separate required publisher-platform event. P01 proposes no protocol, concept-dictionary, crosswalk, source-boundary, eligibility, date-window, or PRISMA semantic change.
- **[observed]** Only this D05 source packet was written. No shared task, protocol, log, schema, dictionary, crosswalk, final-event, script, external adapter, Git index, or commit was changed by P01.

## Human decision needed and smallest next action

**[inferred]** Do not accept this draft, use its queries, or retry P01. First assign a separate adapter code-fix limited to atomically refusing pre-existing normal JSON/CSV/error-artifact destinations and adding focused regression tests. Then have the controller review that commit and obtain human authorization for a new immutable Wiley pilot. The new pilot must still complete every live requirement blocked above; it must not treat the P01 diagnostic date bound as the common cutoff.
