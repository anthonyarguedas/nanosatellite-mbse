---
task_id: S-D11
source_id: arxiv
source_name: arXiv Advanced Search
method_type: direct
status: draft
guideline_version: 0.1.0
validated_at: null
protocol_commit: df530c27c2319f46acf86d8f1715bfde2d8719c1
adapter_path: ../../../../../../agent-tools/academic-research/skills/academic-search/scripts/search_arxiv.py
adapter_version: "2"
adapter_sha256: c794026802ab00365214f5dcf470ef848ec97ffa4a0750de777f083849a2356c
accepted_pilot_ids: []
---

# Source-specific guideline: arXiv Advanced Search

> **Live-first validation:** Apply the [current policy](../../live-first-validation-policy.md). Real-page behavior is primary; use only the minimum launch gate before live work, inspect technical failures on the owned page, patch immediately, and retest live after minimal changed-path checks. Broad offline suites are deferred until a working route is being accepted or merged.


This is a **source-free P01 launch draft**. It is not an accepted source method and contains no live observation, completed campaign, pilot attempt, screening decision, candidate record, or final event. Source-interface statements are labelled **[observed]** only when they describe the local adapter code, **[official_documentation]** only when first-party documentation is actually available in the packet, **[inferred]** for a method consequence, and **[untested]** for current arXiv behavior. No network or provider route was accessed while preparing this packet.

## 1. Source boundary and access route

- **[protocol]** The source boundary is the full multidisciplinary arXiv preprint repository, tracked separately as the `arxiv` interface and as a database/registers source in the current crosswalk. Do not substitute export.arxiv.org, the Atom API, an external index, a publisher page, or a selected arXiv subject category.
- **[observed]** The assigned adapter is a browser-only client for the normal rendered `https://arxiv.org/search/advanced` route. It does not use the Atom API, a direct HTTP client, a fresh browser by default, or a source-side login flow.
- **[observed]** The adapter attaches to the shared local CDP endpoint by default at `http://127.0.0.1:9222`, proves an explicitly supplied open arXiv target when `--target-id` is used, creates one separate owned page, and closes only that page with verified disappearance. The shared lease, profile, browser epoch, broker anchor, sleep checks, receipt, and release remain the controller/supervisor responsibility described in `searches/README.md`.
- **[untested]** Current anonymous arXiv availability, challenge state, exact public corpus boundary, source retention, and whether the rendered route exposes all records in the repository are not claimed. P01 must stop on an access challenge, login, or other access-control page; it must not solve or evade it.
- **[inferred]** The source boundary does not make every result an eligible report. Full-text completion, English language, report type, date/version rule, population, MBSE, and EPS eligibility remain later protocol decisions.

## 2. Interface and field behavior

- **[observed]** The adapter's allowlisted rendered projection expects one Advanced Search form with one `terms-0-term` value, `terms-0-operator=AND`, and `terms-0-field=all`. It also records the visible all-classification, cross-list, submitted-date, abstract-display, page-size, and relevance controls. These are local adapter expectations, not live source acceptance evidence.
- **[untested]** arXiv's current Boolean parser, parentheses, straight-quote phrase handling, punctuation and hyphen normalization, case policy, stemming or lemmatization, automatic expansion, wildcard behavior, token boundaries for acronyms, query rewrite, and query-length limit have not been observed. The P01 cells preserve literal terms and use only the draft `AND`/`OR`/parenthesis/quote syntax.
- **[untested]** The `all` field's precise title, abstract, author, comment, journal-reference, category, or other metadata coverage is not assumed. A match in the source `all` control is not described as a title/abstract-only match.
- **[untested]** No usable arXiv controlled vocabulary or distinct indexed-term supplement has been established. Do not add category labels, subject headings, or a generic `systems engineering` descriptor to any cell. Free text remains mandatory under the protocol.
- **[protocol]** `P`, `E_H`, `E_F`, `M_H`, `M_B`, `R`, `G_model`, `G_structure`, `C1`, and `T2` retain their exact current dictionary meanings. S-C01 candidate terminology is not included.

## 3. Translation approach

[`translation-spec.json`](translation-spec.json) is the exact source-native specification. Every cell is a UTF-8 file containing one all-fields term entered verbatim into the visible arXiv term row. The nine cells are:

