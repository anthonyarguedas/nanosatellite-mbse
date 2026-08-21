---
task_id: S-D11
source_id: arxiv
source_name: arXiv
method_type: direct
status: draft_blocked
guideline_version: 0.1.0
validated_at: null
protocol_commit: ad77460df82764312fb701f6be4ebf7eb5051c41
accepted_pilot_ids: []
---

# Source-specific guideline: arXiv

> **Draft and blocked.** Only a supervising reviewer may accept this guideline. Pilot `S-D11-P01-20260821T045351+0000` is diagnostic only and authorizes no screening, candidate import, final event, or final use of a partial cell set.
>
> **Evidence labels:** **[observed]** is this bounded dated UI pilot; **[official_documentation]** is current public arXiv help viewed through normal browser UI; **[inferred]** is a conservative operating rule; **[untested]** cannot support acceptance. See [`pilots/S-D11-P01-20260821T045351+0000/evidence-index.json`](pilots/S-D11-P01-20260821T045351+0000/evidence-index.json).

## 1. Source boundary and access route

- **[observed]** The current arXiv homepage presented a multidisciplinary archive spanning Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering and Systems Science, and Economics. The intended boundary is the full current arXiv repository, not one category or archive. See `E-BOUNDARY`.
- **[observed]** The route used was the normal rendered **Advanced Search** UI at `https://arxiv.org/search/advanced`, in new owned loopback-Chrome tabs only. No existing user tab, target ID, saved result URL, credential, cookie, login, CAPTCHA/challenge action, API, OAI-PMH route, Atom route, static scraper, PDF, or full text was used.
- **[observed]** The route was initially accessible. A later visible **Add another term +** control became unavailable before BG2-C2 could be submitted. This is an unresolved UI/control failure, not proof of a fixed limit. Source interaction stopped and the draft recommendation is `skip_for_now`. See `E-UI-CONTROL-FAILURE`.

## 2. Interface and field behavior

- **[observed]** Current Advanced Search exposes **All fields** and row operators AND/OR/NOT. The draft selects All fields for every row and uses visible AND between rows.
- **[observed]** Simple raw one-row AND/OR text was accepted and exactly echoed, but tested mixed and parenthesized one-row forms did not demonstrate reliable grouping. Do not use raw nested parentheses or mixed raw precedence in final translations. Use finite OR alternatives within a row and visible multi-row AND instead. See `E-GRAMMAR` and `E-MULTIROW`.
- **[observed]** Quoted multiword behavior differed from unquoted text; quoted hyphenated and spaced finite forms were accepted. Preserve every finite quoted phrase/hyphen spelling in the files.
- **[observed]** Bounded case pairs for CubeSat and MBSE had equal totals, but a battery/batteries comparison differed. **[inferred]** Preserve dictionary case and every finite morphology; rely on no stemming, lemmatization, synonym expansion, acronym expansion, or automatic expansion.
- **[observed]** `nanosat*` was accepted and had an equal bounded total to finite P, but stable-ID-set equality was not checked. **[inferred]** Do not use the wildcard.
- **[untested]** A hard character limit, universal phrase/case/acronym behavior, complete wildcard equivalence, universal query rewrite behavior, and all source grammar behavior remain unproved.

## 3. Translation approach

- **[observed]** [`translation-spec.json`](translation-spec.json) maps A1, A2, A3, B1, B2, BG1, BG2, BC1, BT2, V1, and O1 to 15 exact UTF-8 visible-form cells in [`queries/`](queries/). [`query-integrity.json`](pilots/S-D11-P01-20260821T045351+0000/query-integrity.json) found all dictionary partition mappings, query hashes, finite terms, All fields rows, AND row operators, UTF-8/BOM/LF rules, and no-SmallSat/no-wildcard checks valid locally.
- **[inferred]** A query file is an ordered list of visible `terms-N-operator`, `terms-N-field`, and `terms-N-term` assignments. It is not an API request or a URL.
- **[inferred]** BG1, BG2, and BC1 use prospectively declared lossless cell unions because direct phrase terms and paired branches cannot safely be mixed through unvalidated raw grouping. Use a set union of complete stable arXiv base-ID ledgers with cell provenance. A blocked, failed, short, duplicate, or unexecuted cell makes that whole partition `total=null`; never omit or narrow a cell.
- **[inferred]** Pair cells implement the dictionary left/right alternatives as same-record Boolean companion rows only. They do not claim an unvalidated proximity relationship.

## 4. Controls and common limits

- **[observed]** The pilot selected All fields, category/archive `all`, included cross-lists, Show abstracts, Relevance, and a native page size of 25. The UI offered page sizes 25/50/100/200.
- **[observed]** The UI exposes Date range and three date-type choices: Submission date (most recent), Submission date (original), and Announcement date. A lower-bound diagnostic retained `2011-01-01` with most-recent submission date and no upper bound. `P-001` has not set the exact common upper cutoff.
- **[inferred]** The visible date controls cannot losslessly implement the protocol's substantial-version rule plus a final upper cutoff. A most-recent upper bound can omit a pre-cutoff report revised after cutoff; an original-date control cannot identify the first substantial completed version. A final run must discover unboundedly and apply the date rule from complete local stable-ID/version-history/date data.
- **[observed]** No Language control appeared. **[inferred]** Do not apply a native English restriction; determine full-report language later during screening.
- **[inferred]** Do not apply category, archive, subject, language, access, peer-review, venue, content-type, publication-type, or other discovery narrowing unless a future source limitation is documented and approved.

## 5. Retrieval, pagination, and export

