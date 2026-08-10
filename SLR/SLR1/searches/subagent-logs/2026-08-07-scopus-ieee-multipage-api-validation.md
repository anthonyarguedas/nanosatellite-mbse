# Scopus and IEEE Xplore multi-page API validation — MAJOR-06 audit

**Disposition:** `completed — pilot_not_candidate_search only`.  This is an
empirical pagination/control validation, **not** a discovery run. No pilot
record was screened, retained, placed in the review corpus, or used as
review evidence. Raw responses, IDs/ranks, normalized outputs, source-client
outputs, and merge smoke-test products are Git-ignored and owner-only under
`.searches/eps-mbse-slr-2026/multipage-api-pilots/2026-08-07/independent-academic-client-audit/`
(`0700` directories; `0600` files).

The final audited live retrievals ran on **2026-08-07 15:20:15–15:20:24 UTC**
(11:20:15–11:20:24 EDT), using institutional Scopus access and the
academic-research extension. Both source snapshots completed on their first
attempt, with no total change and no retry event. This validates the request
shape and controls for the historical over-one-page pilots only; it does not
authorize a final run.

## Versioned non-secret artifacts (historical 2026-08-07 snapshot)

The checksums below preserve the version-1.2 state at this report's date; the linked tracked files were later amended prospectively for version 1.3 and are not expected to retain these hashes.

| Artifact | SHA-256 |
|---|---|
| [request templates](../api-pagination-request-templates.json) | `15087ec37cf4c510fae78583df248c28703a3257365e8e1dea6d73cd4b48a66a` (the delegated historical-pilot audit produced `6761dc755a0b96395e0f729f642c27702e35d153a55b3b5a2ae6200d2d3b81e3`; the parent-agent PRESS addendum below added validated no-type-filter final request shapes) |
| [pagination/reconciliation driver](../tools/api_pagination_reconcile.py) | `be9fd8a5202ddb8ef5fec96855d119d840a8c9fbcbbb1f8393836df594d6801e` |
| final Scopus private archive manifest | `f5b23dfe7c080097728ede0de23e2b25aa7d02581963c46f2b062b2904837581` |
| final IEEE private archive manifest | `b83d1f3f47b5d226105b8cf7083bc1f232f2150739021fc001478b514fbf2827` |

Every member listed by both final manifests was re-hashed successfully. The
prior timed-run manifests were also checked intact (Scopus
`b0b395fdd388533912511cc296300c30657dd22fc70a341687fe37b1a6f70619`; IEEE
`c18c2c3d558be6fa8b9c7a931dfd4e40e9765d65fbecdb0ca60254278c97bd25`). A
key-name scan found no serialized API key, token, cookie, authorization,
password, secret, or IEEE `userInfo` field. The driver now forces POSIX
private permissions, redacts sensitive query parameters in absolute and
relative URLs, and removes normalized sensitive/context keys before writing a
response.

## Pilot-only request templates and observed native behavior

The full non-secret request descriptors, exact historical pilot query strings,
headers, field/view, filters, sort, and pagination parameters are frozen in
`api-pagination-request-templates.json`. Scopus authentication was supplied
only as an in-memory `X-ELS-APIKey` header from the secure runtime; neither it
nor a cookie/token was written to the command, templates, archive, or log.

These strings are deliberately labelled **historical/superseded pilots**.
Their `DOCTYPE` clause (Scopus) and `ContentType` facets (IEEE) reproduce the
pilot only; they must not be silently carried into a later authorized final
search if the separately resolved strategy removes or changes those filters.
The driver supports `--ieee-no-content-type-filter` for an authorized
no-content-type IEEE run.

| Source/pilot | Native pagination observed | Explicit order and source ID | Response position contract |
|---|---|---|---|
| Scopus `S-B1` | `count=25`; zero-based `start=0,25,50,75` | `sort=eid`; `entry.eid` | `opensearch:totalResults`, `opensearch:startIndex`, `opensearch:itemsPerPage`, `entry` |
| IEEE `I-B2` | `rowsPerPage=25`; one-based `pageNumber=1,2` | `sortType=newest`; `records[].articleNumber` | `totalRecords`, `startRecord`, exclusive `endRecord`, `recordsPerPage`, `totalPages`, `records` |

