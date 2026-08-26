# PQDT Global X02 live parser diagnostic

- **Session ID:** `S-D08-X02-20260825T232157-0400`
- **Source:** ProQuest Dissertations & Theses Global (PQDT Global)
- **Started / ended:** 2026-08-25T23:21:57-04:00 / 2026-08-25T23:28:35-04:00
- **Controller / interactive agent:** Pi controller / Terra interactive browser agent
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `5f49d29a62b086ce2a56ddc36115e8be368688f60f70d48de9f974eedbed5691`
- **Mode:** diagnostic only; no evidence release, screening, import, gate claim, or final search
- **Live source interval:** 2026-08-26T03:26:43.776906Z to 2026-08-26T03:26:49.883465Z
- **Query receipt:** exact `TI("CubeSat")`, 13 UTF-8 bytes, SHA-256 `ba78df8cd0f352dc03f0f14ce9026d98b1862f3105b6cb93bafca54287c8d2d1`; no date/language suffix

## Parser and control receipt

The patched database parser passed on the database-selection route and preserved the sole selected public label: **ProQuest Dissertations & Theses Global Full Text Included**. The initial Command Line form parser and expanded result-controls parser both passed. Result page options were expanded; Relevance, page size 20, duplicate exclusion off, spelling variants on, plural/adjective forms on, and Full text off were confirmed. The optional role survey was absent on this run.

## Count-only route receipt

There was exactly one submit action. The result parser passed after two same-page polls. The exact-query echo was true; there was one total node, zero native-zero nodes, 20 rendered-row count only, aggregate total 205, and one Next control. Loading, access, busy, and syntax categories were false at the terminal observation. No record content, title, author, identifier, result URL, session state, or relevance judgment was retained.

## Restricted artifacts and cleanup

Restricted screenshots and the bounded live summary are under `.searches/s-d08-proquest-pqdt/S-D08-X02-20260825T232157-0400/` and remain Git-ignored. Their hashes are indexed in `restricted-evidence-index.json`. One fresh owned browser page was created and closed; no pre-existing page was inspected, navigated, or closed. The outer runner independently recorded `cleanup=verified-clean` and `state=released`, preserved the one inert broker anchor, and found no orphan. The phase ran under process-scoped `caffeinate -dims` on AC power with no Sleep/Wake/DarkWake event.

## Implementation

- **Frozen worktree commit:** `4abae7c2c8f06630a3a13bac66c21b251d5360ca`
- **PQDT parser implementation introduced by:** `fbe5b9117170c483207ffbe3f1865ca7c541897c`
- **Frozen adapter SHA-256:** `b569d06db64c12269d704ea2f4585de807d0c4b130447d38868509de3fad7289`
- **Session patch:** none; all four pinned parser stages passed on the real page
- **Remaining unknowns:** other field codes, date/language suffixes, partitions, pair semantics, strict retrieval, stable identity, pagination, and completeness

## Frozen proposed deterministic evidence plan

**Frozen proposal: yes.** The prerequisite patched parser stages and end-to-end count-only route both worked. In one immutable evidence attempt, use one owned page and the same normal PQDT routes; reprove exactly one selected allowlisted database and all listed controls; fill exact `TI("CubeSat")`; click submit once; and poll only that page for an exact query echo plus one internally reconciled aggregate total or native zero. The current freshness comparator is total 205 with 20 rows and one Next control; a changed database total must still reconcile internally. Retain zero records. Any selection/control ambiguity, missing echo/total, challenge, access, busy, syntax, timeout, parser/publication failure, or cleanup discrepancy is `total=null` and returns PQDT to exploration. This exploration is not evidence and makes no acceptance or gate claim.
