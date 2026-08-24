# Browser-route decision and corrective pilot

## Human direction

On 2026-08-24, the review owner directed that `search_ntrs.py` stop using the NTRS JSON API and instead use the normal rendered browser interface, following the other browser-backed academic-search adapters. The same direction authorized one browser-backed retry.

This direction changed the implementation route only. It did not accept a source method, query translation, result count, paired-term fallback, or pilot.

## Browser adapter implementation

The replacement was committed in `agent-tools` as:

- `ecc7588f0aeed0674904d7e09394427442118a1e` — replace the API adapter with the rendered NTRS browser UI; and
- `ff6ed0facc70f95a3096b8ef49b35619b24cacc9` — harden the known Angular zero-card, paginator-range, targetless-Next, and result-card parsing hypotheses.

The adapter defaults to an adapter-owned tab in local Chrome, uses visible controls and rendered DOM evidence, and has a static guard against direct NTRS API transport, page-side fetch/XHR, or fallback. Its selectors remain subject to live pilot validation.

## P03 outcome

Pilot `S-D13-P03-20260824T125840-0400` used a fresh isolated Chrome endpoint and the pinned browser adapter. The sole authorized count-only `nanosatellite` gate failed at the navigation stage after the finite timeout. The failure artifact has `total=null`, zero records, and no visible form, submitted query, result range, canonical ID, or explicit zero. The adapter closed its page and preserved the controller anchor.

P03 stopped without retrying. Consequently, all current-interface behavior and all nine partition transports remain blocked. `code_issue=unresolved`: the evidence does not distinguish current source reachability from an adapter navigation defect without another live attempt.

No API call, screening, candidate import, direct-query fallback, protocol semantic change, or paired-term weakening occurred. A later pilot requires fresh authorization after normal public `/search` reachability has been established independently.
