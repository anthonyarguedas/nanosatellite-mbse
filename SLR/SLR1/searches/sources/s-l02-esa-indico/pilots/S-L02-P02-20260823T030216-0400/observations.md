# S-L02-P02 diagnostic observations — ESA Indico correction checks

- **Status:** partial / not accepted.
- **Diagnostic only:** yes. No record was screened, no eligibility decision or candidate import occurred, and no final event was created.
- **Pilot window:** `2026-08-23T03:02:25-04:00` to `2026-08-23T03:02:32-04:00`.
- **Scope:** two corrective HTTP checks only; no event PDF corpus was downloaded.

## Anonymous access status of P01 static-only links

For event 472 attachment IDs 9769 and 9770, anonymous public GET requests were made with redirect following disabled. Each returned HTTP 302 and was classified `access_restricted_or_login`. The receipts retain the original public route paths, status, timestamp, and zero redirects only. They retain no response header, response body, cookie, redirect target, query, or session identifier ([safe receipt](safe-receipts/static-only-access-status.json)).

Therefore, the links visibly observed by P01 are not evidence of public downloadable PDFs. P01 itself made no direct GET for these static-only links, so its historical state is corrected to `access_unverified`; this separate P02 check supplies the later access finding. Event 472's bounded topology is thirteen export-listed/public PDF routes plus two visible static/rendered links whose anonymous access is restricted, not fifteen public PDFs.

## Legacy material-resource shape

A bounded public export for event 558 using the corrected prospective `detail=subcontributions` route returned one recognized legacy `material[].resources[]` attachment resource, attachment ID 11309, with event ownership. The resource had a same-origin direct attachment URL but no export access proof, so the parser classified its access as `access_unverified`; no owner page, material download, extraction, matching, or screening was performed ([safe receipt](safe-receipts/event-558-legacy-material-shape.json)).

This validates only the observed legacy shape and the parser's safe recognition of a same-origin resource URL. It does not validate full event-558 material coverage, anonymous download access for that resource, non-PDF extraction, nested subcontribution material routes, or the all-public ESA source universe.

## Result

P02 supports a correction to the draft method and P01 evidence; it does not complete `S-L02`. Full source-boundary proof, two-pass all-time enumeration, complete material terminal routing, secure PDF/text/OCR coverage, and guideline acceptance remain blocked.