- **[observed]** One 36-result diagnostic used two rendered pages with ranges 1–25 and 26–36. The normal visible Next controls moved to the second page; on the final range, the Next controls had no href and were marked invisible. See `E-COMPLETENESS`.
- **[observed]** On one 25-row page, every row exposed canonical `/abs/` and `/pdf/` affordances. No Export or Citation control was observed on that bounded page. No PDF was opened or downloaded.
- **[inferred]** Use rendered row/range ledgers and canonical abstract-route base IDs as the complete-capture channel. Do not invent an export route. Store any future raw browser/result material only in rights-controlled ignored storage; retain tracked summaries, hashes, counts, and stable-ID/version-only evidence only.
- **[untested]** Source-wide page/capture caps, export availability, and all-result behavior are unproved.

## 6. Stable identity and completeness

- **[observed]** A normal abstract-route diagnostic exposed a canonical base-ID path and a visible submission-history container with a version/date line. A current result-page two-pass probe reconciled source total = unique canonical base-ID ledger = page/range ledger for 36 records, with exact ordered-ID equality between passes. See `E-IDENTITY` and `E-COMPLETENESS`.
- **[inferred]** Use the canonical arXiv base ID from `/abs/{base-id}` as the within-source stable identity. Preserve every displayed version/date history under that base ID; the latest source revision is not a substitute for historical version dates.
- **[untested]** A multiple-version history and all-version capture were not observed. A future successful final cell must complete two full passes under fixed controls; require unchanged total, contiguous ranges, unique base IDs, exact ledger equality when Relevance order remains stable, and complete per-ID version-history/date capture. Any drift, missing/duplicate ID, stale/short page, missing history, cap, or parse failure is `total=null` and no prefix is imported.

## 7. Failure and zero rules

| Condition | Required result |
|---|---|
| Explicit native no-results heading with exact visible query summary and controls | `total=0`; diagnostic-only or, later, an explicit-zero final event. |
| Login, CAPTCHA, challenge, entitlement/access page, inaccessible browser/source route, or unresolved control failure | `total=null`; zero imports; stop interaction; recommend `skip_for_now`. |
| Raw grouping/rewrite mismatch, wrong field/scope/date controls, bad request, missing exact total/range, query-file/hash mismatch, or unvalidated substitution | `total=null`; no partial import. |
| Changed total, stale/short page, active final-page control, duplicate/missing base ID, failed version-history capture, cap, parse failure, or pass drift | `total=null`; no partial import. |
| Any unexecuted cell in a required lossless union | Whole partition `total=null`; do not use a validated subset as a complete partition. |

**[observed]** A1, A2, A3, B1, B2, BG1-C2, and BG2-C1 showed native zero headings under exact visible summaries. **[observed]** BG2-C2 is a control failure with `total=null`, not zero.

## 8. Final-run procedure

> **[untested future procedure — do not execute during this pilot.]**

1. Confirm `P-001` has committed the common cutoff, a supervisor has accepted a revalidated guideline, and a human normal-UI preflight reproduces the required multi-row controls without the BG2-C2 failure.
2. Verify dictionary/spec/query hashes, UTF-8/BOM/LF integrity, all 15 cell mappings, current All fields behavior, archive/category `all`, included cross-lists, Relevance, no prohibited discovery restriction, and current source boundary.
3. Use unbounded discovery (no source-side upper cutoff), exact visible query-file rows, and the current normal Advanced Search controls. Revalidate every cell count/zero before collection; do not substitute a raw one-row nested expression.
4. For each successful cell, capture complete rendered page/range/base-ID ledgers twice. Require source total = unique base IDs = page/range ledger for both passes and the same ordered ledger whenever Relevance order remains stable.
5. For every base ID, open only the normal visible abstract route as needed to preserve the complete displayed version/date history. Determine the earliest substantial completed version and final cutoff eligibility locally; use only cutoff-available versions later. Do not download PDFs as part of this procedure.
6. Union only fully completed BG1/BG2/BC1 cell ledgers by base ID while retaining cell provenance. If any required cell fails, record the whole partition `total=null` and import nothing.
7. Store later authorized final artifacts only under the then-approved final-event contract. This pilot never authorizes that step.

## 9. Validation evidence

- **[observed]** [`partition-matrix.json`](pilots/S-D11-P01-20260821T045351+0000/partition-matrix.json) records all 15 cell states: eight current UI count validations, one blocked-before-submission cell, and six untested-after-stop cells.
- **[observed]** [`diagnostic-summary.json`](pilots/S-D11-P01-20260821T045351+0000/diagnostic-summary.json) records safe boundary, grammar, date, identity, capture, pagination, and two-pass observations.
- **[observed]** [`query-integrity.json`](pilots/S-D11-P01-20260821T045351+0000/query-integrity.json) validates all query-file/dictionary/spec mappings locally.
- **[official_documentation]** The normal browser-rendered arXiv help page is indexed as comparison/supporting evidence only.
- **[untested]** No pilot proves future UI stability, a final common cutoff, source-wide caps, full version history, or a completed final event.

## 10. Remaining limits and protocol impact

- **[observed]** The unresolved multi-row control failure blocks this packet. Do not accept it, mark S-D11 complete, or use any pilot count/record as a candidate or final discovery event.
- **[untested]** Focused follow-up must reproduce the third-row action, revalidate BG2-C2/C3 and all unexecuted BC1/BT2/V1/O1 cells, test source-wide limits and capture, and observe/reconcile a multiple-version history before final execution.
- **[untested]** `P-001`, `R-002`, final source preflight, and supervisor approval remain mandatory.
- **[observed]** No protocol concept, Boolean relation, evidence-window rule, eligibility rule, or source list changed. No semantic/protocol change is proposed by this draft.
