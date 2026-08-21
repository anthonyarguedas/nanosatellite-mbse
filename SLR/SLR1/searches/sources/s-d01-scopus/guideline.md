---
task_id: S-D01
source_id: scopus
source_name: Scopus
method_type: direct
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: 7d564870a36d049716b66c9f9770554ecb04e414
accepted_pilot_ids: []
---

# Source-specific guideline: Scopus

> **Draft and blocked.** Only a supervising reviewer may accept this guideline. Claim labels mean: **observed** = this dated pilot only; **official_documentation** = a cited Scopus publication; **inferred** = a tool or text-level hypothesis; **untested** = not acceptance evidence.

## 1. Source boundary and access route

- **inferred:** The intended source is the Scopus bibliographic database on the Scopus platform, via the public Advanced Search route `https://www.scopus.com/search/form.uri?display=advanced`. This boundary is specified for SLR1 in the source crosswalk, but the current rendered source scope was not proved. See [pilot observations](pilots/S-D01-P01-20260820T234301-0400/observations.md#authorized-route-and-boundary).
- **observed — blocked:** One default-loopback, adapter-owned count-only attempt ended with `ScopusProtocolError`, `total=null`, and zero retained records before a recognizable rendered result state. It is not a confirmed login, entitlement, CAPTCHA, or syntax diagnosis. See the [safe summary](pilots/S-D01-P01-20260820T234301-0400/safe-summary.json).
- **untested:** A later operator must prove the current Advanced Search form, query field, submit control, exact query echo, Scopus-only scope, public route, and result-route continuity in a new owned tab. Do not use an API, a fresh/headless browser, credentials, cookies, a session/search URL, or an existing user tab.

## 2. Interface and field behavior

| Item | Draft rule | Status and evidence |
|---|---|---|
| Field wrapper | Use the provisional `TITLE-ABS-KEY(...)` wrapper in `translation-spec.json`; do not treat its title/abstract/keyword coverage as established. | **inferred**; [translation spec](translation-spec.json) and [observations](pilots/S-D01-P01-20260820T234301-0400/observations.md#provisional-translation-basis) |
| Literal phrases | Retain every quoted finite literal exactly as supplied. | **inferred** text construction; source phrase behavior **untested** |
| Boolean grouping | Retain the explicit parenthesized AND/OR grouping in each file. | **observed** local text check; source precedence **untested** |
| Paired concepts | Use Boolean conjunction inside the same field wrapper; do not introduce an unvalidated proximity operator. | **inferred**; source pairing behavior **untested** |
| Punctuation/hyphens | Retain both hyphenated and spaced protocol forms. | **observed** local text check; source normalization **untested** |
| Case/acronyms | Retain the supplied case, including `EPS`, `MBSE`, `SysML`, `PCDU`, `PMAD`, `MIL`, `SIL`, `PIL`, and `HIL`. | **observed** local text check; case/acronym semantics **untested** |
| Expansion/stemming/lemmatization | Assume nothing. | **untested** |
| Wildcards | Do not use wildcards; specifically do not replace finite P forms with `nanosat*`. | **observed** local text choice; wildcard safety **untested** |
| Query length and rewrite | Do not assume an accepted character limit or that the source preserves the entered query. | **untested** |

Before this draft can be accepted, use count-only comparisons to validate phrase/Boolean precedence, field coverage, punctuation/hyphen handling, case, acronym boundaries, expansion/stemming/lemmatization, wildcard semantics, full-query length, and exact source echo/rewrite. A count alone does not establish wildcard safety; compare exhaustive stable-ID sets for finite P forms versus `nanosat*` under the same final fields and date scope.

## 3. Translation approach

The exact UTF-8, LF-terminated query files and one-cell mapping are in [`translation-spec.json`](translation-spec.json). The local compilation check in [`query-integrity.json`](pilots/S-D01-P01-20260820T234301-0400/query-integrity.json) found every designated dictionary literal, balanced parentheses, and one wrapper per file. That check does **not** validate Scopus syntax or semantics.

| Partition | Exact provisional cell | Status |
|---|---|---|
| A1 | `A1-01` — [`queries/A1.txt`](queries/A1.txt) | **blocked / untested** |
| A2 | `A2-01` — [`queries/A2.txt`](queries/A2.txt) | **blocked / untested** |
| A3 | `A3-01` — [`queries/A3.txt`](queries/A3.txt) | **blocked / untested** |
| B1 | `B1-01` — [`queries/B1.txt`](queries/B1.txt) | **blocked / untested** |
| B2 | `B2-01` — [`queries/B2.txt`](queries/B2.txt) | **blocked / untested** |
| BG1 | `BG1-01` — [`queries/BG1.txt`](queries/BG1.txt) | **blocked / untested** |
| BG2 | `BG2-01` — [`queries/BG2.txt`](queries/BG2.txt) | **blocked / untested** |
| BC1 | `BC1-01` — [`queries/BC1.txt`](queries/BC1.txt) | **blocked / untested** |
| BT2 | `BT2-01` — [`queries/BT2.txt`](queries/BT2.txt) | **blocked / untested** |
| V1 | `V1-01` — [`queries/V1.txt`](queries/V1.txt) | **blocked / untested** |
| O1 | `O1-01` — [`queries/O1.txt`](queries/O1.txt) | **blocked / untested** |

Each semantic partition currently has one text cell, so no union is claimed or needed in the draft. If current Scopus rejects a full expression for length, define every replacement cell prospectively, retain its exact query and total, and reconcile a lossless stable-ID union. A failed or omitted cell never authorizes a narrower substitute.

## 4. Controls and common limits

- **untested:** Confirm that the selected scope is Scopus and that no hidden database, publication-type, access, peer-review, content-type, venue, or subject limit is active. The draft applies none of those limits.
- **untested:** The protocol window starts on `2011-01-01`. The exact common cutoff is not set (`P-001`), so no date clause is embedded in the query files. Validate whether current Scopus supports an exact-day upper bound; do not turn a year-only control into an exact-date claim.
- **untested:** Do not use a native English metadata filter unless its behavior is validated. In every case, metadata language cannot prove full-text language.
- **untested:** Validate the visible sort/order and whether it is stable enough for two ordered passes. Record the actual control and order; do not assume relevance, date, or another default.
- **observed — failure rule:** The one route diagnostic has `total=null`; it is not a zero. A zero is valid only after the current interface shows an explicit native no-results state together with the exact query echo and validated scope.

## 5. Retrieval, pagination, and export

- **inferred:** The available browser adapter is intended to use rendered result rows, source-publication routes, visible range reconciliation, native next-page controls, and optionally page-level abstract expansion. This is a tool hypothesis, not current interface evidence. See the [pilot evidence register](pilots/S-D01-P01-20260820T234301-0400/observations.md#evidence-register).
- **untested:** Native page size, pagination, capture/export controls, fields, source caps, ordering, and rights conditions.
- **untested required method:** First perform count-only validation. If a retained-record diagnostic is necessary, use a deliberately bounded run with `--skip-full-abstracts`, read its saved JSON, keep any licensed raw artifact only under ignored `searches/worklogs/s-d01-scopus/`, and retain only safe hashes/ID comparisons in Git.
- **untested required method:** Before a complete run, establish a source-native capture or export route that reconciles every displayed row, its source stable identity, contiguous ranges, and the exact total. Native/export bytes and licensed abstracts must stay outside Git when rights require it; a safe manifest can retain paths, hashes, counts, and access classification.

## 6. Stable identity and completeness

- **untested:** No current Scopus stable record identifier, duplicate behavior, or pagination behavior was observed.
- **untested required method:** Accept a stable identifier only after the current UI proves a one-to-one link between each result row and an enduring source record route/identifier. Missing, malformed, or duplicated IDs within an event are a failure, not a reason to invent a title-based identifier.
- **untested required method:** For each future cell, use the observed total to set bounds sufficient to traverse every page. Reconcile total = unique stable IDs = row ledger count and require contiguous visible ranges from the first to last row.
- **untested required method:** Repeat the fully exhausted event independently under the same validated controls. If the source order is stable, require the same total and ordered stable-ID sequence. If no stable order can be set, require the same total, identical stable-ID set, page cardinalities, and complete range ledgers. Preserve duplicate discovery events across different partitions; only duplicates within a single source event are a completeness failure until explained.

## 7. Failure and zero rules

| Condition | Required result |
|---|---|
| Login, entitlement, CAPTCHA/challenge, inaccessible authorized loopback context, or unresolved current route | `total=null`; zero imports; quarantine diagnostic; recommend `skip_for_now` rather than repeated access attempts. |
| Query syntax error, rewritten/non-exact echo, unknown field behavior, wrong source scope, or unvalidated control | `total=null`; no partial import. |
| Missing/conflicting total, range, page, sort, row, or capture/export evidence | `total=null`; no partial import. |
| Changed total/order, stale/short page, pagination failure, duplicate/missing stable ID, parse failure, or two-pass mismatch | `total=null`; no partial import. |
| Limit/max-page prefix or any incomplete cell union | diagnostic-only partial artifact; never a candidate/import source. |
| Explicit native zero after exact echo, scope/control validation, and no rows | `total=0`, `records_retrieved=0`; valid zero event. |

The current pilot meets the first row: it is blocked with `total=null`. It does not establish any other row as current Scopus behavior.

## 8. Final-run procedure

This is a future procedure only; do not execute it while this guideline is draft and blocked.

1. Confirm `P-001` has fixed the exact common evidence cutoff and that a supervisor has accepted a revalidated Scopus guideline.
2. In the authorized loopback browser only, prove the current Advanced Search route, Scopus scope, fields, controls, query echo, total/range, zero behavior, and source order in a new adapter-owned tab.
3. Revalidate all 11 exact query files count-only and record one source total/explicit zero or one explicit failure per cell. Revalidate field/phrase/Boolean, punctuation/hyphen, case/acronym, expansion, wildcard, length, and rewrite behavior before changing any translation.
4. Validate the date and language method against the fixed cutoff. Do not add a publication/access/content limit unless a documented source limitation requires it.
5. Perform only the bounded identity/pagination preflight needed to prove capture; use `--skip-full-abstracts` and quarantined raw output.
6. Freeze the accepted query cells and controls. For every successful final cell, capture all rows with bounds at least the observed total, reconcile ranges and unique stable IDs, and preserve restricted raw material outside Git with a safe event manifest.
7. Repeat every fully exhausted cell. Require the two-pass agreement defined in section 6. Treat any mismatch as a failed event (`total=null`), quarantine all prefixes, and do not import anything from that event.
8. Only after complete source events are available may a later authorized process preserve discovery-event provenance and deduplicate across partitions/sources. Pilot data never enters that process.

## 9. Validation evidence

- **observed:** [`manifest.json`](pilots/S-D01-P01-20260820T234301-0400/manifest.json), [`observations.md`](pilots/S-D01-P01-20260820T234301-0400/observations.md), [`safe-summary.json`](pilots/S-D01-P01-20260820T234301-0400/safe-summary.json), [`safe-partition-summary.json`](pilots/S-D01-P01-20260820T234301-0400/safe-partition-summary.json), and [`query-integrity.json`](pilots/S-D01-P01-20260820T234301-0400/query-integrity.json) are diagnostic-only evidence.
- **inferred:** The adapter source/hash and the provisional `TITLE-ABS-KEY` translation are recorded in the pilot evidence index; they are not proof of the current interface.
- **official_documentation:** None accepted for a current Scopus behavior in this blocked pilot.
- **untested:** All source-interface behavior required for acceptance, including all 11 partition executions and complete capture, remains untested or blocked.

## 10. Remaining limits and protocol impact

- **observed:** No screening, candidate import, final event, `final-events/` change, shared-dictionary change, protocol change, or task-status change occurred.
- **inferred:** The draft preserves the protocol’s finite terms and Boolean relationships at local-text level; it introduces no semantic protocol change.
- **untested:** Current Scopus interface boundary, query acceptance, field behavior, date/language controls, limits, identity, pagination/export, and two-pass completeness remain unresolved.
- **required human verification:** Restore a normal authorized loopback CDP connection and complete the revalidation sequence; set the common cutoff under `P-001`; determine exact-day handling; validate language/filter behavior; and have the supervisor review and accept/revise this draft before any final execution.
