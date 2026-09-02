# AIAA Aerospace Research Central

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py`

The adapter automatically saves `<stem>.search-page.png` and `<stem>.results-page.png` beside every requested JSON output. The screenshots are mandatory and have no opt-out.

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: AIAA Aerospace Research Central (ARC)
- Interface: Web
- Platform: AIAA Aerospace Research Central
- URL: https://arc.aiaa.org/search/advanced
- Search field or local route: Pilot 007 hybrid union across `Title`, `Keywords` (`Keyword`), `Abstract`, and selected `Anywhere` (`AllField`) Advanced Search rows. ARC combines rows with `AND`, so metadata field `OR` is implemented through reconciled field-assignment cells. BG1 uses one direct Anywhere row, while BG2 uses the factor-wise metadata route.
- Main evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. The script applies source month bounds and checks exact retained dates.
- Language: No usable Language control is exposed. Apply no source language filter. Determine English from the full text during screening.
- Publication type: Visible Publication Types facets do not prove a lossless eligible-type union, and journal records can lack a visible type facet. Apply no additional type, peer-review, access, or full-text-availability filter.
- Database or collection selection: Full ARC collection with access set to all and no publication or Topic facet.
- Other shared limits: None.

## Source translation

Use the exact concept membership and compound Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Commit `3194156e90497186664260a8e86435e78d2e2aa1` removed every pair and proximity requirement. [Pilot 007](pilots/007/pilot.md) accepts the hybrid metadata-anchored route below as the prospective canonical screening translation.

- Literal `L(s)`: Use one straight double-quoted token or ordered phrase, except for the accepted `nanosatellit*` substitution below.
- Field atom `A_f(s)`: Place `L(s)` in field `f`, where `f` is Title, Keywords, Abstract, or Anywhere.
- Boolean: Use fully parenthesized uppercase `AND` and `OR`. Pilot 005's known-title controls support quoted ordered-phrase behavior.
- Field block `F_f(S)`: Join every `A_f(s)` in `S` with source `OR`, then fully parenthesize the result.
- Metadata block `META(S)`: `F_Title(S) OR F_Keywords(S) OR F_Abstract(S)`. ARC combines visible rows with `AND`, so implement each required outer field `OR` as a prospectively declared union of field-assignment cells.
- Anywhere block `ANY(S)`: `F_Anywhere(S)`.
- `G_model`: `G_model_fixed OR G_mission_exact OR (G_mission AND M_B)`.
- `G_structure`: `G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)`.
- `C1`: `C1_fixed OR G_DSL`.
- `T_precise`: the ordinary `T_precise` block.
- Wildcard: In every `P` block, replace the exact adjacent literals `"nanosatellite" OR "nanosatellites"` with unquoted `nanosatellit*`. Pilot 009 found equal source totals, raw stable-ID sets, and canonical DOI sets in all 94 paired current-route cells. Keep every other population spelling and punctuation form literal. No other wildcard stem, position, or quoted use is accepted.
- Controlled vocabulary: Pilot 008 resolved exact Topic labels and numeric `ConceptID` values, then rejected Topic as a required filter. The pilot does not establish a controlled vocabulary supplement. Free text remains mandatory. Apply no Topic restriction or supplement.
- Cell execution: Retain every cell query, source total, stable identifier, automatic screenshot reference, failure, and retry. Reconcile each partition and the complete schedule by canonical DOI.

Anywhere includes full text or hidden indexed content. The complete Anywhere schedule is retained as sensitivity evidence because its result volume is infeasible for screening. Pilot 007 anchors population and model factors in metadata while leaving selected body-sensitive factors in Anywhere. The strict factor-wise Pilot 006 result remains a priority tag inside the hybrid corpus.

ARC still exposes no usable Language control. Its Publication Types facets do not form a proved lossless union of eligible journal, meeting-paper, and chapter records. ARC's Topic autocomplete exposes exact labels and numeric `ConceptID` values. It exposes no vocabulary version, preferred-term flag, scope note, hierarchy, or explosion semantics. Pilot 008's least restrictive tested Topic union retained 77 of 119 accepted corpus DOIs and removed 42 records with unclassified eligibility. Apply no language, publication type, Topic, access, peer-review, or full-text-availability filter.

### Pilot 005 Anywhere sensitivity route

Pilot 005 executed every complete current partition in one Anywhere row. Primary totals were A1 `492`, A2 `1,541`, A3 `472`, B1 `1,388`, B2 `1,028`, BG1 `45`, BG2 `3,584`, BC1 `152`, and BT2 `437`. Independent BG1, BG2, BC1, and BT2 repeats returned the same totals.

The current BT2 query is 1,822 characters and executed directly. It replaces the historical 7,679-character pair-expanded remainder and requires no four-part `T2` split. The current BG1 total of `45` is 99.44% below the historical broad-pair total of `8,088`. That comparison measures search burden because the cross-source definition changed.

The remaining precision problem is concentrated in BG2 and also affects BC1 and BT2. BG2's `G_structure_fixed` branch returned `3,571`, and `reference architecture` alone returned `3,536`. Phrase controls rejected quote flattening as the explanation. Rendered-title previews rarely showed all factors, while ARC may match hidden indexing or full text. These warnings require broad-record screening. They do not justify a narrower source translation.

The known eligible DOI `10.2514/6.2015-4474` was retrieved by direct A2, B1, B2, and BC1 checks, its current source-located applicable partitions. Its old `adapted`/`model` pair no longer creates BT2 membership because the current `T_precise` block contains no such pair.

This route resolves the former proximity semantic mismatch and BT2 length failure. Its volume is unsuitable for screening because BG2 remains `3,584` and several core partitions exceed `1,000`. Retain these totals and bounded previews as sensitivity evidence. Do not use the complete Anywhere schedule as the screening corpus.

### Pilot 006 factor-wise metadata route

[Pilot 006](pilots/006/pilot.md) tested `META(s) = Title(L(s)) OR Keywords(L(s)) OR Abstract(L(s))` for every protocol atom. It rebuilt all nine Boolean partitions from those atoms. ARC rows are source `AND` clauses, so the pilot executed every field assignment and reconciled their stable-ID union. It used 225 cells. Every cell was at most 26 records and was completely captured as a non-mergeable rendered-card preview.

The partition DOI unions were A1 `1`, A2 `1`, A3 `1`, B1 `37`, B2 `17`, BG1 `0`, BG2 `2`, BC1 `3`, and BT2 `1`. Their cross-partition union contains `47` canonical DOIs. This is a substantial screening-priority reduction.

The metadata union missed known eligible DOI `10.2514/6.2015-4474` in A2 and B2. It retrieved the DOI in B1 and BC1. It also returned none of the 44 canonical DOIs in Pilot 005's complete BG1 Anywhere result. Those missing records have no eligibility classification that permits exclusion.

The factor-wise route was too restrictive as a standalone screening translation. Keep its 47-record union as a priority tag. Pilot 007 supersedes its canonical-route decision.

Adapter v5 automatically saves mandatory full-page configured-search and first-results screenshots beside every JSON. It also exposes a non-mergeable card-only preview for records whose bulk formatted-citation form is unavailable. Pilot 006 verified 450 required screenshots for 225 successful JSON artifacts. Thirteen retained source failures were recovered by exact retries.

### Pilot 007 accepted hybrid route

Pilot 007 executed 94 current-protocol cells. Every cell was at most 45 records and was captured completely. Partition DOI unions were A1 `18`, A2 `40`, A3 `12`, B1 `37`, B2 `23`, BG1 `44`, BG2 `2`, BC1 `36`, and BT2 `11`. Their deduplicated union contains `119` canonical DOIs.

All 47 Pilot 006 factor-wise records appear in the hybrid union. The hybrid route adds 72 records through selected Anywhere factors. Known eligible DOI `10.2514/6.2015-4474` was retrieved in all four source-located applicable partitions, A2, B1, B2, and BC1.

Accept the Pilot 007 construction as the prospective canonical screening translation. Screen its complete 119-record union. Keep the Pilot 006 factor-wise result as a priority tag. Keep Pilot 005 Anywhere totals as sensitivity evidence, without treating the 3,584-result BG2 Anywhere set as a screening corpus.

Pilot 007 verified 188 mandatory screenshots for 94 successful JSON artifacts. Three retained source failures were recovered by exact retries. Project `.gitignore` excludes generated images under `SLR/SLR1/source-specific/`.

This remains a pilot decision. Final execution requires new source calls, complete source-month treatment, exact-day handling, native export, and final-search artifacts under `final-searches/`.

### Pilot 008 Topic yield diagnostic

[Pilot 008](pilots/008/pilot.md) exercised the visible Topic autocomplete. Seven of nine candidate labels resolved and executed. `Satellites` and `Small Satellites` both resolved to `ConceptID` `135111` and returned equal bounded sets. `CubeSats` and `Nanosatellites` were not offered as exact labels. ARC exposes no evidence that shared IDs establish preferred terms or synonyms.

Four distinct Topic identities retained known eligible DOI `10.2514/6.2015-4474`: `Satellites` (`135111`), `Spacecrafts` (`134410`), `Space Systems and Vehicles` (`135236`), and `Systems Engineering` (`138491`). In the complete BG1 set, their offline union retained 32 of 44 canonical DOIs and removed 12.

The accepted-corpus test used paired source calls and a canonical-DOI projection declared before execution. All six baselines retrieved their complete predeclared chunks. Individual Topic yields were 55 of 119 for `Satellites`, 64 for `Spacecrafts`, 73 for `Space Systems and Vehicles`, and 16 for `Systems Engineering`. Their least restrictive offline union retained 77 of 119 and removed 42, a 35.29% reduction. The removed records have unclassified eligibility.

Reject Topic as a required `AND` filter. Add no Topic supplement from this pilot. Keep the Pilot 007 hybrid route unchanged. Pilot 008 completed 106 successful source artifacts and verified 212 mandatory screenshots. Four unavailable-label failures remain as source evidence. Three transient source or control failures were recovered by exact retries.

### Pilot 009 accepted trailing wildcard

[Pilot 009](pilots/009/pilot.md) paired fresh literal and wildcard calls for all 94 Pilot 007 cells. Each pair differed only by replacing `"nanosatellite" OR "nanosatellites"` with unquoted `nanosatellit*`. The replacement shortened every cell query by 22 characters.

All 94 pairs returned equal source totals, raw stable-ID sets, and canonical DOI sets. Every partition union was equal. The fresh literal and wildcard schedules both contained the same 119 canonical DOIs. The wildcard added zero and lost zero. Known eligible DOI `10.2514/6.2015-4474` remained in A2, B1, B2, and BC1. Two retained titles visibly containing `Nanosatellite` had equal literal and wildcard cell memberships.

Accept this exact wildcard substitution in `P`. Keep all other population variants literal. This grants no general wildcard permission. Pilot 009 supersedes Pilot 002's count-only nonacceptance for this candidate. It verified 376 mandatory screenshots for 188 successful source artifacts. Four transient owned-page creation failures were recovered by exact retries.

### Superseded proximity-era pilots

Pilots 001 through 004 used the earlier paired-block protocol. Their artifacts remain the audit record for the 8,088-result BG1 fallback, Pilot 002's then-unaccepted wildcard candidate, the metadata field proposal, and its one-item recall gate. Commit `3194156e90497186664260a8e86435e78d2e2aa1` supersedes their pair syntax, local pair checks, metadata route, and four-part historical BT2 split. Their no-filter findings remain consistent with the fixed controls above. Pilot 009 supplies the later current-route wildcard decision.

## Query schedule

The table gives the accepted Pilot 007 source construction. Expand each named compound block with the protocol Boolean definition before execution.

| ID | Source construction |
|---|---|
| `A1` | `META(P) AND META(M_H) AND ANY(E_H)` |
| `A2` | `META(P) AND (META(M_H) OR META(M_B)) AND ANY(E_F)` |
| `A3` | `META(P) AND META(M_B) AND ANY(E_H)` |
| `B1` | `META(P) AND META(M_H)` |
| `B2` | `META(P) AND META(M_B) AND ANY(R)` |
| `BG1` | `ANY(P AND G_model)` |
| `BG2` | factor-wise metadata expansion of `P AND G_structure` |
| `BC1` | `META(P) AND ANY(C1)` |
| `BT2` | `META(P) AND META(M_B) AND ANY(T_precise)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): the superseded full A1 and broad-pair BG1 count diagnostics returned `492` and `8,088`.
- [x] [Pilot 002](pilots/002/pilot.md): the historical wildcard candidate returned the same A1 count without stable-ID equality evidence. Pilot 009 supersedes its nonacceptance for the exact `nanosatellit*` substitution.
- [x] [Pilot 003](pilots/003/pilot.md): the superseded metadata field union covered all nine historical partitions as a diagnostic.
- [x] [Pilot 004](pilots/004/pilot.md): the superseded metadata route retrieved one known eligible item in every historically applicable partition.
- [x] [Pilot 005](pilots/005/pilot.md): all nine current Boolean partitions executed directly in one Anywhere row. The semantic and recall translation issues are resolved. Precision remains partly unresolved because BG2 returned `3,584`.
- [x] [Pilot 006](pilots/006/pilot.md): the 225-cell factor-wise metadata union produced 47 canonical DOIs but missed the known eligible sentinel in A2 and B2. It is retained as a priority tag.
- [x] [Pilot 007](pilots/007/pilot.md): the 94-cell hybrid route produced a feasible 119-DOI union and retrieved the sentinel in A2, B1, B2, and BC1. It is the accepted prospective screening translation.
- [x] [Pilot 008](pilots/008/pilot.md): exact Topic selections reduced the accepted corpus. The least restrictive tested union retained 77 of 119 DOIs and removed 42 records with unclassified eligibility. Apply no Topic restriction.
- [x] [Pilot 009](pilots/009/pilot.md): all 94 literal/wildcard pairs and their 119-DOI schedule unions were equal. Accept unquoted `nanosatellit*` only as the replacement for `"nanosatellite" OR "nanosatellites"` in `P`.
