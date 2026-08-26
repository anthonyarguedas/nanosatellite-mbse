---
task_id: S-D09
source_id: oatd
source_name: Open Access Theses and Dissertations (OATD)
method_type: direct
status: draft_pending_controller_and_human_review_blocked
guideline_version: 0.3.1
validated_at: null
protocol_commit: 343ae7987b0fb7239a5a66d1d2dcaa7fb67a5915
adapter_commit: adbf1a06f409aa4c00f739812f9fa0a5ccbe518a
adapter_version: "3"
adapter_sha256: 2e4a403725aea006f7d41798846cc3be7317aa0ff1946eed4fd2243ada039fbc
accepted_pilot_ids: []
---

# Source-specific guideline: Open Access Theses and Dissertations (OATD)

> **Two-mode validation:** Apply the [current policy](../../two-mode-validation-policy.md). First use agent-driven exploration to make the real interface work; then use a separate frozen deterministic evidence attempt. Exploration findings guide implementation but do not pass acceptance gates.


> **Draft only — blocked and not approved.** P02 validated a narrow version-2 count-only route, P03 validated one version-3 basic count-only health gate, and P04 reached a transient challenge before advanced-form submission. P04 remains immutable and was not retried. Exactly one source-free, controller-technical successor is prospectively planned under [`p05-execution-plan.md`](p05-execution-plan.md) to passively wait for that challenge under a finite 30-second policy; no successor attempt ID or source operation exists. No pilot authorizes a final search, screening, candidate import, or source-method acceptance.

## 1. Source boundary and access route

- **[protocol]** OATD remains one required, separate public index of electronic theses and dissertations. Keep one OATD event and total; do not merge it with its contributing repositories or with PQDT. It is an indexed online resource for PRISMA-S and belongs in PRISMA 2020 websites/other methods.
- **[official_documentation]** P01's source-owned FAQ/About receipt remains the boundary evidence: OATD aggregates participating repository/consortium metadata, originating hosts control metadata quality and resource availability, OATD does not store the full text, and PQDT is a distinct service. Do not infer global coverage, degree completion, record provenance, or current resource availability from the aggregation boundary alone. See [P01 documentation receipt](pilots/S-D09-P01-20260823T232059-0400/official-source-documentation-receipt.json).
- **[observed]** P02 used only the repaired adapter's normal rendered basic GET route, `https://oatd.org/oatd/search`, with `q` and `form=basic`, through one adapter-owned page at `http://127.0.0.1:9234`. It did not use OATD APIs, static HTTP against OATD, credentials, a challenge action, a blank advanced form, or a full-text route.
- **[observed]** P03's first direct advanced-form diagnostic used one owned page from the normal home form, observed the nonblank `title` field option plus the visible language, country, earliest/latest, sort, page-size, and CC controls, and attempted `CubeSat AND SysML` in that field. Its native submission/navigation did not yield a reconcilable result state before timeout, so it establishes no field/query semantics, total, or source-record result. The owned page was subsequently identified and closed without touching either controller anchor.
- **[observed]** P03 version 3 `--count-only` health gate on `CubeSat AND SysML` returned exact total 8 with the fixed basic controls, zero retained rows, a terminal marker, and `busy_retries_performed=0`.
- **[observed]** P04's owned page reached a challenge before the advanced form could be mapped or submitted; it failed closed with `total=null` and verified cleanup. The challenge was not solved or reissued.
- **[planned]** The one prospective successor keeps the same owned page and polls passively at 0.2 seconds for at most 30 seconds. A canonical advanced form may continue the original single native submission; a persistent challenge or access/login/CAPTCHA transition fails null with no retry. This passive wait is distinct from candidate adapter version 3's post-submit busy reissue budget.
- **[untested]** Candidate adapter version 3 keeps its owned page open for an unambiguous `Server Too Busy` response, waits under a run-wide finite budget, revalidates the exact canonical GET route, and retries in that same invocation. P03/P04 did not exercise this behavior.

