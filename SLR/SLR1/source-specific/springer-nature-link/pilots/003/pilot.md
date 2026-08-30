# Pilot 003: repaired literal schedule and canonical-ID union

Required changes were applied in commit: NA (pilot-only, with no final-search state change)

Export method: the fixed `search_springer_link.py` adapter through the shared local-browser wrapper.

## Objective

Run all nine literal schedule partitions with `En`, broad whole-platform content, `oldestFirst`, 2011-01-01 through 2026-08-29, and the repaired two-pass canonical-path check. Reconcile each retained stable-ID union without accepting a wildcard or a final-search translation.

## Method

- Every literal and declared pair comes from `pilot_schedule`, and [the query plan](searches/query-plan.json) records all direct rows and lossless cells. It contains no `*` or `?`.
- No content-type, access, full-text, peer-review, subject, discipline, controlled-term, or publication-type filter was used. `En` is a metadata facet only. English full-text screening remains required.
- The direct 3,431-character A2 row had identity/route failures, so its two lossless Boolean cells were used. B1's direct full row repeated a canonical path across pages, so adjacent exact-date source-year cells were reconciled. B2 uses the same year cells and lossless Boolean cells for its failed 2021, 2022, and 2024 routes.
- The 9,013-character BT2 row timed out. Its 224 explicit pairs were first divided into 11 `T2` OR cells (at most 1,994 characters), then only failed cells were subdivided without dropping a pair. All completed cells retained the adapter's two-pass proof.
- The normal event outputs are pilot artifacts, not final searches. [Canonical unions](searches/canonical-unions.json) validates each normal-output marker, controls, artifact digest, and stable path before deduplication.

## Outcomes

Counts are retained, exact-cutoff canonical-path unions after any detail-page date exclusion. “Complete” means every planned source cell in that row completed. It does not mean screened eligible evidence.

| ID | Retained canonical IDs | Outcome |
|---|---:|---|
| A1 | 59 | Complete direct literal row |
| A2 | 304 | Complete lossless Boolean/source-year cell union |
| A3 | 126 | Complete direct literal row |
| B1 | 210 | Complete source-year cell union after raw pagination failure |
| B2 | 481 | Complete source-year/Boolean-cell union |
| BG1 | 33 | Complete direct literal row |
| BG2 | 125 | Complete direct literal row after one pagination retry |
| BC1 | 136 | Complete direct literal row |
| BT2 | 465 retained | **Repaired-route failure:** all other lossless cells completed, but the 2017 `("variability" AND "models")` cell reported 4 records whose canonical detail route redirected on two attempts. Their stable IDs remain `null`. None were invented or merged. |

## >100 noise investigation and no-loss refinement

[The linked investigation](searches/noise-investigation.json) applies the threshold to each deduplicated partition union. It checks every retained title and abstract for the scheduled factors and exact declared pairs in either order with at most five intervening lexical tokens in one visible field. The visible all-factor priority subsets were A2 3, A3 1, B1 29, B2 8, BG2 2, BC1 3, and BT2 1.

This is a no-loss dual-lane refinement: those low-noise metadata subsets are linked screening priorities, while every body-only or metadata-negative source match remains in the broad canonical union. Link has a validated Title field but no independently validated Abstract-only field, and it has no supported proximity. A Title restriction, content-type restriction, access filter, or unproved taxonomy filter could lose records, so none is accepted. The BT2 body-text pair status remains uncertain where the source match is not visible in metadata.

## Controls and limits

- `En`, exact requested dates, `oldestFirst`, native broad content, and two-pass stable-identity checks were source-read back in every normal event.
- No wildcard was submitted or accepted in any partition. A wildcard must be separately stable-ID validated before future use.
- Date source controls are year-effective. The adapter retained unresolved dates and removed only records with a proved detail date outside the requested window.
- Link's Keywords field includes body text. The noise findings therefore do not classify metadata-negative records as false matches.
- The BT2 2017 failure is a source/detail-route failure, not zero results. It prevents accepting a complete BT2 union or a final source translation.

## Runs and checks

- [Query construction and membership tests](../../../../scripts/springer_pilot003/queries.py) and [tests](../../../../scripts/springer_pilot003/test_queries.py)
- [Canonical union receipt](searches/canonical-unions.json)
- [Noise investigation](searches/noise-investigation.json)
- [All adapter artifacts](searches/)

## Result

- [x] Document a source limitation

The repaired tie normalization supported the completed literal/cell unions, but does not repair Link's one canonical-detail redirect. Keep the literal schedule and broad fallback. Do not promote any Pilot 003 route to `final-searches/`.
