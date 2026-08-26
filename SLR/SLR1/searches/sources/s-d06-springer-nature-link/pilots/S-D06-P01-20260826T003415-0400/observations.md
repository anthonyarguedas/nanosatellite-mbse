# S-D06 P01 deterministic health evidence observations

**Status:** failed closed at the evidence-publication contract; diagnostic only; not accepted.

- P01 executed the one-operation health route frozen by `S-D06-X01-20260826T001901-0400` using exact `"CubeSat"`, source years 2011–2026, English, Relevance, page size 20, one rendered page, and no source retry. Adapter commit/hash were pinned to `aa10b5f885a20603f3fef0c77bbb9cf2ab45b6a7` / `6ebf902cfb279224759622c260040b1dd78a365f891862f7f46615e68b81327d`; no implementation was patched.
- The adapter exited zero and its restricted diagnostic reported source total 2,132, one page, 20 rendered rows, and verified source controls, matching X01's live comparator.
- The deterministic publication nevertheless contradicted the frozen evidence contract: it set `observed_exact_query_echo=false` and `executed_query=""`, while also serializing 20 ordered canonical record paths in count-only metadata. The frozen plan required positive exact query readback and zero retained card/identity data. The accepted evidence total is therefore `null`, not 2,132 or zero; no gate is passed from this operation.
- This is a controller-technical output/publication failure, not a provider failure or methodological uncertainty. Preserve P01 once and return Springer to exploration; do not patch or retry in evidence mode.
- The restricted identity list was not copied into Git, screened, judged, imported, or used as a candidate prefix. Records imported remain zero.
- The canonical lease released with `cleanup=verified-clean`; one inert anchor was preserved and no orphan remained. Exact-window checks found no Sleep/Wake/DarkWake or System Information/About This Mac launch.
- No native CSV, detail page, partition, completeness pass, screening, import, or final event occurred.
