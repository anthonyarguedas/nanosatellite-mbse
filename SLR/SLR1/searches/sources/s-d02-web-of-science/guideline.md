---
task_id: S-D02
source_id: wos-core
source_name: Web of Science Core Collection
method_type: direct
status: draft_p01_not_run
guideline_version: 0.1.0
validated_at: null
protocol_commit: 29535a39c4c810b0ccdb0a660af89a0521be4c76
accepted_pilot_ids: []
---

# Source-specific guideline: Web of Science Core Collection

> **Live-first validation:** Apply the [current policy](../../live-first-validation-policy.md). Real-page behavior is primary; use only the minimum launch gate before live work, inspect technical failures on the owned page, patch immediately, and retest live after minimal changed-path checks. Broad offline suites are deferred until a working route is being accepted or merged.


**Draft only.** This is a new source packet. No campaign, pilot attempt, live observation, screening decision, candidate import, or final search has been created. The local Web of Science domain guide is interface knowledge only; its dated observations are not current live proof and are not acceptance evidence for this packet.

## 1. Source boundary and access route

- **[protocol]** Treat Web of Science Core Collection as the separate bibliographic-database source assigned to `S-D02`. Keep its totals and events separate from Scopus, citation routes, and other Web of Science collections.
- **[local guide / untested]** The planned interface is the normal visible Web of Science Basic Search route at `https://www.webofscience.com/wos/woscc/basic-search`. The planned database boundary is **Web of Science Core Collection**, with **All current editions** selected. The current edition names and count must be read at runtime; do not hard-code the historical count.
- **[protocol]** A live phase may use only the shared CfT lease at `127.0.0.1:9222`, one newly owned page, and the normal visible interface. Do not launch a browser, create a profile or port, use an API, replay an opaque summary route, use Fast 5000, or bypass a challenge or access control.
- **[untested]** Current collection coverage, account-dependent access, edition inventory, and the exact current route have not been live-validated in this new run.

## 2. Interface and field behavior

- **[local guide / untested]** The planned field control is the visible **Topic** field. The exact source-native files use the `TS=(...)` Topic-field wrapper. The local guide records selectors for the Core Collection database control, All-editions picker, Topic field, Publication Date controls, English row, and normal submit button; these selectors must be re-observed during P01.
- **[source-free translation]** Every finite dictionary spelling is retained as a quoted literal atom. Boolean groups are fully parenthesized. No wildcard, stemming shortcut, lemmatization assumption, automatic expansion, acronym substitution, or dropped punctuation form is used. Phrase, hyphen, punctuation, and standalone-acronym behavior remain **untested**.
- **[source-free translation / untested]** Pair clauses in `BG1`, `BG2`, `BC1`, and `BT2` use `NEAR/6` as a provisional same-Topic, unordered, recall-preserving candidate for the protocol rule of at most five intervening lexical tokens. Its current WoS syntax and distance semantics are not established by this packet. Do not claim exact equivalence or execute a pair-bearing final query until the source behavior is validated and any resulting methodological decision is recorded.
- **[untested]** No genuine WoS controlled-vocabulary or indexed-term supplement is accepted here. Free text remains mandatory. A later descriptor can be added only as a source-validated OR supplement to its mapped concept; a generic systems-engineering descriptor cannot independently satisfy `M_H`. The P01 scope does not inspect or use a thesaurus.

## 3. Translation approach

- [`translation-spec.json`](translation-spec.json) is the exact source-native specification for the nine required partitions: A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2.
- [`queries/`](queries/) contains one UTF-8 Topic-field cell for each partition: `A1.wos-topic.txt`, `A2.wos-topic.txt`, `A3.wos-topic.txt`, `B1.wos-topic.txt`, `B2.wos-topic.txt`, `BG1.wos-topic.txt`, `BG2.wos-topic.txt`, `BC1.wos-topic.txt`, and `BT2.wos-topic.txt`.
- **[source-free]** The cells reproduce the v4 concept dictionary and Boolean schedule exactly. BT2 expands every declared T2 left/right pair. No lossless shard is present because no current source query-length limit is established. If a current limit later requires splitting, retain complete cells, document the reason, and reconcile their union by a validated stable identity before accepting it; do not silently narrow or drop terms.
- **[P01 scope]** Submit only `A1.wos-topic.txt`, a non-pair query. P01 does not test `NEAR/6`, BT2, controlled-term supplements, query-length limits, or the other eight cells. Candidate terminology remains absent and non-normative.
- The query files contain the reviewed search expression, not date or language clauses. Date and English are visible source controls, and no document-type restriction is added.

