# Springer Nature Link

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_springer_link.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

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
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Keep A1 literal: Pilot 002's three-family trailing-`*` candidate was not submitted after a second A1 identity-order failure. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `L(s)` inside the Keywords expression.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `(A(a) AND A(b))` in the same Keywords field. This is the broader fallback candidate.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Link exposes no supported proximity operator. Apply exact pair checking where retained fields permit it and report body-text uncertainty.
- Pilot 001 A1 count-only execution reached the two-pass identity check, then failed because the verification pass returned a different canonical-path order. The failure artifact has no total and must not be treated as zero. Stop before BG1 and retain the native `oldestFirst` and strict identity checks.

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

- [x] [Pilot 001](pilots/001/pilot.md): A1 count-only diagnostic stopped on source canonical-path order drift. BG1 was not attempted under the stop rule. Do not use this artifact as a final search.
- [x] [Pilot 002](pilots/002/pilot.md): a fresh literal A1 retry requested `En`, broad content, and `oldestFirst` in two-pass count-only identity mode, then failed again on canonical identity order. No total, wildcard candidate, or BG1 run was accepted.

## Pilot 003 diagnostic note (no completion-state change)

[Pilot 003](pilots/003/pilot.md) used the repaired two-pass canonical-path check and retained literal, broad-content `En`/`oldestFirst` pilot unions for A1–BC1. Its direct A2/B1/B2 routes were replaced only by documented lossless Boolean and exact-date source cells; the 9,013-character BT2 row was divided into explicit pair cells without a wildcard. No content-type, access, full-text, peer-review, or taxonomy limiter was added.

The linked [canonical-union receipt](pilots/003/searches/canonical-unions.json) retains the nine outcomes. BT2 remains an explicit pilot failure: four 2017 records in the `("variability" AND "models")` cell had a canonical detail-route redirect on two attempts, so their identifiers are null rather than inferred. The >100 unions have a linked [visible Title/Abstract metadata noise investigation](pilots/003/searches/noise-investigation.json); its low-noise priority subsets do not replace the broad source union because Link has no independently validated Abstract-only field or supported proximity operator. No Pilot 003 output is a final search.