| Partition | Protocol expression | Role | Exact cell |
| --- | --- | --- | --- |
| A1 | `P AND E_H AND M_H` | Named EPS × explicit MBSE | [`queries/A1.arxiv-advanced.txt`](queries/A1.arxiv-advanced.txt) |
| A2 | `P AND E_F AND (M_H OR M_B)` | EPS functions or analyses × all model terms | [`queries/A2.arxiv-advanced.txt`](queries/A2.arxiv-advanced.txt) |
| A3 | `P AND E_H AND M_B` | Named EPS × broad structured model | [`queries/A3.arxiv-advanced.txt`](queries/A3.arxiv-advanced.txt) |
| B1 | `P AND M_H` | Embedded-thread baseline | [`queries/B1.arxiv-advanced.txt`](queries/B1.arxiv-advanced.txt) |
| B2 | `P AND M_B AND R` | Controlled broad-model expansion | [`queries/B2.arxiv-advanced.txt`](queries/B2.arxiv-advanced.txt) |
| BG1 | `P AND G_model` | Precise reusable model or template | [`queries/BG1.arxiv-advanced.txt`](queries/BG1.arxiv-advanced.txt) |
| BG2 | `P AND G_structure` | Structural reusable artifact | [`queries/BG2.arxiv-advanced.txt`](queries/BG2.arxiv-advanced.txt) |
| BC1 | `P AND C1` | Conservative central asset | [`queries/BC1.arxiv-advanced.txt`](queries/BC1.arxiv-advanced.txt) |
| BT2 | `P AND M_B AND T2` | Model-linked tailoring | [`queries/BT2.arxiv-advanced.txt`](queries/BT2.arxiv-advanced.txt) |

- **[inferred]** Each partition currently has one cell, and its lossless union is the identity set of that cell. The current local adapter safety bound is 50,000 query characters; the largest draft cell is far below that bound. This is not evidence that arXiv's server or rendered form accepts every cell.
- **[untested]** arXiv has not yet validated this Boolean syntax or the source-side meaning of the all-fields boundary. No cell may be narrowed, wildcard-compressed, or silently rewritten after a live parser failure. A length-driven split must be defined prospectively, retrieve every shard completely, and reconcile stable arXiv IDs before any source event can be accepted.
- **[inferred]** The pair-bearing cells use the protocol-permitted broader fallback: a left OR-group and right OR-group are conjuncted within the one visible `all` route. This cannot lose an exact unordered pair if the route is one searchable field, but it may admit distant or cross-subfield matches. It is not claimed to implement the exact five-intervening-token rule until P01 validates the boundary.
- **[protocol]** The cells generate candidates only. They do not establish Route A/Route B eligibility, artifact genericity, reuse, outcomes, V&V, or report inclusion.

## 4. Controls and common limits

- **[observed]** The adapter exposes `--year-start` and `--year-end` integer controls and renders `date-filter_by=date_range`, `date-date_type=submitted_date`, and the corresponding year values. With no year bound it renders `all_dates` and empty date values. The adapter checks that the rendered controls equal the requested values.
- **[untested]** The source's inclusive date semantics, timezone, date precision, version-date display, and treatment of a one-sided bound have not been observed. The adapter's current control is year-granular; it is not an exact day cutoff.
- **[protocol]** The evidence window starts at `2011-01-01`. P-001 has not set the common final cutoff. In P01 only, use the actual UTC execution year as a clearly labelled **pilot-date diagnostic upper-year bound**. This bound is neither P-001 nor a final cutoff. Do not use an execution timestamp to claim a final date result.
- **[protocol]** If the source cannot apply the eventual exact P-001 day locally, retain the unaltered source total and apply the exact date/version rule locally, reporting removed and unresolved records. The current adapter's submitted-year projection is not enough by itself for that final decision.
- **[protocol]** No native English filter is applied. No publication-type, access, peer-review, venue, major-topic, full-text, or content-type discovery limit is applied. English full text and the permitted report types are determined under the protocol after retrieval.
- **[observed]** The local safety defaults are a requested limit of 20, native page sizes 25/50/100/200 with a local maximum of 100, maximum three pages, a 30-second finite browser timeout, and a 0.2-second page delay. These are bounded adapter settings, not claims about arXiv source caps or rate policy. P01 may use only the larger bounds predeclared in `p01-execution-plan.md`.

