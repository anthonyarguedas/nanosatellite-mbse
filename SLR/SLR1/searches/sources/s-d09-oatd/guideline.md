---
task_id: S-D09
source_id: oatd
source_name: Open Access Theses and Dissertations (OATD)
method_type: direct
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: ad77460df82764312fb701f6be4ebf7eb5051c41
accepted_pilot_ids: []
---

# Source-specific guideline: Open Access Theses and Dissertations (OATD)

> **Draft blocked diagnostic.** This is not an accepted operating method and does not authorize a final event, screening, candidate creation, import, retrieval, or full-text download. Claim labels are **[observed]**, **[official_documentation]**, **[inferred]**, and **[untested]**. A Cloudflare managed challenge stopped the pilot before any query-cell submission.

## 1. Source boundary and access route

- **[official_documentation]** For this review, the protocol and source-interface crosswalk define OATD as the full public index of electronic theses and dissertations, an indexed online resource with a separate total; they place it in PRISMA 2020 `other_methods`, not databases/registers. This is the review's required accounting rule, not independent proof of the current OATD index boundary. See `E-04`.
- **[observed]** A normal rendered public OATD home page opened through local CDP without login or credential entry. It exposed branding, a basic GET form at `/oatd/search`, and a visible advanced composer form at `/oatd/search-composer`. Its homepage copy advertised theses/dissertations and more than 1,100 institutions. See `E-01`.
- **[observed]** A direct-HTTP attempt to retrieve OATD's public FAQ received HTTP 403 with `Cf-Mitigated: challenge` and a Cloudflare “Just a moment” response. Per the pilot stop rule, no source query, challenge interaction, credential entry, retry loop, endpoint substitution, or workaround followed. See `E-02`.
- **[untested]** The current OATD indexed-resource boundary; inclusion and completeness of participating repositories; scope of index metadata; relationship among index record, repository, resource/detail URL, and linked content; and exact source-total semantics are not established.
- **[official_documentation]** The protocol says an OATD record does not prove a linked full text remains available and that OATD metadata cannot establish degree completion, full-report language, or eligibility. Do not equate a future OATD record with a completed/eligible thesis, a working repository URL, or accessible full text. See `E-04`.

## 2. Interface and field behavior

- **[observed]** The visible basic form has `q`, hidden `form=basic`, and Search controls and uses GET `/oatd/search`. The visible advanced form has four `joiner`/`box`/`field` rows, three inter-row And/Or controls, language, country, earliest, latest, sort, Creative Commons, page-size, and hidden `form=advanced` controls. See `E-01`.
- **[observed]** The currently visible advanced field labels are any field, title, author name, abstract, university/publisher, subjects/keywords, and department/discipline. Visible advanced page-size choices are 30, 60, and 100. These observations do not establish result behavior. See `E-01`.
- **[untested]** Basic and advanced phrase/quote semantics; AND/OR/NOT semantics and precedence; parentheses; punctuation/hyphens; case/acronym behavior; stemming, lemmatization, automatic expansion; wildcard behavior; maximum query/GET length; query echo/rewrite; field scope; and all advanced-control semantics. No source query was submitted.
- **[inferred]** The prospective basic candidates use explicit parentheses, uppercase `AND`/`OR`, quoted multiword/hyphenated finite literals, no wildcard, and no field restriction. This is a local text construction, not an accepted OATD grammar.

## 3. Translation approach

- **[observed]** [`translation-spec.json`](translation-spec.json) maps every required partition to one exact UTF-8, BOM-free candidate file. [`pilots/S-D09-P01-20260821T043952+0000/translation-integrity.json`](pilots/S-D09-P01-20260821T043952+0000/translation-integrity.json) found no missing designated finite dictionary terms, wildcard, prohibited SmallSat term, unbalanced parenthesis, encoding error, or hash mismatch in local checks.
- **[untested]** The candidate files are not current source-native translations until a challenge-free public basic/advanced diagnostic proves parser acceptance, exact echo/rewrite, fields, and lossless semantics. No candidate is usable for a final run.

| Partition | Prospective cell | Exact file | Current status |
|---|---|---|---|
| A1 | A1-C1 | [`queries/A1.txt`](queries/A1.txt) | blocked / untested |
| A2 | A2-C1 | [`queries/A2.txt`](queries/A2.txt) | blocked / untested |
| A3 | A3-C1 | [`queries/A3.txt`](queries/A3.txt) | blocked / untested |
| B1 | B1-C1 | [`queries/B1.txt`](queries/B1.txt) | blocked / untested |
| B2 | B2-C1 | [`queries/B2.txt`](queries/B2.txt) | blocked / untested |
| BG1 | BG1-C1 | [`queries/BG1.txt`](queries/BG1.txt) | blocked / untested |
| BG2 | BG2-C1 | [`queries/BG2.txt`](queries/BG2.txt) | blocked / untested |
| BC1 | BC1-C1 | [`queries/BC1.txt`](queries/BC1.txt) | blocked / untested |
| BT2 | BT2-C1 | [`queries/BT2.txt`](queries/BT2.txt) | blocked / untested |
| V1 | V1-C1 | [`queries/V1.txt`](queries/V1.txt) | blocked / untested |
| O1 | O1-C1 | [`queries/O1.txt`](queries/O1.txt) | blocked / untested |

- **[inferred]** Each file is intentionally an unsplit candidate that locally preserves the corresponding normative Boolean expression. If a future validated interface cannot accept a complete cell, prospectively define all replacement cells with a distributive Boolean proof, complete every cell twice, preserve cell provenance, and union only stable OATD Record IDs. A failed or missing cell makes the partition `total=null`; counts never prove a union.

