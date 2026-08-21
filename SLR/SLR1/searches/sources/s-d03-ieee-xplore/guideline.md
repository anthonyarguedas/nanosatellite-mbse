---
task_id: S-D03
source_id: ieee-xplore
source_name: IEEE Xplore
method_type: direct
status: draft_blocked
guideline_version: 0.1.0
validated_at: null
protocol_commit: ad77460df82764312fb701f6be4ebf7eb5051c41
accepted_pilot_ids: []
---

# Source-specific guideline: IEEE Xplore

> **Draft and blocked; not accepted.** Only a supervising reviewer may accept, revise, or replace this guideline. Claim labels mean: **observed** = this dated pilot only; **official_documentation** = a cited official/review document; **inferred** = a cautious tool or text-level hypothesis; **untested** = not acceptance evidence.

## 1. Source boundary and access route

- **official_documentation — review protocol:** Part 2 designates IEEE Xplore as a bibliographic and full-text database. That planning designation does not prove the live IEEE platform boundary, selected database, default search field, or normal scope. See `protocol-discovery-and-appraisal.md#electronic-databases-collections-and-indexed-online-resources`.
- **observed — blocked:** At `2026-08-21T00:36:54-04:00`, the authorized local browser harness reported Chrome and its daemon running but **zero active browser connections**. No IEEE Xplore tab, page, request, query, result, or source control was created. The access evidence is `pilots/S-D03-P01-20260821T003654-0400/evidence-index.json#E-001`.
- **untested:** The current rendered IEEE Xplore boundary, normal default input scope, visible source/database scope, account/entitlement state, query control, result route, and any scope controls. Do not infer institutional sign-in from the user's report.
- **inferred:** A later retry may use only the normal rendered IEEE Xplore UI in a new adapter-owned tab through a restored authorized loopback Chrome connection. Do not use a direct JSON/REST endpoint, a fresh/headless browser, a target ID, an existing tab, saved result URL, credentials, cookies, or a challenge workaround.

## 2. Interface and field behavior

| Item | Draft operating rule | Status |
|---|---|---|
| Default field/scope | Submit the provisional files through the normal visible search input without a field wrapper or unvalidated field restriction. | **untested** |
| Boolean and grouping | Retain explicit `AND`, `OR`, and parentheses in every file. | **observed** local text only; source grammar **untested** |
| Phrases | Retain every multiword, hyphenated, and acronym literal in double quotation marks. | **observed** local text only; source phrase behavior **untested** |
| Punctuation/hyphens | Retain both finite hyphenated and spaced protocol forms. | **observed** local text only; source normalization **untested** |
| Case/acronyms | Retain supplied case, including `EPS`, `MBSE`, `SysML`, `PCDU`, `PMAD`, `MIL`, `SIL`, `PIL`, and `HIL`. | **untested** |
| Expansion/stemming/lemmatization | Rely on none. | **untested** |
| Wildcards | Do not use a wildcard; specifically do not replace finite P forms with `nanosat*`. | **observed** local text choice; source wildcard behavior **untested** |
| Rewrite/echo and limits | Do not assume query preservation, a syntax error, a character limit, or a native error response. | **untested** |

The academic-search adapter documentation describes a normal rendered UI route and visible facets, but that is a tool description, not source-interface evidence. See `E-002`; no source behavior was validated.

## 3. Translation approach

[`translation-spec.json`](translation-spec.json) maps one **provisional, unvalidated** normal-search text cell to each required semantic partition. Exact UTF-8, BOM-free, LF-terminated files are in [`queries/`](queries/). The local integrity evidence in [`pilots/S-D03-P01-20260821T003654-0400/translation-integrity.json`](pilots/S-D03-P01-20260821T003654-0400/translation-integrity.json) verifies the finite dictionary literals, hashes, parentheses, encoding, terminal LF, and no-wildcard/no-`SmallSat` rules. It does **not** validate IEEE parsing or semantics.

