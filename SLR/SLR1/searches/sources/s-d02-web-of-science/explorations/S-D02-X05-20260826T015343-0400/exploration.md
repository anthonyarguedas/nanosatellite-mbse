# Web of Science X05 interactive hydrated-control exploration

- **Session:** `S-D02-X05-20260826T015343-0400`
- **Mode:** X diagnostic only
- **Terminal:** guardian deadline after live inspection; no query submit; outer cleanup verified

One owned page navigated to the normal Basic Search route and retained screenshots before semantic projections. Live inspection isolated the current controls:

- the database, `All` edition, and Topic comboboxes each exist semantically after later hydration;
- the old exact edition selector and dialog are valid once ready; Select All was checked and all 10 individual editions were checked;
- a language criterion is added through Add Row → Language → English, which produced one accessible Language/English control and no Document Type;
- publication dates require the visible Add Date Range path before selecting Publication Date and filling the date inputs.

These observations explain X04: initial hydration returned before the edition control was durably ready, and the existing date helper assumed Publication Date was already exposed. X05 did not reach exact date/query preparation or native submit before the lease reserve. Source submits/reissues are zero; total is `null`, not zero. No records, identifiers, screening, import, gate, or final event occurred.

The outer guardian closed the owned page, preserved one inert anchor, found no orphan, and released with `cleanup=verified-clean`. Exact-window Sleep/Wake/DarkWake and System Information/About This Mac checks were zero. Child exit 124 is controller timing, not provider failure.

**No freeze.** A source-free patch must wait/retry the semantic edition surface and implement Add Date Range → Publication Date, then a later X must live-prove the one-submit aggregate route.