## 4. Controls and common limits

- **[P01 required]** Verify, before submission, that the visible controls represent Core Collection, All current editions, Topic, Publication Date, English, and no Document Type restriction. The probe records only booleans and edition cardinalities.
- **[diagnostic only]** Set the lower date bound to `2011-01-01` and supply the pilot execution date as the inclusive upper bound. The P01 plan uses `2026-08-25` as its planned execution-date diagnostic bound. This is not the common evidence cutoff. `P-001` remains required before the first final search, and no pilot bound may enter final accounting.
- **[untested]** Date precision and the reliability of the native English control must be demonstrated live. The full report, not just English metadata, must be English during screening. No publication-type, access, venue, peer-review, or content-type discovery restriction is imposed.
- **[protocol]** Do not add a major-topic restriction or any source-specific limit that changes recall. Absence of Document Type is a control to verify, not a document-type filter.

## 5. Retrieval, pagination, and export

- **[P01 diagnostic]** The probe submits one A1 query and returns only aggregate evidence: native-zero versus summary state, source-reported total when all required checks pass, summary route page number, page-size-50 presence, current page, expected versus observed lazy-card count, aggregate stable-ID availability (`uniform`, `partial`, or `none`), and export-control presence. It does not open records, retrieve abstracts, enumerate identifiers, download, or export.
- **[local guide / untested]** The planned summary contract is page size 50, current page 1, and `app-record` cardinality equal to `min(50, total - 50*(page-1))`. The probe scrolls only the owned summary page under a finite deadline to allow lazy cards to hydrate. It does not click Next.
- Native Export is not activated. An export button's presence is a diagnostic availability fact, not proof that export is usable, complete, rights-safe, or mapped to stable identifiers. No final capture method is selected by this draft.
- **[protocol]** A later final method must retain all required bibliographic fields, preserve rights-safe evidence, and prove complete ordered retrieval or an accepted equivalent. This probe is deliberately insufficient for that purpose.

## 6. Stable identity and completeness

- **[P01 diagnostic]** The page projection counts whether each currently visible `app-record` has a nonempty `data-wos-id` or `docid` attribute, without returning the values. `uniform` is an availability observation only; it is not an accepted identity contract.
- **[untested]** The local guide records that those attributes were not uniform across historical cards and that native RIS `AN` reconciliation had not yet been validated. P01 must not claim a stable identifier, complete enumeration, two-pass agreement, export reconciliation, or completeness.
- A final event must fail closed on a missing, duplicate, changed, or unreconciled identity; source-total/card/page mismatch; incomplete lazy hydration; page drift; export mismatch; or any other completeness failure. A partial prefix is never imported.

## 7. Failure and zero rules

- A valid zero is only the exact visible native alert `Your search found no results`, after the required controls and submitted-control display are verified. A missing alert, route reset, access message, challenge, syntax error, timeout, or incomplete control echo is `total=null`, not zero.
- A summary observation is accepted by this probe only after the source route is a summary route, the submitted Topic/English/Publication Date controls are visible and Document Type is absent, the source total is a positive integer, the page-size/current-page checks pass, and lazy-card cardinality reaches the expected value twice under the finite bound. Otherwise the aggregate result is blocked and its total is null.
- Challenge, login/access wall, busy/rate-limit condition, query/parser failure, changed selector, transport failure, total/page/card failure, and cleanup failure stop the operation. The probe performs no automatic query retry and no challenge retry. It records no partial prefix.
- Pilot observations remain diagnostic-only: `diagnostic_only=true`, `screening_performed=false`, `candidate_import_permitted=false`, and zero candidate records. A zero is a source result state, not an eligible-record count.

