# S-D13-P05 NTRS diagnostic observations

## Terminal status and scope

**[observed]** Attempt `S-D13-P05-20260825T112127-0400` was allocated as the prospectively authorized `controller_technical` attempt under `D-TECH-NEXT-P05`. It is **failed at the conditional rendered operation** after completing both allowed live operations. The live phase performed exactly **2 of 2** planned operations: one source-health precheck and one conditional rendered count-only classification.

**[observed]** The source-health precheck passed. Its record-free receipt reports one root navigation, HTTP `2xx`, `normal_source_route`, source identity, a visible search control, two stable samples, no challenge/access/login/busy/error marker, `source_total=null`, zero records, and verified closure of its adapter-owned page while preserving the baseline page.

**[observed]** Because health passed, the sole conditional rendered operation ran once with the exact immutable 13-byte `nanosatellite` input, `--limit 1`, `--max-pages 1`, `--count-only`, `--skip-full-abstracts`, 90-second timeout, zero delays, no date control, and the canonical loopback endpoint. It reached a normal rendered navigation (`2xx`) but stopped at the adapter's ordering-control reconciliation stage before query echo, result total, range, row, canonical ID, or explicit zero was observed. The adapter output is a record-free failure with `total=null` and `results=[]`; its `executed_query` is blank because exact source echo was not established.

**[observed]** No partial prefix, explicit zero, screening input, candidate record, relevance classification, PRISMA identification count, or final event was created. `null` is retained for the unobserved source total; no zero is claimed.

## Operations and accounting

| Operation | Status | Source total | Records | Evidence |
| --- | --- | ---: | ---: | --- |
| 1. Record-free rendered source-health root navigation | **passed** | `null` / not applicable | 0 | restricted `op-01-source-health.json` |
| 2. Conditional rendered count-only `nanosatellite` classification | **failed at ordering reconciliation** | `null` | 0 | restricted `op-02-rendered-g01.json` |

The fixed `RP-D13-BUSY-01` policy allowed no retries or same-tab busy reissues. The three-second interval between the distinct operations was passive pacing, not a source retry. No challenge or busy condition was observed. No API/HTTP fallback, second query, partition, date control, detail visit, export, completeness pass, or other source was attempted.

## Browser, lease, power, and cleanup

**[observed]** The complete live phase ran attached through process-scoped `caffeinate -dims` and the required `run_with_browser_lease.py` wrapper with owner, source, immutable receipt, `--wait 30`, and `--lease-timeout 600`. The lease receipt reports the independently current browser epoch `bldqawxcF3fqkU-S9IBNeLhNxQf0jcIT`, one protected inert baseline page, and `cleanup=verified-clean` with `state=released` and child exit status 1.

**[observed]** Before and after the phase, the canonical shared CfT used `127.0.0.1:9222`, the canonical shared profile, one top-level CfT profile owner, CfT bundle `com.google.chrome.for.testing`, and matching runtime/disk version `152.0.7977.54`. The protected inert anchor remained intact and no lease child/group remained. AC power was present at 100%, and the read-only Sleep/Wake log check observed no Sleep/Wake/DarkWake transition during the exact lease window.

The launch-context prompt reported epoch `5ASpPQYHIFJh_uD--zoyM7LG5u6fCcKh`, while independent current-instance reconciliation reported `bldqawxcF3fqkU-S9IBNeLhNxQf0jcIT`; the released prior lease metadata named the older epoch. The current proven instance epoch was used. This was a controller-technical provenance reconciliation, not a source or review-semantic change.

## Capability and code decisions

**[observed]** `G-SOURCE-HEALTH` now has a stable observed pass for this phase through the health receipt. `G-RENDERED-NAVIGATION` remains failed: normal root navigation was observed, but the one permitted adapter classification did not reach a reconcilable rendered result state. `G-PARTITION-TRANSPORT` and all nine partition translations remain blocked. No capability gate is accepted merely from this diagnostic.

**[observed]** Current source-free adapter tests passed (34 focused tests); the source-health probe tests passed (14 tests); CLI help checks, exact query/hash checks, translation-cell checks, and the shared infrastructure validator passed. The external `agent-tools` checkout was read-only; its unrelated dirty paths were preserved. No external adapter patch was made.

**[unresolved]** `code_issue=unresolved`. The live failure is specifically `NTRSProtocolError` at ordering-control reconciliation after a healthy normal route, but the record-free artifact does not prove whether the current source rendered an unsupported/ambiguous ordering surface or the adapter's current ordering projection is defective. The smallest technical diagnosis is source-free inspection of the current `parse_visible_controls` / `NTRS_FORM_STATE_SCRIPT` ordering branch, followed—only if the observed payload proves an implementation defect—by a behavior-preserving external adapter patch with a focused fixture and rerun of the offline suite. No P05 live retry is authorized.

No methodological decision was made or requested. Query semantics, source boundary, fields, limits, date/language rules, identity, capture, completeness meaning, and PRISMA accounting were unchanged; semantic impact is none. The attempt is not an accepted pilot and does not support a final search.

**Smallest next action:** preserve this failed attempt and independently diagnose the ordering-control evidence; obtain a separately authorized corrective live scope only if the owner/supervisor decides it is warranted. Do not rerun P05, widen the query, or proceed to partitions.

**Explicitly:** no screening, candidate import, final event, or relevance classification occurred.
