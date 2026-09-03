# Open Access Theses and Dissertations

Last pilot saved in commit: 38aedc3de4731e0da5f063a053e92ebd88a84db0
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`

Save final per-gate evidence under `final-searches/gates/` and the hydrated deduplicated source union as `final-searches/hydrated-union.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Open Access Theses and Dissertations (OATD)
- Interface: Web
- Platform: OATD
- URL: https://oatd.org/oatd/search
- Search field or local route: Raw basic `q` across the source-advertised metadata scope.
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. The adapter expands years to calendar bounds. Screen the cutoff year against the exact cutoff if needed.
- Language: A dated technical healthy-route check confirmed the native English metadata option `English` with source value `(en OR eng OR english)`. Apply it only when that event has an exact source-rendered route/query readback. Otherwise leave the event unrun or failed rather than assuming the control applied. This metadata restriction does not prove report language. Full-text screening remains authoritative.
- Publication type: OATD is ETD-scoped, but apply no degree, level, completion, peer-review, availability, access, or full-text filter. Metadata can include incomplete, undergraduate, or abstract-only work. Resolve those statuses during screening.
- Database or collection selection: Full OATD index with no country, university, degree, level, or Creative Commons restriction.
- Other shared limits: None.

## Selected final search route

Retire the broad `P`-only detail route. Pilot 004 proved a dated controlled `P` total of 1,249 and stopped after hydrating 338 records. Every resume repeated a 42-page identity scan, and the last continuation ended on HTTP 504.

Use the following exact eight-gate union under the same English and year controls:

```text
(P AND M_H)
OR (P AND M_B AND E_F)
OR (P AND M_B AND E_H)
OR (P AND M_B AND R)
OR (P AND M_B AND T_precise)
OR (P AND G_model)
OR (P AND G_structure)
OR (P AND C1)
```

This is algebraically equal to the original nine-partition candidate union. `B1` contains `A1` and the `M_H` branch of `A2`. The four `M_B` gates cover the other `A2` branch, `A3`, `B2`, and `BT2`. The final three gates equal `BG1`, `BG2`, and `BC1`.

Pilot 005 completed exact count readback for all eight gates. Totals were 16, 2, 2, 10, 0, 0, 3, and 1. Their occurrence sum is 34, so the deduplicated candidate union cannot exceed 34 for that dated observation. Count-only events do not establish the exact union.

Pilot 006 collected two complete card-ID passes for every gate without opening Record Details. All pass pairs had equal stable-ID sets. The 34 gate occurrences deduplicated to 26 stable source IDs, with eight duplicate occurrences. Nine IDs intersect the partial Pilot 004 detail checkpoint, and 17 have no saved detail. Pilot 006 does not approve reuse of earlier details for a final search.

Pilot 007 obtained a fresh initial snapshot for every gate, hydrated all 26 unique IDs once without reusing Pilot 004 records, and reconciled every post-hydration confirming set. It completed with no busy retry or native-order drift. Twenty-five records exposed an abstract. One explicitly lacked an abstract.

A final search must repeat the complete Pilot 007 workflow with the final common cutoff and fresh outputs. Store only validated public metadata and path-free checkpoint evidence. Preserve gate provenance. Publish the hydrated union through the standard merge and report contract. A failed detail or incomplete confirming gate leaves the complete source union null.

Apply `English` with source value `(en OR eng OR english)` and `--year-start 2011 --year-end <cutoff-year>` to every gate. Require exact rendered query readback. The exact cutoff day remains a screening and local date-accounting check for records in the cutoff year.

Adapter v10 always saves full-page `<output-stem>.search-page.png` and `<output-stem>.results-page.png` files beside each CLI JSON. The first image shows the exact raw query in the basic query field. The second follows first-results and exact-query validation. The CLI has no screenshot opt-out.

Retain the visible Record Details Publication Date as `publicationDateReadback`. Its status is `within_bounds`, `absent_unresolved`, or `visible_date_conflicts_with_source_filter`. It never removes a source card. Local schedule annotations may support audit and screening priority. A local negative never removes a source record because source analyzer equivalence and complete visible-field coverage remain unproved.

## Local schedule annotation translation

Use the exact concept membership and Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-screening.md#search-streams-and-set-construction) at protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`. The local plan retains every listed literal and Boolean relation. It uses no wildcard, proximity operator, pair expansion, or unrequested variant.

- Literal `L(s)`: Use one straight double-quoted literal.
- Boolean: Use uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: Join every ordinary member with `OR`. Fully parenthesize the block.
- Compound blocks: Render the protocol definitions directly. Use `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))` for `G_model`. Use `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))` for `G_structure`. Use `F(C1_fixed) OR F(G_DSL)` for `C1`.
- Controlled vocabulary: Add no supplement. Free text remains mandatory.

## Local schedule annotations

The table identifies local plan expressions. It no longer defines nine final source submissions.

| ID | Source construction |
|---|---|
| `A1` | `F(P) AND F(E_H) AND F(M_H)` |
| `A2` | `F(P) AND F(E_F) AND (F(M_H) OR F(M_B))` |
| `A3` | `F(P) AND F(E_H) AND F(M_B)` |
| `B1` | `F(P) AND F(M_H)` |
| `B2` | `F(P) AND F(M_B) AND F(R)` |
| `BG1` | `F(P) AND F(G_model)` |
| `BG2` | `F(P) AND F(G_structure)` |
| `BC1` | `F(P) AND F(C1)` |
| `BT2` | `F(P) AND F(M_B) AND F(T_precise)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): `A1` count-only succeeded with total `1`. `BG1` was a complete named-field translation, but OATD did not become ready within the bounded request. Do not treat it as zero or syntax success, and do not use the artifact as a final search.
- [x] [Pilot 002](pilots/002/pilot.md): the unchanged one-page `BG1` retry again failed readiness with no total. The stop rule left English `A1` and wildcard checks unrun.
- [Pilot 003](pilots/003/pilot.md): the canonical shared browser completed a healthy route and exact English readback, then attempted the first lossless cell in every partition under a 20-invocation round-robin budget. Six cells completed strict capture and three had explicit source failures. All incomplete partition totals and unions remain null. The 2,029-cell plan is retired for final use. Retain it only as diagnostic evidence for Pilot 003. This is not a final search.
- [x] [Pilot 004](pilots/004/pilot.md): the controlled `P` route returned 1,249 stable IDs and hydrated 338 details through a durable checkpoint. Repeated busy, challenge, metadata, and HTTP 504 failures prevented completion. Pilot 005 retires this broad detail route. No Pilot 004 artifact is mergeable.
- [x] [Pilot 005](pilots/005/pilot.md): all eight exact candidate-union gates completed count-only readback with totals 16, 2, 2, 10, 0, 0, 3, and 1. Their sum gives a 34-record upper bound before cross-gate deduplication. Pilot 006 validates their stable-ID union.
- [x] [Pilot 006](pilots/006/pilot.md): all eight gates completed two card-only passes with no busy retry, order drift, or detail request. The 34 occurrences deduplicated to 26 stable IDs. Pilot 007 validates bounded hydration.
- [x] [Pilot 007](pilots/007/pilot.md): fresh initial and confirming snapshots retained all 26 stable IDs. The run hydrated all 26 normalized details once, reused no Pilot 004 record, and needed no busy retry. One 2026 record has only year precision and requires exact-cutoff resolution during screening. Use this route for a fresh final search with standard merge and report publication.
