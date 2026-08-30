# Wiley Online Library

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Wiley Online Library
- Interface: Web
- Platform: Wiley Online Library
- URL: https://onlinelibrary.wiley.com/search/advanced
- Search field or local route: One Advanced Search `Anywhere` (`AllField`) row.
- Main evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. The script applies source month bounds and checks exact retained dates.
- Language: Wiley exposes no Language field or facet on this route. Full-text screening must confirm English.
- Publication type: `articlesChapters` is the source record-family boundary. Do not narrow with `PubType`. It cannot safely replace that route. Do not apply peer-review, access, or full-text-availability limits.
- Database or collection selection: Full Wiley platform. Use the Articles & Chapters route for bibliographic records. Do not treat Collections as records.
- Other shared limits: None.
- Pilot 003 diagnostic capture: the normal native-RIS adapter failed with `total: null` (unrecognizable RIS or a missing Export Citations control). Its non-mergeable two-pass rendered DOI/source-ID ledgers are pilot evidence only. They are not a final bibliographic export or a substitute for native capture.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair except the accepted A1 population compression below. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal except the three accepted unquoted trailing-`*` A1 population atoms below.
- Atom `A(s)`: `L(s)` inside the single Anywhere row.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `(A(a) AND A(b))` in the same Anywhere row. This is the broader fallback candidate.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Accepted A1 population compression only: replace `"CubeSat" OR "CubeSats"`, `"nanosat" OR "nanosats" OR "nanosatellite" OR "nanosatellites"`, and `"SmallSat" OR "SmallSats"` with `CubeSat*`, `nanosat*`, and `SmallSat*`, respectively. Preserve every other punctuation, spacing, phrase, and spelling literal. Re-test before applying this to another partition. Pilot 003 again obtained the Pilot 002 A1 ordered-ID hash. It did not use a wildcard outside A1.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Wiley exposes no supported proximity operator. Apply exact pair checking to retained title and abstract text. Pilot 003's diagnostic check uses either pair order in one field with at most five intervening lexical tokens. Missing visible metadata never removes a source ID.
- Pilot-only cell fallback: A2 and BC1 used documented lossless cells after their complete Anywhere queries failed, and BT2 used a prospective nine-cell union because its 9,013-character expression exceeded the observed accepted 2,770-character literal A1. The 2,700-character ceiling and all cell strings are recorded in [Pilot 003](pilots/003/pilot.md). Revalidate native capture and source stability before any final use.
- Pilot 001 accepted the complete `A1` and `BG1` Anywhere expressions with exact source query readback in two count-only passes. Source totals were `A1: 21` and `BG1: 8`. The run requested the diagnostic upper bound 2026-08-29, while Wiley applied the enclosing 2026-08 source month and retained no cards. Final collection must reconcile that source-month total with exact-day client exclusions. Exact pair checking remains required.

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

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and `BG1` count-only diagnostics completed with exact query and date-control readback. Totals were `21` and `8`. No records were retained, so pair checking remains a final-run limitation.
- [x] [Pilot 002](pilots/002/pilot.md): literal and three-family wildcard A1 runs each returned 21 Articles & Chapters records with the same ordered 21 DOI IDs. The A1-only compression is accepted. No Language or `PubType` limiter was available or applied.
- [Pilot 003](pilots/003/pilot.md): all nine schedule entries were attempted with exact-day/source-month reconciliation. A1, A2 (3 cells), A3, B1, BG2, BC1 (3 cells), and BT2 (9 cells) have complete non-mergeable DOI/source-ID ledgers. B2 and BG1 retain null-total failures. Native RIS capture is not accepted for a final Wiley run.
