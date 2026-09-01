# Compendex

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Compendex
- Interface: Web
- Platform: Elsevier Engineering Village
- URL: https://www.engineeringvillage.com/search/expert.url?database=1
- Search field or local route: Expert Search `ALL` field in one paired Compendex and Inspec event.
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen records in the cutoff year against the exact common cutoff.
- Language: Append `(English WN LA)` with `AND` to each raw Expert expression. This metadata limiter does not replace English full-text screening.
- Publication type: Apply no `DT`/facet limiter: conference article, journal article, preprint, conference proceeding, dissertation, and article in press can hold eligible reports, and assignment can be missing. Do not apply peer-review, access, or full-text-availability limits.
- Database or collection selection: Select Compendex and Inspec together. Retain the Compendex records and count separately.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Keep source terms literal: Pilot 002's three-family A1 trailing-`*` proposal was not submitted after a date-control failure, so it is not accepted. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted token or ordered phrase.
- Atom `A(s)`: `(L(s) WN ALL)`.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `((L(a) NEAR/5 L(b)) WN ALL)`. `NEAR/5` is unordered and counts intervening indexed words.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: The paired artifact covers both databases. Preserve its source-specific Compendex projection and never combine the two source totals.
- Pilot 001 accepted the complete `A1` and `BG1` Expert expressions, the 2011-2026 Published range, and `Date (Oldest)` in one paired event. The paired Python API was used for the bounded diagnostic because the public CLI requires strict complete JSON/CSV publication and has no count-only option. The artifact retains separate rendered row counts for Compendex and Inspec. Its one-record export is partial and does not prove complete capture or pair no-loss.

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

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and `BG1` bounded diagnostics succeeded. Compendex projections were `A1: 5` and `BG1: 6` rendered rows. The paired CLI has no count-only mode, so the Python API used one-page, one-record diagnostics. These are not final searches.
- [x] [Pilot 002](pilots/002/pilot.md): the paired literal A1 request added `English WN LA` but stopped before source submission when the start Published-year control was hidden without a visible Select2 trigger. No count or wildcard comparison was accepted.

## Pilot 003 record (pilot only, completion state unchanged)

[Paired Pilot 003](pilots/003/pilot.md) used the repaired visible Published controls and ran the literal nine-partition schedule in paired Compendex+Inspec events. Eight marker-gated strict two-pass captures succeeded. The historical pairs use marker v2. B2 is an explicit null failure with no count or accession inference. Any prospective rerun uses the reviewed v14 output namespace schema v2 and marker v3 under the [rerun guidance](../../scripts/engineering_village_pilot003/RERUN_GUIDANCE.md). Keep the separate Compendex projection and accession union in the paired reconciliation, do not accept a wildcard or controlled-term supplement, and do not treat this as a final search.