### arXiv publication type and version handling

- **[protocol]** An arXiv result is a repository preprint record. The source label `Preprint`, an arXiv identifier, a DOI, or an abstract does not by itself prove a substantial completed primary report, English full text, or peer review.
- **[observed]** The adapter emits the shared `documentType` value `Preprint`, a stable bare `paperId`, `sourceRecordId`, an optional separately preserved `sourceRecordVersion`, and the visible `sourceSubmittedDate` label. It does not infer `v1` when the rendered route has no version suffix.
- **[protocol]** For screening, use the earliest arXiv version that contains a substantial completed report, record every available version and date, and keep preprint/formal-version provenance. Do not merge versions merely because title, DOI, authors, or topic appear similar.
- **[protocol]** **An arXiv posting/submission date is not another source's publication date.** The normalized `year` is a submitted-year convenience field and is explicitly tagged `arxiv_submitted_date_year_not_publication_date`; it must not be used to relabel a journal, conference, thesis, or formal publication date, and it does not resolve the protocol's full version/date rule.

## 5. Retrieval, pagination, and export

- **[observed]** Count-only mode submits the normal rendered search and validates the first rendered result state, exact heading total/range, query echo, all-fields control, date controls, abstract-display control, page size, and relevance control, while retaining no bibliographic rows and writing no merge-compatible CSV.
- **[observed]** Non-count-only collection retains source-order rows up to `--limit`; it records every source row on visited pages for page/total reconciliation, uses the rendered native Next control, and validates that page ranges and totals do not change. It uses each retained row's visible native `More` control for a full abstract when requested; it does not fan out to abstract pages or download PDFs.
- **[untested]** Native export, source bulk export, source result caps, stable result ordering across passes, and any exact full-repository traversal have not been observed. A PDF link is provenance only and is not an access or publication-type filter.
- **[protocol]** P01's metadata/abstract diagnostic is bounded to at most two retained records and at most two pages. It is diagnostic only: no screening, import, merge, or report-level decision is allowed.
- **[inferred]** A later complete final event must retrieve every row in each accepted cell, reconcile the exact source total and stable identity ledger, and perform the source's validated equivalent of two complete ordered passes. A P01 prefix or count-only artifact cannot satisfy final completeness.

## 6. Stable identity and completeness

- **[observed]** The adapter requires one canonical same-origin `/abs/<id>` route per row, validates the optional `/pdf/<id>` route against the same base ID and version, rejects duplicate IDs within a page and across visited pages, and retains the base ID as `paperId`.
- **[observed]** An explicit route suffix such as `v2` is preserved as `sourceRecordVersion` and in the canonical route while the stable base identity remains `sourceRecordId`/`paperId`. A missing suffix is represented as not exposed, not as `v1`.
- **[untested]** The current rendered result's actual version suffix, persistence of arXiv IDs, duplicate behavior, and identity stability across two complete passes have not been observed. DOI, title, author, or synthesized rank is never an identity fallback.
- **[inferred]** A missing, malformed, conflicting, or repeated base ID/version route is an identity failure. A failure, stale page, changed total, short nonterminal page, or pass mismatch has `total=null` and no importable prefix.
- **[protocol]** Version identity is a report-level provenance matter as well as a source-record matter. Preserve source version/date evidence before any later companion-report or family decision.

## 7. Failure and zero rules