A live IEEE probe at 15:21:53 UTC found `pageNumber=0` aliases page 1, so the
reconciler prohibits zero and derives pages strictly as `1,2,…`. With the
otherwise identical request, explicit `sortType=newest` produced first-page ID
digest `7c5d0571c9e909261b8933853e34a5a22a17e191767e3ee7dd8a8d8454e3515`,
while omitting `sortType` produced
`7264ba4100a827fb83ebb2620e38436d3c26b10b3f4f4f7208e1ff7c54998d2b`.
Thus the source default must not be relied on. Scopus accepted `sort=eid`; in
both full passes its 80 EIDs were lexically non-increasing.

## Actual over-one-page retrieval and reconciliation

| Pilot | Native pages per pass | Source total | Retrieved per pass | Global ranks | Ordered-ID passes identical | Missing/duplicate pages or IDs | Retries | `retrieved == source total` |
|---|---|---:|---:|---|---|---|---:|---|
| Scopus `S-B1` | `start=0:25`, `25:25`, `50:25`, `75:5` | 80 | 80, 80 | 1–25, 26–50, 51–75, 76–80 | yes | none | 0 | yes, both passes |
| IEEE `I-B2` | `page=1, start/end=0/25:25`; `page=2, start/end=25/42:17` | 42 | 42, 42 | 1–25, 26–42 | yes | none | 0 | yes, both passes |

The source-order global-ID sequence checksums were:

- Scopus: `e51c5e04645b2b7bd2e5b7a3215dedbcb569d83928bb09206e068e45c4ef6960`
- IEEE Xplore: `d39223ea029b945a1a1e4803127f31ed0c53773df6d25c088bbf747a8af70ad5`

Each private page report records its native requested parameter/value, expected
and observed source position, rank range, page-ID sequence checksum, response
and non-secret request checksums, and retry events. The final run metadata
records `successful_snapshot_attempt=1` and
`invalidated_total_change_attempts=[]` for both sources.

## Stop, retry, total-change, and reconciliation controls

The reusable driver fixes the empirically validated page size at 25, rejects
nonvalidated ordering values (`eid`/`newest` are required), refuses a
non-empty output directory, and requires at least two complete passes. Its
final-run contract is:

1. use only fixed zero-based Scopus offsets or fixed one-based IEEE page
   numbers; never infer a cursor or stop at arbitrary `max-pages`;
2. use the empirically validated explicit source order (`sort=eid`;
   `sortType=newest`) and require an identical complete second ordered-ID
   pass;
3. assign global rank from source position, require every `eid`/`articleNumber`,
   reject duplicate IDs within/across pages and repeated page-ID sequences, and
   reject a wrong offset, short nonterminal page, or absent expected page;
4. retry only network failures and HTTP 408/425/429/5xx, three times after the
   initial attempt; honor parseable `Retry-After`, otherwise wait 1/2/4 seconds
   (each wait capped at 60 seconds); redirects, access/challenge pages,
   non-JSON, and other 4xx are terminal failures;
5. invalidate and restart from page one once if the total changes during a pass
   or between verification passes; the second total change is terminal and
   produces no success summary; and
6. normalize/merge only if all expected pages exist, IDs are unique, both
   ordered passes match, and `retrieved == source total`. Failed/partial
   snapshots are never candidates.

No-network synthetic controls (all synthetic IDs; no candidate records)
passed against the final driver checksum above. They rejected a duplicate
source ID, repeated page-ID sequence, short nonterminal page, and unexpected
offset/missing page; rejected an in-pass total change; verified one clean
page-one restart after a total change and terminal failure after the second;
verified retry-after-429 behavior and terminal HTTP 403; verified the
sensitive-scrub, fixed-page-size, and fixed-order guards; and verified that
the explicit IEEE no-content-type option emits only the retained
`Language:English` facet.

## Merge compatibility preflight

