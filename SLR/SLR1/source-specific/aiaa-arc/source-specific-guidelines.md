# AIAA Aerospace Research Central

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: AIAA Aerospace Research Central (ARC)
- Interface: Web
- Platform: AIAA Aerospace Research Central
- URL: https://arc.aiaa.org/search/advanced
- Search field or local route: One `Anywhere` (`AllField`) Advanced Search row.
- Main evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. The script applies source month bounds and checks exact retained dates.
- Language: No usable Language control is exposed. Apply no source language filter. Determine English from the full text during screening.
- Publication type: Visible Publication Types facets do not prove a lossless eligible-type union, and journal records can lack a visible type facet. Apply no additional type, peer-review, access, or full-text-availability filter.
- Database or collection selection: Full ARC collection with access set to all and no publication or Topic facet.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Exact literals remain normative. A trailing wildcard may be tested only as a nonaccepted compression diagnostic. Preserve punctuation, spacing, phrase, and spelling forms outside each replacement, and do not accept it from totals alone.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `L(s)` inside one Anywhere row.
- Boolean: Use explicit parentheses and uppercase `OR`. Whitespace is the source AND operation.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `(A(a) A(b))` in the same Anywhere row. This is the broader fallback candidate.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: ARC exposes no supported proximity operator. Apply exact pair checking to retained title, keyword, and abstract text. Pilot 001 accepted `BG1` with total `8,088`. Its `A1` total was `492`. A [100-row preview](diagnostics/BG1-first-100.md) found a population term in only 10 titles and an artifact phrase in none. `P` alone returned `9,358`, `G_model` alone returned `32,702`, and explicit `AND` left `BG1` at `8,088`. Anywhere searches hidden indexed content, so title inspection cannot prove false matches, but it confirms poor visible precision. Pilot 002's full-A1 `nanosatellit*` candidate also returned `492` count-only after a 22-character shortening. No stable-ID equality or superset was proved, so it is unaccepted and is not a precision remedy.

### Uncommitted Pilot 003 proposal (not accepted)

Pilot 003 tested a prospective **metadata population field union**: complete literal `P` in Title, Keywords, and Abstract in three separate cells, with the unchanged semantic remainder in Anywhere. For a three-cell upper bound over 100, it tested the complete `P` block and the defining model/artifact block in all nine Title/Keywords/Abstract assignments, while keeping `E_H`, `E_F`, `R`, or `T2` in Anywhere. Each cell retains the exact field rows and controls in [the Pilot 003 assessment](pilots/003/searches/schedule-assessment.json). Its source-month 3-by-3 bounds before exact-day exclusions were A1 42, A2 119, A3 33, B1 87, B2 56, BG1 93, BG2 20, and BC1 52. The `BT2` full Anywhere `T2` row failed in all three primary cells. Four disjoint, lossless 56-pair `T2` OR subcells gave a 205-cell-sum bound and a 23-record DOI-first union. A2's 119 source events reduced to 40 DOI-first records.

This is a **field/noise proposal, not a final translation**. Its A2 and BT2 audits show that Anywhere's required third block often lacks visible title/abstract/keyword confirmation (A2: visible `E_F` in 1/40 DOI-first records. BT2: visible declared `T2` pair in 0/23). Those are possible hidden-index or full-text warnings, not false-match determinations. The repository and Pilot 001 contain no stable-ID register of known eligible AIAA records, so there is no known-item evidence that moving `P` or a defining block out of Anywhere has no observed recall loss. Do not accept or use this field union for a final search until that check exists.

ARC still exposes no Language control. Its Publication Types facets cannot be shown to be a lossless union of eligible journal, meeting-paper, and chapter records, so do not apply a type filter. Topic `ConceptID` has no exposed descriptor, scope, hierarchy, or explosion semantics. It cannot safely be used as an AND noise filter. Do not use the Pilot 002 wildcard candidate.

### Prospective fielded route after Pilot 004 (not a final search)

[Pilot 004](pilots/004/pilot.md) records observed recall acceptance for a known eligible item in the Pilot 003 metadata union. It links the source-located sentinel, exact applicable partition set, normal CLI field rows, all-cell DOI unions, and retained null failures. It does not change the header completion state or the final-search state above.

For a later final execution, use complete `P` in Title, Keywords, and Abstract as a union. When that three-cell conservative sum exceeds 100, use all nine `P`/defining-block Title/Keywords/Abstract assignments. Leave the third semantic block in Anywhere. For BT2, retain all four disjoint 56-pair T2 OR subcells wherever its full Anywhere row is unavailable. Reconcile every stable DOI union. Investigate a DOI-first union over 100. The field route remains subject to the fixed rules above. It uses no language filter, no type filter that could be lossy, no Topic filter, no access restriction, and no wildcard.

Pilot 004 is diagnostic only. Its non-mergeable previews and count-only zero receipts cannot enter a final corpus. A final run still requires its own complete source-month partitioning, exact-day treatment, native export, and final-search artifacts under `final-searches/`.

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

- [x] [Pilot 001](pilots/001/pilot.md): full `A1` and `BG1` count-only translations succeeded with diagnostic totals `492` and `8,088`. Final collection still requires source-month partitioning.
- [x] [Pilot 002](pilots/002/pilot.md): full-A1 wildcard compression remained at `492` count-only. No language/type restriction or narrower field was adopted.
- [x] [Pilot 003](pilots/003/pilot.md): all nine schedule entries received a metadata field union diagnostic. The uncommitted field proposal is explicitly **not accepted** pending a known eligible AIAA item recall check.
