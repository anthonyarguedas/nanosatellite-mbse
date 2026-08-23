# S-D01 Scopus P09 method-completion observations

- **Pilot ID:** `S-D01-P09-20260822T145405-0400`
- **Status:** `partial` diagnostic pilot; not accepted and not report-ready.
- **Execution window:** 2026-08-22T14:54:05-0400 to 2026-08-22T15:04:45-0400.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** P09 ran only the assigned three BT2 cell captures and one broad count-only diagnostic. It performed no screening, candidate import, final event, source fallback, full-text retrieval, sign-in, challenge action, access-control bypass, user-tab mutation, native export, adapter edit, or test edit.

Basis labels: **[observed]** is a saved command, receipt, or narrow current-interface observation. **[official_documentation]** is a directly retrieved current Elsevier/Scopus Support claim. **[inferred]** is a constrained conclusion. **[untested]** remains unresolved. Protocol requirements are not source-behavior claims.

## 1. P06 investigation disposition

- **[observed]** P09 reverified patched adapter SHA `edec4799e3e431d14d62d64d297ec03943e9b1ae829007df01a8bae830228b56`, the exact reviewed two-file dirty diff (SHA-256 `2a8e8b930edcc4682cbee5deabd07f32b48b2ed7e8de46b274266c43e687a163`), and one focused suite: **24 passed, 2 subtests passed in 0.06s**.
- **[observed]** The reviewed patch closes a real control-flow defect: before it, a transient `_form_state`/`page.evaluate` inspection error could escape `wait_for_advanced_form` immediately, rather than being bounded by its 60-second readiness deadline. The patch runs inspection inside the remaining deadline, retries passive transient inspections, and handles terminal page/browser loss separately. The three added focused tests cover transient retry, persistent bounded failure, and terminal loss.
- **[inferred]** P06's restricted safe artifact exposes only a controlled `form_readiness` failure; it cannot identify the precise underlying Playwright exception. Therefore the trigger of P06 remains uncertain, but the readiness-budget control-flow defect is proved and the patch was warranted. This is not “P06 is unexplained, so no code edit was warranted.”
- **[observed]** P08 independently bounded-validates the patched path: 10/10 no-query readiness passes; matching A1 native-full-abstract repeats; matching two-page A2 repeats; and BT2-03 native explicit zero. P09 added three complete BT2 captures and no new reproducible adapter defect.

## 2. BT2 union and capture method

- **[observed]** BT2-01, BT2-02, and BT2-04 each completed with `--skip-full-abstracts --limit 20 --max-pages 2 --timeout 60 --page-delay-seconds 1`. Their exact totals/retained counts were 2/2, 3/3, and 4/4, respectively; each had one complete rendered page. P09 stopped on no failure. BT2-03 was not rerun: P08's native explicit zero is linked and reused.
- **[observed]** In restricted storage, P09 reconciled all four cells by adapter-normalized canonical Scopus publication identity cross-checked to canonical publication path. The union has 9 occurrences, 9 unique identities, 0 duplicate occurrences, and a zero off-diagonal overlap matrix. Per-cell provenance remains restricted. The tracked receipt contains only counts, overlap counts, paths, and hashes.
- **[inferred]** The rendered adapter pagination/capture route is selected for a later final event. The protocol requires a complete reconciled capture/pagination route, not a native file export. Native export is therefore not an acceptance blocker. P01's observed menu choices and untested export-cap facts remain documented, but P09 did not activate an export. A final rendered capture still needs its protocol-required two complete ordered identity passes and must use the native full-abstract action unless a future documented final field decision changes that choice.

## 3. Broad cap/failure rule

- **[observed]** P09 ran exactly one broad patched-adapter count-only diagnostic: `TITLE-ABS-KEY("CubeSat")`. It returned controlled `ScopusProtocolError` at `result_reconciliation`, `total=null`, zero pages, zero records, and no retained partial prefix.
- **[inferred]** This is the required fail-closed cap/reconciliation behavior. The safe artifact intentionally does not preserve raw page text, a rendered numeric count, or a raw exception, so it does not independently prove which reconciliation condition triggered. Browser history's 8,930 is not a reconciled source total and is not used.

