# NASA Technical Reports Server

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ntrs.py`

For every CLI JSON, adapter v13 automatically saves `<name>.search-page.png` and `<name>.results-page.png` in the same directory. The first image shows the configured search page before Search. The second shows the stable first results page. There is no screenshot opt-out. A successful event requires both PNGs. Its JSON records their filenames, hashes, dimensions, and privacy flags.

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, screenshots, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: NASA Technical Reports Server (NTRS)
- Interface: Web
- Platform: NASA
- URL: https://ntrs.nasa.gov/search
- Search field or local route: General `q` over metadata fields and document full text in the rendered interface.
- Main evidence window: Use exact `--date-start 2011-01-01 --date-end <cutoff>` publication-date bounds.
- Language: No usable Language control is exposed. Apply no source language filter. Determine English from the full text during screening.
- Publication type: The Type control accepts one exact option per run, but its vocabulary and missing-assignment behavior do not prove a lossless OR union of articles, conference papers, and technical reports. Apply no additional type, peer-review, access, or full-text-availability filter.
- Database or collection selection: Full public NTRS database with no type, center, subject, collection, or distribution restriction.
- Other shared limits: None.

## Source translation

Use the exact concept membership and compound Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction), as revised by commit `3194156e90497186664260a8e86435e78d2e2aa1`. Every listed term is an ordinary token or ordered phrase. Use no proximity operator, token distance rule, pair expansion, or local pair filter.

- Literal `L(s)`: Use one straight double-quoted token or ordered phrase.
- Atom `A(s)`: Place `L(s)` in general `q`.
- Boolean: Use `+` for AND, `|` for OR, and explicit parentheses.
- Ordinary block `F(S)`: Join `A(s)` for every member of `S` with source OR. Fully parenthesize the result.
- `G_model`: `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))`.
- `G_structure`: `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))`.
- `C1`: `F(C1_fixed) OR F(G_DSL)`.
- `T_precise`: Use its ordinary OR block.
- Controlled vocabulary: Add no supplement. NTRS exposes exact Subject Category and Keyword strings, without a proved NASA Thesaurus term, hierarchy, or expansion route. Free text remains mandatory.

### Accepted standalone wildcard translation

Use each wildcard below as one unquoted general `q` term. Preserve every other term exactly.

- `F*(P)`: Replace `CubeSat` and `CubeSats` with `CubeSat*`. Replace `nanosat`, `nanosats`, `nanosatellite`, and `nanosatellites` with `nanosat*`. Replace `SmallSat` and `SmallSats` with `SmallSat*`.
- `F*(R)`: Use `requirement*`, `function*`, `behavior*`, `behaviour*`, `architectur*`, `interface*`, `trace*`, `allocat*`, `constraint*`, `parametric*`, `analys*`, `design*`, `decision*`, `tradeoff*`, `verif*`, and `validat*` for their matching declared forms. Keep `decision-making`, `decision making`, `trade study`, `trade studies`, and both `trade-off` forms literal.
- `F*(G_structure_fixed)`: Replace `metamodel` and `metamodels` with `metamodel*`.
- `F*(T_precise)`: Use `tailor*`, `customiz*`, `customis*`, `parameteriz*`, `parameteris*`, and `instantiat*` for their declared morphology families. Keep `variability`, `variation point`, and `variation points` literal.

These 26 wildcard atoms replace 88 literals. Pilot 005 found exact literal-wildcard canonical-ID set equality in all nine partitions. The complete unions each contain 14 IDs, with no missing or wildcard-only record.

Keep all phrase terms literal, including their singular and plural forms. Keep all acronym variants literal so each acronym remains a standalone lexical token. Pilot 006 tested 114 aggressive wildcard atoms that replaced 284 literals, including phrase and multi-term forms. The candidate lost five literal IDs and six partition occurrences. Do not use that translation.

The general query includes indexed full text. Language remains a full-text screening decision. Adapter v13 waits for stable pre-submit and post-submit result signatures so an intermediate date-only result cannot become query evidence. Apply no language, type, access, collection, source, distribution, subject, keyword, peer-review, or full-text-availability restriction.

## Query schedule

Render each row with the source operators and accepted wildcard blocks above. Expand every compound definition before execution.

| ID | Source construction |
|---|---|
| `A1` | `F*(P) AND F(E_H) AND F(M_H)` |
| `A2` | `F*(P) AND F(E_F) AND (F(M_H) OR F(M_B))` |
| `A3` | `F*(P) AND F(E_H) AND F(M_B)` |
| `B1` | `F*(P) AND F(M_H)` |
| `B2` | `F*(P) AND F(M_B) AND F*(R)` |
| `BG1` | `F*(P) AND G_model` |
| `BG2` | `F*(P) AND G_structure`, with `F*(G_structure_fixed)` |
| `BC1` | `F*(P) AND C1` |
| `BT2` | `F*(P) AND F(M_B) AND F*(T_precise)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and historical `BG1` count-only translations returned `0` and `0`.
- [x] [Pilot 002](pilots/002/pilot.md): the historical full-A1 `nanosatellit*` compression was a count-only zero and remained unaccepted.
- [x] [Pilot 003](pilots/003/pilot.md): the historical proximity schedule produced a 15-ID union. Protocol commit `3194156e90497186664260a8e86435e78d2e2aa1` supersedes its BG1, BG2, BC1, and BT2 translations.
- [x] [Pilot 004](pilots/004/pilot.md): four literal A1 attempts remained null. The pilot exposed an intermediate date-only result race and led to adapter v13's stable-state repair.
- [x] [Pilot 005](pilots/005/pilot.md): all 18 current literal and standalone-wildcard events completed. Every partition set was equal. The 26 standalone wildcard atoms are accepted. All accepted JSON artifacts have both required screenshots.
- [x] [Pilot 006](pilots/006/pilot.md): nine maximal-wildcard events completed. The aggressive phrase candidate lost five literal IDs across A2, B1, and B2. It is rejected. Pilot 005 remains the accepted wildcard boundary.