## 2. Interface and field behavior

- **[observed]** Six P02 and one P03 paced repaired `--count-only` runs reconfirmed the basic route's exact query echo, fixed basic controls (relevance value `relevanace`, page size 30, blank language/country/earliest/latest, unchecked CC), exact rendered totals, and zero retained rows. The outputs are non-mergeable diagnostic artifacts.
- **[observed]** Uppercase `AND` and `OR` were accepted in the narrow basic contrasts `CubeSat AND SysML` (8) and `(CubeSat OR CubeSats) AND SysML` (8). Parenthesized basic expressions were also accepted.
- **[observed]** Parentheses materially affected the aggregate result: `CubeSat OR (nanosatellite AND SysML)` reported 1,332 while the unparenthesized `CubeSat OR nanosatellite AND SysML` reported 2. This establishes that unparenthesized behavior is unsafe for this method; every draft cell retains explicit grouping. It does **not** establish a general conventional precedence rule or record-set equivalence.
- **[observed]** The straight-quoted phrase diagnostic `CubeSat AND "systems engineering"` was accepted and reported 85. It supports acceptance of straight quotes as syntax only; it does not prove phrase order, tokenization, or an identical/different record set against an unquoted contrast.
- **[blocked]** P02's first strict run returned the adapter's access/busy state before record traversal. P03's first permitted nonblank advanced title-field attempt then ended with an unreconciled navigation timeout and no result state. Under each pilot's source stop rule, no later query was submitted. `NOT`, case, punctuation/hyphen variants, acronym token boundaries, stemming/lemmatization/automatic expansion, wildcard behavior, parser-length behavior, malformed syntax, proximity, and all advanced field semantics remain untested.

### Indexed terms and controlled vocabulary

- **[observed]** P01 observed a visible advanced `subjects/keywords` selector, but that observation alone is not controlled vocabulary evidence.
- **[blocked]** P02 did not reach a positive Record Details page or an advanced field result after the access/busy stop. No scope note, hierarchy, narrower term, explosion, assignment, or source-supported descriptor mapping was established.
- **[inferred]** No controlled-vocabulary or indexed-term supplement is accepted. Free text remains mandatory; do not emulate a thesaurus or use a generic systems-engineering subject as MBSE.

## 3. Translation approach

- **[observed]** P02 regenerated the 12 exact UTF-8 basic cells byte-for-byte from `slr1-search-concepts/v4`. The offline audit found zero missing finite literals and zero missing clauses across all 292 required pair cross-products. It did not add an `S-C01` candidate, wildcard compression, synonym expansion, or term deletion. See [P02 translation audit](pilots/S-D09-P02-20260824T105026-0400/translation-audit.json) and [translation specification](translation-spec.json).
- **[observed]** The accepted small parser diagnostics support uppercase Boolean operators, straight quotes, and explicit parentheses as the conservative basic syntax used in the draft cells.
- **[blocked]** No partition cell was submitted in P02 after E-007's access/busy failure or in P03 after E-002's advanced-form timeout. A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2 remain draft mappings, not accepted final translations.
- **[blocked]** OATD has no demonstrated unordered same-field `<=5` intervening-token proximity implementation. The broad `(left AND right)` clauses in BG1, BG2, BC1, and BT2 are only transparent literal inventories in an unqualified basic query. They can cross fields and are **final-use-prohibited**. Do not treat them as the protocol-permitted broader same-field fallback.
- **[inferred]** BT2's four disjoint 14-left-term cells retain the full 56 × 4 clause inventory under OR algebra, but that algebra is not source syntax, same-field, or pair-semantic evidence.

## 4. Controls and common limits

