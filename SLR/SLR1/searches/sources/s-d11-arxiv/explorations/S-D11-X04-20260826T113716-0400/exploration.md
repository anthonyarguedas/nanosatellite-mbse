# arXiv X04 successful human-demonstration exploration

- **Session ID:** `S-D11-X04-20260826T113716-0400`
- **Source boundary:** full multidisciplinary arXiv preprint repository through normal rendered Advanced Search
- **Started / ended:** 2026-08-26T11:37:55-04:00 / 2026-08-26T11:40:30-04:00
- **Controller / operator:** Pi Terra controller / review owner operating the visible recorder-owned page
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `1b5d142c8465466dafaab9eff68239fb082982132d630d1f39c99476f12857c9`
- **Diagnostic only:** yes; no screening, import, gate claim, evidence acceptance, or final event
- **Controller classification:** successful human demonstration; evidence plan not frozen

## Question and starting state

X03 reached a normal result summary but retained arXiv's default Title field instead of the intended All fields boundary. X04 repeated the same seven-byte count-only sentinel `CubeSat` (SHA-256 `f4d8581ea796810254a292e207a7e3f680c3b60f6d41ca16d9ec7f5a68225023`) and required the operator to select **All fields** explicitly before one submit.

The canonical recorder self-test passed again. The unintended-proxy check found no effective system or environment proxy. CfT/runtime health, one inert broker anchor, canonical profile/endpoint, free lease, and no orphan were verified before launch.

## Real-page observations

The normal query-stripped `/search/advanced` route returned HTTP 200. Before submit, the bounded recorder projection proved:

- the redacted Search term had seven UTF-8 bytes;
- **Field to search = All fields**;
- every visible classification category checkbox was clear and the physics subtopic remained `all`;
- **Include cross-listed papers** was checked;
- **Date range** was checked with two four-character values;
- **Submission date (most recent)** was checked;
- **Show abstracts** was checked; and
- native page size was 25.

The operator deliberately reselected some source defaults to verify them. Those diagnostic toggles and duplicate fills are not automation steps. The working recipe sets each desired state directly, reads it back, and submits once.

One visible Search activation generated one trusted DOM submit. The terminal result surface retained 25/page, Relevance, and two semantically duplicated native Next controls. This establishes a normal positive summary transition. The recorder intentionally retained neither result text nor the numeric aggregate, so the explicit accounting is **positive aggregate observed; numeric `total=null` (not retained)**. It is not zero and no candidate/result record was retained.

No challenge or busy interval occurred, and no challenge-time action exists.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical disposition | Live result |
|---|---:|---:|---|---|
| 1 | Explicitly changed Field to search from Title to All fields | no | Semantic combobox selection plus exact readback | All fields proved before submit |
| 2 | Reconfirmed all-classification/cross-list/date/abstract controls and filled years | no | Collapse toggles and repeated typing into direct state checks and one fill per value | Intended control state proved |
| 3 | Activated visible Search once | yes | One source operation; DOM submit is not a second operation | Normal positive summary, 25/page, Relevance, Next controls |

## Bounded automation patch

The X03-derived isolated worktree commit `a1d60a8c3db20a9d0b3f3c9cdc26543b221fbe97` already matches the corrected X04 recipe: semantic role/name controls, explicit All-fields selection/readback, all-classification assertion, direct desired radio states, parameterized query/years, 25/page, Relevance, and one Search activation. X04 introduced no additional code change.

Generated structural fieldset/div/label selectors, repeated default toggles, character-level and duplicate fills, result-container clicks, and post-result verification clicks were rejected. No challenge selector, login action, result card, recommendation control, candidate metadata, detail route, export, or opaque route appears in the patch.

- **Adapter commit:** `a1d60a8c3db20a9d0b3f3c9cdc26543b221fbe97`
- **Adapter SHA-256:** `9b1089da25d3ed3fc05a0fcb7d3d9420fa2ff65718777f4d95c87ea5c3dca3c7`
- **Domain-note SHA-256:** `94ca43a9e08c576e22dc4ffca1bad1a3540a7f56b112910de7d0e0353c45b5af`
- **Focused check:** `uv run pytest -q tests/test_search_arxiv_browser.py` — 16 passed
- **Automated live replay:** not run; it requires a separately allocated and paced X session

## Cleanup, floor, and next step

The recorder wrote `DONE.json` with owned-page cleanup verified. The attached Terminal exited 0. The outer lease reports `state=released`, `cleanup=verified-clean`; browser status returned to exactly one inert protected anchor, a free OS lock, and no orphan.

**Successful-demo floor satisfied: yes.** A human operated the canonical recorder-owned page; the exact source boundary and normal interface were reached; the intended All-fields/count-only route completed with one submit and a positive aggregate state; challenge actions were absent; and owned-page cleanup plus lease release were verified.

This is not deterministic evidence and passes no campaign gate. Queue a later automated X replay of commit `a1d60a8` requiring exact submitted controls, query echo, aggregate/native-zero reconciliation, and cleanup before any evidence-mode plan can be frozen. Field semantics, exact date/version policy, stable identity, pagination completeness, and retrieval remain outside this demonstration.
