---
task_id: S-D03
source_id: ieee-xplore
source_name: IEEE Xplore
method_type: direct
status: draft_p06_year_control_technically_blocked
guideline_version: 0.5.0
validated_at: null
protocol_commit: 38ab61287443693ddabdd4bb855d535a4585ae35
accepted_pilot_ids: []
---

# Source-specific guideline: IEEE Xplore

> **Live-first validation:** Apply the [current policy](../../live-first-validation-policy.md). Real-page behavior is primary; use only the minimum launch gate before live work, inspect technical failures on the owned page, patch immediately, and retest live after minimal changed-path checks. Broad offline suites are deferred until a working route is being accepted or merged.


**DRAFT — not accepted and not authorized for a final run.** P04 live-validated the committed small-result-page adapter fix on the exact full A1 query and count-tested all nine current semantic cells. P05 then failed closed at its visible publication-year diagnostic, and P06 was the one controller-technical successor using the bounded transitional wait. P06 again returned `total=null` with `IEEEProtocolError` after exact query/year readback but an unreconciled rendered range; content, language, and record-bearing completeness remained correctly unrun. Controller review and source-free technical isolation remain required.

## 1. Source boundary and access route

- **[inferred]** The intended boundary is the IEEE Xplore database/collection on the IEEE Xplore platform, as assigned by `S-D03` and the source/interface crosswalk.
- **[observed]** P02 and P04 used only the normal rendered IEEE Xplore Search, Advanced Search, result-card, and document-detail interfaces through the rendered-browser adapter. No IEEE JSON or REST endpoint, login, challenge bypass, PDF download, or native export was used.
- **[observed]** P02 observed separate Advanced Search options for `All Metadata`, `Full Text & Metadata`, `Full Text Only`, `Document Title`, `Abstract`, `Index Terms`, `Author Keywords`, and `IEEE Terms`.
- **[untested]** Complete collection exclusions, authenticated-versus-anonymous coverage, and a collection-selection control remain unvalidated.

## 2. Interface and field behavior

- **[observed]** P02 found equal totals for unqualified `nanosatellite` and `All Metadata` `nanosatellite`, while Full Text comparators differed. The draft uses explicit `All Metadata`, not an unqualified route.
- **[observed]** The atomic free-text form is `("All Metadata":"term")`. Field labels around a Boolean group produced native zeros in nonzero comparators, so every Boolean atom is fielded individually and outer Boolean groups are explicit and parenthesized.
- **[observed]** P02 validated the current individually fielded Boolean, quoted phrase, punctuation, acronym, wildcard, and field-route diagnostics. Every normative term remains quoted; no wildcard is used.
- **[observed]** P04 ran the minimum predeclared generic `NEAR/6` controls with exact echoes: forward and reverse totals were both 573,342, and grouped and distributed-OR totals were both 670,735. This validates current syntax, unordered reversal equality, and grouped/distributed equality for those generic same-field diagnostics.
- **[inferred_and_human_approved]** `NEAR/6` is the accepted conservative same-field fallback for the protocol's at-most-five-intervening-token pair rule. It cannot lose a qualifying pair under either common endpoint/intervening counting convention, but may admit one extra intervening token. The review owner accepted that broader-recall implementation under [`D-METHOD-NEAR6`](human-review.md); it is not claimed as exact equivalence.
- **[observed]** P02 found searchable Index Terms, Author Keywords, and IEEE Terms fields but did not establish a usable current hierarchy, narrower-term, explosion, scope-note, and mapping route. P04 found no contrary evidence.
- **[observed]** No controlled-vocabulary descriptor supplement is included. Free-text remains mandatory.
- **[untested]** Case sensitivity, literal token-boundary semantics beyond P02 diagnostics, stemming/lemmatization/automatic expansion, and a formal source query-length or result cap remain unaccepted.

## 3. Translation approach

