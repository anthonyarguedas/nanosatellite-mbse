---
task_id: S-D12
source_id: iaf-digital-library
source_name: IAF Digital Library
method_type: direct
status: accepted
guideline_version: 1.0.0
validated_at: 2026-08-21
protocol_commit: ad77460df82764312fb701f6be4ebf7eb5051c41
accepted_pilot_ids: [S-D12-P01-20260821T043836+0000]
---

# Source-specific guideline: IAF Digital Library

> **Accepted reusable method, subject to the final-run preconditions below.** `S-D12-P01-20260821T043836+0000` remains diagnostic-only: it created no candidate, screening decision, import, corpus, or final event. Claim labels are **[observed]**, **[official_documentation]**, **[inferred]**, and **[untested]**; only the first two support a reusable operating rule.

## 1. Source boundary and access route

- **[official_documentation]** The public Access Policy calls IAF Digital Library a collection of technical papers presented in IAF events from 1950 onward. It distinguishes public library pages from subscription/purchase access to PDF full text. See [`observations.md`](pilots/S-D12-P01-20260821T043836+0000/observations.md) and evidence `E-ACCESS`.
- **[observed]** Current `robots.txt` permits the ordinary public `/search/` and canonical `/event/{event}/paper/{paper}/` metadata routes; it disallows `/api/`, `/f/`, `/m/`, `/u/`, and `/a/cart/`. This draft uses only the permitted public routes, anonymously, with no cookies, credentials, session reuse, login, cart, manuscript, API, or PDF request.
- **[observed]** The normal `GET https://dl.iafastro.directory/search/` form has query parameter `q`; a full-library `CubeSat` probe exactly echoed an unscoped query, reported 2,109 results, and exposed canonical cards from more than one event code. No event parameter or hidden event restriction was present in the submitted form/query/pagination controls. The selected scope is therefore the full public IAF Digital Library, not a single event.
- **[inferred]** Recheck `robots.txt`, the public form action, query echo, visible scope, and canonical detail route immediately before any later final event. A changed route/scope is a source failure (`total=null`), not a reason to substitute another route.

## 2. Interface and field behavior

- **[observed]** The current public form exposes `maxlength="500"`, `q`, and page-size controls 10/50/100/200/500. The normal adapter/public diagnostic fixes `l=50`.
- **[observed]** Double-quoted phrase syntax was exactly echoed. A controlled quoted phrase had 16 results versus 433 for its unquoted whitespace-conjunction comparator. Multiword and hyphenated dictionary literals are therefore quoted.
- **[observed]** Whitespace conjunction and explicit `AND` returned the same 14 ordered stable IDs in a controlled pair. Query files use whitespace conjunction, with every block parenthesized.
- **[observed]** Uppercase `OR` was exactly echoed. A bounded three-query stable-ID check showed that the upper-`OR` result set equalled the actual stable-ID union of its two operand result sets (29 IDs, not a count sum).
- **[observed]** Parenthesized grouping was exactly echoed; `(CubeSat OR nanosatellite) MBSE` and `CubeSat OR (nanosatellite MBSE)` had materially different totals. Never rely on unparenthesized precedence.
- **[observed]** Direct attempts to submit `title:…`, `year:…`, and `language:…` were rewritten with the colon removed and failed the exact-echo guard. No field qualifier is used. The only visible field examples were `title` and `lastname`; broader native field coverage is **[untested]**.
- **[observed]** `nanosat*` was rewritten without the star and failed the exact-echo guard. No wildcard, stemming, lemmatization, synonym, or automatic-expansion behavior is relied on; all finite protocol forms remain explicit.
- **[observed]** Quoted `nano-satellite` and `nano satellite` were exactly echoed; controlled totals/page IDs matched, but both finite spellings remain in every applicable cell. Controlled `CubeSat`/`cubesat`, `MBSE`/`mbse`, and `EPS`/`eps` probes matched in total and first-page IDs. Preserve dictionary spelling/case anyway; these probes do not prove universal normalization.
- **[observed]** A 500-ASCII-character ordinary GET query and a 501-ASCII-character ordinary GET query were both exactly echoed. Thus 500 is not a validated server-side character limit. A 500-character/998-byte non-ASCII probe failed exact echo, so byte versus visible-character server behavior is unresolved. The visible form and current public adapter both enforce 500; every planned ASCII cell is independently kept at <=500 exact submitted characters/bytes.

