## Observations — `pilot_not_candidate_search`

- **W-A2** — 2026-08-06 20:23:50 EDT (UTC−04:00): Articles & Chapters **40**; Collections **2**.
- **W-B2** — 2026-08-06 20:24:21 EDT (UTC−04:00): Articles & Chapters **105**; Collections **4**.
- Both used unrestricted Wiley Advanced Search, one `Anywhere`/`AllField` row, January 2011–August 2026.
- Normal UI RIS export succeeded with abstracts; untouched native file: `/tmp/slr1-wiley-pilot.ris`.
- Native RIS: **1** record. Tags: `AU:5, DA:1, DO:1, ER:1, IS:1, JA:1, JF:1, JO:1, KW:8, N2:1, PB:1, PY:1, SN:1, SP:1, T1:1, T2:1, TY:1, UR:1, VL:1, Y1:1, Y2:1`. `N2` abstract preserved.
- Normalized CSV: `/tmp/slr1-wiley-normalized.csv`; **1** row. Headers: `Search source, Query, Rank, Paper ID, DOI, Title, Authors, Publication year, Abstract, Citation count, URL, Open access PDF, Source total`.
- Source, exact query, source total, and global rank (offset 0 → rank 1) preserved. Merge: `/tmp/slr1-wiley-merged.json`; raw/unique **1/1**, preserved.

## Recommended plan wording

```md
On 2026-08-06, unrestricted Wiley Advanced Search pilots used one `Anywhere`
(`field1=AllField`) row with `AfterMonth=1`, `AfterYear=2011`,
`BeforeMonth=8`, and `BeforeYear=2026`, with no journal, content-type,
access, or venue facet. W-A2 returned 40 Articles & Chapters and 2
Collections at 20:23:50 EDT (UTC−04:00); W-B2 returned 105 Articles &
Chapters and 4 Collections at 20:24:21 EDT (UTC−04:00). Both exact strings
were accepted. These are `pilot_not_candidate_search` observations; rerun
every accepted strategy after protocol authorization.

A one-record, first-page W-A1 normal-UI Export Citation(s) pilot using RIS
with `include=abs` completed successfully. The native RIS contained an `N2`
abstract field, and normalization preserved source, exact query, global rank,
and source total; the merge smoke test preserved 1 raw and 1 unique record.
These artifacts are `pilot_not_candidate_search` only.
```
