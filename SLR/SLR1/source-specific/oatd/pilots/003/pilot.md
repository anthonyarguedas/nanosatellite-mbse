# Pilot 003: lossless route-cell and Record-ID-union diagnostic

Required changes are contained in this Pilot 003 commit.

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`, invoked only through the shared local-browser wrapper by the [Pilot 003 runner](../../../../scripts/oatd_pilot003/run_pilot.py).

## Objective

Plan and, when the local browser is healthy, execute all nine direct OATD partitions with the 2011–2026 native-year window and diagnostic cutoff of 2026-08-29. This is a diagnostic pilot, **not** a final search.

The pilot must preserve every protocol literal, every named-field two-order `~5` pair, and every Boolean relation. Every route over the adapter's conservative 1,500 encoded-character cell target is represented as an explicitly grouped, lossless distributive cell. A partition receives a total only after every cell has two complete source-rendered Relevance traversals with matching ordered OATD Record IDs and the cells' Record-ID union reconciles.

## Method

- The runner imports the shared `pilot_schedule` concept declarations and the repaired read-only OATD adapter; it does not copy or shorten either translation.
- It never navigates a complete oversized query. It uses the adapter's 8,000-character navigation guard and calls `plan_lossless_oatd_or_query_cells` for every emitted grouped cell. The planner must return that cell unchanged.
- Each accepted source cell would use `English` (`(en OR eng OR english)`), `pub_dt` years 2011–2026, native 30-row pages, and source-rendered Relevance. The 2026 records still need screening against the exact 2026-08-29 cutoff.
- Before applying English to a schedule cell, the runner requires a healthy `title:(microRNA)` route in the same 2011–2026 year window, followed by that same route with English and exact rendered query readback. English metadata would remain only a metadata restriction; full-text language screening remains authoritative.
- It applies no country, Creative Commons, degree, level, completion, access, full-text, publication-type, facet, controlled-term, or wildcard restriction.
- The execution policy is sequential and rate-aware. It first count-checks a route, then runs strict two-pass capture only when its total is within the configured record cap. It uses OATD's bounded busy cooldown, distributes the request budget round-robin across the nine partitions, and leaves a total null rather than treating an unattempted/failing cell as zero.
- A complete deduplicated Record-ID union over 100 would receive a local investigation artifact. It may be refined only by a demonstrated no-loss metadata/language/eligible-type/controlled-term control; no such refinement is preaccepted.

## Exact cell plan

The [lossless cell plan](searches/lossless-cell-plan.json) retains the exact query for every cell, its SHA-256, route length, factor-group membership, coverage arithmetic, and named-pair audit. It has 2,029 cells in total.

| ID | Cells | Full grouped route chars (never navigated) | Largest cell chars | Planned outcome |
|---|---:|---:|---:|---|
| A1 | 16 | 3,411 | 1,493 | strict Record-ID union or null |
| A2 | 20 | 4,192 | 1,462 | strict Record-ID union or null |
| A3 | 8 | 2,701 | 1,490 | strict Record-ID union or null |
| B1 | 3 | 2,347 | 1,286 | strict Record-ID union or null |
| B2 | 8 | 2,731 | 1,488 | strict Record-ID union or null |
| BG1 | 17 | 11,944 | 1,443 | strict Record-ID union or null |
| BG2 | 17 | 10,777 | 1,407 | strict Record-ID union or null |
| BC1 | 148 | 37,542 | 1,452 | strict Record-ID union or null |
| BT2 | 1,792 | 135,090 | 1,439 | strict Record-ID union or null |

`BG1`, `BG2`, `BC1`, and `BT2` retain respectively 16, 16, 36, and 224 complete pair unions. Their audit confirms 192, 192, 432, and 2,688 individual named-field/two-order `~5` clauses. `BT2` is intentionally large: the 224 complete pair unions were not flattened, omitted, or sent through the historical oversized route.

## Execution result

The [shared-browser preflight](searches/browser-preflight.json) at 2026-08-30 UTC found no usable local Chrome binary. No OATD page was opened and no source request was made. This is a local browser-availability failure, not an OATD zero, syntax result, or route/readiness observation.

The [execution assessment](searches/execution-assessment.json) therefore records all 2,029 cells as unattempted and all nine outcomes/unions as null:

| ID | Strict-complete cells | Record-ID union / total |
|---|---:|---:|
| A1 | 0 / 16 | null |
| A2 | 0 / 20 | null |
| A3 | 0 / 8 | null |
| B1 | 0 / 3 | null |
| B2 | 0 / 8 | null |
| BG1 | 0 / 17 | null |
| BG2 | 0 / 17 | null |
| BC1 | 0 / 148 | null |
| BT2 | 0 / 1,792 | null |

The integration OATD note records dated technical evidence that a healthy route followed by English read back the native metadata clause. That evidence was not promoted to a Pilot 003 source event because this pilot could not obtain its own healthy route. No English-filtered schedule cell, count, record, or language conclusion is claimed here.

No deduplicated set was available, so the over-100 investigation threshold was not triggered. No refinement was applied.

## Known source limits retained

- Native oldest-first Date ordering remains unavailable. Strict capture, when possible, retains labelled source-rendered Relevance rather than client-sorting a prefix.
- OATD has no native article/document-type selector. Degree and level facets are not a lossless completed eligible-thesis filter.
- OATD exposes no named controlled vocabulary, descriptor mapping, hierarchy, or explosion option.
- The `"phrase"~N` form and the required named pair clauses are preserved, but true slop/token/direction semantics remain partly unknown; no local proximity approximation is made.
- OATD provides neither bulk download nor OAI-PMH export. Adapter-normalized strict capture is the only eligible record export route.

## Result

- [x] Document route-cell and local-browser limitations
- [ ] Accept a final OATD translation or final search

A later pilot may resume only through a healthy shared local browser, repeat the health-plus-English exact readback, and execute the saved cells without changing their literals, pairs, Boolean relations, controls, or cell IDs. It must retain any source/busy failure and keep the affected partition union null.
