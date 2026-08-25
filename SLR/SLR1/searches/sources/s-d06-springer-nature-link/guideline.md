---
task_id: S-D06
source_id: springer-nature-link
source_name: Springer Nature Link
method_type: direct
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: cfe7087c6f1230b6f1214e1f4ec21b90c8681cd7
accepted_pilot_ids: []
---

# Source-specific guideline: Springer Nature Link

> **Two-mode validation:** Apply the [current policy](../../two-mode-validation-policy.md). First use agent-driven exploration to make the real interface work; then use a separate frozen deterministic evidence attempt. Exploration findings guide implementation but do not pass acceptance gates.


> **Draft launch packet only.** No live Springer request or pilot observation has been made. All current-interface behavior below is labelled as adapter contract, protocol requirement, or untested. Do not use this packet for a final search until a validated campaign accepts every required gate.

## 1. Source boundary and access route

- **[protocol]** `S-D06` is a separate required event for the full Springer Nature Link publisher platform, with its own total. It is not a proxy for Springer journals, books, or another publisher source. See the [crosswalk](../../source-interface-prisma-crosswalk.json) and Part 2 information-sources section.
- **[adapter contract; live untested]** The current route is the normal rendered `https://link.springer.com/search` GET interface through the adapter-owned page. The adapter declares whole-platform scope and does not add content-type, access, subject, brand, venue, or supplementary-file facets.
- **[shared contract]** Any live phase must use exactly one shared CfT lease at `127.0.0.1:9222`, a new immutable receipt, an attached trusted local runner, one owned page at a time, and the verified cleanup/release procedure in [`searches/README.md`](../../README.md). No fresh browser, profile, or port is prescribed here.

## 2. Interface and field behavior

- **[adapter contract; live untested]** The adapter submits one raw query string as Springer **Link Keywords**, described by the implementation as title, abstract, and body text, excluding supplementary files. The visible query control is `#search-springerlink`; the adapter requires the rendered query to match exactly.
- **[adapter contract; live untested]** Draft atoms are double-quoted dictionary literals and Boolean groups are fully parenthesized uppercase `AND`/`OR` expressions. Exact source-native drafts are in [`translation-spec.json`](translation-spec.json) and the nine UTF-8 files under [`queries/`](queries/).
- **[untested]** Current Boolean precedence, `NOT`, phrase/token behavior, punctuation and hyphen normalization, case, standalone acronym boundaries, stemming, lemmatization, automatic expansion, wildcard behavior, parser rewrite/echo, query length, and any native proximity syntax.
- **[untested]** No genuine controlled vocabulary, thesaurus, hierarchy, scope note, narrower-term, explosion setting, or distinct indexed-term field is accepted. Free text remains mandatory. A future descriptor may only be an observed OR supplement to its mapped concept; generic systems engineering cannot satisfy `M_H` alone.
- **[untested and blocked for acceptance]** `BG1`, `BG2`, `BC1`, and `BT2` retain all pair literals as explicit Boolean left/right conjunction cross-products in the draft. This preserves concepts but does not prove the required unordered same-field pair with at most five intervening lexical tokens. Do not call those cells accepted until a native proximity or documented non-lossy same-field fallback is validated.

## 3. Translation approach

[`translation-spec.json`](translation-spec.json) is the exact source-native draft for all required direct partitions:

- `A1 = P AND E_H AND M_H`;
- `A2 = P AND E_F AND (M_H OR M_B)`;
- `A3 = P AND E_H AND M_B`;
- `B1 = P AND M_H`;
- `B2 = P AND M_B AND R`;
- `BG1 = P AND G_model`;
- `BG2 = P AND G_structure`;
- `BC1 = P AND C1`; and
- `BT2 = P AND M_B AND T2`.

**[observed offline]** Each partition has one complete cell, one terminal LF, no wildcard compression, no candidate terminology, and no dropped dictionary literal. No source query-length limit has been observed, so no lossless shards are currently required. Every cell has `source_reported_total: null` and `draft_regenerated_offline_not_submitted` status. A source access, syntax, rewrite, control, total, or completeness failure never authorizes an unrecorded narrower query.

## 4. Controls and common limits

- **[adapter contract; live untested]** The only validated adapter language value is `En`. The source-side year controls are custom `dateFrom`/`dateTo` years; exact calendar dates are supplied separately with `--date-start` and `--date-end` for strict complete mode and checked locally for every rendered record.
- **[protocol]** The evidence window starts at `2011-01-01`. The pilot uses the actual execution date as a clearly labelled diagnostic upper bound only. It is not `P-001`, not a common cutoff, and never a final-search cutoff.
- **[adapter contract; live untested]** Supported sort values are `relevance`, `newestFirst`, and `oldestFirst`; P01 uses `relevance`. The rendered page size is fixed at 20. Do not impose publication-type, access, peer-review, venue, content-type, or English-full-text discovery restrictions for convenience.
- **[untested]** Current visible filter labels, date application, language application, sort retention, result totals, and any source-side query expansion remain to be established by P01.

## 5. Retrieval, pagination, and export