## 4. Official documentation and source semantics

- **[official_documentation]** Elsevier Support's [Advanced search guidance](https://www.elsevier.support/scopus/answer/how-can-i-best-use-the-advanced-search) was accessed at 2026-08-22T19:03:37Z; its visible update date is 2024-08-15. It describes fields, Boolean/proximity use, proximity as near/within a specified distance, and no stated explicit query-length limit.
- **[official_documentation]** Elsevier Support's [complex-search guidance](https://www.elsevier.support/scopus/answer/search-tips-what-makes-a-scopus-search-complex) was accessed at 2026-08-22T19:03:37Z; its visible update date is 2025-10-20. It defines `W/n` and `PRE/n` as AND within/preceding by a specified distance, but does not state whether `n` counts endpoints, positions, or intervening lexical tokens.
- **[inferred]** `W/6` is not claimed to be exact for the protocol's at-most-five-intervening-token rule. It is a lossless conservative same-field fallback under either common convention and may be one token broader if Scopus counts intervening tokens. Retain the documented limitation for human semantic review.
- **[observed_and_documented]** P01 found an `INDEXTERMS` field and a known record with separate indexed-term sections, but no visible hierarchy, thesaurus browser, narrower-term navigation, or explosion control. The official Advanced Search guidance names the field but provides no Scopus-wide hierarchy/explosion semantics. No descriptor meets the source-supported scope/hierarchy prerequisite, so no OR-supplement descriptor test is authorized or performed; free text remains mandatory.
- **[inferred]** P01/P08/P09 evidence reconciles the database boundary, date/language syntax limits, default ordering, pagination, stable identity, selected rendered capture, display-cap failure rule, and no-partial-prefix rule. P-001 remains necessary before date controls can be fixed; language metadata does not prove full-report English.

## 5. Translation and safety validation

- **[observed]** The P09 offline audit passed for all nine direct semantic partitions and all 12 source-native cells. Every translation-spec checksum/character count matched; BT2 has 56 distinct left forms × 4 right forms = 224 rendered `W/6` clauses, with zero missing pair clauses.
- **[observed]** Preflight and postflight launcher checks passed. Chrome runtime/disk version was 151.0.7922.174, AC power and sleep assertions were active, and controller anchor `C02CA183D7757FFA07F9FFE63511DE8B` remained the sole page target. Exact-window logs show zero actual sleep/wake and zero About This Mac markers.
- **[observed]** The first BT2-01 invocation initially received a relative output path resolved by the external adapter worktree rather than the project restricted directory. No output was overwritten; its single generated restricted file was immediately moved into the intended ignored P09 restricted directory before review, and all subsequent adapter outputs used absolute project paths. This is a local output-path correction, not a source-query or source-method failure.

## 6. Disposition and remaining dependencies

- **[inferred]** `code_issue=false`: the patched adapter passed all assigned P08/P09 bounded checks. The P06 original trigger remains unknown, but the specific readiness-budget defect is patched and validated.
- **[untested]** No final cell set has been executed under the common cutoff with the required two full identity passes. The final operator must still record the current Scopus boundary/control state, implement the P-001 cutoff, preserve native full abstracts through the selected rendered capture route, and fail closed on any cap, total, page, identity, or completeness mismatch.
- **[protocol]** `S-C01`, `P-001`, `S-002`, the remaining source tasks, human review, and authorization of `R-002` remain prerequisites. P09 does not accept S-D01 or authorize a final event.

No protocol semantic change is proposed. The guideline and translation specification are updated only to record the validated BT2 union, selected rendered capture route, P06 control-flow disposition, cap rule, and source-semantics resolution.
