# Pilot 003: metadata field union noise diagnostic

Required changes were applied in commit: NA (uncommitted proposal only)

Export method: `~/agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py`, through the shared browser wrapper.

## Objective

Test a prospective metadata-field union that preserves every term and Boolean relation for all nine scheduled queries. The requested diagnostic window was 2011-01-01 through 2026-08-29. ARC applied inclusive 2011-01 through 2026-08 source-month controls, so count totals are conservative before exact-day exclusions. This is not a final search.

## Method

For every schedule entry, `P` was placed separately in **Title**, **Keywords**, and **Abstract**. The unchanged semantic remainder stayed in **Anywhere**. Each three-cell sum is only a conservative upper bound. Above 100, `P` and its defining model/artifact block were assigned in all 3-by-3 Title/Keywords/Abstract combinations, with the third block left in Anywhere.

`BT2`'s unsplit 7,679-character Anywhere remainder timed out in all three primary cells. Its 224 declared `T2` pairs were therefore split prospectively into four disjoint 56-pair OR subcells. No literal or pair was removed. The source failures and each replacement cell are retained.

No wildcard was used: Pilot 002 did not prove stable-ID equality or a superset for `nanosatellit*`. No Language, publication-type, Topic, access, or other narrowing filter was applied.

## Runs

- [All required cells, controls, totals, sums, replacements, failures, and statuses](searches/schedule-assessment.json)
- [A2 DOI-first sampled-prefix audit](searches/A2-sampled-prefix-doi-dedup-audit.json) and [visible metadata recheck](searches/A2-sampled-prefix-page-metadata-recheck2.json)
- [BT2 DOI-first sampled-prefix audit](searches/BT2-sampled-prefix-doi-dedup-audit.json) and [visible metadata recheck](searches/BT2-sampled-prefix-page-metadata-recheck.json)
- [Pilot query construction and membership/pair declarations](../../scripts/aiaa_arc_pilot003/queries.py)

The current CLI's field-row-only count-only writer has an empty raw-query alias conflict after the live source result. The [pilot runner](../../scripts/aiaa_arc_pilot003/run_fielded_count.py) therefore invokes the same ARC adapter function through the shared browser wrapper and saves an exact field-row/control projection. This is an output-serialization limitation, not a source zero or false match.

## Result

| ID | Three P-field cells | 3-by-3 upper bound | DOI-first records / source events | Finding |
|---|---:|---:|---:|---|
| A1 | 140 | 42 | NA | Low-volume upper bound |
| A2 | 479 | 119 | 40 / 119 | Low-volume DOI union. Visible `E_F` noise |
| A3 | 144 | 33 | NA | Low-volume upper bound |
| B1 | 394 | 87 | NA | Low-volume upper bound after two recovered source failures |
| B2 | 283 | 56 | NA | Low-volume upper bound |
| BG1 | 2,307 | 93 | NA | Low-volume upper bound after four recovered source failures |
| BG2 | 1,722 | 20 | NA | Low-volume upper bound after recovered source failures |
| BC1 | 52 | NA | NA | Low-volume upper bound |
| BT2 | 1,018 after lossless `T2` subcells | 205 | 23 / 205 | Low-volume DOI union. No sampled visible `T2` pair |

The 100-record investigation threshold applies to a conservative cell-sum upper bound or to DOI-first deduplicated investigation records. It does not apply to overlapping raw source events across cells. All A2 and BT2 refined cells were exhausted, then their 119 and 205 source events reconciled to 40 and 23 DOI-first records.

The sampled A2 union had visible `P` in 29/40, a model block in 22/40, and `E_F` in 1/40 records. The BT2 union had visible `P` in 15/23, `M_B` in 16/23, and a declared `T2` pair in 0/23. These are visible metadata warnings, not false-match decisions. ARC Anywhere includes hidden indexed material and full text.

ARC exposes no Language control or facet. Publication Types are result facets only and have not been shown to form a lossless union of eligible journal, meeting-paper, and chapter records, so no type filter was used. Topic `ConceptID` supplies no descriptor, scope note, hierarchy, or explosion semantics and was not used as an AND noise filter.

- [x] Change the source translation or schedule
- [x] Document a source limitation

### Uncommitted proposal: **not accepted**

For a later pilot, use the metadata `P` union and, where needed, the 3-by-3 `P`/defining-block union with the third block in Anywhere. Keep the named `T2` OR subcells if ARC's full row remains unavailable. **Do not adopt this as the final translation yet.** The repository has no stable-ID register of known eligible AIAA reports, and Pilot 001 is count-only. Therefore no known-item check can show that moving `P` or the defining block out of Anywhere has no observed recall loss.
