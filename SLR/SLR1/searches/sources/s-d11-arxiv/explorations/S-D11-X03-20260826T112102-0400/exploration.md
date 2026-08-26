# arXiv X03 human-demonstration exploration

- **Session ID:** `S-D11-X03-20260826T112102-0400`
- **Source boundary:** full multidisciplinary arXiv preprint repository through normal rendered Advanced Search
- **Started / ended:** 2026-08-26T11:21:54-04:00 / 2026-08-26T11:24:27-04:00
- **Controller / operator:** Pi Terra controller / review owner operating the visible recorder-owned page
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `b058f4a1ef18da733479b9aa5e545bf57940f397713ff539d20a2af4cc02a802`
- **Diagnostic only:** yes; no screening, import, gate claim, evidence acceptance, or final event
- **Controller classification:** blocked by submitted field mismatch; not a provider or setup failure

## Question and starting state

The crosswalk row had no qualifying human demonstration. X03 asked the operator to demonstrate one visible Advanced Search using the seven-byte count-only sentinel `CubeSat` (SHA-256 `f4d8581ea796810254a292e207a7e3f680c3b60f6d41ca16d9ec7f5a68225023`), All fields, all classifications, cross-list inclusion, submitted years 2011–2026, Show abstracts, 25/page, and Relevance.

The canonical recorder self-test passed. The unintended-proxy check found no effective system or environment proxy. CfT/runtime health, one inert broker anchor, the canonical profile/endpoint, free lease, and no orphan were verified before launch.

## Real-page observations

The normal query-stripped `/search/advanced` route returned HTTP 200 and remained on the expected route family. The operator entered the sentinel, selected Date range, filled two four-character year controls, retained Submission date (most recent), retained Show abstracts, and activated Search once. The recorder observed one trusted DOM submit and no challenge or busy interval.

The terminal result surface exposed Relevance, 25 results per page, and native Next controls. The operator confirmed the aggregate terminal state with `done`; the recorder deliberately retained neither result text nor the numeric aggregate. The safe outcome is therefore **positive summary observed, numeric `total=null` (not retained)**, not zero and not a failed route.

Crucially, the pre-submit projection proved that the **Field to search** combobox still held its source default **Title**, not the instructed **All fields**. The route completed, but the intended field recipe did not. X03 therefore does not satisfy the successful-demo floor and cannot freeze an evidence plan.

The generated draft also contained character-level input events and structural clicks on a label/result container. Those were rejected. No result-container action, result card, recommendation control, opaque route, or structural ordinal selector was promoted into the implementation.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical change | Live result |
|---|---:|---:|---|---|
| 1 | Entered the redacted seven-byte sentinel in semantic **Search term** | no | Consolidate to one parameterized fill | Exact length/readback observed |
| 2 | Selected **Date range**, filled **From** and **to**, retained submitted-date behavior | no | Use role/name controls and exact readback assertions | Date range and both four-character values observed |
| 3 | Activated visible **Search** once | yes | Count the click plus DOM submit as one source operation | Normal positive summary controls; numeric total intentionally not retained |
| 4 | Bounded post-cleanup control review | no | Explicitly select/read back `all`; reject source default `title` | Submitted field mismatch identified |

## Bounded automation patch

Isolated worktree commit `a1d60a8c3db20a9d0b3f3c9cdc26543b221fbe97` changes the rendered adapter to use one visible Advanced Search form sequence instead of direct initial result navigation. It parameterizes query and years, selects and reads back **All fields**, verifies all category checkboxes clear, cross-list inclusion, submitted-date mode, Show abstracts, page size, and Relevance, then activates the semantic Search button once. It includes no challenge, login, result-card, detail, export, or candidate behavior.

- **Adapter SHA-256:** `9b1089da25d3ed3fc05a0fcb7d3d9420fa2ff65718777f4d95c87ea5c3dca3c7`
- **Domain-note SHA-256:** `94ca43a9e08c576e22dc4ffca1bad1a3540a7f56b112910de7d0e0353c45b5af`
- **Focused check:** `uv run pytest -q tests/test_search_arxiv_browser.py` — 16 passed
- **Live replay:** not run; another source submit requires a separately allocated and paced X session

## Cleanup and floor disposition

The recorder wrote `DONE.json` with owned-page cleanup verified. The attached Terminal exited 0. The outer lease reports `state=released`, `cleanup=verified-clean`; browser status returned to exactly one inert protected anchor with a free OS lock and no orphan.

**Successful-demo floor satisfied: no.** The human-operated normal route and cleanup succeeded, but the intended All-fields boundary was not submitted. Queue a new human X04 with an explicit Field-to-search step. Only after that succeeds should a separate automated X replay exercise commit `a1d60a8` and assert the exact submitted controls and aggregate/native-zero contract. No evidence acceptance is claimed.
