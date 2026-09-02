# Compendex

Last pilot saved in commit: 9420c567dedd2cf5de6f242b803446f093623d6f
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, screenshots, and failures. This file records only fixed decisions and pilot conclusions.

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
- Screenshots: Adapter v16 automatically saves `<query-id>.search-page.png` and `<query-id>.results-page.png` beside each JSON artifact. The first image shows the configured Expert form. The second shows the verified first results page. This behavior has no opt-out. A missing or mismatched screenshot fails the event. The bounded single-pass and strict paired checks are recorded in the [adapter validation](pilots/005/searches/adapter-v16-screenshot-validation.json).
- Current capture status: Pilot 004 exposed positive pages without a numeric result interval and with mirrored Next anchors sharing one legacy ID. Adapter v15 now treats the interval as optional corroboration, scopes the top paginator, and waits through the brief empty-row transition after one click. Bounded one-page, two-page, strict two-pass, and paired strict checks passed. Pilot 005 then completed strict literal and wildcard A1 events. Adapter v16 completed its focused screenshot checks. Pilot 008 completed all nine current wildcard partitions through strict paired capture and verified both mandatory screenshots for every accepted event. No final schedule has run.

## Source translation

Use the exact concept membership and compound definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction), as revised by protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`. Every listed term is an ordinary token or ordered phrase. Use no proximity operator, token distance rule, same field pair, or pair expansion. Keep terms literal except for the approved population compression below. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted token or ordered phrase.
- Atom `A(s)`: `(L(s) WN ALL)`.
- Wildcard usage: **Approved for every schedule entry.** In every `F(P)` block, replace the literal `CubeSat`/`CubeSats`, `nanosat`/`nanosats`/`nanosatellite`/`nanosatellites`, and `SmallSat`/`SmallSats` atom unions with `(CubeSat* WN ALL)`, `(nanosat* WN ALL)`, and `(SmallSat* WN ALL)`, respectively. Keep the wildcard tokens unquoted. Preserve every other P term and every term in the other blocks. Pilot 005 found equal complete six-accession Compendex A1 sets. The reviewer then approved the same population translation for all nine entries in the [source translation approval](pilots/005/searches/source-translation-approval.json). Use no `?`, manual `$` stemming, or other `*` form.
- Boolean: Uppercase `AND`, `OR`, and explicit parentheses.
- Ordinary block `F(S)`: join `A(s)` for every member of `S` with source OR. Fully parenthesize the result.
- `F(G_model)`: `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))`.
- `F(G_structure)`: `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))`.
- `F(C1)`: `F(C1_fixed) OR F(G_DSL)`.
- `F(T_precise)`: the ordinary union of every precise tailoring term.
- Controlled vocabulary: Compendex exposes the Ei Thesaurus through `CV`, with separate `MH` Main heading and `CVM` Major term fields. Add no Ei Thesaurus supplement to the current translation. Pilot 004 verified assigned P candidates and a context qualified M_H construction, then found no B1 accession unique to the candidates. Free text remains mandatory. Use no hierarchy explosion, focus, `MH`, or `CVM` restriction.
- Source limitation: The paired artifact covers both databases. Compendex and Inspec have separate thesauri despite sharing the `CV` field code. Preserve the source-specific Compendex projection and never combine the two source totals.
- Pilot 001 accepted the complete `A1` and historical `BG1` Expert expressions, the 2011-2026 Published range, and `Date (Oldest)` in one paired event. The paired Python API was used for the bounded diagnostic because the public CLI requires strict complete JSON/CSV publication and has no count-only option. The artifact retains separate rendered row counts for Compendex and Inspec. Its one-record export is partial and does not prove complete capture or pair no-loss. Its `BG1` expression predates protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source operators and the compound definitions adopted after proximity removal. Use the approved wildcard-compressed `F(P)` block in every row.

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

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and `BG1` bounded diagnostics succeeded. Compendex projections were `A1: 5` and `BG1: 6` rendered rows. The paired CLI has no count-only mode, so the Python API used one-page, one-record diagnostics. These are not final searches.
- [x] [Pilot 002](pilots/002/pilot.md): the paired literal A1 request added `English WN LA` but stopped before source submission when the start Published-year control was hidden without a visible Select2 trigger. No count or wildcard comparison was accepted.
- [x] [Pilot 004](pilots/004/pilot.md): the preflight after proximity removal is pinned to commit `3194156e90497186664260a8e86435e78d2e2aa1`. Four assigned labels were exact Ei descriptors. The two lossless candidate-only B1 routes each returned source zero twice. No descriptor supplement was accepted.
- [x] [Pilot 005](pilots/005/pilot.md): strict literal and three-wildcard A1 events each returned the same six Compendex accessions. The subsequent reviewer decision approves this population wildcard translation for all nine Compendex schedule entries. The paired Inspec projection remains separate.
- [x] [Pilot 006](pilots/006/pilot.md): A1, A2, A3, and B1 passed before current B2 stopped on an unverified page transition. The strict null failure ended this first consolidated attempt.
- [x] [Pilot 007](pilots/007/pilot.md): current B2, BG1, and BG2 passed before a pre-submission owned-page setup failure ended the second consolidated attempt at BC1.
- [x] [Pilot 008](pilots/008/pilot.md): all nine current wildcard partitions passed under adapter v16. The accepted events completed 18 strict source passes and retained 18 verified screenshots. Current B2 returned 173 Compendex and 90 separate Inspec records. BG1, BG2, BC1, and BT2 validated the changed definitions live. The Compendex route is ready for a separate final search.

## Pilot 003 record (historical schedule only)

[Paired Pilot 003](pilots/003/pilot.md) used the repaired visible Published controls and ran the then-current nine-partition proximity schedule in paired Compendex+Inspec events. Eight marker-gated strict two-pass captures succeeded. The historical pairs use marker v2. B2 is an explicit null failure with no count or accession inference. Protocol commit `3194156e90497186664260a8e86435e78d2e2aa1` later changed BG1, BG2, BC1, and BT2. Do not use their Pilot 003 sets as current schedule evidence. Pilot 008 supplies fresh current-schedule evidence for B2 and all four changed definitions while leaving Pilot 003 unchanged. Pilot 004 reuses only B1 record level assignment evidence because B1 remained `P AND M_H`. Keep the separate Compendex projection and accession union in the historical reconciliation. Do not treat any pilot artifact as a final search.
