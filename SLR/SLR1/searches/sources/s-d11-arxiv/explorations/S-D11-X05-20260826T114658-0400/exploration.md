# arXiv X05 automated replay exploration

- **Session ID:** `S-D11-X05-20260826T114658-0400`
- **Source boundary:** full multidisciplinary arXiv preprint repository through normal rendered Advanced Search
- **Started / ended:** 2026-08-26T11:47:14-04:00 / 2026-08-26T11:48:03-04:00
- **Controller / executor:** Pi Terra controller / patched deterministic adapter
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `b8e79ddbd248ccdd7d2c855b414c9f65f13b6c2089c2bdca7fa606fffb01b3f1`
- **Diagnostic only:** yes; no screening, import, gate claim, evidence acceptance, or final event
- **Controller classification:** failed automated replay; no retry

## Replay question

X04 supplied a successful current human demonstration of `CubeSat` in All fields with all classifications, cross-list inclusion, submitted years 2011–2026, Show abstracts, 25/page, Relevance, and one positive-summary submit. X05 tested whether isolated adapter commit `a1d60a8c3db20a9d0b3f3c9cdc26543b221fbe97` could replay that visible recipe once.

The invocation was count-only with one owned page, one source-owned Advanced Search start, `limit=1`, `max-pages=1`, no abstract expansion, no retry, and create-only restricted output.

## Result

The adapter exited 1 after about one 45-second control deadline with `ArxivProtocolError`. It published a record-free non-mergeable failure artifact with:

- `total=null` and no explicit zero;
- zero pages, source entries, results, or discarded prefix;
- no exact query echo and no effective executed query;
- zero retained/imported records; and
- no access/challenge error classification.

The safe failure artifact does not expose whether the Search activation was dispatched, so query-submit accounting is explicitly `null`, not guessed. No source operation was reissued.

The initial patch required a pre-submit **Sort results by** control, while the human recording demonstrated Relevance on the resulting summary surface. The 45-second protocol timeout is consistent with that premature locator, but the adapter intentionally collapsed the underlying control stage; this diagnosis is **inferred**, not observed. A source-free follow-up removed the pre-submit sort requirement and leaves Relevance to the existing post-submit result-state assertion.

## Implementation after failure

- Failed replay commit: `a1d60a8c3db20a9d0b3f3c9cdc26543b221fbe97`
- Source-free follow-up commit: `85dfce52d97c254eab49d005ef265a252f6c3d4f`
- Current adapter SHA-256: `cd89251884b6e6e66299dacbbc9254d95fbd03c52b4c97cf7bc7589fe2fa73a9`
- Current domain-note SHA-256: `2f439e9445f1af47f3370084460bc8e30c3483123cdcabc30a63a47ae609327e`
- Focused check: `uv run pytest -q tests/test_search_arxiv_browser.py` — 16 passed
- Follow-up live replay: not run; X05 permits no retry and another source submit would require a new paced session

The current follow-up remains unvalidated on the real page. X05 therefore confirms that the demonstration-to-automation conversion is **not yet robust enough** for deterministic use. X04 still satisfies the human-demo floor, but no evidence plan may be frozen.

## Cleanup and next disposition

The outer lease reports `state=released`, `cleanup=verified-clean`. Postflight browser status returned to exactly one inert protected anchor with a free OS lock and no orphan.

Stop the serial demonstration campaign here for controller redesign. Any future arXiv work starts with a new X session, stage-specific safe observability, and a single replay of the corrected commit; it is not authorized by this record. No evidence acceptance is claimed.
