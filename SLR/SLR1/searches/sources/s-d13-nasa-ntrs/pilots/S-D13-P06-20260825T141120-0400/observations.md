# S-D13-P06 NTRS corrective technical observations

## Terminal status and exact scope

**[observed]** `S-D13-P06-20260825T141120-0400` was the one prospectively authorized `controller_technical` continuation under `D-TECH-NEXT-P06`. It is **failed at the conditional rendered operation**. The attached canonical lease executed exactly two sequential live operations: one record-free source-health navigation and, only after health passed, one exact 13-byte `nanosatellite` count-only adapter operation.

**[observed]** The source-health operation passed with one 2xx normal NTRS route, source identity, visible search surface, two stable samples, no challenge/access/login/busy/error state, null source total, zero records, and verified owned-page cleanup.

**[observed]** The conditional adapter operation used the immutable P03 query bytes exactly (`nanosatellite`, 13 UTF-8 bytes, SHA-256 `3fc7d31e9abb58d42acd5c95a9549835545de822d0843e28265c6979b1a466d4`) with `limit=1`, `max-pages=1`, `count-only`, `skip-full-abstracts`, timeout 90, zero page/detail delays, no date, no retry, and no fallback. Normal rendered navigation completed with 2xx, but the adapter stopped at its ordering-stage control reconciliation before exact query echo, source total, range, row, canonical ID, or explicit zero. The failure artifact is record-free with `total=null` and no imported prefix.

## Immediate technical investigation

**[observed]** The shared adapter was exactly commit `d872f59f5f20913fbd0ef4de16ea2ab79a6bc883`. Its source-free focused NTRS suite passed 38 tests after the live failure; the source-health suite passed 14 tests. The static guard continues to reject direct NTRS API transport, page-side fetch/XHR fallback, and alternate routes.

**[observed]** Source-free ordering fixtures confirm the committed behavior: absent pre-submit ordering is tolerated; harmless duplicate/default/late `Relevance` observations project to one `Relevance`; non-default/conflicting ordering fails closed; and post-submit `Relevance`/default is required before any result evidence is accepted.

**[observed]** A bounded postflight status observation showed the canonical CfT healthy, the same browser epoch, one inert anchor, a released lease, and no orphan child/group. The sanitized cleanup and release receipts verify owned-page closure and anchor preservation. AC power and process-scoped `caffeinate -dims` covered the phase; no Sleep/Wake transition occurred in its window.

**[inferred]** The safe failure artifact intentionally retains no raw DOM projection. The current adapter wrapper labels all `parse_visible_controls` failures as `error_stage=ordering`, although that parser also validates page-size controls. A synthetic source-free duplicate-page-size payload therefore demonstrates an observability ambiguity: it raises a page-size error before the wrapper assigns the ordering stage. The live artifact proves a pre-submit control-reconciliation failure, but cannot distinguish an ordering-value rejection from a page-size ambiguity without retaining disallowed raw DOM state.

**[observed]** The demonstrated behavior-preserving ordering repair is present and tested. No additional adapter defect is proven by the allowlisted evidence, no shared `~/agent-tools` path was edited, and no source operation was reissued. Query/source/order/identity/completeness semantics were not weakened.

## Accounting and disposition

- Live operations: exactly 2 of 2 planned; source-search operations: 1; health operations: 1.
- Retries: 0. Fallbacks: 0. API calls: 0.
- Source total: `null`; explicit zero: not observed.
- Records retrieved/imported: 0/0; screening/import/relevance classification/final event: none.
- `G-SOURCE-HEALTH`: passed for P06.
- `G-BROWSER-ADAPTER-SAFETY`: passed source-free for P06.
- `G-RENDERED-NAVIGATION`: failed for P06 at control reconciliation.
- `G-PARTITION-TRANSPORT`: remains blocked; no partition was attempted.
- `code_issue`: `unresolved`; the current safe artifact does not prove whether the live control state or adapter projection caused the rejected state.
- Semantic/protocol impact: none. Exact query/source/order/identity/completeness rules remain unchanged.

**[observed]** P06 remains an immutable technical failure. Cleanup and release were verified before supervision ended. No retry, source fallback, partition, screening, candidate import, partial-prefix retention, or final event follows it.