- **[observed]** `translation-spec.json` and all nine current query files are regenerated from `search-concept-dictionary.json` v4. P04's `translation-algebra-audit.json` found every required term and Boolean tree, exactly one cell per partition, no wildcard, and the required pair grouping.
- **[observed]** A1, A2, A3, B1, and B2 are byte-unchanged from the P02/P03 field-native draft. BG1, BG2, BC1, and BT2 use `NEAR/6` only in their `G_model`, `G_structure`, C1, and T2 pair rules.
- **[observed]** P04 count-tested one exact cell for every partition: A1=5, A2=11, A3=4, B1=39, B2=65, BG1=0 (native explicit zero), BG2=8, BC1=23, and BT2=11. These are diagnostic counts only, not a final search or accepted source union.
- **[inferred_and_human_approved]** The pair fallback is accepted as a protocol-permitted broader implementation. No protocol concept or Boolean schedule changed.

## 4. Controls and common limits

- **[observed]** P04 applied no final evidence-window, language, content-type, publication-type, access, venue, or peer-review restriction. `P-001` remains unresolved.
- **[observed]** P04, P05, and P06 all failed the required visible publication-year diagnostic with `IEEEProtocolError`, `total=null`, zero pages, and zero records. P06 observed exact query/year readback but a mismatched rendered range, singleton summary, and five cards; its bounded same-page wait stopped after three repeated contradictory polls. The requested source-side year application and its precision are therefore unverified; it is not a common cutoff and no date limit is adopted.
- **[untested]** The visible Journals-plus-Conferences multiple-selection diagnostic and the rendered Language-facet inventory did not run because the year-control failures required an immediate stop. No English limit is adopted; full-report language remains for screening if the method is later accepted.
- **[planned]** A future separately authorized phase may rerun the visible year diagnostic first, then the content-type control, then [`ieee_language_control_probe.py`](../../../scripts/ieee_language_control_probe.py) on one adapter-owned page. The probe records only fixed counts/booleans, never returns facet text, and does not select English. Its offline tests are not live evidence.
- **[observed]** The adapter fixes Relevance when the native rendered UI exposes a sort selection. Complete small result pages can omit a visible Items Per Page selection; P04 A1 count-only observed five cards and an inferred native page size of 25 without treating a hidden control as selected.
- **[observed]** P02 observed a generic count of 1,301,997 for an individually fielded `power AND system` diagnostic. This is a broad-count observation, not a validated source cap.

## 5. Retrieval, pagination, and export

- **[observed]** P02 reconciled two singleton record-bearing passes with matching rendered document details, full abstracts, DOI fields where rendered, and salted ordered stable-identity hashes.
- **[observed]** P04's exact A1 count-only gate returned total 5 with an exact query echo, zero retained records, and safe owned-page closure. This bounded-live-validates adapter commit `702063f1aedf36337e1233e31e9cb083bd38c7c1` for the P03 small-page defect.
- **[untested]** P04 did not reach its two exact-A1 full-detail passes, multipage selection, page-size-10 transition, or two-pass rendered-capture checks because the mandatory year-control diagnostic failed closed.
- **[untested]** Native export is untested and not required by the protocol. No REST citation endpoint is used.

## 6. Stable identity and completeness

- **[observed]** The adapter uses a rendered numeric article number reconciled to a canonical rendered document route and matching title. P02 observed stable singleton identities without exposing them in tracked evidence.
- **[untested]** P04 did not establish exact-A1 record-bearing repeatability, multi-record duplicate/missing-ID behavior, source-total/retrieved-total equality for an exact partition, a genuine page transition, or two-pass order stability. The prospective capture method is therefore not selected.
- **[inferred]** A later authorized pilot must fail closed on missing/duplicate identities, changed totals, incomplete detail reconciliation, unequal source/retrieved totals, pass-order drift, or any partial prefix. Retain only restricted raw records and tracked salted aggregate identity hashes.

## 7. Failure and zero rules

