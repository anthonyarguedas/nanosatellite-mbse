# S-L02-P01 diagnostic observations — ESA Indico

- **Status:** partial / not accepted.
- **Diagnostic only:** yes. No record was screened, no eligibility or source-quality judgment was made, no candidate corpus was built, and nothing was written under `searches/final-events/`.
- **Pilot started:** `2026-08-23T01:56:22-04:00`.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Source:** ESA Indico, public anonymous routes only.
- **Scope:** bounded route/topology and local-method diagnostics; not a final harvest.

## Browser safety

Before the one bounded rendered-page observation, the controller-safe preflight recorded a process-scoped sleep assertion, healthy local Chrome, runtime `Chrome/151.0.7922.174`, one page target, and AC power. Only safe facts were copied; no tab URL, cookie, token, or session/search identifier was retained ([observed preflight summary](safe-receipts/browser-preflight-summary.json)). A later controller check found no `Sleep`, `Wake`, or `DarkWake` entry timestamped within the declared P01 window; this does not resolve the separate anchor-continuity incident ([postflight sleep check](safe-receipts/controller-postflight-sleep-check.json)).

The browser probe opened and closed an adapter-owned tab for the event-472 rendered timetable. **Supervisor correction:** after that owned-tab closure, page-target count was observed as zero; the controller ran the normal launcher, restored and verified a safe page anchor, and the next read-only check passed with two page targets. It cannot be determined whether the original anchor independently disappeared or was closed. Controller-anchor continuity is therefore unproved, and P01 does not claim `controller_anchor_untouched=true` or `controller_anchor_closed=false`. The reproducible queue, corrected receipt, and validation retain event/attachment IDs only ([queue](safe-receipts/rendered-timetable-navigation-queue.json), [receipt](safe-receipts/rendered-timetable-navigation-receipt.json), [validation](safe-receipts/rendered-timetable-receipt-validation.json), [correction](safe-receipts/supervisor-correction-20260823.json)).

## Observed public routes and bounded coverage

| Observation | Status and evidence | Interpretation limit |
|---|---|---|
| Category-0 export accepted a November 2023 `from`/`to` input, reported 8, returned 8 rows, and two runs had the same ordered event IDs and response hash. | **Observed**: [pass ledgers](safe-receipts/bounded-category-2023-11.json) and [reconciliation](safe-receipts/category-pass-reconciliation.json). | A bounded monthly result only. Its rows include source start dates outside the requested month, so the exact date-overlap semantics must be validated before all-time use. It does not prove root-category recursion, all-time coverage, pagination/cap behavior, or a source lower-date sentinel. |
| Historical P01 event export `detail=contributions` for event 472 gave 15 stable contribution IDs. Its true export ledger had 13 export-listed/public PDF routes; public static owner pages yielded 15 attachment links, with 9769 and 9770 static-only. This topology was reproducible in two P01 passes. | **Observed P01 topology**: [event pass reconciliation](safe-receipts/event-472-pass-reconciliation.json), with safe pass ledgers. **Supervisor correction:** P01 made no direct GET for the static-only links, so they are `access_unverified` in P01; separate P02 anonymous no-redirect GETs classified both `access_restricted_or_login` ([correction](safe-receipts/supervisor-correction-20260823.json)). | The event export cannot by itself enumerate materials. Event 472 did not have fifteen public PDFs: it had thirteen export-listed/public PDF routes plus two visible static/rendered links whose anonymous access is restricted. The bounded result does not prove all event types or source-wide material coverage. |
| Static event root page can carry event materials. A separate bounded event export had 1 event material, 111 contribution materials, 84 PDF materials, and 28 non-PDF materials. | **Observed**: [event-407 topology probe](safe-receipts/event-407-material-topology-probe.json). | Event 407 contribution pages were deliberately not fully traversed; this is topology evidence, not a complete event harvest. A corrective method requires every public non-PDF to take a deterministic text route or replayable manual/LLM queue; no MIME type is a silent no-match. |
| A static contribution owner page responded to GET but not HEAD. | **Observed**: [GET/HEAD probe](safe-receipts/head-get-route-probe.json). | Use GET; do not use HEAD as a source zero or availability/completeness test. |
| Two hypothesized contribution-export routes were unusable (404 and 503). | **Observed**: [failed-route receipt](safe-receipts/unusable-contribution-export-route-probe.json). | They are failed routes, not zero results, and are not used in the draft route plan. |
| Public direct PDFs can be fetched and processed as separate documents without retaining content in Git. | **Observed**: [PDF text probe](safe-receipts/pdf-text-probe.json). | Only two PDFs were streamed and parsed. This does not prove all PDF download, parser, or OCR coverage. |

