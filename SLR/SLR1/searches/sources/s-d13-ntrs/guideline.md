---
task_id: S-D13
source_id: ntrs
source_name: NASA Technical Reports Server (NTRS) / NASA STI Repository
method_type: direct
status: accepted
guideline_version: 1.0.0
validated_at: 2026-08-21
protocol_commit: 7d564870a36d049716b66c9f9770554ecb04e414
accepted_pilot_ids: [S-D13-P01-20260821T034216+0000]
---

# Source-specific guideline: NASA Technical Reports Server (NTRS)

> **Accepted reusable guideline.** The linked pilot remains diagnostic and supplies no candidate, screening decision, final event, or import authorization. Acceptance applies to the operating method and exact translations, subject to the final-run preconditions below.
>
> **Evidence labels:** **[observed]** is a bounded 2026-08-21 diagnostic; **[official_documentation]** is NASA's public guidance; **[inferred]** is an operating conclusion from those facts; **[untested]** must not be relied on for acceptance. Evidence is indexed in [`pilots/S-D13-P01-20260821T034216+0000/evidence-index.json`](pilots/S-D13-P01-20260821T034216+0000/evidence-index.json).

## 1. Source boundary and access route

- **[official_documentation]** The NTRS landing page calls the service the NASA STI Repository/NASA Technical Reports Server and describes public access to NASA metadata records, online documents, images, and videos; it lists conference papers, journal articles, meeting papers, patents, research reports, images, movies, and technical videos as included STI types. It separately says registered content is the complete NASA and non-NASA aerospace STI collection and requires NASA authentication. See `E-02` in the evidence index.
- **[observed]** Anonymous `POST https://ntrs.nasa.gov/api/citations/search` returned a JSON `stats`/`results` envelope without credentials. A default-scope probe returned public records from more than one current index bucket; no `index` restriction was supplied. See `E-03`, `E-04`, and `E-06`.
- **[inferred]** For this review, the source boundary is the default anonymous public `citations` search scope exposed by NTRS, with no `index`, publication-type, access, venue, or content-type filter. It is not NTRS Registered and it does not add the separately surfaced `/pubspace/search` route.
- **[observed]** The response exposes `stiType`/`stiTypeDetails`, distribution, dissemination, date, author/organization, identifier, download, and related-record metadata. The pilot observed multiple STI types, including presentations, conference papers, abstracts, preprints, reprints, technical memoranda/publications, contractor/grantee reports, proceedings, book chapters, posters, and other records. See `E-10` and `E-16`.

## 2. Interface and field behavior

- **[official_documentation]** NASA says the search box searches all metadata fields and then document full text; it identifies title, abstract, author, and full text as result-match locations. NASA documents the visible filters Title, Author, Organization, Publication Date, Date Acquired, Type, Center, Subject Category, Report Numbers, Funding Numbers, and Keywords. See `E-01`.
- **[observed]** The public client and live endpoint support `GET` and `POST` `/api/citations/search`; the final method uses **POST** with an UTF-8 `application/json` body containing `q`, `page`, `highlight`, `published`, and explicit `sort`. URL-encoded GET returned a valid query total, but its supplied JSON-shaped `page` control was not honored in this diagnostic; it is not the final route. See `E-03`, `E-04`, and `E-05`.
- **[inferred]** Do not restrict `q` to title or abstract: retain the documented global search scope. A POST title probe changed the controlled total from 133 to 55, but displayed/lowercase title values had the same total; general field-filter and case semantics are not established, so no field filter is adopted. See `E-14`.

