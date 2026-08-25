---
task_id: S-D05
source_id: wiley-online-library
source_name: Wiley Online Library
method_type: direct
status: draft
guideline_version: 0.2.0
validated_at: null
protocol_commit: cf9129b7e63633468499c27ed76df9d52f20623c
accepted_pilot_ids: []
---

# Source-specific guideline: Wiley Online Library

> **Live-first validation:** Apply the [current policy](../../live-first-validation-policy.md). Real-page behavior is primary; use only the minimum launch gate before live work, inspect technical failures on the owned page, patch immediately, and retest live after minimal changed-path checks. Broad offline suites are deferred until a working route is being accepted or merged.


> **Draft only; final use prohibited.** P01 remains immutable and blocked by its old-adapter no-clobber defect. P02 verified the corrective adapter only offline, then stopped before its first Wiley request because the required dedicated browser endpoint was stale. No P02 source-interface claim is accepted.

## 1. Source boundary and access route

- **[protocol]** `S-D05` is a separate required event for the full Wiley Online Library publisher platform, with its own total. It is not a proxy for another publisher platform. See the [crosswalk](../../source-interface-prisma-crosswalk.json) and Part 2 information-sources section.
- **[observed]** P02's controller preflight had recorded the dedicated profile, matching version, AC power, an open-clamshell observation, four `caffeinate -dims` assertions, and the controller anchor. Its required immediately-before-source read-only check then reported that `http://127.0.0.1:9236` was not live. P02 made no Wiley request, source query, adapter source invocation, or custom-owned page. See [`browser-preflight-failure.json`](pilots/S-D05-P02-20260824T134448-0400/browser-preflight-failure.json).
- **[untested]** Current full-platform boundary, the normal Advanced Search route, active-tab semantics, and Articles & Chapters versus Collections totals and routes.

## 2. Interface and field behavior

- **[untested]** Current visible Advanced Search field inventory; one-row Anywhere/AllField behavior; query echo or rewrite; uppercase Boolean parsing; precedence; phrases; punctuation/hyphen normalization; case; standalone acronym boundaries; wildcard behavior; stemming, lemmatization, and automatic expansion; source length; and any native proximity syntax.
- **[untested]** A Wiley-native unordered <=5-intervening-token proximity method or a compliant same-field fallback. Aggregate Anywhere behavior has not been observed and cannot establish same-field pair semantics.
- **[untested]** A genuine controlled vocabulary, a distinct indexed-term field, hierarchy, scope note, narrower-term, explosion, or record-level descriptor surface. Do not call a visible keyword controlled vocabulary merely by its label. Free text remains mandatory, and generic systems engineering alone never qualifies as MBSE.

## 3. Translation approach

- **[observed]** P02 regenerated all nine root query expressions in memory from `slr1-search-concepts/v4` and reconciled them byte-for-byte to the exact UTF-8 files in [`queries/`](queries/). The audit found every finite literal and pair cross-product, no candidate terminology, no wildcard compression, expected hashes/lengths, and one terminal LF. This is source-free construction evidence only. See [`query-regeneration-audit.json`](pilots/S-D05-P02-20260824T134448-0400/query-regeneration-audit.json).
- **[inferred]** [`translation-spec.json`](translation-spec.json) keeps one complete draft cell for A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2. None was source-submitted in P02; every source total remains `null`; final use is prohibited.
- **[untested]** The draft Boolean syntax, exact source query-length behavior, one-field semantics, and source counts for every cell.
- **[blocked]** BG1, BG2, BC1, and BT2 expand pair cross-products as broader Boolean conjunctions. They do not establish the required unordered <=5-token same-field relation. Do not submit or accept a pair-bearing cell until a later healthy current-interface pilot validates exact proximity or a documented broader same-field route that cannot lose an exact pair and applies exact local matching wherever retained fields permit.

## 4. Controls and common limits

- **[protocol]** The evidence window begins on 2011-01-01 and ends only at the common cutoff selected under `P-001`; `P-001` remains unresolved.
- **[inferred]** P02 prospectively labelled 2011-01-01 through 2026-08-24 as a diagnostic execution-date bound only. It is neither `P-001` nor a final cutoff.
- **[untested]** Current month-granular date controls, exact-day local disposition, language-filter availability/reliability, Earliest ordering, fixed page size, active route, total semantics, source caps, and absence of prohibited convenience limits.
- **[protocol]** Do not apply a publication-type, access, peer-review, venue, content-type, or native-English discovery limit for convenience. Collections, if later exposed, are coverage containers and never primary-evidence records.

## 5. Retrieval, pagination, and export

