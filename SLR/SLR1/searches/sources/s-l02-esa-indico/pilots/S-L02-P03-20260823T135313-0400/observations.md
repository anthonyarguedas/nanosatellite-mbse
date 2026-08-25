# S-L02-P03 diagnostic observations — ESA Indico

- **Status:** partial method-validation diagnostic; not accepted.
- **Pilot window:** `2026-08-23T13:53:13-04:00` to `2026-08-23T14:58:03-04:00`.
- **Diagnostic only:** yes. No record was screened, no eligibility or source-quality decision was made, no candidate was imported, and `searches/final-events/` was untouched.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Source:** ESA Indico public anonymous HTTP routes. Browser use was limited to local Chrome Google discovery of official documentation; no rendered ESA route was used as a substitute for deterministic HTTP traversal.

## Official documentation, separately from live observation

The stable Indico exporter documentation confirms `detail=subcontributions` and its case-sensitive `subContributions` field, plus the separate `sessions` detail. Its category-export page gives the category URL and a `from`/`to` example, but does **not** specify root recursion, date-overlap semantics, pagination/caps, or all-time sentinels. The latest category-model documentation confirms generic category hierarchy/subtree concepts but does not establish ESA's `/export/categ/0.json` behavior. The documentation capture remains outside Git; the content-safe review receipt is [official-documentation-review.json](safe-receipts/official-documentation-review.json).

## Root category, dates, and cap diagnostic

**Observed, bounded only:** category 0 returned eight November-2023 event IDs in two identical ordered/hash passes. Its ID set exactly equalled the disjoint union of explicit category-5 and category-6 requests for that same window ([scope comparison](safe-receipts/category-root-component-scope-comparison.json)). This shows that root category 0 returned the tested nonzero category IDs; it does not prove recursion across every descendant or the all-public all-time source universe.

The one-day observations support inclusive event-period overlap in this sample: event 472 appeared on 2023-11-16 and not 2023-11-17, event 467 appeared on both, and long-running events remained on 2023-11-18 ([window reconciliation](safe-receipts/category-root-window-reconciliation.json)). Inputs exactly at 1900-01-01 and 2100-01-01 were accepted and returned bounded zeros. They are candidate sentinels, not a final boundary proof.

A deliberately bounded 2020-2024 category-0 cap probe returned 148 rows for native `count=148` in two identical ordered/hash passes ([receipt](safe-receipts/root-cap-probe-2020-2024-reconciliation.json)). The response exposed no usable `complete` flag. Therefore P03 verifies count/row reconciliation at 148 rows but does not establish no cap; final planning needs a parent-window versus overlapping child-window calibration and an accepted all-time sentinel decision.

## Event/contribution/material traversal

**Observed:** P03 compared event 407's `detail=subcontributions` export with `detail=sessions`. The former had 62 contribution IDs; the latter had 11 top-level plus 51 session-held IDs, with exactly the same stable-ID set and no duplicates ([receipt](safe-receipts/event-407-detail-coverage.json)). This validates the selected export detail for one session-bearing event.

No non-empty `subContributions` record was found in 19 successful bounded export-shape observations. One additional sampled event (321) failed closed because attachment ID 6771 had conflicting title metadata ([receipt](safe-receipts/event-321-export-identity-failure.json)). P03 did not manufacture a nested owner/material route. A final run must stop with coverage `null` if a non-empty nested record occurs before a validated receipt resolves it.

**Observed:** event 407 was fully traversed through its event page and all 62 exported contribution owner pages. It reconciled 112 attachment IDs, with 84 confirmed public PDFs and 28 confirmed public non-PDF videos. The 28 non-PDF routes entered a replayable queue; they were not silently dropped ([summary](safe-receipts/event-407-nonpdf-owner-reconciliation-summary.json)). A content-free unsupported-video receipt was rejected by the validator, correctly retaining incomplete coverage rather than a no-match ([validation](safe-receipts/event-407-nonpdf-7873-receipt-validation.json)). No irregular/external export route appeared in P03's successful bounded shape scans; that branch remains unobserved rather than assumed absent.

## Complete bounded event-specific PDF/OCR route

**Observed:** P03 freshly fetched event 472 using `detail=subcontributions`, its event page, and every one of its 15 contribution owner pages. The reconciled all-route attachment ledger had 15 IDs. Thirteen direct routes passed anonymous no-redirect public-PDF checks; two static-only routes returned 302 and were explicitly classified restricted/non-public rather than public PDFs.

Every one of the 13 confirmed public PDFs was separately fetched into the approved external secure workspace, SHA-256 hashed, and passed to deterministic UTF-8 `pdftotext`. Eleven had non-empty deterministic text. Two empty parses were sent through exactly the mandated `pdf_to_markdown.py --image-mode keep` OCR handoff outside Git; both yielded non-empty OCR bodies with content-safe hashes/counts. The local matcher ran only after attachment, PDF, OCR, and queue coverage reconciled. It was dictionary-hash locked and produced no candidate route in this bounded event; that is a diagnostic matching outcome, not an ESA source zero or screening decision. See [bounded summary](safe-receipts/event-472-complete-public-pdf-ocr-summary.json) and [exact-command OCR receipts](safe-receipts/event-472-ocr-exact-command-completion-receipts.json).

P03 also corrects a method risk in the draft implementation: event/contribution/attachment metadata and filenames are now auditable noncandidate routes. Only terminal confirmed public PDF text or completed PDF OCR text can emit an ESA candidate. No terms are combined across routes.

## Result and smallest next experiment

P03 validates substantial route mechanics but cannot establish the all-public source universe, a non-empty nested material route, a real irregular/external route, or terminal routing for every public non-PDF. It also exposes an event-local attachment metadata conflict that a final run must fail closed.

**Smallest next experiment:** with supervisor agreement on a non-final bounded sample, locate one event whose `subContributions` is non-empty (or document a reproducible bounded search that cannot locate one), then traverse its actual owner/material route through access classification and a terminal receipt. In parallel, locate one export material with an irregular/external route and run its generated queue through a terminal receipt. Neither experiment should start an all-time census or import a candidate.
