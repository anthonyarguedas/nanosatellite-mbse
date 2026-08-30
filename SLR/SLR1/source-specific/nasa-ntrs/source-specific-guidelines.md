# NASA Technical Reports Server

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ntrs.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

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

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Exact literals remain normative. A trailing wildcard may be tested only as a nonaccepted compression diagnostic. Preserve punctuation, spacing, phrase, and spelling forms outside each replacement, and do not accept it from totals alone.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `L(s)` in general `q`.
- Boolean: Use `+` for AND, `|` for OR, and explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `("a b"~5 | "b a"~5)`, substituting the complete lexical phrase for each operand. This tests both orders with at most five skipped positions.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: The general query includes full text. Apply exact pair checking where retained fields permit it and report full-text-only uncertainty. Pilot 001 accepted complete `A1` and `BG1` `q` expressions with exact zero totals. Pilot 002 shortened complete `A1` by 22 characters with `nanosatellit*` and also returned zero count-only. Count-only retained no records, so pair no-loss, wildcard equality/superset, and complete capture remain untested. Wildcard use is unaccepted.

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

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and `BG1` count-only translations succeeded with totals `0` and `0`. These are not final searches.
- [x] [Pilot 002](pilots/002/pilot.md): full-A1 wildcard compression was a count-only zero. Language and lossless eligible-type controls remain unavailable, and the wildcard is unaccepted.
- [Pilot 003](pilots/003/pilot.md): all nine literal partitions have complete canonical-ID unions. BC1 and BT2 use linked lossless cells after preserved null failures. This does not complete piloting or authorize a final search.
