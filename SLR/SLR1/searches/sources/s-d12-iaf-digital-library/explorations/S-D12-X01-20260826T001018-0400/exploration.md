# IAF Digital Library X01 serialized HTTP exploration

- **Session ID:** `S-D12-X01-20260826T001018-0400`
- **Source:** full public IAF Digital Library
- **Started / ended:** 2026-08-26T00:10:18-04:00 / 2026-08-26T00:10:20-04:00
- **Mode:** exploration; diagnostic only; no campaign, evidence gate, screening, import, or final event
- **Route:** anonymous server-rendered XHTML `GET https://dl.iafastro.directory/search/`; no browser/CfT lease, API, credentials, event restriction, PDF, or detail request

## Live operation

The minimum launch gate verified exact `"CubeSat"` plus terminal LF in `diagnostics/health-query.txt` (10 UTF-8 bytes; SHA-256 `1f815b10f205251c9fad04f963baaf0187264af9a1d701c0a86109d8351b979b`), command startup, an absent create-only output, and the pinned adapter. One attached serialized adapter operation used `--count-only --limit 1 --max-pages 1 --timeout 20 --request-delay-seconds 1 --retries 1`.

The public XHTML parser passed. It retained exact query echo `"CubeSat"`, full-library scope, no event scope, one reconciled page at page size 50, source total **2,109**, 50 source rows counted, zero records retained, and count-only stop status. The operation exited zero. No source retry was requested by the controller; the adapter policy allowed at most one same-operation transient retry, but its output does not publish an attempt-level retry ledger.

Restricted output and command receipts are under `.searches/s-d12-iaf-digital-library/S-D12-X01-20260826T001018-0400/` and are hash-bound by `restricted-evidence-index.json`. No card title, author, event/paper identity, detail record, abstract, DOI, or relevance judgment is copied into Git.

## Implementation and remaining unknowns

- **Pinned agent-tools commit:** `aa10b5f885a20603f3fef0c77bbb9cf2ab45b6a7`
- **Frozen adapter SHA-256:** `ea279787ad59b16f51dc2453f72a41c477acfa1af422e22f3640368f6587b608`
- **Session patch:** none
- **Still unknown:** explicit-zero behavior; A1 cell query echo; source field/Boolean/pair semantics; year filtering; record/detail identity; pagination beyond one page; stable ordering; completeness; and failure surfaces

## Frozen proposed evidence plan

**Frozen for the health capability only.** Allocate the brand-new campaign and runtime P01 only when executing one immutable operation. Use the same pinned adapter, exact `"CubeSat"`, full-library/no-event scope, count-only flags, 20-second timeout, one-second pacing, and at most one same-operation transient retry. Require exact query echo, full-library scope, no event restriction, one internally reconciled native total or explicit zero, page size 50, zero retained records, terminal artifact publication, and serialized cleanup. Any redirect, access/challenge, transport exhaustion, changed query/scope, parser/range/total mismatch, publication failure, or residual child yields `total=null` and returns IAF to exploration. This narrow P01 cannot pass field, date, retrieval, identity, pagination-completeness, or final-search acceptance; the remaining source-plan operations require later X→P capability ladders.
