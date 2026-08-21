# Scopus diagnostic pilot observations

- **Pilot:** `S-D01-P01-20260820T234301-0400`
- **Status:** blocked; diagnostic only; not accepted.
- **Scope guard:** no screening, relevance assessment, candidate construction, import, final event, export, or full-text retrieval was performed.
- **Evidence convention:** every behavioural statement below is labelled **observed**, **official_documentation**, **inferred**, or **untested**. “Observed” applies only to this dated diagnostic, not to a future Scopus interface.

## Access disposition

- **observed — blocked:** The only authorized count-only attempt saved an error artifact with `total: null`, `results_retrieved: 0`, `completion_status: "error"`, and `error_type: "ScopusProtocolError"`. It did not produce a recognizable rendered result state, a source total, a native zero, a field echo, a source-boundary indication, or a result range. [E-001](#evidence-register)
- **observed:** Immediately before the source attempt, the local browser-harness doctor reported Chrome running but `active browser connections — 0`. This is a local browser-harness observation only; it does not establish the cause of the Scopus adapter error. [E-002](#evidence-register)
- **observed:** The source attempt used the adapter’s default loopback route and did not supply a target ID, existing result URL, fresh browser, credentials, cookies, or challenge action. [E-001](#evidence-register)
- **inferred:** The adapter is designed to create and close an owned tab rather than navigate an existing tab. That general-purpose design is not proof that the current Scopus interface exposed the needed form or results controls, but this worker did not issue any existing-tab navigation or close command. [E-003](#evidence-register)
- **observed:** This pilot stopped after that failed count-only route test rather than retrying or attempting access-control handling. The access disposition is therefore **unresolved current rendered-interface/route failure**, not a confirmed login, entitlement, CAPTCHA, or query-syntax diagnosis. [E-001](#evidence-register)

## Authorized route and boundary

- **inferred:** The candidate public route is `https://www.scopus.com/search/form.uri?display=advanced`, and the intended database/platform boundary is Scopus as the bibliographic database named in the SLR1 source crosswalk. Neither the current rendered form nor the selected scope was proved in this pilot. [E-003](#evidence-register)
- **untested:** Visible Advanced Search controls, one query input, one submit control, an exact rendered query echo, database scope, and result-route continuity must be demonstrated before a future source run.
- **untested:** No claim is made about account authentication despite the supplied authorization context; the failing artifact did not provide a source-side confirmation.

## Provisional translation basis

- **observed:** The failed count-only diagnostic deliberately entered `TITLE-ABS-KEY(CubeSat)`. The saved artifact retains that exact entered query but gives no current parse, echo, or field-coverage proof. [E-001](#evidence-register)
- **inferred:** The draft query files use one `TITLE-ABS-KEY(...)` wrapper around each complete Boolean expression. All literals are quoted; every finite population form is retained; `nanosat*` is not used; paired concepts use Boolean conjunction inside the same wrapper; and no date, language, publication-type, access, venue, or content restriction is added. This is a text-level translation choice only. [E-004](#evidence-register)
- **observed:** A local UTF-8 integrity check found all 11 query files present, one wrapper per file, balanced parentheses, and no missing required literal from the designated concept blocks. It cannot validate Scopus parsing or semantics. [E-005](#evidence-register)
- **untested:** `TITLE-ABS-KEY` field coverage, quotation/phrase behavior, Boolean precedence, punctuation and hyphen handling, case handling, acronym boundaries, automatic expansion, stemming, lemmatization, wildcard behavior, maximum accepted query length, and query rewrite/echo behavior.

## Partition matrix

| Partition | Query cell | Local text check | Current Scopus validation | Source total |
|---|---|---:|---|---:|
| A1 | `A1-01` / `queries/A1.txt` | observed pass | blocked / untested | null |
| A2 | `A2-01` / `queries/A2.txt` | observed pass | blocked / untested | null |
| A3 | `A3-01` / `queries/A3.txt` | observed pass | blocked / untested | null |
| B1 | `B1-01` / `queries/B1.txt` | observed pass | blocked / untested | null |
| B2 | `B2-01` / `queries/B2.txt` | observed pass | blocked / untested | null |
| BG1 | `BG1-01` / `queries/BG1.txt` | observed pass | blocked / untested | null |
| BG2 | `BG2-01` / `queries/BG2.txt` | observed pass | blocked / untested | null |
| BC1 | `BC1-01` / `queries/BC1.txt` | observed pass | blocked / untested | null |
| BT2 | `BT2-01` / `queries/BT2.txt` | observed pass | blocked / untested | null |
| V1 | `V1-01` / `queries/V1.txt` | observed pass | blocked / untested | null |
| O1 | `O1-01` / `queries/O1.txt` | observed pass | blocked / untested | null |

The table’s local-pass column is not a source-behaviour claim. Exact query strings, hashes, character counts, concept blocks, and single-cell status are in [`../../translation-spec.json`](../../translation-spec.json) and [`query-integrity.json`](query-integrity.json).

## Controls, retrieval, and completeness

- **blocked:** The pilot did not validate a visible source/database scope, date control, language control, prohibited-limit state, native sort/order, source total, explicit zero state, page size, next-page mechanism, export, capture, stable record identity, duplicate behavior, or a complete two-pass traversal. [E-001](#evidence-register)
- **untested:** The evidence window must begin on `2011-01-01` and end on the exact common cutoff once `P-001` sets it. The current pilot did not establish whether Scopus can apply an exact-day cutoff or only a coarser date control.
- **untested:** A metadata-language filter must not be treated as proof of full-text English. No language filter is included in the draft queries.
- **inferred:** The adapter’s documented intended capture mechanism is rendered result rows with a source-publication identifier and page/range reconciliation; the default optional abstract expansion is not a substitute for a source-native export validation or two-pass completeness proof. [E-003](#evidence-register)

## Required revalidation sequence before any final Scopus event

1. **untested required action:** A human operator must make the normal authorized local-CDP context available without sharing credentials, cookies, existing-tab URLs, or a session/search URL. If a login, CAPTCHA, challenge, entitlement wall, or another unresolved route failure remains, record `total: null`, import nothing, and recommend `skip_for_now` rather than retrying aggressively.
2. **untested required action:** In a new adapter-owned tab, prove the current Advanced Search form, exact submitted-query echo, Scopus scope, visible controls, an exact positive total/range or an explicit native zero, and the public route. Save and read each count-only JSON in ignored worklogs.
3. **untested required action:** Run count-only diagnostics for every exact A1, A2, A3, B1, B2, BG1, BG2, BC1, BT2, V1, and O1 query file. A successful query needs an exact echo and a reconciled total; a native explicit zero is the only valid zero. A syntax, rewrite, access, control, total, or range failure remains `null` and blocks that partition.
4. **untested required action:** Use controlled count-only comparisons to establish phrase/Boolean precedence; title, abstract, and keyword coverage; hyphen/punctuation and case behavior; acronym boundaries; expansion/stemming/lemmatization; and wildcard semantics. Keep finite P forms unless an exhaustive stable-ID comparison under the final field/date scope proves `nanosat*` both captures the finite forms and does not add an unapproved meaning.
5. **untested required action:** Validate query length by executing every full partition. If a source limit requires cells, prospectively define every cell and reconcile the stable-ID union; do not narrow, drop a cell, or infer a union from counts.
6. **untested required action:** After the exact cutoff is set, validate source-side date behavior from `2011-01-01` through that date. If only a coarser source date is available, preserve the unaltered source total and establish a complete, auditable local date filter from a source field with sufficient precision; unresolved dates must be reported rather than silently excluded. Validate language separately and do not impose any prohibited discovery limit unless a documented source limitation requires it.
7. **untested required action:** Use one bounded retained-record preflight only if needed for identity/pagination testing, with `--skip-full-abstracts`; keep raw licensed output only in ignored worklogs and compare safe hashes of stable IDs. Validate native page size, contiguous ranges, next-page advancement, unique stable source IDs, and adapter capture or native export reconciliation.
8. **untested required action:** Before a final event, predefine a complete capture bound from the observed total. On pass 1, retrieve every page and reconcile the row ledger, page ranges, unique stable IDs, and total. On an independent pass 2 under the same validated controls and order, require the same total and the same ordered stable-ID sequence when the source order is stable; otherwise require identical stable-ID sets plus identical total, range ledger, and page cardinalities. Any drift, duplicate/missing ID, short/stale page, changed total, export/capture mismatch, parse failure, or incomplete pass makes the event failed (`total: null`); no prefix may be imported.

## Evidence register

| ID | Claim status | Safe evidence | Notes |
|---|---|---|---|
| E-001 | observed | `SLR/SLR1/searches/worklogs/s-d01-scopus/d01-route-field-baseline.json` | SHA-256 `ad67656140210f221c8fa549e22628bd861bc37f7c17f30121fa7d58a1f06c46`; ignored raw diagnostic; no records retrieved. |
| E-002 | observed | `safe-summary.json` | Records the non-sensitive browser-harness doctor result observed before the source attempt. |
| E-003 | inferred | Adapter source hash in E-001: `search_scopus.py` SHA-256 `ba11613b8b5daa6e2a6d91b50b8570ab139c15d46a7ee424052c92bff244a9b3` | Adapter code and academic-search guidance are a hypothesis/tool description, not current-interface evidence. |
| E-004 | inferred | `../../translation-spec.json` | Documents provisional wrapper and no-narrowing choices. |
| E-005 | observed | `query-integrity.json` | Local file integrity only; it does not establish any Scopus behavior. |

No **official_documentation** source-specific behavioural claim was accepted in this blocked pilot, and no **untested** item is used as acceptance evidence.
