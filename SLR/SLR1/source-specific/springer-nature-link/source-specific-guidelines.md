# Springer Nature Link

Last pilot saved in commit: 49c0cca95b2f4d5551a0d1cb5ce24dc01a8ba7b8
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_springer_link.py`

Save primary final searches in `final-searches/` and name each JSON artifact with its query ID, such as `A1.json`. Adapter version 12 always saves `A1.search-page.png` and `A1.results-page.png` beside that JSON. There is no screenshot option. A successful event requires both PNGs and their hashes, dimensions, and privacy receipt in the JSON.

The JSON and its sibling screenshots are authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Springer Nature Link
- Interface: Web
- Platform: Springer Nature Link
- URL: https://link.springer.com/search
- Search field or local route: Raw Keywords field over title, abstract, and body text.
- Main evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. The script applies source year bounds and checks exact retained dates.
- Language: Apply the validated `En` Link language facet. This metadata limiter does not replace English full-text screening.
- Publication type: Apply no content-type limiter: Link content-type facets overlap and card labels can differ from facet values, so Article plus Chapter is not a demonstrated complete eligible-report union. Do not apply peer-review, access, or full-text-availability limits.
- Database or collection selection: Full Springer Nature Link platform with no content type, access, subject, or brand facet.
- Discipline and Subdiscipline filters: Do not use either UI filter. A pilot search returned *Magnetometer-only linear attitude estimation for bias momentum pico-satellite*, which Springer Nature Link classified under `Civil engineering`. This example shows that those categories do not reliably represent aerospace subject scope. It makes no claim about the paper's review eligibility.
- Other shared limits: None.

## Source translation

Use the exact concept membership and Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Every current term is an ordinary token or ordered phrase. The current schedule uses no proximity operator, pair expansion, or local pair test. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal except the three accepted unquoted trailing-`*` population atoms below.
- Atom `A(s)`: Place `L(s)` inside the raw Keywords expression.
- Boolean: Use uppercase `AND` and `OR` with explicit parentheses.
- Ordinary block `F(S)`: Join every atom in `S` with source `OR` and fully parenthesize the result.
- Compound blocks: Render the protocol definitions directly. Use `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))` for `G_model`. Use `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))` for `G_structure`. Use `F(C1_fixed) OR F(G_DSL)` for `C1`.
- Accepted population compression: In every partition, replace `"CubeSat" OR "CubeSats"`, `"nanosat" OR "nanosats" OR "nanosatellite" OR "nanosatellites"`, and `"SmallSat" OR "SmallSats"` with `CubeSat*`, `nanosat*`, and `SmallSat*`. Preserve every other punctuation, spacing, phrase, and spelling literal. Pilot 004 found a complete stable-card-path superset in all nine partitions. Six sets were equal. Both wildcard-only records remained within the intended population meaning.
- Wildcard boundary: Link offers an unbounded unquoted trailing `*`. A quoted `*` did not expand in the validated contrasts. The source exposes no bounded suffix operator that can reproduce the other declared variant families exactly, so keep every other ordinary term literal.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Cell plan: Use one direct query for A1, A3, B1, BG1, BG2, BC1, and BT2. Implement A2 as the stable-ID union of one complete `P AND E_F AND M_H` cell and four fixed contiguous `M_B` term cells. Implement B2 with one complete query per source year. Use the fixed two-by-two `M_B` and `R` Boolean union for 2021, 2022, and 2024. These cells are lossless.
- Date reconciliation: Link applies inclusive publication years. Final collection must reconcile the source-year total and card-path ledger with exact visible detail dates. Retain unresolved exact days and remove only a proved out-of-window day.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source operators, compound definitions, accepted population wildcards, and fixed source cells above.

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

- [x] [Pilot 001](pilots/001/pilot.md): A1 count-only diagnostic stopped on source canonical-path order drift. BG1 was not attempted under the stop rule. Do not use this artifact as a final search.
- [x] [Pilot 002](pilots/002/pilot.md): a fresh literal A1 retry requested `En`, broad content, and `oldestFirst` in two-pass count-only identity mode, then failed again on canonical identity order. No total, wildcard candidate, or BG1 run was accepted.
- [x] [Pilot 004](pilots/004/pilot.md): 74 current-schedule events and eight fresh retests completed two full card-path passes each. The accepted translation uses five A2 cells and 25 B2 cells per variant. Every wildcard union retained every literal path. The two wildcard-only records remained within the intended population meaning, so the three population wildcards are accepted in all nine partitions. Adapter version 10 also passed its no-option screenshot smoke. The pilot validates 166 sibling PNGs. Its external Nature canonical-link finding is resolved by Pilot 005.
- [x] [Pilot 005](pilots/005/pilot.md): adapter version 11 retained the exact Link 10.1038 card route with zero redirects, read the visible Link abstract and exact date, and accepted the matching `www.nature.com/articles/<DOI suffix>` canonical metadata URL without navigating to Nature. Final response status is outside the acceptance contract.
- [x] [Pilot 006](pilots/006/pilot.md): adapter version 12 completed three strict two-pass events in the shared Chrome window through target-scoped CDP while other tabs remained open. It validated the Nature mapping, exact-day inclusion, unresolved-day retention, post-cutoff exclusion, terminal publication, and six mandatory screenshots. Springer has no pending source pilot and is ready for final rendered searches.

## Pilot 003 historical note

[Pilot 003](pilots/003/pilot.md) preserves the superseded pair-based schedule, its repaired two-pass unions, and its explicit BT2 detail-route failure. Commit `3194156e90497186664260a8e86435e78d2e2aa1` retired its pair syntax and 9,013-character BT2 construction. Its no-filter findings remain consistent with the fixed controls above. No Pilot 003 output is a final search.

## Shared-browser transport

Use adapter version 12's target-scoped shared-browser transport for target-less rendered searches. The invocation-local browser-harness daemon creates one background target, attaches only to that target, and closes only that target. It does not wait for every pre-existing tab to initialize. Pilot 006 demonstrated strict complete runs while unrelated shared-browser tabs remained open.

Explicit `--target-id` and native CSV workflows retain Playwright. Native CSV is optional and is not part of the accepted rendered final-search path.

## Detail route control

For future runs, retain the raw search card path as the identifier, source URL, ordering identity, pass hash, and ledger value. The adapter accepts an exact detail route by default. A changed route requires two complete reconciled raw card path passes before detail navigation starts. A one pass diagnostic can retain an exact route only.

The adapter accepts only `/book/<DOI>` to `/referencework/<same DOI>` as a changed navigation route. It verifies HTTPS `link.springer.com`, a default port, no query or fragment, allowed content paths, equal nonempty normalized DOIs, and a normalized H1 equal to the card title. It uses the `page.goto()` response to inspect the complete main frame request chain. Final response status is not an acceptance condition. An exact route has zero redirects. The approved navigation alias has one same origin default port redirect from the exact card URL to `/referencework/<same DOI>`. Every hop must have an allowed Link URL with no credentials, query, or fragment. It rejects every other redirect, intermediate login or challenge route, extra hop, delayed route change, or mismatch. Rendered access, route, title, abstract, canonical, and date checks remain active.

For an exact Link `/article/10.1038/<suffix>` route, allow the canonical metadata URL `https://www.nature.com/articles/<suffix>`. Require the same DOI suffix, the exact hosts and paths, no credentials, query, or fragment, zero redirects, and a matching visible title. Keep the Link card path as identity. Read the abstract and date from Link. Do not navigate to Nature.

Retain one validated route evidence entry for every verified detail page, including a date excluded page. Each entry binds the raw card ledger identity, public source and resolved Link URLs, canonical link, alias state, and fixed date status. Derive alias, exact route, unresolved, and exclusion counts from these entries. Compact output retains only validated public URLs and checks the compact persisted form before publication.

The observed 2026-08-30 route for `Encyclopedia of GIS` is `/book/10.1007/978-3-319-23519-6` to `/referencework/10.1007/978-3-319-23519-6`. The final page has no exact date. Retain the record with unresolved exact day status.

Pilot 004 found the exact Link article route `/article/10.1038/s44359-026-00173-2` with `https://www.nature.com/articles/s44359-026-00173-2` as its canonical metadata URL. Pilot 005 validated and implemented this mapping in adapter version 11. Pilot 006 then retained the mapping through strict complete normalized publication in shared Chrome. The same pilot validated an included exact day, a retained unresolved day, and a proved post-cutoff exclusion. The external canonical-link and exact-day readiness blockers are resolved.

Springer has no pending source pilot. Proceed to final rendered searches with the accepted Pilot 004 cell plan, wildcards, `En`, `oldestFirst`, exact-day reconciliation, terminal markers, and mandatory sibling screenshots.