| Behavior | Accepted source-native rule | Evidence status |
|---|---|---|
| AND | Use `+` between fully parenthesized blocks. A space also returned the same controlled total, but is not used. | **[official_documentation] [observed]** `nanosatellite+CubeSat` and the space form both returned 55; see `E-01`, `E-07`. |
| OR | Use `|` inside parentheses. | **[official_documentation] [observed]** The controlled OR returned 1,230; see `E-01`, `E-07`. |
| NOT | Use `-` only when a future protocol translation explicitly requires it; none does. | **[official_documentation] [observed]** `nanosatellite+-CubeSat` returned 78 versus 133 for the base probe; see `E-01`, `E-07`. |
| Phrase | Use double quotes for every multiword or hyphenated protocol phrase. | **[official_documentation] [observed]** `"CubeSat model"` returned 2 versus 98 for `CubeSat+model`; see `E-01`, `E-07`. |
| Parentheses/precedence | Parenthesize every OR, pair, and block; never rely on unparenthesized precedence. | **[official_documentation] [observed]** `(CubeSat|nanosatellite)+MBSE` returned 5, while `CubeSat|(nanosatellite+MBSE)` returned 1,152. An unmatched opening parenthesis still returned HTTP 200 and a broad total. See `E-01`, `E-07`, `E-17`. |
| Literal escaping | The NASA page documents a preceding backslash for literal operator characters. The query files avoid a need for raw operator literals by quoting phrases. | **[official_documentation]** See `E-01`. **[observed]** quoted report-number probes with and without escaped hyphens both returned 2; general literal-escape semantics remain **[untested]**. See `E-07`. |
| Hyphens/punctuation | Preserve every finite hyphenated and spaced form as a quoted phrase; do not normalize or collapse them. | **[observed]** quoted `"nano-satellite"` and `"nano satellite"` were accepted; all 11 complete translations containing quoted punctuation were accepted. See `E-07`, `E-12`. |
| Case/acronyms | Preserve protocol spelling/case in files, although global `q` behaved case-insensitively in bounded probes. | **[observed]** controlled `CubeSat`/`cubesat`, `MBSE`/`mbse`, and `EPS`/`eps` pairs had equal totals. **[official_documentation]** warns that visible left filters are case-sensitive. See `E-01`, `E-07`. |
| Stemming, lemmatization, automatic expansion | Do not rely on any of them. | **[observed]** `nanosatellite+battery` returned 8 and the plural form returned 2. **[untested]** no general stemming, lemmatization, synonym, or acronym-expansion guarantee was established. See `E-07`. |
| Wildcards | Do not use `nanosat*` in a final translation. | **[official_documentation]** NASA documents a suffix `*` prefix query. **[observed]** `nanosat*` was accepted, but finite P returned 1,587 versus 1,590 after replacing only finite nanosat forms with `nanosat*`. See `E-01`, `E-07`. |
| Query length/transport | Use one POST cell per current partition; validate payload bytes before each final event. | **[observed]** all current cells (largest `BT2` payload 1,200 bytes in the diagnostic) succeeded; a 2,068-character synthetic q succeeded, while an 8,212-character synthetic q returned HTTP 504 HTML. **[untested]** this does not identify a fixed source limit. See `E-07`, `E-12`. |

## 3. Translation approach

- **[observed]** The exact UTF-8, BOM-free translations are in [`translation-spec.json`](translation-spec.json) and [`queries/`](queries/). [`pilots/S-D13-P01-20260821T034216+0000/translation-integrity.json`](pilots/S-D13-P01-20260821T034216+0000/translation-integrity.json) found no missing serialized protocol terms, no wildcard, and no prohibited SmallSat term in all 11 files.
- **[observed]** One bounded, no-screening source diagnostic was run for each of `A1`, `A2`, `A3`, `B1`, `B2`, `BG1`, `BG2`, `BC1`, `BT2`, `V1`, and `O1`; the matrix is in `E-12`. The file SHA-256 covers its UTF-8 terminal LF; diagnostics assigned `q` from the file after removing exactly that one terminal LF and made no other text transformation.
- **[inferred]** The current translations use one complete cell per partition, so no union is presently required. If a future fixed limit requires cells, each cell must independently complete two ID passes; take the lossless union by NTRS citation `id`, retain cell provenance, and fail the entire partition if any cell fails.
- **[inferred]** Dictionary pair rules are represented as explicit same-record Boolean conjunctions, not as a proximity claim. No source-specific proximity behavior is used to make a pair qualify.

## 4. Controls and common limits

