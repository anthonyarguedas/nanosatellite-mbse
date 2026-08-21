# S-D12 IAF Digital Library diagnostic observations

- **Pilot:** `S-D12-P01-20260821T043836+0000`
- **Task/source:** `S-D12` / IAF Digital Library (`iaf-digital-library`)
- **Protocol commit:** `ad77460df82764312fb701f6be4ebf7eb5051c41`
- **Status:** `partial` diagnostic only; worker recommendation: `revise`
- **Scope guard:** no screening, relevance/eligibility decision, candidate creation/import, corpus, final event, full-paper/manuscript retrieval, credential entry, login, cart, API, or robots-disallowed route occurred.

**Claim labels:** **[observed]** is a bounded 2026-08-21 public-route diagnostic; **[official_documentation]** is current public IAF text; **[inferred]** is a conservative future operating rule; **[untested]** cannot support acceptance.

## Boundary, robots, and public route

- **[observed]** Current `robots.txt` disallows `/api/`, `/f/`, `/m/`, `/u/`, and `/a/cart/`; `/search/` and canonical public `/event/{event}/paper/{paper}/` were not disallowed. Only the latter two ordinary public routes were used.
- **[official_documentation]** The public Access Policy describes IAF Digital Library as a large collection of technical papers presented in IAF events from 1950 onward, while treating PDFs as subscription/purchase material.
- **[observed]** The current `/search/` form action is `/search/`, with public `q`, `o`, and `l` controls. A plain, unscoped `CubeSat` request exactly echoed `q`, reported total 2,109/range 1–50, and returned canonical cards from IAC and GLEX event codes. Its submitted form and pagination controls had no event restriction. This proves the selected pilot scope is the full public IAF Digital Library rather than a hidden event scope.
- **[observed]** The baseline response exposed 50 unique canonical event/paper IDs. The next normal offset (`o=50`, `l=50`) reported the same total, range 51–100, 50 unique IDs, and no overlap with the first page.

## Current grammar and interface matrix

| Requirement | Bounded current result | Label / evidence |
|---|---|---|
| Query echo / positive range | Exact echo and native positive ranges observed for unscoped public queries. | **[observed]** `E-UI`, `E-GRAMMAR` |
| Phrase | Quoted phrase: 16; unquoted whitespace comparator: 433. | **[observed]** `E-GRAMMAR` |
| Implicit conjunction | `CubeSat MBSE` and `CubeSat AND MBSE` each had 14 identical ordered stable IDs. Files use whitespace. | **[observed]** `E-GRAMMAR` |
| Uppercase OR | A grouped uppercase-`OR` query yielded the exact stable-ID union of its two operands: 29 IDs, with one operand overlap. | **[observed]** `E-GRAMMAR` |
| Parentheses / precedence | Parenthesized and precedence-comparator expressions were both echoed and had different totals (15 vs 2,110); every file is parenthesized. | **[observed]** `E-GRAMMAR` |
| Fields | `title:…`, `year:…`, and `language:…` were rewritten with `:` removed; no field qualifier is reusable. | **[observed]** `E-FIELDS` |
| Wildcard | `nanosat*` was rewritten without `*`; no wildcard is used. | **[observed]** `E-GRAMMAR` |
| Hyphens / punctuation | Quoted `nano-satellite` and `nano satellite` were exactly echoed and each showed 334 in the bounded check. Both finite forms are retained. | **[observed]** `E-GRAMMAR` |
| Case / acronyms | Controlled upper/lower pairs matched in total and first-page IDs: CubeSat 2,109; MBSE 102; EPS 216. Original dictionary case is still preserved. | **[observed]** `E-GRAMMAR` |
| Stemming / expansion | No safe general behavior established. | **[untested]** |
| Visible controls | `q` input has `maxlength=500`; page-size buttons 10/50/100/200/500 are visible. | **[observed]** `E-UI`, `E-LENGTH` |

## Character-limit diagnostic

| Probe | Exact echo? | Native result | Interpretation |
|---|---:|---:|---|
| ASCII 500 characters / 500 bytes | yes | explicit zero | At/below visible limit accepted. |
| ASCII 501 characters / 501 bytes | yes | explicit zero | Server did **not** enforce 500. |
| Non-ASCII 500 characters / 998 bytes | no | query rewrite/ambiguous | Cannot identify a server byte/character unit. |
| Current public adapter at 501 ASCII | pre-request refusal | `total=null` | Adapter enforces 500 before network. |

**[observed]** The normal form has a 500-character `maxlength`, but the ordinary server route accepted 501 ASCII characters unchanged. **[inferred]** Treat 500 as a normal visible-input/adapter constraint, not a server-limit claim. Every planned cell is ASCII, UTF-8/no-BOM/no-final-LF, and at most 500 exact submitted characters/bytes; no query relies on the ambiguous non-ASCII behavior.

## Prospective translation, integrity, and bounded cell executions

**[observed]** All 48 source-native cells were written under `queries/` before cell execution. The prospective plan and validator verified every required finite term, pair-rule witness, balanced grouping, file hash, no BOM/no final newline, all 11 partitions, lossless split coverage, and the `<=500` rule. Every saved raw cell XHTML response was read and reparsed against the exact file before the following matrix was written.

`total/rows@chars` means native cell source total / diagnostic rows parsed / exact submitted characters. `diagnostic union` is calculated from actual stable IDs, never by summing counts; it is one-pass pilot evidence only and **not** a final partition total.