## 4. Controls and common limits

- **[official_documentation]** The review's fixed lower bound is 2011-01-01; its common upper cutoff remains unset under P-001. The protocol requires one unchanged cutoff for every final source. See `E-04`.
- **[observed]** Advanced earliest/latest text controls and a language selector with English are visible. Date format, inclusivity, indexed date field, exact-day behavior, and language-filter behavior were not tested. See `E-01`.
- **[inferred]** Apply no date, language, country, institution/repository, Creative Commons/access, content, peer-review, publication-type, venue, or other discovery limit unless a future accepted pilot validates the exact control and the protocol authorizes it. The current pilot submitted no search and applied none.
- **[untested]** A future re-pilot must test the exact P-001 date once set. If native exact-day control is unavailable, first fully preserve the unaltered validated source result, then apply a separately auditable local exact-day procedure to captured source date labels; retain unresolved precision and do not screen while doing so.

## 5. Retrieval, pagination, and export

- **[observed]** The advanced form visibly offers page sizes 30, 60, and 100; no result page, range, page size in effect, ordering, pagination link, capture, or export was tested. See `E-01`.
- **[untested]** Basic page size, displayed total/range wording, result route, detail route, total cap, pagination, sort stability, duplicate behavior, metadata fields, export/capture behavior, and rights restrictions.
- **[inferred]** A later successful pilot must preserve safe source totals/ranges and ID ledgers, while retaining raw source/adaptor responses only in ignored worklogs. It must not download full text merely to test OATD metadata routes.

## 6. Stable identity and completeness

- **[untested]** No current Record Details page was opened. No OATD Record ID, record/detail route, repository metadata, resource URL, duplicate behavior, or resource accessibility was observed.
- **[inferred]** A future stable identity may be adopted only after the current public Record Details route proves a visible OATD Record ID and corresponding unescaped route identifier agree. Repository, university/publisher, DOI, and resource URL must remain metadata/provenance fields, not substitute identities.
- **[inferred]** Before a final event, validate all page ranges and source totals, require a nonempty unique stable Record ID on every row, reconcile total = rows = unique IDs, and repeat a complete comparable pass. A changed total/order, short/stale page, missing/duplicate ID, inaccessible expected detail page, parse failure, cap, or unreconciled range requires `total=null` and no partial import.

## 7. Failure and zero rules

- **[observed]** The public FAQ request's Cloudflare managed challenge is an access/challenge failure, not a source zero. The pilot records `total=null`, zero retrieved diagnostic records, and recommendation `skip_for_now`. See `E-02`.
- **[untested]** OATD's native no-results wording, exact query echo, total/range controls, syntax failure behavior, and explicit-zero conditions.
- **[inferred]** A future `total=0` is valid only after the exact submitted query/echo, current scope/controls, a native no-results condition, and zero visible rows are all observed. Access, challenge, busy, transport, syntax, rewrite, control, total, pagination, export/capture, identity, duplicate, or completeness failures require `total=null`, never a partial prefix or zero.

## 8. Final-run procedure

1. **[untested]** Do not run a final event until P-001 supplies the exact common cutoff, a supervisor accepts a revalidated guideline, and R-002 is authorized.
2. **[inferred]** Reopen only the normal public rendered OATD interface. If a login, consent/auth wall, CAPTCHA, Cloudflare, Server Too Busy state, or other challenge appears, stop once with `total=null`, no import, and `skip_for_now`; do not bypass, retry-loop, or enter credentials.
3. **[inferred]** Revalidate boundary, basic/advanced controls, public scope, query grammar, exact echo/rewrite, field behavior, punctuation, case/acronym behavior, expansion/wildcards, length/GET behavior, date/language controls, and all 11 byte-pinned query candidates before calling any translation lossless.
4. **[inferred]** Validate results, stable OATD Record ID, repository/resource treatment, total/range/page behavior, duplicate handling, and two complete ID passes. Use no access/content/type limit and do not download full text.
5. **[inferred]** For each final partition/cell, retain only after full two-pass reconciliation; on any failure record `total:null`, quarantine any raw prefix in ignored storage, and import nothing.
6. **[inferred]** Create final events only later in the authorized final-event namespace. This pilot does not authorize that action.

## 9. Validation evidence

- **[observed]** `E-01` is the parsed safe browser UI summary in the ignored worklog; it supports only the visible home/basic/advanced form facts.
- **[observed]** `E-02` is the parsed HTTP diagnostic showing `Cf-Mitigated: challenge`; its raw response remains ignored and is not a source total or documentation proof.
- **[observed]** `E-03` is the local query-file integrity check; it supports only local byte/term/parenthesis checks.
- **[official_documentation]** `E-04` is the review protocol and crosswalk governing OATD accounting and later eligibility/retrieval cautions; it is not OATD interface proof.
- **[untested]** No current source query, result record, detail record, indexed-resource boundary proof, native zero, date/language behavior, stable identity, pagination, export, duplicate, or completeness proof is available from this stopped pilot.

## 10. Remaining limits and protocol impact

- **[observed]** The Cloudflare managed challenge blocks source-interface validation. The smallest follow-up is one normal rendered-browser public access preflight after the challenge condition is absent; it must stop again on any challenge.
- **[untested]** All direct query behavior, all 11 source executions, exact boundary/provenance, date/language controls, result accounting, identity, and completeness remain unresolved.
- **[observed]** No screening, candidate creation/import, final-event write, full-text download, credential entry, or external/depth-3 delegation occurred.
- **[inferred]** No protocol semantic change is proposed. `semantic_change:false` is recorded in the translation specification and pilot manifest; only a future verified interface limitation could require a documented method or protocol decision.
