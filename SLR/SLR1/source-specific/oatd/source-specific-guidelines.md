# Open Access Theses and Dissertations

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

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

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Use no wildcards in an accepted translation and assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `L(s)` in raw `q`.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: for each of `title`, `author`, `abstract`, `publisher`, `subject`, and `discipline`, OR `field:("a b"~5)` with `field:("b a"~5)`. Substitute each complete lexical phrase.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: The default field list is not fully enumerated. Validate the named-field two-order slop union once and apply exact pair checking to retained fields. Pilot 002's unchanged `BG1` retry failed readiness, so its lack of an English readback is not retroactive source evidence. Pilot 003 later confirmed English only after a healthy route and exact source query echo. Every English-filtered event still needs its own exact route-query readback. No wildcard conclusion is accepted.
- Pilot 001 accepted the complete `A1` count-only expression with total `1`. The complete `BG1` named-field two-order `~5` expression did not reach a ready result page within 60 seconds. The artifact records a route/readiness failure with no total, so no source syntax or zero-result conclusion is drawn.
- Pilot 003's canonical shared-browser run confirmed `title:(microRNA) AND language:(en OR eng OR english) AND pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]` with source total `999` and exact source echo. Its first cells were all under the 1,500-character route target. Three strict cells failed after source-side Record Details behavior, including one bounded busy retry for each of `B1` and `BG2`. Every incomplete partition total remains null.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source operators above. `F(G_model)`, `F(G_structure)`, `F(C1)`, and `F(T2)` include fixed phrases and expanded pairs.

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
| `BT2` | `F(P) AND F(M_B) AND F(T2)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): `A1` count-only succeeded with total `1`. `BG1` was a complete named-field translation, but OATD did not become ready within the bounded request. Do not treat it as zero or syntax success, and do not use the artifact as a final search.
- [x] [Pilot 002](pilots/002/pilot.md): the unchanged one-page `BG1` retry again failed readiness with no total. The stop rule left English `A1` and wildcard checks unrun.
- [Pilot 003](pilots/003/pilot.md): the canonical shared browser completed a healthy route and exact English readback, then attempted the first lossless cell in every partition under a 20-invocation round-robin budget. Six cells completed strict capture and three had explicit source failures. All incomplete partition totals and unions remain null. This is not a final search.