## Why PDF full text is a required local route

For bounded attachment 7310, literal `MBSE` and `CubeSat` occurrences were observed in streamed PDF text, while the same contribution title, contribution description, and attachment filename each lacked both literals. The parent event title is an independent route and was not combined with the contribution or PDF. No source text was retained, and this was not treated as a candidate or eligibility decision ([observed](safe-receipts/pdf-text-probe.json)).

Therefore event, contribution, and attachment metadata/filenames alone are insufficient for the local method. Every public PDF needs a separate full-text route, checksum, parser/OCR terminal state, and coverage accounting.

## One-box search diagnostics

All search observations below are diagnostic only; `total=-1` is recorded as unavailable, never as zero.

| Focused test | Observation | Consequence |
|---|---|---|
| Boolean-like strings | In the event type probe, `MBSE` returned four IDs; `MBSE AND CubeSat` and `MBSE OR CubeSat` each returned an explicit zero. | **Observed**, but not claimed as a complete grammar proof. No lossless Boolean translation is accepted; ESA remains a local harvest. [Evidence](safe-receipts/one-box-event-search-probes.json) |
| Quotes/phrases | Quoted and unquoted `MBSE`, and quoted and unquoted `model based systems engineering`, had the same bounded event IDs/hash. | **Observed only**; no general exact-phrase behavior is inferred. [Evidence](safe-receipts/one-box-event-search-probes.json) and [follow-up](safe-receipts/one-box-phrase-followup.json) |
| Hyphen/punctuation | Hyphenated `model-based systems engineering` returned zero in the bounded event test; spaced wording returned four IDs. | **Observed**; do not rely on native hyphen normalization. [Evidence](safe-receipts/one-box-event-search-probes.json) |
| Acronym/token boundary | `MBSE` and `MBSE2023` produced event rows, but event keywords can explain the hits. | **Unknown** whether native standalone acronym boundaries are enforced. Local matching supplies its own boundaries. [Evidence](safe-receipts/one-box-event-search-probes.json) |
| Stemming/expansion | First pages and response hashes differed for `nanosatellite`, `nanosatellites`, and `nanosat`; all had unavailable totals and next pages. | **Unknown** whether any native stemming/expansion exists. It is not used locally. [Evidence](safe-receipts/one-box-contribution-search-probes.json) |
| Materials type | A separate attachment result type returned a bounded first page and unavailable total. | **Observed**; it is a route-discovery probe, not a complete material enumeration. [Evidence](safe-receipts/one-box-material-search-probe.json) |

## Controlled vocabulary/index terms

The bounded public event/contribution export schema exposed generic `keywords` but no observed descriptor, subject/index-term, thesaurus, hierarchy, scope-note, or explosion field/control. **Observed conclusion limited to tested public fields:** no usable genuine controlled vocabulary or distinct indexed-term field is validated; `keywords` are not emulated as controlled vocabulary ([schema probe](safe-receipts/export-schema-controlled-vocabulary-probe.json)). This is not proof about untested/private administration routes.

## Current method result

The source-specific implementation and draft specification are present, but this pilot is not complete because:

1. all-public root-category boundary, date semantics, lower/upper sentinel, and cap behavior remain unproved;
2. nested subcontribution material routes have not been observed/validated;
3. only two diagnostic PDFs were parsed, not every public PDF in any source-wide final universe;
4. no all-source two-pass ledger exists; and
5. P-001 has not set the common evidence cutoff and no supervising reviewer has accepted the guideline.

A final ESA result must therefore be `null`/failed if attempted now; it must not use these diagnostic results as a partial prefix. The P01 route/timestamp facts remain historical (`detail=contributions`), while corrected prospective behavior and the separate P02 access/legacy-material checks are documented in [the supervisor correction receipt](safe-receipts/supervisor-correction-20260823.json) and the P02 packet.

## Smallest next experiment

With no final harvest: use a **second bounded, disjoint root-category window** plus one category-descendant cross-check to establish whether category 0 recursively returns descendants and whether `from`/`to` selects overlapping event periods. Reconcile count, rows, category IDs, stable event IDs, and source date fields in two passes. In parallel, obtain/locate one public event containing a nested subcontribution and validate its owner/material route or explicitly retain that branch as a final coverage failure. These are the smallest missing route-boundary tests before considering an all-time census design.