- **[observed]** Put the evidence window in the POST payload, not in `q`: `published: {"gte":"2011-01-01", "lte":"<P-001 common cutoff>"}`. A 2011-to-2100 sentinel changed a controlled total from 133 to 80; a same-day 2015 range returned 1; malformed `published.gte` returned HTTP 400. See `E-07`.
- **[untested]** The protocol's common evidence cutoff is still `TBD`, so the exact final upper date is blocked pending P-001; no final event may substitute the pilot's `2100-12-31` sentinel. Set the P-001 date before any final run, then repeat a one-record date preflight with that exact date.
- **[observed]** No reliable native language control was established: a POST `language: "English"` probe returned the same total as the unfiltered control, the inspected record lacked a `language` field, and the documented visible filters do not list Language. See `E-01`, `E-07`, and `E-14`.
- **[inferred]** Apply no language limit at discovery; preserve available language metadata and determine report language only in the protocol's later screening process.
- **[official_documentation]** The UI default order is Best Match and offers Publication Date newest/oldest. **[observed]** `sort: {"field":"published","order":"asc"}` produced repeatable ordered IDs in the small test. The final procedure must use this explicit sort rather than the default. See `E-01`, `E-08`, `E-11`.

## 5. Retrieval, pagination, and export

- **[official_documentation]** The documented UI page choices are 25, 50, and 100. **[observed]** POST `page: {"from":0,"size":100}` returned all five records in the bounded diagnostic. See `E-01`, `E-11`.
- **[observed]** POST offsets 0, 2, and 4 returned 2, 2, and 1 IDs against the unchanged source total of 5. The response reported `stats.total` with `estimate:false`. See `E-08`, `E-11`.
- **[inferred]** Use `page.from=0` and `page.size=100`, increasing `from` by the expected page width. Do not derive a total from retrieved rows; `stats.total` is the source total only when every response is parseable and `estimate:false`.
- **[observed]** `GET /api/citations/{id}` returned the requested `id` and a metadata object with title, abstract, author affiliations, publication/meeting dates, source identifiers, downloads, STI type, distribution, and related fields. See `E-13`.
- **[observed]** `POST /api/export` returned JSON export rows and stable IDs for all five records even when the supplied search page size was 2. **[inferred]** Use the paged search responses as the completeness channel; an export may be retained only as a post-completeness capture/cross-check because its paging/cap behavior is not established. See `E-13`.
- **[untested]** No global NTRS total cap, export cap, or all-result export behavior was established. Do not impose an undocumented discovery cap; treat any cap indicator, short page, or mismatched export as a failure.

## 6. Stable identity and completeness

- **[observed]** Search, detail, and export outputs all exposed the same NTRS citation `id`; use its decimal string form as the within-source stable ID. DOI is optional metadata, not the source identity. See `E-08`, `E-13`.
- **[observed]** A bounded `B1` diagnostic retrieved five unique IDs across offsets 0/2/4, reconciled each pass to source total 5, and repeated the identical ordered list in a second pass under explicit `published asc` ordering. See `E-08`.
- **[inferred]** For every final partition/cell, make two complete passes with the byte-identical q file, date filter, sorting, page size, and no other filters. For each pass: record the first `stats.total`; require the same non-estimated total on every page; require exactly `min(100, total-from)` rows per page; require a nonempty unique `id` on every row; and require the concatenated count to equal total. Require the pass-2 ordered ID list to equal pass 1 exactly.
- **[inferred]** A duplicate ID inside one pass, an absent/changed ID, a changed total, a short/empty premature page, non-ascending requested page sequence, or any pass-list difference makes the event incomplete. Set `total=null`, retain only a failure receipt, and import no prefix.
- **[inferred]** Keep same-ID discoveries from different partitions as separate discovery events until the protocol's later within-source/cross-source deduplication stage; this does not relax the no-duplicate rule inside one source-page pass.

## 7. Failure and zero rules

