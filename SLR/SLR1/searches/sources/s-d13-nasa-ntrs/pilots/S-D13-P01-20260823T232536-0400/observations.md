# NTRS diagnostic observations — S-D13-P01-20260823T232536-0400

## Disposition

**Status: blocked.** This is exactly one diagnostic-only pilot. `screening_performed=false`, `candidate_import_permitted=false`, no candidate IDs/metadata were retained, and `total=null` is used for every failed search attempt. Claim bases are explicitly labelled **[observed]**, **[official_documentation]**, **[inferred]**, or **[untested]**.

**[observed]** Browser preflight is **not applicable**: this source is assigned an API/HTTP route; no Chrome/browser process, tab, login, cookie, session URL, registered route, or full-text download was used.

## 1. Scope, route, and access

- **[official_documentation]** The first-party public NTRS client identifies NTRS/NASA STI Repository and distinguishes public content from separately registered content. This pilot uses the protocol's exact boundary: the full **public** technical-report database, not NTRS Registered/PubSpace, a center, a content type, or a selected date range as a source boundary. [`interface-and-access-receipt.json`](interface-and-access-receipt.json)
- **[observed]** `HEAD https://ntrs.nasa.gov/` returned 200 at `2026-08-24T03:20:56Z`. Static current-client inspection identified API root `/api`, `POST /citations/search`, JSON request body/response negotiation, advanced-search property names, and page-size controls. This static route evidence does not prove a successful API search.
- **[observed]** A non-mutating `OPTIONS` request to the exact API route returned 404 at `2026-08-24T03:20:55Z`. It neither proves nor disproves the POST route; it is retained only as a method receipt.
- **[untested]** Anonymous API authorization cannot be confirmed from a successful response. Neither direct POST probe received a result envelope, and no authentication challenge/credential route was attempted.

## 2. Direct API and adapter receipts

| Execution | Exact operation/control | Result | Total / IDs | Basis and receipt |
|---|---|---|---|---|
| `NTRS-API-PROBE-01` | POST `q=nanosatellite`, `page={from:0,size:1}`, `highlight=false`, `published={gte:2011-01-01,lte:2026-08-23}` | curl read timeout after 35 seconds and zero response bytes | `null` / none | **[observed]** [`api-transport-probes.json`](api-transport-probes.json) |
| `NTRS-API-PROBE-02` | POST `q=nanosatellite`, `page={from:0,size:1}`, `highlight=false` | HTTP 504, `Content-Type: text/html`, source Date `2026-08-24T03:22:07Z` | `null` / none | **[observed]** [`api-transport-probes.json`](api-transport-probes.json) |
| `NTRS-ADAPTER-PROBE-01` | `uv run search_ntrs.py --query nanosatellite --limit 1 --max-pages 1` | exit 1; `NTRSRequestError`; error artifact retained | `null` / none | **[observed]** [`adapter-route-test.json`](adapter-route-test.json) |

**[observed]** The first direct probe uses `2026-08-23` as a clearly labelled execution-date **diagnostic upper bound only** because P-001 is unresolved. It is not a final common cutoff. The no-response result does not validate API date parsing or inclusion.

**[observed]** The current client code expects a response with `results`, `aggregations`, and `stats`; that is a client expectation, not an observed current response envelope. **[untested]** Total type/meaning, record schema, query echo/rewrite, aggregations, response page/range data, and all fields remain unresolved.

## 3. q semantic contrast register

No count or retrieval result below is negative evidence: the failure occurred before a valid response could be parsed. All entries are blocked by the same route condition documented above.

| Required contrast | Status | Basis | Conservative conclusion |
|---|---|---|---|
| Boolean operators and precedence | blocked | **[observed]** transport failure | `+`/`|` are only draft notation; parser semantics unproven. |
| Parentheses | blocked | **[observed]** transport failure | Grouping acceptance unproven. |
| Ordered phrase matching | blocked | **[observed]** transport failure | Quoted multiword handling unproven. |
| Punctuation/hyphen normalization | blocked | **[observed]** transport failure | Keep every spaced and hyphenated normative form. |
| Case | blocked | **[observed]** transport failure | No case-folding assumption. |
| Standalone acronyms/tokens | blocked | **[observed]** transport failure | No token-boundary assumption for MBSE, SysML, EPS, PDU, PCDU, PMAD, OPM, or OOSEM. |
| Wildcard behavior | blocked | **[observed]** transport failure | No wildcard is used. |
| Stemming, lemmatization, automatic expansion | blocked | **[observed]** transport failure | No expansion assumption; all variants remain literal. |
| Special-character escaping | blocked | **[observed]** transport failure | Hyphenated literals are retained quoted but unvalidated. |
| Query rewrite/echo visibility | blocked | **[observed]** transport failure | Exact request receipts exist; server echo/rewrite behavior is unknown. |
| Practical/query-length behavior | blocked | **[observed]** transport failure | Draft cell lengths are 592–2,302 UTF-8 bytes; no server limit is claimed. |
| q field scope and same-field co-occurrence | blocked | **[observed]** transport failure | No claim that terms combine in title/abstract or any single field. |