| Partition | Cells: `total/rows@chars` | Diagnostic stable-ID union | Split block |
|---|---|---:|---|
| A1 | C01 1/1@488; C02 1/1@484 | 1 (1 cross-cell duplicate) | M_H |
| A2 | C01 0/0@482; C02 0/0@482; C03 1/1@481; C04 1/1@498; C05 0/0@498; C06 1/1@482; C07 2/2@488; C08 0/0@490; C09 0/0@491; C10 0/0@480 | 3 (2 cross-cell duplicates) | M_H ∪ M_B |
| A3 | C01 1/1@480; C02 0/0@482 | 1 | M_B |
| B1 | C01 29/29@380 | 29 | none |
| B2 | C01 16/16@493; C02 10/10@488 | 18 (8 cross-cell duplicates) | R |
| BG1 | C01 3/3@478; C02 0/0@215 | 3 | G_model |
| BG2 | C01 2/2@402 | 2 | none |
| BC1 | C01 4/4@496; C02 0/0@454; C03 0/0@475; C04 0/0@436 | 4 | C1 |
| BT2 | C01 0/0@495; C02 1/1@488; C03 0/0@495; C04 0/0@495; C05 1/1@487; C06 0/0@493; C07 0/0@494; C08 0/0@486; C09 0/0@489; C10 0/0@500; C11 2/2@495; C12 0/0@469 | 4 | T2 left alternatives |
| V1 | C01 0/0@500; C02 0/0@487; C03 0/0@499; C04 0/0@480; C05 0/0@492; C06 0/0@437 | 0 | V1 |
| O1 | C01 0/0@486; C02 0/0@485; C03 0/0@494; C04 0/0@496; C05 1/1@493; C06 1/1@464 | 1 (1 cross-cell duplicate) | O1 |

- **[observed]** Each zero cell had exact echo, full-library/no-limit controls, the native no-results summary, and zero rows. It is an explicit **cell diagnostic** zero only.
- **[inferred]** For every split partition, let `O` be the normative OR block and `O_j` its documented disjoint source cell chunks. Each cell is `other-required-blocks AND O_j`; therefore `OR_j(other AND O_j) = other AND O`. The plan records atom membership, and the validator confirms no atom/finite witness is omitted. Pair rules use the equivalent expansion `OR_left(left AND right-OR)`.
- **[inferred]** A final union must retain all `{event-code}/{paper-number} -> cell_id[]` provenance, not sum the matrix counts. A failed/re-written cell or incomplete final pass gives the entire partition `total=null`.

## Date, language, limits, and rights

- **[observed]** Adapter include/exclude year diagnostics left the exact source total unaltered and applied record publication year client-side after full source traversal; `year:` direct syntax rewrote and cannot be used.
- **[untested]** `P-001` has not set the common upper cutoff. IAF’s public result/detail date in this pilot is year-level, not an exact day. A final cutoff-year decision must use sufficiently precise source metadata where available, retain unresolved dates, and never claim a year control is an exact-day control.
- **[observed]** `language:` rewrote. **[inferred]** No native English limit is applied; full-report language remains later screening work.
- **[observed]** A public singleton detail route reconciled canonical identity and publication year and exposed metadata/abstract fields. Its manuscript control pointed to a robots-disallowed `/f/` route, which was not requested. **[official_documentation]** Access Policy describes PDF subscription/purchase. Raw metadata/abstract responses remain ignored; no PDF/full paper was downloaded.

## Pagination, identity, and completeness

- **[observed]** The 50-row page and next 50-row offset reconciled total/ranges and had no cross-page duplicate IDs.
- **[observed]** A two-pass, 14-ID bounded query had equal totals/ranges, unique IDs, and identical ordered ID lists.
- **[inferred]** A later final run uses `o=0`, `l=50`, expected contiguous ranges, canonical event/paper IDs, and two complete passes per cell. Any changed total/order, stale or short page, cap, missing/duplicate ID, parse/detail mismatch, or unresolved range mismatch requires `total=null` and no import.
- **[untested]** No source-wide cap or stable-sort guarantee was proved. The two-pass failure rule, not an assumed cap/sort behavior, is the final safeguard.

## Failure and zero rules

- **[observed]** Field/wildcard rewrites were source-query failures with `total=null`, never zeros.
- **[inferred]** Login, CAPTCHA, Cloudflare, access denial, busy/rate limit, timeout, non-XHTML, syntax/rewrite, scope/control, total/range/page, identity, duplicate, rights, or completeness failure is `total=null`; no partial prefix can be candidate/import material.
- **[inferred]** A valid final zero requires exact query echo, validated full-library controls, source native no-results state, and zero rows in both required completeness passes.

## Evidence index and remaining human checks

See [`evidence-index.json`](evidence-index.json) for classifications, hashes, and ignored-worklog references. The raw inventory records 172 ignored artifacts (86 restricted source/adapter captures, 83 metadata-only receipts, 3 public documents) and is itself hash-indexed there.

**[untested / human follow-up]** Set `P-001`’s common cutoff; decide treatment of cutoff-year records with year-only metadata; review the source’s same-record Boolean representation of explicit pair rules; recheck the current public route/robots/rights/page behavior before final execution; and have a supervisor accept/revise this draft. No protocol semantic change is proposed (`semantic_change:false`).
