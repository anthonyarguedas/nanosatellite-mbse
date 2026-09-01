# Advanced Technologies & Aerospace Index

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Interface screenshots

- [Command Line Search page](screenshots/command-line-search-page.png)
- [First results page](screenshots/results-page.png)
- [Capture receipt](screenshots/screenshot-receipt.json)

These full-page screenshots use the representative query `NOFT("CubeSat") AND LA(English)` with All dates. They document the general ATAI interface and are not pilot or final-search artifacts.

## Fixed source configuration

- Source or collection: Advanced Technologies & Aerospace Index
- Interface: Web
- Platform: ProQuest
- URL: https://www.proquest.com/ataindex/commandline
- Search field or local route: Command Line Search `NOFT` field.
- Main evidence window: Use exact `--date-start 2011-01-01 --date-end <cutoff>` publication-date bounds.
- Language: Apply exact `LA(English)`. This metadata restriction does not prove report language. Full-text screening remains authoritative.
- Publication type: Apply no type, peer-review, access, or full-text-availability filter. `DTYPE` and Document type vocabulary, including missing-type behavior, are tenant/corpus controlled. No lossless union for all shared eligible report types is proved.
- Database or collection selection: Select only Advanced Technologies & Aerospace Index. Deselect every parent and other ProQuest database.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Use no wildcards in an accepted translation and assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `NOFT(L(s))`.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `NOFT(L(a) NEAR/5 L(b))`. `NEAR/5` is unordered and counts intervening words.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no Technology Thesaurus supplement. Free text remains mandatory. Pilot 004 verified six assigned `SUBJECT` labels as exact descriptors, then found the same ordered 19 IDs for fresh literal and descriptor-augmented `B1` runs, with no candidate-only ID. The candidate controlled MBSE construction matched only five of seven selected records, so controlled terms cannot replace free text and showed no marginal recall value.
- Source limitation: Keep this source in an event separate from PQDT Global. `NOFT` searches anywhere except full text, reducing bias toward searchable full text while remaining sensitive to uneven metadata. Validate `NOFT` field coverage and pair behavior separately. Pilot 002's equal count-only wildcard total did not establish stable-ID equality or a superset, so compression is unaccepted.

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

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and `BG1` count-only diagnostics succeeded with totals `0` and `2`. These are not final searches.
- [x] [Pilot 002](pilots/002/pilot.md): English literal/candidate `A1` count-only checks totaled `0`/`0`. Language read back, no type restriction was accepted, and the wildcard candidate was not adopted.
- [Pilot 003 record](pilots/003/pilot.md): all nine exact literal partitions have pilot-only stable-ID reconciliations. `A3` and `B1` retain their historical null-total adapter v3 strict failures. Their same-query stable-ID repairs did not establish full-record stability at that time. Pilot 005 records the repaired adapter v4 strict reruns. No deduplicated pilot union exceeded 100, and no noise refinement was applied.
- [x] [Pilot 004](pilots/004/pilot.md): seven selected records supplied 58 assigned `SUBJECT` terms. Six candidates were exact Technology Thesaurus descriptors. A context-qualified `B1` supplement added no stable ID, so no descriptor was accepted.
- [x] [Pilot 005](pilots/005/pilot.md): adapter v4 removed the transient terminal abstract `More` token, integrated exact restore-session dismissal and inventory-proven cleanup, and passed fresh strict two-full-record checks for A3 and B1. Historical and fresh abstract comparisons found no truncation.