- **[observed]** Every successful P02 basic count-only artifact retained the fixed unfiltered basic controls listed above. E-004 and E-006 each validated a 30-row first result page; this is current basic-page evidence only.
- **[blocked]** P02 did not safely test advanced earliest/latest date precision or meaning; English, country, CC-only, sort, and 60/100 page-size behavior; or advanced/basic equivalence. Do not apply any of these as discovery limits.
- **[protocol]** P-001 remains unresolved. A later operator must retain the unaltered OATD total and apply 2011-01-01 through the eventual common cutoff, English-full-text status, completed master's/doctoral status, undergraduate/non-degree/proposal exclusion, and retrieval uncertainty locally when source metadata cannot establish them. English metadata is not proof of English full text.

## 5. Retrieval, pagination, and export

- **[observed]** P02 `--count-only` requested no Record Details pages and retained no records. Its outputs demonstrate one rendered first-page total/range validation, not retrieval or exhaustion.
- **[official_documentation]** P01's FAQ receipt says OATD offers no bulk collection download or OAI-PMH metadata export.
- **[blocked]** Three selection probes found totals of 8, 8, and 85, not a safe 31–60 set. The selected one-page strict run then stopped before traversal on the access/busy state. Multi-page pagination, strict completion, live CSV publication, and detail pacing are unresolved.
- **[untested]** Native export, resource URL/format behavior, and any full-result capture method remain unvalidated.

## 6. Stable identity and completeness

- **[blocked]** No P02 Record Details page was reached. OATD Record ID, card/title/detail reconciliation, publisher/repository provenance, resource URL/format, abstract missingness, duplicate behavior, and locally usable pair fields remain untested.
- **[observed]** E-007 is a strict `--require-complete` failure with `total=null`, zero pages, zero entries, and an empty result array; no prefix, CSV, or terminal marker was published. The adapter's fail-closed accounting is correct for that source state.
- **[inferred]** A later final event would require a newly authorized successful strict two-pass run with finite bounds, fixed order, unique Record IDs, matching ordered-ID hashes, source-total reconciliation, and no page/detail/control failure. Do not sum partition totals as a union total.

## 7. Failure and zero rules

- **[protocol]** Only a reproducible native zero is zero. A challenge, durable access state, unsafe route, syntax/control/total/range/page/detail/identity/transport/completeness failure, or busy state that persists after an authorized finite recovery budget is `null`; no partial prefix is importable.
- **[observed]** E-007's version-2 error artifact records `OATDMetadataAccessError`, `total=null`, and no retained record. Its historical safe label combined an access challenge and Server Too Busy state; it was not clicked, reloaded, or retried. P03 E-002 similarly preserves `total=null` and zero records because its direct advanced-form navigation had no reconcilable source result; it was not reissued.
- **[untested]** Candidate version 3 distinguishes an exclusive busy page from challenge/access/source content. Defaults are a run-wide maximum of two recovery attempts after 30- and 60-second waits; repeated busy/clear cycles consume that same finite budget. If the post-wait state remains busy, the adapter reconstructs the validated canonical search or Record Details GET URL in memory and reissues it, avoiding the mutable current destination. A state that clears during the wait continues without another request; challenge, access denial, CAPTCHA, syntax, redirects, source-content pages, and unsafe routes are never retried. `--busy-retries 0` disables this recovery. The successor's 30-second challenge window is passive DOM polling only and never consumes these busy reissue slots.
- **[official_documentation]** P01's explicit native zero remains historical source evidence, but P02 did not revalidate a repaired-adapter zero after the terminal stop.

## 8. Final-run procedure

Do not execute a final OATD event until P-001, source-method approval, and R-002 authorization.

1. Do not directly reissue prior evidence operations. First complete the agent-driven exploration in [`resume-plan.md`](resume-plan.md), using the visible advanced composer and freezing a working interaction recipe. Only then use the held [`p05-execution-plan.md`](p05-execution-plan.md) as deterministic evidence.
2. Re-establish the dedicated-browser, power, anchor, and post-sleep preflight. Keep the successor's passive 30-second/0.2-second challenge policy separate from version 3's default finite busy policy; busy recovery remains one invocation, not authorization for a new failed-execution retry.
3. Revalidate the advanced route with a nonblank field-specific diagnostic; parser, case, punctuation, acronym, expansion, wildcard, malformed/proximity, and planned-cell behavior; controlled-vocabulary status; Record Details provenance; controls; and a naturally bounded strict two-pass route.
4. Demonstrate a valid unordered same-field pair method or a documented recall-preserving broader same-field construction with local exact-pair handling before permitting BG1, BG2, BC1, or BT2.
5. Only after approval, execute every accepted cell with the exact common cutoff/local limit handling, preserve each unaltered source total, and keep every final event separate from this pilot.

