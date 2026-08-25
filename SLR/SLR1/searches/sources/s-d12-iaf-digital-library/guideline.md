---
task_id: S-D12
source_id: iaf-digital-library
source_name: IAF Digital Library
method_type: direct
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: 26dab91618e9d679db077bfd3e8808fc3c7097ad
accepted_pilot_ids: []
---

# Source-specific guideline: IAF Digital Library

> **Live-first validation:** Apply the [current policy](../../live-first-validation-policy.md). Real-page behavior is primary; use only the minimum launch gate before live work, inspect technical failures on the owned page, patch immediately, and retest live after minimal changed-path checks. Broad offline suites are deferred until a working route is being accepted or merged.


This is a new-run, diagnostic-only draft. No IAF request, source observation,
pilot, screening decision, candidate import, or final event was made while
preparing it. Behaviour labels below mean **[inferred]**, **[untested]**, or
**[planned]** unless they explicitly say that they come from the local adapter
implementation. The current interface must be checked during P01; local code
is not live evidence.

## 1. Source boundary and access route

- **[inferred from the current local adapter]** The boundary is the full public
  IAF Digital Library at `https://dl.iafastro.directory`, using the normal
  server-rendered `/search/` metadata route and its public event-paper landing
  pages. The default query has no event restriction.
- **[planned]** P01 must confirm the full-library boundary, the echoed query,
  and the absence of an implicit event restriction. Do not pass
  `--event-code`; that option is an explicit narrowing and is not part of this
  packet.
- **[inferred from the adapter]** The route is anonymous HTTP GET. Do not use
  `/api/`, authentication/cart routes, manuscript forms, DOI destinations,
  PDF/full-text links, browser state, or credentials. This is not a browser
  source and requires no CfT lease.
- **[untested]** Current authorization, source coverage, and any public
  collection exclusions remain unknown. A redirect, login, challenge, access
  page, or unexpected route is a source failure, not an empty result.

## 2. Interface and field behaviour

- **[inferred from the current adapter and translation draft]** Cells use an
  unqualified public-search expression. The exact indexed fields, field
  combination, stemming, lemmatization, case, punctuation/hyphen handling,
  acronym boundaries, automatic expansion, and query precedence are untested.
- **[inferred]** The draft source-native spelling is a fully parenthesized
  Boolean expression with double-quoted literals, uppercase `OR`, and
  uppercase `AND`. Every normative finite spelling is retained literally;
  no wildcard or S-C01 candidate term is used. The exact cells are in
  [`translation-spec.json`](translation-spec.json) and `queries/`.
- **[untested]** No usable controlled vocabulary or distinct indexed-term
  supplement is accepted. A future descriptor may supplement, never replace,
  the mandatory free text, only after scope, hierarchy, mapping, and known-item
  behaviour are demonstrated.
- **[inferred, unaccepted pair fallback]** For G_model, G_structure, C1, and
  T2, the draft uses a broader unqualified conjunction of each left term with
  the complete right-term group. This retains an exact pair but may retrieve
  cross-field or distant matches. It is not a claim that IAF implements the
  protocol's unordered same-field, at-most-five-token rule. P01/P02 must test
  this boundary and record the limitation before source acceptance; do not
  silently narrow or delete pair clauses.

## 3. Translation approach

[`translation-spec.json`](translation-spec.json) maps the exact normative
partitions A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2. The partitions retain
the current protocol expressions and roles:

- A1: `P AND E_H AND M_H`;
- A2: `P AND E_F AND (M_H OR M_B)`;
- A3: `P AND E_H AND M_B`;
- B1: `P AND M_H`;
- B2: `P AND M_B AND R`;
- BG1: `P AND G_model`;
- BG2: `P AND G_structure`;
- BC1: `P AND C1`; and
- BT2: `P AND M_B AND T2`.

The local adapter rejects a query longer than its source-free
`MAX_SOURCE_QUERY_CHARACTERS = 500` check. This packet therefore uses a
**499-character safety ceiling** (excluding the terminal LF) and a deterministic
contiguous balanced Cartesian sharding algorithm. It does not truncate a
concept, use `nanosat*`, remove a phrase, or add a synonym. Every combination
of shards is required; the stable event/paper identity union of complete cells
is the partition result. The generated counts are A1 80, A2 100, A3 60, B1 6,
B2 60, BG1 6, BG2 4, BC1 12, and BT2 336 (664 cells total). The largest cell
is 498 characters. These are source-free adapter-limit facts, not live source
counts or live syntax validation.

A cell failure makes that cell's total `null` and invalidates the partition;
never import a successful prefix from an incomplete lossless union. Each
successful cell remains a separate diagnostic or final discovery event before
identity union and deduplication.

## 4. Controls and common limits

- **[planned]** The evidence lower bound is 2011-01-01. Before P-001 supplies
  the common exact cutoff, P01 uses only a diagnostic bound:
  `PILOT_YEAR=$(date -u +%Y)`, with `--year-start 2011 --year-end "$PILOT_YEAR"`.
  This is an inclusive client-side card/detail publication-year bound and is
  not the common cutoff.
- **[inferred from the adapter]** The adapter does not translate the year
  bounds into IAF's query expression. It reports the source total before
  client-side year exclusions. Exact date precision and the treatment of
  records in the cutoff year are **[untested]** and must be reported rather
  than silently treated as exact.