## 8. Final-run procedure

Do not execute this procedure during the draft P01 preparation. For a brand-new source, the controller must first create the initial campaign and manifest at runtime from the shared templates; this packet intentionally contains neither `campaign.json` nor a completed attempt.

1. Create a fresh runtime campaign ID `S-D02-C01-<timestamp-with-offset>` and attempt ID `S-D02-P01-<timestamp-with-offset>`. Create `campaign.json` and `pilots/<attempt-id>/manifest.json` from the shared templates before source work. Allocate one initial attempt with a maximum of one source operation, zero retries, and a new probe receipt and new shared-lease receipt.
2. Complete the shared CfT, broker-anchor, power/sleep, ownership, pacing, and lease preflight. Use one attached command under the exact shared wrapper; do not launch or repair the browser from the probe.
3. Invoke the source-specific entry point with `--execute`, `--query-file queries/A1.wos-topic.txt`, `--date-upper 2026-08-25` (or the actual execution date recorded for that attempt), `--receipt pilots/<attempt-id>/wos-probe-receipt.json`, `--timeout-seconds 60`, and `--poll-interval-seconds 0.25`. The wrapper's `--receipt` is a separate new path such as `pilots/<attempt-id>/shared-lease-receipt.json`.
4. The probe navigates once to Basic Search, verifies Core Collection and the current all-editions inventory, sets Topic, Publication Date `2011-01-01` through the diagnostic upper bound, English, and no Document Type, fills the exact A1 query, and submits the one visible native submit once. It then classifies the native zero or bounded summary state. It never opens a record, clicks Next, invokes Export, or reissues a busy query.
5. Keep the same owned page for any bounded passive state polling. On challenge or busy, stop with a nonzero/null terminal result. On unknown state or lazy-card timeout, stop with null total. Close only the proven owned page while the lease is live, verify target disappearance, baseline-page preservation, exact baseline-target restoration, and lease release.
6. The controller checkpoints the immutable manifest and campaign evidence. No pilot count or observation is copied to `final-events/`, screening, or the candidate corpus. A failed late diagnostic gate does not become a source zero.

The exact runtime variable allocation and attached `caffeinate -dims` / shared-lease / `uv run` command are maintained in [`p01-execution-plan.md`](p01-execution-plan.md); do not copy an older command shape from pilot memory. The timestamp is created once for the attempt and used in every path; paths are new and unique. No live command is authorized by this draft.

## 9. Validation evidence

- `translation-spec.json` records the v4 dictionary fingerprint, every partition/cell path, and every query hash. These are source-free generation records, not live acceptance evidence.
- `wos_core_pilot_probe.py` and `test_wos_core_pilot_probe.py` provide the narrow aggregate diagnostic and deterministic mocked tests. The tests do not connect to a browser or source.
- The local `webofscience/search.md` guide is retained outside this repository as assigned interface knowledge. Its historical observations are labelled local/untested here and cannot satisfy an acceptance gate.
- No `campaign.json`, pilot manifest, immutable receipt, accepted pilot ID, or current interface observation exists yet. The controller must create those only for an actually allocated P01; this agent must not fabricate them.

## 10. Remaining limits and protocol impact

- Current live behavior for boundary, Topic syntax, quoted phrases, Boolean precedence, pair syntax/distance, acronym boundaries, stemming, edition inventory, date precision, English filtering, no-Document-Type state, summary totals, lazy hydration, stable IDs, and export availability remains unknown.
- `NEAR/6` is a provisional source-native rendering for pair-bearing cells, not a demonstrated exact translation. Resolving whether its current semantics are suitable is a source-method decision; it must not be silently treated as exact or used to claim pair completeness.
- The P01 date upper bound is explicitly diagnostic and does not select or amend the common cutoff. No protocol concept, query semantics, source boundary, date/language/content limit, recall rule, completeness definition, or PRISMA accounting rule changed.
- This packet is ready for a bounded source-free/then-authorized P01 only. It is not ready for final retrieval, export, screening, candidate import, or a completeness claim.