| Partition | Exact provisional cell | Current validation |
|---|---|---|
| A1 | `A1-C1` — [`queries/A1.txt`](queries/A1.txt) | **blocked / untested** |
| A2 | `A2-C1` — [`queries/A2.txt`](queries/A2.txt) | **blocked / untested** |
| A3 | `A3-C1` — [`queries/A3.txt`](queries/A3.txt) | **blocked / untested** |
| B1 | `B1-C1` — [`queries/B1.txt`](queries/B1.txt) | **blocked / untested** |
| B2 | `B2-C1` — [`queries/B2.txt`](queries/B2.txt) | **blocked / untested** |
| BG1 | `BG1-C1` — [`queries/BG1.txt`](queries/BG1.txt) | **blocked / untested** |
| BG2 | `BG2-C1` — [`queries/BG2.txt`](queries/BG2.txt) | **blocked / untested** |
| BC1 | `BC1-C1` — [`queries/BC1.txt`](queries/BC1.txt) | **blocked / untested** |
| BT2 | `BT2-C1` — [`queries/BT2.txt`](queries/BT2.txt) | **blocked / untested** |
| V1 | `V1-C1` — [`queries/V1.txt`](queries/V1.txt) | **blocked / untested** |
| O1 | `O1-C1` — [`queries/O1.txt`](queries/O1.txt) | **blocked / untested** |

Each partition has one local draft cell; no source query-length finding supports a split or a union. The paired concepts use explicit same-query Boolean conjunction only as a draft text representation; no proximity or source-specific pair semantics are claimed. If a restored interface rejects a complete expression, define all replacement cells prospectively, retain every exact cell and stable-ID result, and reconcile a lossless union. A failed cell never permits a narrower substitute.

## 4. Controls and common limits

- **untested:** The protocol evidence window begins on `2011-01-01`. `P-001` has not set the common upper cutoff. The blocked pilot did not test a Year control, a lower bound, a future sentinel, an unbounded comparison, or whether IEEE offers year-only versus exact-day control. Do not claim a year control supplies exact-day precision.
- **inferred:** Until source validation, embed neither date nor language syntax in the query files. A later operator must use the visible source control only after proving its behavior. If it is year-only, preserve complete source results and apply a documented later exact-day process without silently excluding uncertain dates.
- **untested:** No reliable native language control was observed. Do not use metadata English as proof that a full report is English; determine report language later during screening unless a source-side control is prospectively proved reliable.
- **observed:** No content-type, language, access, peer-review, venue, subject, publication-type, or other discovery restriction was applied: no IEEE source action occurred. The draft specification directs a future operator to apply none unless a demonstrated source limitation requires it.
- **untested:** Visible page-size, ordering, Year, Content Type, and other controls; a future operator must record defaults and fixed selections rather than assume them.

## 5. Retrieval, pagination, and export

- **untested:** Rendered page size, result ranges, pagination, default and selected ordering, source totals, export/capture route, page cap, source cap, and detail behavior.
- **inferred:** The adapter documentation describes native items-per-page, rendered cards, and document pages. It cannot prove that the current live UI exposes or preserves those controls; its described behavior is not accepted source evidence.
- **untested required method:** First validate count-only rendering, exact query echo, source total/range, visible page-size and sort. If a retained-record diagnostic is necessary solely to establish card/article-number/detail identity, run at most one deliberately tiny adapter run with `--skip-full-abstracts`; save/read its raw JSON only under the ignored S-D03 worklog. Do not screen or review it.
- **untested required method:** A future successful capture must reconcile every rendered row/range with a stable source identity and total. Restricted raw output, titles, abstracts, bibliographic records, and session/search URLs must remain out of Git.

## 6. Stable identity and completeness

- **untested:** No IEEE article number, document route, title/DOI behavior, duplicate behavior, or stable ordering was observed.
- **untested required method:** Accept a source identity only after a current rendered card and its normal document route prove a one-to-one enduring article number/document identity. DOI is optional metadata, not a substitute for an unproven source identity.
- **untested required method:** For each later cell, use the current exact total to set a bound that exhausts all pages. Require `source total = row/range ledger = unique stable article IDs`; reject a missing, duplicate, stale, short, changed, or unreconciled row.
- **untested required method:** Repeat each exhausted cell under fixed controls. If an explicit stable order can be selected, require the same total and ordered stable-ID sequence; otherwise require the same ID set, page cardinalities, and complete range ledger. A cap, pass drift, or export/capture mismatch is a failure (`total=null`), never completion.

