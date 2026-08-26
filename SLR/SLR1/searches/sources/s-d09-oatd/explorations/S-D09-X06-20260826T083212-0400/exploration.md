# OATD X06 home-entry exploration

- **Session ID:** `S-D09-X06-20260826T083212-0400`
- **Source:** Open Access Theses and Dissertations (OATD)
- **Started / ended:** 2026-08-26T08:32:12-04:00 / 2026-08-26T08:42:13-04:00
- **Controller / interactive agent:** Pi controller / Terra interactive browser agent
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `65e5e75fc86374b1493528872d5d2086a56f8c971d5e34c7f69f50418461c6cc`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Terminal status:** agent deadline before activating Advanced Search; outer cleanup verified

## Question and live observation

X06 tested the review owner's report that the usable composer should be entered from the normal home page instead of opening `/oatd/search-composer` directly. One owned page navigated once to `https://oatd.org/`. It rendered the normal source home without challenge, access, or busy state. Restricted screenshots visibly show the source-owned blue control labelled **Advanced search options** below the basic query box.

The agent searched for the stricter label “Advanced Search” and produced several bounded DOM/accessibility projections, but did not resolve the actual visible **Advanced search options** control as an actionable element before the 600-second deadline. It therefore clicked it zero times, did not reveal or inspect the composer, did not fill the held 17-byte title sentinel, and dispatched no native submit or reissue. Total remains `null`, not zero.

The screenshots retain current home-page records only in restricted storage; no record content was projected, screened, or imported. The guardian closed the lease-new page, preserved the inert anchor, reported `cleanup=verified-clean`, found no orphan, and released the lease. No Sleep/Wake/DarkWake or About This Mac/System Information event occurred.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical change | Result |
|---|---|---:|---|---|
| 1 | Opened the normal home page and captured the viewport before semantic inspection. | no | none | Normal home rendered; **Advanced search options** visibly present. |
| 2 | Ran bounded DOM and accessibility projections using the stricter “Advanced Search” label. | no | none | Actual control was not resolved; no click occurred. |
| 3 | Stopped at the guardian deadline. | no | none | Composer and aggregate route remain untested. |

## Working interaction recipe

The first step is now live-proven: navigate only to the home page. The exact visible label is **Advanced search options**, not “Advanced Search”. A complete interaction recipe is not yet frozen because X06 did not activate that control.

## Proposed evidence attempt

**Not frozen.** The next X session should use the exact visible label **Advanced search options**, click it once on the same owned home page, require the canonical advanced form to become visible, then fill and submit the title sentinel once and reconcile an aggregate result. P05 remains held.