- **[untested]** Current page size, page transition, total/range/card reconciliation, stable ordering, DOI availability, page-scoped RIS-with-abstracts export, export selection behavior, and raw/native preservation.
- **[inferred]** The P02 plan prospectively required one naturally bounded 21–40-record method set, two ordered passes, and page-scoped RIS reconciliation only after a healthy count gate. That phase did not begin. See [`diagnostic-plan.json`](pilots/S-D05-P02-20260824T134448-0400/diagnostic-plan.json).

## 6. Stable identity and completeness

- **[untested]** Whether DOI is present, unique, stable, and sufficient; fallback identity behavior; duplicate handling; two-pass agreement; and source/export completeness.
- **[protocol]** A later positive diagnostic must reconcile the source total, page ranges and cards, stable identifiers, order, and page-scoped export. A changed total, short/stale page, duplicate/missing identifier, export mismatch, or incomplete pass makes the total `null` and imports no prefix.

## 7. Failure and zero rules

- **[protocol]** Only a reproducible native Wiley no-result state can be recorded as `total=0`. Access, login, CAPTCHA, challenge, syntax, rewrite, query/control, total, range, page, identity, export, parsing, or completeness failures require `total=null`; no partial prefix is imported.
- **[observed]** P01 demonstrated `code_issue=true` for its older adapter, which overwrote normal JSON/CSV destinations. P01 remains immutable. P02 verified the pinned corrective commit's source-free no-clobber suite (8 tests plus 2 subtests) with exact required script and test hashes; it demonstrated no new code issue. See [`adapter-verification.json`](pilots/S-D05-P02-20260824T134448-0400/adapter-verification.json).
- **[observed]** P02's stop condition was a stale dedicated browser endpoint before H-001, not a Wiley zero, source failure, or code failure. No adapter source invocation occurred. See [`source-request-ledger.json`](pilots/S-D05-P02-20260824T134448-0400/source-request-ledger.json).

## 8. Final-run procedure

Do **not** execute a final run from this draft. Under [`campaign.json`](campaign.json), the controller may allocate the bounded technical successor without new human authorization. Before a final run, complete the campaign, resolve any genuinely methodological decision, and complete `P-001`:

1. Acquire and verify the global shared CfT lease, browser epoch, power/version/baseline-page health, and cleanup contract immediately before source work.
2. Run the one planned count-only health gate before any interface inspection; stop on access, rewrite, source, adapter, or environment failure.
3. Validate current fields, parser behavior, pair semantics, controlled/indexed terms, date/language controls, active routes, ordering, page size, totals, native zero, and export/identity completeness.
4. Regenerate and audit all nine translations from the then-current dictionary. Use exact free-text literals; do not add `S-C01` candidates or wildcard compression. Submit only cells whose parser, field, pair, and length gates are supported.
5. Preserve licensed results, RIS, raw JSON/CSV, DOM/page text, screenshots, record identifiers, and stateful source URLs only in the approved restricted location; retain only rights-safe aggregate receipts in Git.
6. Do not screen, import, self-approve, create a final event, or alter central search accounting during any pilot.

## 9. Validation evidence

- **[observed]** P01 remains unaccepted and byte-for-byte immutable; P02 recorded its current tree digest in [`p01-immutability-receipt.json`](pilots/S-D05-P02-20260824T134448-0400/p01-immutability-receipt.json).
- **[observed]** P02 is diagnostic only, has zero Wiley requests and zero restricted source captures, and is blocked before H-001. See [`manifest.json`](pilots/S-D05-P02-20260824T134448-0400/manifest.json), [`observations.md`](pilots/S-D05-P02-20260824T134448-0400/observations.md), and [`restricted-capture-ledger.json`](pilots/S-D05-P02-20260824T134448-0400/restricted-capture-ledger.json).
- **[untested]** Every live Wiley behavioral claim remains unavailable from P02 because its required pre-source browser check failed.

## 10. Remaining limits and protocol impact

- **[observed]** The next action is the controller-authorized technical attempt in [`resume-plan.md`](resume-plan.md), using the global shared CfT lease; the prior operator-terminated dedicated endpoint is historical, not a Wiley failure.
- **[inferred]** A later live P02 successor still needs current source validation even though the corrective adapter passed source-free no-clobber tests.
- **[protocol]** No protocol semantic change is proposed. `TASKS.md`, `search-log.md`, protocol files, the dictionary, the crosswalk, schemas, final events, screening data, and candidate imports remain untouched.

## Future browser operations

Historical per-source endpoint/profile facts remain immutable evidence. All future browser phases use the global shared CfT lease at `127.0.0.1:9222`; do not reinterpret historical observations.