- **[adapter contract; live untested]** Count-only validates the rendered first result page and exact total but retains no card text and opens no record pages. Record mode follows each retained card only to its exact same-host canonical Link content path and retains the visible abstract when one unambiguous abstract section is exposed; otherwise it marks `abstract_not_available`.
- **[adapter contract; live untested]** The adapter reconciles rendered `Showing start-end of total results` evidence, 20-record page arithmetic, scoped Next-page evidence, and duplicate-free canonical paths. A complete run requires two identical exhaustive ordered canonical-path passes.
- **[protocol and adapter contract]** Native Link CSV is not a strict-complete method: the current adapter rejects `--native-csv-output-path` with `--require-complete`, and its native schema is unpinned/unreconciled. P01 makes no native CSV claim. A normalized JSON diagnostic is likewise never imported or screened.
- **[untested]** DOI availability, content-type coverage, abstract availability rates, source cap behavior, export controls, and any complete-run source limit remain untested. The adapter's strict complete source cap is 1,000; P01's diagnostic pilot cap is narrower.

## 6. Stable identity and completeness

- **[adapter contract; live untested]** The stable identity is the canonical same-host Link content path exposed by each rendered result card (`/article/`, `/chapter/`, `/book/`, `/rwe/`, and related allowlisted content routes). A missing or malformed canonical path fails closed; title or DOI cannot substitute.
- **[planned]** If the A1 total is positive and no greater than the fixed P01 cap of 40, retrieve the complete two-page-or-less set with two ordered passes, reconcile total/ranges/rows/Next, and compare the ordered canonical-path sequences. If the total is zero or above 40, do not start this diagnostic.
- **[protocol]** A changed total, short/stale page, duplicate or missing path, pass drift, detail-route mismatch, unresolved strict date, or incomplete page traversal makes the operation `total=null` and imports no prefix. An explicit native no-results state is the only valid zero.

## 7. Failure and zero rules

- **[protocol and adapter contract]** Access denial, login, CAPTCHA/client challenge, busy or timeout without a prospectively authorized finite wait, syntax/query rejection, query rewrite, changed controls, conflicting totals, range/page arithmetic failure, canonical identity failure, detail failure, or completeness failure is a failed diagnostic with `total=null`, not zero.
- **[planned]** P01 uses one safe non-normative explicit-zero control query from [`diagnostics/native-zero-control.springer-link-keywords.txt`](diagnostics/native-zero-control.springer-link-keywords.txt). It is not a review concept or partition. If the rendered native no-results state is not positively identified, record `null` and stop; never reinterpret an empty or challenged page as zero.
- **[shared contract]** A challenge is not retried or bypassed. A busy condition may be passively waited on or reissued only under a predeclared finite policy, on the same owned page, with attempted/completed counts recorded. P01 declares no automatic reissue. A partial prefix is never imported, and no pilot operation screens or imports records.

## 8. Final-run procedure

Do not execute a final run from this draft. After `P-001`, source acceptance, and all required gates:

1. Generate the runtime campaign and attempt IDs and instantiate the shared campaign/manifest templates before source work; reserve a new receipt and unique create-only output paths.
2. Acquire the single shared CfT lease and record the required preflight health, browser provenance, pacing, finite wait policy, owned-page identity, and broker-anchor state.
3. Regenerate and audit all nine exact cells from the current dictionary. Use only cells whose field, parser, pair, length, date/language, and failure gates are accepted; do not add candidate terminology or silently narrow a cell.
4. Run the accepted cells serially through the attached trusted local runner with the exact source controls and strict complete mode. Use exact final `P-001` dates, English `En`, and the accepted source ordering. Do not use native CSV in strict complete mode.
5. Require two exhaustive ordered canonical-path passes, exact total/range/page reconciliation, identity and detail-route checks, and the adapter's create-only complete output publication. Record source totals separately for this Springer event.
6. Verify owned-page closure, anchor preservation, receipt release, and all output/receipt hashes. Only a fully reconciled final event may enter later merge accounting; a failed or cancelled event contributes no partial prefix.

## 9. Validation evidence

- **[observed offline]** The nine query files and translation spec are byte/hash-linked to dictionary v4. The current adapter and its agent-tools commit/hash are recorded in `translation-spec.json`.
- **[untested]** No current-interface claim, source total, explicit zero, controlled-vocabulary result, date/language result, stable-identity result, pagination result, or completeness result has been accepted. P01's future manifest/evidence index and campaign checkpoint must link each gate to immutable evidence and hashes.
- The initial campaign and P01 manifest are intentionally absent from this brand-new packet. The runtime plan must create them from the shared templates; no completed campaign or attempt is fabricated here.
- No screening, candidate import, final event, central log update, protocol edit, dictionary edit, crosswalk edit, or methodological decision is made by this draft.

## 10. Remaining limits and protocol impact

- **[blocked]** Current Springer parser/field semantics, controlled vocabulary, pair implementation, source date/language controls, native zero, identity, pagination, completeness, and source limits require the bounded P01 sequence in [`p01-execution-plan.md`](p01-execution-plan.md).
- **[planned]** The current rendered-UI adapter is sufficient for a count-only health gate, A1 control/query transport, an explicit native-zero control, and a capped strict-complete diagnostic if the A1 total is at most 40. No adapter change is proposed.
- **[protocol]** No concepts, Boolean schedule, source/field boundary, date or language limits, recall rule, completeness definition, or PRISMA accounting rule changes. Pair-bearing draft cells remain blocked pending source evidence; that is a validation status, not a semantic change.

The packet remains draft until a controller records a real immutable attempt, its evidence, exact adapter pin, and the required shared-validator result.