- **[planned]** Do not apply a language, publication-type, access, peer-review,
  venue, content-type, or major-topic discovery limit. Determine English full
  report status during retrieval/screening under the protocol.
- **[planned]** All operations are serial. Although no browser lease is used,
  this source phase must not overlap another live source phase under current
  policy. Do not acquire a CfT lease or use a fresh browser/profile/port.

## 5. Retrieval, pagination, and export

- **[inferred from the adapter]** Search pages use a fixed 50-record page size
  with offset parameter `o` and source query parameter `q`; the adapter
  validates the echoed query, source total, displayed range, normal GET
  pagination form, result cards, and canonical detail links.
- **[inferred]** A detail request is made only to the card-proved public
  `/event/{event}/paper/{paper}/` route. The retained allowlisted metadata is
  title, authors, DOI when exposed, publication year, abstract, event code,
  paper number, publication title, source rank, and the public landing URL.
  No PDF or manuscript form is requested.
- The adapter's bounded limits are `--limit 1..5000`, `--max-pages 1..100`,
  per-request `--timeout 0..300` (strictly positive),
  `--request-delay-seconds 0..60`, and `--retries 0..5`. P01 uses
  `--limit 1 --max-pages 1 --timeout 20 --request-delay-seconds 1
  --retries 1`.
- P01 outputs are diagnostic only. They are written to new, unique paths and
  are never copied to `final-events/`, screening, or the candidate corpus.
  The shared output saver is create-only/no-clobber; a destination collision
  is a hard stop before source work.

## 6. Stable identity and completeness

- **[inferred from the adapter]** The stable source identity is the compound
  `(event_code, paper_number)`, represented as
  `iaf-digital-library:{event}:{paper}`. A DOI or title must not substitute
  for a missing, duplicate, or changed source identity.
- The search card and detail page must reconcile event, paper number, title,
  and publication year; the detail breadcrumb must identify the expected
  event. Duplicate IDs or URLs across pages, missing IDs, conflicting links,
  changed totals, changed ranges, short/nonterminal pages, or detail mismatch
  are completeness failures.
- **[untested]** Stable ordering and a two-pass completeness proof have not
  been demonstrated. P01 is deliberately bounded and cannot establish final
  completeness. A later accepted final method must exhaust every cell, retain
  its unchanged source total and ordered identity ledger, and perform two
  identical complete passes (or a separately validated equivalent) before
  that cell can contribute to PRISMA accounting.

## 7. Failure and zero rules

- Retry only the adapter's finite transient set (408, 425, 429, 500, 502, 503,
  504, and network/read failures) under the declared retry count and pacing.
  A challenge, login, CAPTCHA, access denial, redirect, or unsafe route is
  never retried or bypassed. Preserve the same HTTP operation and stop when
  the finite policy is exhausted.
- Query syntax/length errors, changed query echo, unexpected content type,
  malformed XHTML, missing or changed total/range, pagination mismatch,
  duplicate/missing identity, detail mismatch, parse failure, and incomplete
  traversal are failures. Write `total=null`, retain no partial prefix, and
  stop the affected operation. An explicit native no-results summary with its
  exact query echo is the only valid zero (`total=0`).
- A timeout, access/challenge page, transport error, empty local buffer, or
  skipped operation is never zero. A bounded positive retrieval is `partial`,
  not complete, even if its displayed total is small.

## 8. Final-run procedure

Do not execute a final event from this draft. Execute the P01 procedure in
[`p01-execution-plan.md`](p01-execution-plan.md) only after the controller has
created the runtime campaign and manifest from the shared templates. It
creates no campaign or attempt in this new packet.

For any later final event, the controller must execute every cell listed in
`translation-spec.json` serially, retain one unique output/receipt per cell
(and per complete pass), apply the exact P-001 cutoff without silently
substituting the pilot year, reconcile stable identities only after every cell
is complete, and preserve `null` for every failed cell. No screening or
candidate import is allowed in P01.

## 9. Validation evidence

- **[source-free]** Adapter entry point:
  `../agent-tools/academic-research/skills/academic-search/scripts/search_iaf_digital_library.py`.
- **[source-free]** Focused test:
  `../agent-tools/academic-research/skills/academic-search/tests/test_search_iaf_digital_library.py`.
  The current focused suite passed offline before this packet was written. The
  CLI `--help` was also checked offline. Neither is live source evidence.
- **[source-free]** Translation files and hashes are recorded in
  [`translation-spec.json`](translation-spec.json); no pilot manifest,
  campaign, or accepted pilot exists because this is a brand-new source.
- **[untested]** Current interface field behavior, exact phrase/Boolean
  semantics, pair behavior, date precision, language metadata, explicit zero,
  pagination, stable ordering, complete retrieval, and failure pages require
  the bounded P01 operations. No human methodological change is proposed.

## 10. Remaining limits and protocol impact

The packet is launch-ready for a bounded diagnostic P01, not accepted for a
final search. Remaining blockers are the absence of live observations, the
unresolved exact P-001 cutoff/date precision, unvalidated field and pair
semantics, and the missing two-pass completeness evidence. The 500-character
handling is an implementation constraint only; no concept, Boolean
relationship, source boundary, language/content limit, recall rule, or PRISMA
definition was changed.
