---
task_id: S-D13
source_id: ntrs
source_name: NASA Technical Reports Server
method_type: direct
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: 343ae7987b0fb7239a5a66d1d2dcaa7fb67a5915
accepted_pilot_ids: []
---

# Source-specific guideline: NASA Technical Reports Server (NTRS)

> **Two-mode validation:** Apply the [current policy](../../two-mode-validation-policy.md). First use agent-driven exploration to make the real interface work; then use a separate frozen deterministic evidence attempt. Exploration findings guide implementation but do not pass acceptance gates.


This is a **draft, blocked** operating method. It is not accepted and cannot support a final discovery event. Claim labels are **[observed]**, **[official_documentation]**, **[inferred]**, and **[untested]**; no unlabelled source-behavior claim is intended.

## 1. Source boundary and access route

- **[official_documentation]** The first-party public NTRS client distinguishes public NTRS/STI Repository access from a separate registered collection. This task's protocol boundary is the **full public technical-report database**, not registered-only content, PubSpace, an individual center, or a selected publication type. See [`interface-and-access-receipt.json`](pilots/S-D13-P01-20260823T232536-0400/interface-and-access-receipt.json).
- **[observed]** P01/P02's public API route timed out/returned 504 and was later abandoned by review-owner direction. Do not use it as a fallback.
- **[observed]** P05/P06 demonstrated a healthy anonymous normal rendered root under the shared browser, with no login/challenge state, but failed before query submission while reconciling visible ordering/page-size controls.
- **[planned]** Use only the normal rendered public interface in `S-D13-X01`; do not attempt registered routes, sign-in, NAMS, cookies, or API fallback.

## 2. Interface and field behavior