- **[observed]** The adapter distinguishes input, browser, request, access/challenge, protocol, and snapshot-change failures; it does not automate login, CAPTCHA, challenge solving, profile rotation, or API fallback. It uses only a finite passive state-poll deadline while a normal browser page may settle.
- **[protocol]** A challenge, login, anti-automation page, busy/service page that is not a reconciled result, timeout, non-arXiv route, bad request, query rewrite, dropped control, malformed heading, changed total, short/stale page, missing or duplicate identity, abstract-expansion failure, pagination failure, or cleanup failure is a failed operation. Record `total=null`, stop the operation, discard any prefix, and do not import it.
- **[observed]** The adapter's failure artifact now discards retained rows and exposes `total=null` even when a source total was seen before a later failure. It marks the artifact non-mergeable and records only bounded failure progress; a source total observed before failure is not a successful event total.
- **[protocol]** `total=0` is valid only for an explicit rendered no-results state whose native route and visible controls exactly match the requested query, all-fields boundary, date controls, and other fixed controls, with no rows or next page. A timeout, challenge, bad request, empty local buffer, or adapter failure is never zero.
- **[protocol]** A positive count-only result with zero retained rows is `count_only`, not an explicit source zero. It is not screening data and is not merge-eligible.
- **[protocol]** Busy and challenge handling is explicit: keep the same owned page, do not automatically reissue a failed operation, do not create a fresh page/browser/profile/port, and stop when the predeclared finite timeout or lease policy expires. A user termination is `cancelled`; cancel and collect the attached child, verify owned-page closure and lease release, and preserve the immutable receipt.

## 8. Final-run procedure

Do not execute a final event from this draft. After P01 and source-method acceptance, a later R-002 operator shall:

1. Confirm P-001's exact common cutoff and use the same value for every source. Confirm the accepted adapter commit and the accepted translation-spec/query hashes.
2. Acquire the one shared CfT lease through the exact command in [`p01-execution-plan.md`](p01-execution-plan.md), with a new per-attempt receipt, the single proven shared context, one adapter-owned page at a time, and no fresh browser/profile/port. The normal route does not require an existing arXiv target.
3. Verify the all-fields route, query echo, Boolean/phrase behavior, date control semantics, no language/publication-type/access limits, and no usable controlled vocabulary. Stop on any unresolved semantic rewrite; do not choose an unlogged narrower query.
4. Execute all nine cells from [`translation-spec.json`](translation-spec.json), including every prospective shard if a later accepted length rule requires one. Retain separate partition events and reconcile each cell/union by stable base arXiv ID and explicit version evidence.
5. Retrieve complete records only after exact total, page-range, identity, and completeness checks pass. Preserve submitted-date/version provenance without calling it a formal publication date.
6. Keep all pilot diagnostics outside `final-events/`, screening, imports, and PRISMA final accounting. A blocked, failed, or cancelled event imports no partial prefix.

## 9. Validation evidence

- **[observed]** Source-free focused tests are in the assigned agent-tools path: `academic-research/skills/academic-search/tests/test_search_arxiv_browser.py`. They cover the rendered Advanced Search URL, all-fields and submitted-date controls, version-separated identity, explicit zero, failure/null accounting, count-only no-row behavior, native abstract expansion, and owned-page cleanup wiring.
- **[observed]** The adapter's offline CLI help path works without opening a browser or contacting arXiv. No provider request was made for this packet.
- **[untested]** No P01 manifest, campaign, source receipt, source count, source zero, source failure, source field observation, pagination observation, or live abstract observation exists yet. `accepted_pilot_ids` therefore remains empty and no gate is accepted.
- **[protocol]** At runtime, create the initial campaign and manifest from the shared templates before source work. Do not pre-create or commit a completed campaign/attempt for this brand-new source.

## 10. Remaining limits and protocol impact

- **[untested]** Current source availability, parser semantics, all-fields subfield coverage, phrase/token behavior, query length, controlled/indexed terms, year/date meaning, language metadata, publication/version display, pagination ordering, identity persistence, and complete retrieval remain unresolved until P01.
- **[untested]** The current adapter does not itself establish the earliest substantial arXiv version or exact day-level cutoff required for final screening. P01 is a diagnostic launch, not a final-search implementation.
- **[inferred]** If P01 exposes an implementation defect that can be corrected without changing review semantics, the controller may allocate only the predeclared bounded technical correction. A change to concepts, Boolean meaning, field/source boundary, date/language/content limits, identity rule, or PRISMA accounting is a methodological decision and must not be made in this packet.
- **[protocol]** No protocol concept, query semantic, source boundary, date/language/content limit, recall rule, completeness definition, or PRISMA accounting has been changed.

Historical or future browser endpoint/profile facts do not override the shared contract. Every future browser phase uses the shared CfT lease at `127.0.0.1:9222` and a new immutable receipt.