## 3. Translation approach

- **[observed]** [`translation-spec.json`](translation-spec.json), `queries/`, and the dated prospective plan map every required direct partition: A1 (2 cells), A2 (10), A3 (2), B1 (1), B2 (2), BG1 (2), BG2 (1), BC1 (4), BT2 (12), V1 (6), and O1 (6): 48 cells total.
- **[observed]** Every UTF-8, no-BOM, no-terminal-newline query was defined before cell execution, is <=500 characters, was exactly echoed, and was reparsed from its saved public XHTML response. See [`pre-execution-query-validation.json`](pilots/S-D12-P01-20260821T043836+0000/pre-execution-query-validation.json) and [`cell-execution-validation.json`](pilots/S-D12-P01-20260821T043836+0000/cell-execution-validation.json).
- **[inferred]** A split is lossless because it distributes one required OR block into documented disjoint chunks while retaining every other required block in every cell: `OR_j(other AND O_j) = other AND OR_j(O_j)`. Pair rules distribute each finite left alternative against its complete right OR group; they make a same-record Boolean conjunction, not an unvalidated proximity claim.
- **[inferred]** For a future final run, finish two complete ID passes for each cell, then union by canonical `event-code/paper-number`, retaining all cell IDs as provenance. Never add cell totals or infer a union from counts. A failed cell/pass makes its whole partition `total=null`.

## 4. Controls and common limits

- **[observed]** The pilot applied no event, year, language, publication-type, access, peer-review, venue, or content-type restriction.
- **[observed]** The public adapter’s bounded year diagnostic retained the unaltered source total and applied a client-side record-publication-year check after card/detail reconciliation. An include-year run retained the singleton and an exclude-year run removed it while the source total remained one.
- **[untested]** `P-001` has not selected the common upper cutoff. Do not run a final event. The protocol lower bound is 2011-01-01; IAF public result/detail metadata currently supplies a year, not an exact publication day. A source year control is not an exact-day cutoff. At final execution, preserve the unaltered source total, apply only a documented local year filter, and retain cutoff-year records without sufficient day precision for later date resolution.
- **[observed]** The native language expression rewrote. **[inferred]** Apply no English limit at discovery and determine full-report language only during later screening.

## 5. Retrieval, pagination, and export

- **[observed]** `l=50` yielded 50 rows/range 1–50 for a 2,109-result probe; `o=50` yielded range 51–100 with 50 different stable IDs and the same source total. The UI exposes 10/50/100/200/500, so 50 is a fixed method page size, not a claimed universal source default/cap.
- **[observed]** A public singleton detail page reconciled its search card, canonical event/paper route, paper ID, and publication year and visibly exposed public metadata/abstract fields. The page also exposed a manuscript form, which was not requested. The official Access Policy says PDFs require subscription/purchase.
- **[inferred]** Public metadata/abstract capture is permissible only as ordinary public page metadata, retained rights-safely outside Git when raw text may be copyrighted. Do not download a full paper. No native export route was validated; use fully reconciled public pages as the completeness channel.
- **[inferred]** A future final pass starts at `o=0`, increments by 50, requires a constant exact source total and contiguous expected ranges, captures every row’s canonical event/paper ID, and stops with `total=null` on any short/stale page, missing range, changed total, cap, parse failure, or route mismatch.

## 6. Stable identity and completeness

- **[observed]** The stable within-source identity is the canonical `event-code/paper-number` pair parsed from `/event/{event}/paper/{paper}/`; a singleton search/detail diagnostic reconciled that ID and the publication year.
- **[observed]** A bounded two-pass 14-result public query had exact query echo, total/range reconciliation, 14 unique IDs per pass, and identical ordered ID lists. This is diagnostic evidence only.
- **[inferred]** For every final cell, conduct two complete passes with byte-identical query text and controls. Require source total = contiguous rows = unique IDs on each pass, then require the ordered ID lists to match. Preserve cross-cell duplicates as cell provenance until the defined stable-ID union; duplicate IDs inside a pass are a failure.
- **[observed]** The pilot’s diagnostic stable-ID unions were computed from reconciled IDs rather than counts, but remain one-pass diagnostics and cannot be imported. See [`diagnostic-stable-id-unions.json`](pilots/S-D12-P01-20260821T043836+0000/diagnostic-stable-id-unions.json).