## 4. Controlled vocabulary / indexed terms

- **[observed]** The static public client exposes `subjectCategory` and `keyword` search controls and shows `subjectCategories`/`keywords` on record presentation.
- **[untested]** The pilot could not inspect a live record, a field response, a scope note, hierarchy, narrower term, explosion behavior, or descriptor assigned to a suitable public known record.
- **[observed]** No descriptor was appended to any query cell. The operative draft conclusion is: **no usable validated controlled-vocabulary or distinct indexed-term field is available for the direct translation at this time**. This means “not accepted for use,” not “proven absent.” A generic systems-engineering heading alone would never satisfy MBSE.

## 5. Controls, dates, language, limits, and completeness

- **[observed]** Static client inspection shows `published` request construction and page `from`/`size` properties, with visible UI choices 25/50/100. **[untested]** Exact API date filtering, date labels/precision, offset origin, size ceiling, total consistency, page completion, order, caps, export/capture fields, and stable NTRS IDs were not established.
- **[untested]** Language metadata and native filtering reliability are unknown. No English restriction was imposed.
- **[inferred]** No publication-type, access, peer-review, venue, content-type, major-topic, or full-text restriction belongs in the planned direct discovery controls. This rule must be rechecked against a successful response.
- **[untested]** A safely small two-page result set, two complete ordered-ID passes, duplicate/missing-ID check, and source-total/retrieved-total reconciliation could not be run. No partial prefix is represented as complete.

## 6. Cells and transport status

**[inferred]** The exact dictionary renderer produced one UTF-8 draft cell for each required partition. Literal occurrence receipts and hashes are in [`../../query-construction-receipt.json`](../../query-construction-receipt.json); mappings are in [`../../translation-spec.json`](../../translation-spec.json).

| Partition | Cell | Query file | Sent in this pilot? | Result |
|---|---|---|---|---|
| A1 | `NTRS-A1-C01` | [`A1.txt`](../../queries/A1.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |
| A2 | `NTRS-A2-C01` | [`A2.txt`](../../queries/A2.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |
| A3 | `NTRS-A3-C01` | [`A3.txt`](../../queries/A3.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |
| B1 | `NTRS-B1-C01` | [`B1.txt`](../../queries/B1.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |
| B2 | `NTRS-B2-C01` | [`B2.txt`](../../queries/B2.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |
| BG1 | `NTRS-BG1-C01` | [`BG1.txt`](../../queries/BG1.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |
| BG2 | `NTRS-BG2-C01` | [`BG2.txt`](../../queries/BG2.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |
| BC1 | `NTRS-BC1-C01` | [`BC1.txt`](../../queries/BC1.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |
| BT2 | `NTRS-BT2-C01` | [`BT2.txt`](../../queries/BT2.txt) | no | **[observed]** blocked after global API failure and `code_issue=true`; `total=null` |

**[untested]** The draft pair constructions in BG1/BG2/BC1/BT2 do not prove unordered <=5-token same-field proximity. They are held as broader, unaccepted transport placeholders; the protocol semantics have not changed.

## 7. External adapter assessment and stop

**[observed]** Adapter commit `3231ebddefcc3e7bc707b2a7d66fbe831d363286` was pinned and test-run once. `code_issue=true` for two concrete reasons:

1. Its emitted NTRS PRISMA descriptor says `online_resource`, inconsistent with the tracked crosswalk's required `databases_registers` technical-report-database accounting.
2. Its year-only bounds cannot express an arbitrary exact P-001 upper date, and its bounded traversal has no strict final-run mode for validated fixed ordering, nonempty unique IDs, and two complete ordered-ID passes.

The assessment is preserved in [`adapter-assessment.json`](adapter-assessment.json). **[observed]** No patch was made. Once `code_issue=true` was established, all affected NTRS live querying stopped; no P02 or retry was launched.

## 8. Human decisions / recommendations

1. **Adapter corrective scope — recommendation: approve a separate code-fix task.** Correct NTRS PRISMA category and add exact ISO dates plus strict complete two-pass ID/order/duplicate controls before another pilot. Evidence: [`adapter-assessment.json`](adapter-assessment.json).
2. **Source availability — recommendation: do not accept this pilot; schedule a new authorized pilot only after the corrective fix and successful public API health/search response.** The timeout/504 is a source failure, not a zero or a basis for narrowing. Evidence: [`api-transport-probes.json`](api-transport-probes.json), [`adapter-route-test.json`](adapter-route-test.json).
3. **Pair transport — recommendation: retain normative pairs unchanged and require a future same-field/proximity recall proof before accepting BG1/BG2/BC1/BT2.** Do not approve the broad draft conjunct as an exact pair implementation merely because it is syntactically compact. Evidence: [`../../translation-spec.json`](../../translation-spec.json#paired_term_handling).

**[inferred]** No semantic or protocol change is recommended. The impact is a blocked source implementation and unaccepted draft translations, not a change in source list, concept blocks, Boolean relationships, eligibility, evidence window, or PRISMA source placement.
