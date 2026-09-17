# Pilot 009: trailing wildcard acceptance

Pilot 009 is diagnostic and separate from final search. It uses 2011-01-01 through 2026-08-29. All source artifacts are non-mergeable.

## Objective

Test `nanosatellit*` as a narrow replacement for the two unhyphenated population literals `"nanosatellite" OR "nanosatellites"`. Compare every current Pilot 007 hybrid cell in fresh literal and wildcard source calls using complete stable DOI capture.

The [predeclared paired plan](searches/event-plan.json) changed one exact fragment per cell. It kept `nanosat`, hyphenated forms, spaced forms, CubeSat forms, SmallSat forms, and small-satellite forms literal. The replacement shortened each cell query by 22 characters.

## Results

All 94 pairs completed. The 188 successful source events were at most 45 records and were captured completely.

For every pair:

- The source total was equal.
- The raw stable-ID set was equal.
- The canonical DOI set was equal.
- The source read back the exact literal or wildcard field rows.

| Partition | Literal DOI union | Wildcard DOI union |
|---|---:|---:|
| A1 | 18 | 18 |
| A2 | 40 | 40 |
| A3 | 12 | 12 |
| B1 | 37 | 37 |
| B2 | 23 | 23 |
| BG1 | 44 | 44 |
| BG2 | 2 | 2 |
| BC1 | 36 | 36 |
| BT2 | 11 | 11 |
| Complete schedule | 119 | 119 |

The fresh literal schedule reproduced Pilot 007's 119-DOI union. The wildcard schedule returned the same 119 DOIs. It added zero and lost zero. Known eligible DOI `10.2514/6.2015-4474` remained present in A2, B1, B2, and BC1.

Two retained records visibly exercise the unhyphenated singular form: `10.2514/6.2013-5325` and `10.2514/6.2017-0400`. Their literal and wildcard cell memberships were equal.

## Decision

Accept this exact source translation:

```text
"nanosatellite" OR "nanosatellites"  ->  nanosatellit*
```

Use the wildcard unquoted and only in the population block `P`. Keep every other population spelling and punctuation form literal. This decision grants no general permission for other stems, wildcard positions, or quoted wildcards.

Pilot 009 supersedes Pilot 002's count-only nonacceptance for this one candidate. Pilot 002 had no stable-ID comparison. Pilot 009 supplies complete paired raw-ID and canonical-DOI equality across the current route.

## Runs and audit evidence

- [Predeclared paired event plan](searches/event-plan.json)
- [Complete assessment](searches/assessment.json)

Pilot 009 verified 376 mandatory screenshots for 188 successful JSON artifacts. Four transient owned-page creation failures remain in the audit record. Exact retries recovered every event. No failure became zero.

Final execution still requires new source calls, source-month treatment, exact-day handling, native export, and final-search artifacts.