## 9. Validation evidence

- **[observed]** [P02 manifest](pilots/S-D09-P02-20260824T105026-0400/manifest.json), [observations](pilots/S-D09-P02-20260824T105026-0400/observations.md), [evidence index](pilots/S-D09-P02-20260824T105026-0400/evidence-index.json), and [translation audit](pilots/S-D09-P02-20260824T105026-0400/translation-audit.json) are diagnostic only.
- **[observed]** P02 independently verified its historical external implementation commit `5ad2a3158b404cc1bafa3df473bf9755d9cd2eef`, adapter version 2, and SHA-256 `9dacff622fb27f2b04c19c2fa91b86e86ef5c5e53b77d20718e3397b56fdd66d`; 24 focused offline OATD tests passed.
- **[observed]** The post-P02 human-directed candidate is external commit `adbf1a06f409aa4c00f739812f9fa0a5ccbe518a`, adapter version 3, SHA-256 `2e4a403725aea006f7d41798846cc3be7317aa0ff1946eed4fd2243ada039fbc`. P03 independently verified a clean worktree and ran 39 focused OATD/challenge tests plus 28 subtests. Its first live version-3 count-only gate succeeded with exact total 8 and zero busy retries; busy recovery remains **[untested]** at the source. See [P03 manifest](pilots/S-D09-P03-20260824T130849-0400/manifest.json), [observations](pilots/S-D09-P03-20260824T130849-0400/observations.md), and [evidence index](pilots/S-D09-P03-20260824T130849-0400/evidence-index.json).
- **[observed]** P03 preflight and final postflight retained both protected controller anchors `25DDEE93F8D83818D177C8DB2F365647` and `DE53021723E8E6CED2311290D731B1A4` at `chrome://newtab/`, passed the exact read-only launcher check at Chrome 151.0.7922.174, retained AC power and the process-scoped sleep assertions, and found no actual Sleep/Wake/DarkWake event in the pilot window. Its direct advanced-form probe left one identified owned page after timeout; that page alone was closed through local CDP and final anchor/no-owned-page verification passed.

## 10. Remaining limits and protocol impact

- **[blocked]** P03's terminal advanced-form navigation timeout leaves the required advanced-field, pair, controlled-vocabulary, controls, positive-detail, pagination, identity, strict-completeness, CSV, and all-cell source checks unresolved.
- **[observed]** The version-3 basic count-only/marker path succeeded in P03 with no busy recovery. P03's separate permitted direct advanced probe had a timeout and initially left its owned page open; this does not demonstrate a defect in the pinned adapter because that adapter does not submit the advanced composer. Candidate-adapter `code_issue` is therefore **[unresolved]** rather than assumed false for the untested advanced/strict paths. Live strict two-pass, busy recovery, CSV, and no-clobber collision behavior remain untested.
- **[protocol]** No protocol semantic change is proposed. OATD remains a separate required source, and pair-bearing partitions remain prohibited from final use.
- **[planned]** The next action is a new exploration using the home page's visible **Advanced Search** transition, as specified in [`resume-plan.md`](resume-plan.md), rather than direct composer navigation. Exploration may inspect, patch, and retest live but cannot pass gates, screen/import records, or run a final search. Hold P05 until that route works.

## Future browser operations

Historical per-source endpoint/profile facts remain immutable evidence. All future browser phases use the global shared CfT lease at `127.0.0.1:9222`; do not reinterpret historical observations.