The academic-research extension's `merge_search_results.py` consumed only the
first successful **private pilot** normalized pass for each source. Products
are marked `PILOT-ONLY-DO-NOT-SCREEN` and remain excluded from the review.

| Pilot | Raw | Unique | Removed | Merged private-file SHA-256 |
|---|---:|---:|---:|---|
| Scopus `S-B1` | 80 | 80 | 0 | `bb54d94c947820be4b50a45654a81088180f14f87cf5529a4930389c7cd1d0b5` |
| IEEE `I-B2` | 42 | 42 | 0 | `77a983b266605c13820adead303bfe49ac2c6ee6a368f94c4ddad42ffa85d959` |

## Tool provenance and audit note

| Tool | Version/checksum |
|---|---|
| `uv` | `0.9.28 (0e1351e40 2026-01-29)` |
| CPython used by the driver | `3.13.5` |
| `requests` pinned by the driver | `2.34.2` |
| academic `search_scopus.py` | `1c92dde7a62b43d8003767eb0b2c7c262d35ef12ac09da430da65b642def6d9d` |
| academic `search_ieee_xplore.py` | `7d09758723b759f03d5db95264bfce4c749f43022dd6b2d9c51a1d0be033ab77` |
| academic `merge_search_results.py` | `fcf0168dd25480dc882de6e53c505fb47eebc3839d772bd96fdfc1b1c921dde4` |

The extension's IEEE client independently saved and was read as a private
no-screening two-page, 42-record pilot (no warnings); its default order was
not used for reconciliation. The extension's Scopus client reached the live
source but then raised a `TypeError` while concatenating a null author
`given-name`, so it did not save an output. This is a non-blocking upstream
normalization defect for that client, not an access failure: the audited
reconciler normalizes null author fields safely and completed both live Scopus
passes through the same secure institutional credential route.

## PRESS-corrected unrestricted request addendum

After the delegated MAJOR-06 audit closed the pagination question, the parent agent applied MAJOR-01/02/07 to the final strategy and reran the same audited driver against the corrected broad requests. These are also `pilot_not_candidate_search`, with no screening or candidate use. The exact prospective request shapes are now frozen under `prospective_final_execution` in the request-template artifact.

| Corrected preflight | UTC interval | Type filter | Pages per pass | Source total | Retrieved per pass | Ordered-ID passes | Merge preflight |
|---|---|---|---:|---:|---:|---|---|
| Scopus final `S-B1` | 15:27:45–15:27:56 | none; no `DOCTYPE` clause | 4 (`25/25/25/10`) | 85 | 85, 85 | identical; 85 unique EIDs; sequence SHA-256 `d133619ebb55d0cb40e68a1781e0fbd738092f3a3c49056a6666cf61b95bf8cd` | 85 raw / 84 bibliographically unique / 1 duplicate manifestation |
| IEEE final `I-B2` | 15:27:45–15:27:53 | none; sole refinement `Language:English` | 2 (`25/22`) | 47 | 47, 47 | identical; 47 unique article numbers; sequence SHA-256 `66b71e0afa32cd9c337b6d5946b76bfc4f22b2ad7c2b3726414447e534001f39` | 47 raw / 47 unique / 0 removed |

No page was missing, repeated, short before the terminal page, or retried; each pass satisfied `retrieved == source total`. The owner-only manifests are SHA-256 `e89596345c9da44c09807b71ba205dd6a350e7de515251b443fdaad045c0a3f9` (Scopus) and `1d475b5e8fd562459c011fc8fc678f8d374b9dc87435b6c50e1a0e0b8b998934` (IEEE). The current request-template checksum in the artifact table includes both the delegated historical audit descriptors and these corrected prospective-final descriptors.

## Limitation and final-run handoff

This closes **MAJOR-06's API pagination/reconciliation validation**, not the
other strategy findings. Source totals/order can change. After the parent
strategy artifacts freeze the corrected final query strings and filters, each
authorized `S-*`/`I-*` query must be rerun from a new clean output directory
with this contract. The resulting final output—not any pilot here—is the only
material eligible to enter later deduplication/screening.