- **[observed]** An explicit native rendered zero is valid only when the adapter's native-zero invariant succeeds. P04 BG1 is a current example: total 0, one count-only page, zero retained records, and exact echo.
- **[observed]** P04's visible-year-control diagnostic is `total=null`, not zero: it returned `IEEEProtocolError`, zero pages, and zero records after the requested 2011–2026 control. It stopped all remaining source actions.
- **[planned]** P05 preserves the same null-vs-zero rule. The Language probe treats challenge, busy, source, route, projection, and cleanup failures as blocked and never converts them to a language-filtered zero.
- **[inferred]** Access, query rewrite, control, total, range, card, identity, detail, export, pagination, or completeness failures must remain null and must never yield a partial import.

## 8. Final-run procedure

1. **[inferred]** Do not execute a final IEEE event from this draft.
2. **[observed]** Keep the current one-cell field-native translations and P04 receipts intact. Do not reuse P03 split files.
3. **[observed]** P05 and its source-bearing successor were preserved under the campaign; P06 then used one runtime attempt, exact A1 only, four conditional gates in order, the shared `127.0.0.1:9222` lease, and the patched bounded same-page wait. No NEAR/6 or prior-partition rerun occurred. Its date bound was the pilot execution date, not `P-001`.
4. **[inferred]** Obtain controller disposition of the P05/P06 year-control nulls before accepting any method. A later scope must not treat either null as zero or silently remove the date-control requirement.
5. **[inferred]** Before any final event, prospectively complete visible year, content-type, and language decisions; exact-A1 full-detail repeats; fixed multipage selection and two page-size-10 passes; stable-identity and total reconciliation; and the required rights-safe capture proof.
6. **[inferred]** Apply the common `P-001` cutoff only after it is set. Do not add a prohibited final discovery restriction.

## 9. Validation evidence

- **[observed]** P04 evidence is in `pilots/S-D03-P04-20260824T131301-0400/`; P05 evidence is in its two immutable attempt directories; and P06 evidence is in `pilots/S-D03-P06-20260825T135127-0400/`, including `year-control-receipt.json`, browser cleanup/release receipts, `source-free-diagnosis.json`, and the restricted inventory.
- **[observed]** P06 verified the trusted agent-tools main implementation at `d872f59f5f20913fbd0ef4de16ea2ab79a6bc883`, containing IEEE stabilization commit `f76610f12bb6f832244ea49d93d0c4d8add8116e`; the patched adapter, focused test, and IEEE domain note were exact-hash matched, and the focused adapter suite passed 26 tests plus 10 subtests after the live failure. The Language probe suite passed 8 tests.
- **[observed]** P01–P05 remain immutable. P06 preserved the broker anchor, matching browser version/epoch, AC power, process-scoped sleep protection, and zero exact-window Sleep/Wake/DarkWake events; lease and owned-target release were verified.
- **[untested]** No accepted pilot ID, final-run method, source-specific approval commit, or accepted rendered-capture equivalence exists.

## 10. Remaining limits and protocol impact

- **[observed]** `code_issue=unresolved`: P06's safe artifact records an exact query/year readback followed by a repeated rendered range mismatch, singleton summary, and five cards. Source-free regressions confirm that the f76610f wait tolerates twenty `Loading results` polls and rejects stable contradictions, but cannot distinguish an IEEE control-hydration state from an adapter selector/invariant issue. The source-bearing operation was not reissued and no shared dirty checkout was edited.
- **[observed_and_human_approved]** P04 introduced no protocol semantic change. The review owner accepted its `NEAR/6` implementation under the existing broader-fallback rule; P05/P06 introduced no method or cutoff decision.
- **[observed]** The IEEE stage of S-C01 remains explicitly excluded and wholly unstarted: no candidate register, B1∪B2 baseline, candidate-family query, deduplication, sampling, inspection, or coding occurred.
- **[inferred]** S-D03 method work is not complete enough for separate IEEE S-C01 authorization because control and completeness validation remain incomplete and the date-control null needs disposition.

## Future browser operations

Historical per-source endpoint/profile facts remain immutable evidence. All future browser phases use the global shared CfT lease at `127.0.0.1:9222`; do not reinterpret historical observations.