- **[observed]** The static first-party client contains advanced-search properties `q`, `title`, `status`, `author`, `created`, `published`, `center`, `organization`, `stiTypeDetails`, `subjectCategory`, `reportNumber`, `fundingNumber`, and `keyword`; it displays `subjectCategories` and `keywords` on records. It also presents page sizes 25, 50, and 100 and publication-date sort choices. This is client-interface evidence only, not proof that the current server accepts, indexes, or applies each field. [Receipt](pilots/S-D13-P01-20260823T232536-0400/interface-and-access-receipt.json)
- **[untested]** The live response envelope, actual q scope, title/abstract versus metadata coverage, field-specific syntax, response query echo/rewrite visibility, and export/capture schema remain unverified because the API produced no successful response. The client expects `results`, `aggregations`, and `stats`, but that expectation is not a live-envelope observation.
- **[untested]** Boolean `+`/`|` behavior and precedence; parentheses; ordered phrases; punctuation and hyphen normalization; case; standalone acronym/token matching; wildcard; stemming, lemmatization, automatic expansion; special-character escaping; query rewrite/echo; and query-length limits were not tested successfully. No missing record or zero count is interpreted as a negative result. See the contrast register in [`observations.md`](pilots/S-D13-P01-20260823T232536-0400/observations.md).
- **[observed]** `subjectCategory`/`keyword` controls and `subjectCategories`/`keywords` properties are candidate indexed-term surfaces only. **[untested]** No hierarchy, scope note, explosion behavior, descriptor semantics, or suitable public known-record assignment was retrieved. Therefore **no controlled-vocabulary or indexed-term supplement is accepted** for this draft. Do not add generic `systems engineering` as an MBSE substitute. [Translation decision](translation-spec.json#controlled_vocabulary)

## 3. Translation approach

- **[inferred]** [`translation-spec.json`](translation-spec.json) maps all nine normative partitions—A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2—to one UTF-8 query cell each in [`queries/`](queries/). The renderer copied literals from the current normative dictionary and added neither S-C01 candidate terminology nor wildcard abbreviation.
- **[inferred]** Each draft cell quotes every literal, groups alternatives with parentheses, uses `|` for OR and `+` for AND, and submits it only in the API `q` property. This is a source-syntax hypothesis, not an accepted translation: the failed transport prevents parsing, precedence, token-boundary, and field-scope validation.
- **[untested]** No server query-length limit is known. The current cells are 592–2,302 UTF-8 bytes and are not split. If a limit is later demonstrated, define all cells prospectively, preserve every cell query/total/ID ledger, and use the stable-NTRS-ID union only after complete retrieval; never silently narrow a block.
- **[untested]** NTRS support for unordered <=5-token proximity is not established. Draft BG1, BG2, BC1, and BT2 use broad left-group + right-group conjuncts solely to retain every literal. They are not accepted as a same-field or exact-pair implementation until a live validation proves that no exact pair can be lost, or a native proximity form is established. See [`translation-spec.json`](translation-spec.json#paired_term_handling).
- **[observed]** No descriptor is OR-supplemented in any draft cell. A future proven descriptor may supplement—not replace—the mapped free-text block.

## 4. Controls and common limits

- **[observed]** One direct transport probe attempted `published: {"gte":"2011-01-01","lte":"2026-08-23"}`. The upper date is explicitly a **pilot execution-date diagnostic upper bound**, not the final common cutoff; P-001 remains unresolved. The request timed out before the server responded, so exact-date behavior and date precision are unvalidated. [Probe](pilots/S-D13-P01-20260823T232536-0400/api-transport-probes.json)
- **[observed]** The current external adapter has only integer year controls and constructs year-end bounds; it cannot express an arbitrary exact P-001 upper date. This is part of `code_issue=true`; do not use it for an eventual exact-date final event without a separately reviewed fix. [Assessment](pilots/S-D13-P01-20260823T232536-0400/adapter-assessment.json)
- **[untested]** Language metadata and a reliable native English filter were not validated. No English filter is imposed; report language remains a screening/retrieval decision.
- **[inferred]** This draft applies no publication-type, access, peer-review, venue, content-type, major-topic, or proprietary/full-text limit. The public source boundary itself is retained; it does not establish final publication type or language.
- **[untested]** The source's actual default ordering and any accepted explicit sort have not been validated. A final event must not claim a stable order until it has been demonstrated.

## 5. Retrieval, pagination, and export

- **[observed]** The public client presents page sizes 25, 50, and 100; its UI code forms `page.from` and `page.size` request properties. This does not prove offset origin, maximum accepted size, final-page behavior, result count semantics, source caps, or pagination correctness.
- **[untested]** No source-reported total, result row, stable ID, export, citation metadata, or download metadata was retained because the only API/adapter executions failed before a JSON result set. `total=null`, `records_retrieved=0`, and no IDs are recorded for each failed probe; this is not a zero or an empty successful page.
- **[inferred]** A future final event should retain only the minimum public bibliographic/diagnostic fields needed for result reconciliation and the eventual normalized transfer: source NTRS record ID, title, relevant date label/value/precision, source identifiers, public canonical record path, source rank/order, and the source total. It must not download full texts during search validation or treat a public PDF link as an access filter.
- **[untested]** Export/capture route, source caps, server total versus retrieved accounting, and rights behavior require live validation before final use.

## 6. Stable identity and completeness

- **[untested]** NTRS record `id` is the proposed stable identity only; its non-nullness, uniqueness, persistence, and relationship to a public citation route have not been observed in this pilot. Do not substitute DOI, title, or a synthesized identifier when an NTRS ID is missing.
- **[inferred]** For each cell, a valid final retrieval requires: one nonempty NTRS ID per returned row; no duplicate IDs; all offsets/pages reconciled to one unchanged exact source total; no short/stale page before the terminal page; exhaustive traversal; and two complete passes with the same ordered ID ledger under a validated fixed ordering. Compare each cell independently before any within-source or cross-source deduplication.
- **[untested]** Neither a safe two-page set nor two complete passes could be exercised. No completeness claim, stable order, duplicate conclusion, or source cap conclusion is made.

## 7. Failure and zero rules

- **[inferred]** Treat DNS/TLS/connect/read timeout; HTTP redirect; 401/403; 429; 5xx; non-JSON; malformed envelope; absent/noninteger total; query syntax failure; unexplained rewrite or inability to prove query transport; unvalidated/changed control; changed total; offset/range mismatch; empty/short/stale nonterminal page; parse failure; absent/duplicate ID; changed pass order; incomplete traversal; export mismatch; or unauthorized/restricted route as a failed event. Set `total=null`; preserve only a compact failure receipt; import no prefix.
- **[inferred]** Treat `total=0` only after a successful reproducible public API JSON response explicitly reports zero and its empty result list/range is consistent. A timeout, 404 to an OPTIONS probe, 504, null, adapter error, or a local empty buffer is never zero.
- **[observed]** The pilot's exact-date direct probe timed out, its minimal direct probe received HTTP 504, and its adapter probe yielded `NTRSRequestError`; all have `total=null` and no imported records. [Receipts](pilots/S-D13-P01-20260823T232536-0400/api-transport-probes.json) and [adapter output](pilots/S-D13-P01-20260823T232536-0400/adapter-route-test.json)
- **[inferred]** A partial diagnostic prefix has no screening, candidate-import, PRISMA-identification, or final-event value. If any cell fails, preserve its failure separately rather than replacing it with a narrower unrecorded query.

## 8. Final-run procedure

Do not define the final-run procedure until exploration and evidence validate the normal rendered NTRS interface; the API route is historical and abandoned.

1. Complete the agent-driven rendered-interface exploration in [`resume-plan.md`](resume-plan.md), freezing the visible input, submit, default ordering, page size, result summary, stable ID, pagination, date-control, and failure state machine.
2. Run a separate deterministic evidence campaign over sentinel, field/control, partition, and completeness capabilities using the frozen rendered route.
3. After `P-001`, execute each accepted cell with exact source-side/client-side date handling, complete stable-ID ledgers, and two-pass or equivalent completeness. Fail closed on discrepancies.
4. Never move exploration or pilot results into `final-events/` or screening.

## 9. Validation evidence

- **[observed]** The pilot manifest is [`manifest.json`](pilots/S-D13-P01-20260823T232536-0400/manifest.json); compact receipts and checksums are in [`evidence-index.json`](pilots/S-D13-P01-20260823T232536-0400/evidence-index.json).
- **[observed]** The external adapter was pinned at `3231ebddefcc3e7bc707b2a7d66fbe831d363286` and runtime-tested once. Its failure artifact is [`adapter-route-test.json`](pilots/S-D13-P01-20260823T232536-0400/adapter-route-test.json).
- **[observed]** `code_issue=true`: its emitted PRISMA category is inconsistent with the tracked NTRS crosswalk, and it lacks exact-date and strict two-pass stable-ID final-run controls. The unpatched assessment and smallest scoped fix are in [`adapter-assessment.json`](pilots/S-D13-P01-20260823T232536-0400/adapter-assessment.json).
- **[observed]** P02–P04 are checkpointed in [`campaign.json`](campaign.json). P05/P06 subsequently passed rendered source health but failed pre-submit control reconciliation before query echo; they establish no total or partition transport.
- **[planned]** `S-D13-X01` exploration will diagnose ordering/page-size controls on the actual page. Exploration cannot satisfy acceptance. `accepted_pilot_ids` remains empty.

## 10. Remaining limits and protocol impact

- **[observed]** The API route failed historically and is abandoned. The rendered root is healthy, but P05/P06 did not reconcile pre-submit ordering/page-size controls.
- **[untested]** Rendered query echo, totals, fields, dates, pagination, stable identity, partitions, and completeness remain unresolved.
- **[inferred]** No protocol semantic change is proposed. The next work is technical `X` exploration, requiring no human approval. Until later deterministic evidence passes, NTRS remains an unaccepted source-method limitation.

## Future browser operations

Historical per-source endpoint/profile facts remain immutable evidence. All future browser phases use the global shared CfT lease at `127.0.0.1:9222`; do not reinterpret historical observations.
