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

The [canonical-main shared-browser preflight](searches/browser-preflight.json) was healthy on 2026-08-30 UTC. The prior integration-worktree launcher did not load the canonical browser configuration and its local-binary finding is replaced by this source run.

### Healthy route and exact English readback

The runner first accepted both count-only source events in the 2011 through 2026 window:

| Route | Exact source-rendered query | Total |
|---|---|---:|
| Ordinary health route | `title:(microRNA) AND pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]` | 1,733 |
| English health route | `title:(microRNA) AND language:(en OR eng OR english) AND pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]` | 999 |

Both artifacts have an exact source query echo. The English route read back display label `English` and source value `(en OR eng OR english)`. This proves the metadata control for this pilot event only. It does not prove the language of a retained report.

### Rate-aware first-cell round

The run used a 20 adapter-invocation budget. Two invocations established the health routes. The remaining 18 were spent in round-robin order on the first cell of every partition, first for a count and then for strict capture. This gave all nine semantic partitions one attempted cell before any second cell could be sent.

| ID | Attempted cell | Count-only source total | Strict outcome | Remaining unattempted cells |
|---|---|---:|---|---:|
| A1 | `A1-0001-of-0016` | 0 | complete with 0 | 15 |
| A2 | `A2-0001-of-0020` | 0 | complete with 0 | 19 |
| A3 | `A3-0001-of-0008` | 1 | complete with 1 | 7 |
| B1 | `B1-0001-of-0003` | 13 | failed, OATD could not return from Record Details to search results | 2 |
| B2 | `B2-0001-of-0008` | 6 | failed, OATD Record Details page had an ambiguous resource URL | 7 |
| BG1 | `BG1-0001-of-0017` | 0 | complete with 0 | 16 |
| BG2 | `BG2-0001-of-0017` | 3 | failed, OATD could not return from Record Details to search results | 16 |
| BC1 | `BC1-0001-of-0148` | 1 | complete with 1 | 147 |
| BT2 | `BT2-0001-of-1792` | 0 | complete with 0 | 1,791 |

`B1` and `BG2` each recorded one bounded busy retry before the Record Details return failure. `B2` recorded no busy retry. The runner made no manual replay after those failures. The strict failures have null cell totals.

Every partition remains incomplete, so every partition Record-ID union and total is **null**. The 2,020 unattempted cells are null, not zero. The six strict-complete cells are only cell evidence and cannot be summed or promoted to a partition outcome.

### Request-size and rate-safe feasibility limit

OATD publishes no route-size maximum. Its observed behavior imposes a practical limit. The historical 11,902-character BG1 route returned HTTP 520 after a healthy route and a 7,642-character subexpression returned no usable result state. The repaired adapter rejects routes at 8,000 encoded characters and this pilot sends only lossless cells at or below the conservative 1,500-character target.

Strict capture requires two complete source-rendered Relevance traversals and ordered Record-ID reconciliation for every cell. The 100-record strict cell cap and the adapter's bounded busy policy of at most two retries after 30 and 60 seconds make a full 2,029-cell completion infeasible in this rate-safe diagnostic budget. No unattempted cell is inferred to have a source total. Completion remains open.

No deduplicated partition set was available, so the over-100 investigation threshold was not triggered. No refinement was applied.

## Known source limits retained

- Native oldest-first Date ordering remains unavailable. Strict capture, when possible, retains labelled source-rendered Relevance rather than client-sorting a prefix.
- OATD has no native article/document-type selector. Degree and level facets are not a lossless completed eligible-thesis filter.
- OATD exposes no named controlled vocabulary, descriptor mapping, hierarchy, or explosion option.
- The `"phrase"~N` form and the required named pair clauses are preserved, but true slop/token/direction semantics remain partly unknown; no local proximity approximation is made.
- OATD provides neither bulk download nor OAI-PMH export. Adapter-normalized strict capture is the only eligible record export route.

## Result

- [x] Document canonical-browser source evidence, route-cell limits, and incomplete unions
- [ ] Accept a final OATD translation or final search

A later pilot may resume only through a healthy shared local browser, repeat the health-plus-English exact readback, and execute the saved cells without changing their literals, pairs, Boolean relations, controls, or cell IDs. It must retain any source/busy failure and keep the affected partition union null.