## 7. Failure and zero rules

- **[observed]** Exact-echo public no-result pages with zero rows occurred for the 500-character control and multiple exact cells. Those are valid *diagnostic* explicit zeros only when the submitted query, unscoped full-library controls, native no-results state, and zero rows all reconcile.
- **[inferred]** Record `total=0` in a future event only after that complete final condition. Set `total=null` for access/login/CAPTCHA/Cloudflare/busy/rate-limit states; HTTP/transport failure; rewrite; syntax/control/scope failure; missing/conflicting total/range; short page; missing/duplicate stable ID; parse/detail mismatch; cap; or pass drift. Never import a partial prefix.
- **[observed]** The source rewrote field-colon and wildcard probes. Those are `null` diagnostics, not zeros and not alternate translations.

## 8. Final-run procedure

1. **[untested]** Wait for `P-001` and `R-002` authorization; this accepted guideline does not authorize a final event.
2. **[inferred]** Recheck robots, the unscoped public `/search/` form, 500 visible-input behavior, exact query echo, `l=50`, canonical detail route, Access Policy, and scope. Stop on any changed/blocked behavior.
3. **[inferred]** Verify every query file hash/UTF-8/no-BOM/no-newline/<=500 value against `translation-spec.json`; do not edit or recombine a cell after beginning execution.
4. **[inferred]** For each cell, submit only its exact decoded text on the full-library public route, with no unapproved limit. Save restricted raw page receipts outside Git and validate every range/ID page in two complete passes.
5. **[inferred]** Apply the P-001 window locally only after complete raw traversal; retain unaltered source total, removed counts, and cutoff-year unresolved dates. Do not use a native year/language expression.
6. **[inferred]** Form per-partition unions by stable ID with cell provenance only after every cell’s two passes reconcile. Any failure gives that partition `total=null`; do not substitute pilot records or a narrower query.
7. **[inferred]** Only a later authorized process may write a final-event artifact, normalize/import complete results, deduplicate, retrieve reports, or screen.

## 9. Validation evidence

The dated diagnostic packet is [`pilots/S-D12-P01-20260821T043836+0000/`](pilots/S-D12-P01-20260821T043836+0000/). It contains the prospectively defined cell plan, query validation, per-cell safe receipt matrix, stable-ID-union diagnostic, observations, evidence index, and manifest. Raw source/adapter XHTML/JSON and parser receipts remain only in the ignored `searches/worklogs/s-d12-iaf-digital-library/S-D12-P01-20260821T043836+0000/` tree.

- **[official_documentation]** `E-ACCESS`: current public Access Policy.
- **[observed]** `E-ROBOTS`, `E-UI`, `E-GRAMMAR`, `E-LENGTH`, `E-CONTROLS`, `E-PAGINATION`, `E-IDENTITY`, `E-RIGHTS`, and `E-CELLS` are indexed in the dated evidence index.
- **[untested]** Future interface stability, a source-wide ordering guarantee/cap, an exact common cutoff, native field semantics, exact-day data precision, native language behavior, and final two-pass coverage remain open.

## 10. Remaining limits and protocol impact

- **[observed]** The supervising review accepted this v1.0.0 method while retaining the historical pilot manifest as `partial`/`revise`. P-001, field/date/language precision, source order/cap rechecks, and the final two-pass procedure remain mandatory preconditions, not reasons to reuse pilot results.
- **[untested]** A human must set the common cutoff; decide the final treatment of cutoff-year records with year-only metadata; recheck the public route/rights immediately before final execution; and review whether same-record Boolean pair rendering is adequate for the dictionary’s explicit-pair rule on this source.
- **[observed]** `semantic_change:false`: no protocol concept, Boolean relationship, source list, eligibility rule, or common-limit rule was changed. No shared file, final-event artifact, candidate, screening decision, full paper, credential, or login was created.