- **[observed]** A valid HTTP 200 response with `stats.total:0`, `estimate:false`, and `results:[]` occurred for several complete partition diagnostics. This is an explicit source zero. See `E-12`.
- **[observed]** A malformed date returned HTTP 400, and an 8,212-character synthetic query returned HTTP 504 with non-JSON HTML. See `E-07`.
- **[observed]** An unmatched parenthesis returned HTTP 200 with a broad result total rather than a safe syntax error. Local query-file/hash/parenthesis preflight is therefore mandatory. See `E-17`.
- **[inferred]** Record `total=0` only when the complete explicit-zero conditions above hold. Record `total=null` for access/authentication/challenge/rate-limit/timeout/transport/HTTP failure; non-JSON or malformed envelope; request-file/hash/control mismatch; invalid date; missing or estimated total; page/range/ID/duplicate/parse/export mismatch; source cap; incomplete pass; or pass drift. Never treat an error, zero retrieved rows, or a partial prefix as zero.

## 8. Final-run procedure

1. **[untested]** Do not run this procedure until P-001 sets and records the common cutoff and a supervisor authorizes R-002; accepting this guideline does not satisfy those final-run gates.
2. **[inferred]** Recheck `https://ntrs.nasa.gov/`, the public search tips, and one anonymous POST preflight. If the route, response envelope, syntax, fields, or page behavior differs, stop with `total=null` and reopen the source pilot.
3. **[inferred]** Verify the SHA-256 and UTF-8/BOM status of every current query file against `translation-spec.json`; reject malformed parentheses and any changed query bytes. The checksum includes one terminal LF; remove exactly that LF when assigning `q` in the JSON body and make no other text transformation. Use the exact P-001 cutoff in `published.gte/lte`, no language/type/access/content filter, `highlight:false`, and `sort:{"field":"published","order":"asc"}`.
4. **[inferred]** For each partition cell, make the two complete paged ID passes in Section 6. Preserve each request payload, raw response hash, source total, page offsets, response count, ordered IDs, and parse receipt without retaining credentials, session URLs, or full text.
5. **[inferred]** Accept an explicit zero only under Section 7. Otherwise, on any failure, write a final failure receipt with `total:null`, discard the prefix, and do not resume/mix it with a later request.
6. **[inferred]** Only after both passes reconcile, capture the normalized metadata and optionally make the source-native JSON export cross-check. If export count/IDs do not reconcile, fail the event; do not use export to replace page completeness.
7. **[inferred]** Store a later authorized final event only under `searches/final-events/` using the then-current final-event contract. This pilot does not authorize that action.

## 9. Validation evidence

- **[official_documentation]** `E-01` is NASA's Search Tips page and `E-02` is the NTRS landing page; their extracted copies and public URLs are in the pilot evidence index.
- **[observed]** `E-05` through `E-17` index public API diagnostics, safe captures, the 11-partition matrix, integrity check, and two-pass receipt.
- **[inferred]** The operating rules in Sections 3–8 are conservative consequences of the documented/observed facts, not an accepted final-event claim.
- **[untested]** No pilot can prove future interface stability, a fixed hard query limit, a source-wide cap, universal field-filter behavior, or an exact common cutoff before P-001.
- **[observed]** The supervising review accepted pilot `S-D13-P01-20260821T034216+0000` as support for this reusable guideline; the pilot records themselves remain diagnostic-only.

## 10. Remaining limits and protocol impact

- **[untested]** P-001 must set the common evidence cutoff before a final date-bounded run; that exact final-date test remains blocked.
- **[untested]** Revalidate the public boundary, export cap, source-wide pagination behavior, and interface immediately before R-002; NTRS index labels, metadata, and response ordering can change.
- **[inferred]** If a revised protocol creates a query near or beyond the observed 2,068-character success / 8,212-character failure region, prospectively create and validate lossless cells before use; do not silently shorten terms.
- **[observed]** No protocol concept, Boolean relationship, source list, evidence-window rule, or eligibility rule was changed by this pilot.
- **[inferred]** P-001 must still be set and the API/interface must be verified immediately before final execution. See [`supervisor-review.md`](supervisor-review.md) for the acceptance rationale. No screening or import is permitted from this packet.