## 7. Failure and zero rules

| Condition | Required result |
|---|---|
| Inaccessible loopback browser, login, entitlement wall, CAPTCHA, unusual-traffic/challenge page, or unresolved route | `total=null`; zero imports; stop without aggressive retry; recommend `skip_for_now`. |
| Query rejection/rewrite, unknown default scope, unvalidated field/control, or absent exact total/range | `total=null`; no partial import. |
| Changed total/order, short or stale page, pagination failure, duplicate/missing stable identity, cap, parse failure, or export/capture mismatch | `total=null`; no partial import. |
| Bounded diagnostic prefix or incomplete cell union | Diagnostic-only partial artifact; never a candidate or import source. |
| Explicit native no-results state after exact echo, scope/control validation, and no cards | `total=0`, `records_retrieved=0`; only then a valid zero. |

**observed:** This pilot met the first row before source navigation: the browser connection was inaccessible. It did not observe a source zero or validate any other source behavior.

## 8. Final-run procedure

This is a future procedure only. Do not execute it while this guideline is draft/blocked.

1. Confirm a human has restored normal authorized loopback Chrome access without exposing credentials, cookies, existing-tab URLs, or session/search URLs. Stop again on any access control or browser failure.
2. Confirm `P-001` has fixed the common exact cutoff and a supervisor has accepted a revalidated IEEE guideline.
3. In a new adapter-owned IEEE tab only, prove platform/default scope, visible controls, exact query echo, total/range, explicit zero, Boolean/phrase/grouping, punctuation/hyphen, case/acronym, expansion, wildcard, query length, and rewrite behavior using controlled count-only diagnostics.
4. Revalidate all 11 exact files. Preserve finite P forms unless a complete fixed-scope stable-ID comparison proves that `nanosat*` is lossless and adds no unapproved meaning.
5. Validate lower-year handling and whether any source date control is exact-day or year-only. Validate language independently; apply no content/access/type/venue/subject restriction unless a documented source limitation requires one.
6. If needed, make only one tiny `--skip-full-abstracts` retained-record diagnostic to validate native page size, sort, ranges, article number, document route, title/DOI behavior, duplicate handling, and safe capture/export method.
7. Before any later final event, exhaust every cell twice under fixed controls and require total/row/unique-ID/range reconciliation plus repeat stability. Quarantine any prefix on failure and write the later authorized final artifact only under the final-event contract.

## 9. Validation evidence

- **observed:** The sole browser-access diagnostic is indexed as `E-001` in [`pilots/S-D03-P01-20260821T003654-0400/evidence-index.json`](pilots/S-D03-P01-20260821T003654-0400/evidence-index.json). Its ignored worklog checksum is `c94afc450dd14a81303b2b089d59a627300b02108173f05ef71d0e97262ab5f9`.
- **observed:** [`translation-integrity.json`](pilots/S-D03-P01-20260821T003654-0400/translation-integrity.json) and [`partition-matrix.json`](pilots/S-D03-P01-20260821T003654-0400/partition-matrix.json) establish only local structural coverage for all 11 cells.
- **inferred:** `E-002` records the inspected adapter hash and its documented normal-rendered-UI intent. It is not evidence of the live IEEE UI.
- **untested:** Source boundary/default scope, all grammar, every partition execution, date/language controls, explicit-zero behavior, pagination/capture, identity, duplicates, limits, and two-pass completeness.

## 10. Remaining limits and protocol impact

- **observed:** No IEEE source query, screening, relevance assessment, candidate construction/import, full-text/PDF retrieval, final event, task change, shared-file edit, or supervisor acceptance occurred.
- **inferred:** The draft preserves the finite dictionary terms and all Part 2 Boolean relationships at local-text level. It proposes no protocol semantic change.
- **untested:** The exact current IEEE source boundary, default scope, grammar, controls, limits, identity, capture, and completeness remain unavailable until the loopback browser is accessible.
- **required human/supervisor checks:** Restore/authorize the local browser connection; repeat the source pilot from the controlled count-only route check; set `P-001`; review date/language and no-restriction handling; decide whether the provisional normal-input syntax and same-query paired-term representation are acceptable after source testing; and accept/revise this packet before any final execution.
