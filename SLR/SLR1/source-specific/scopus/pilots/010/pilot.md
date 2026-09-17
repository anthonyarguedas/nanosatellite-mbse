# Pilot 010: same-year source-order diagnostic

**Status:** passed diagnostic. This is not a final search.

## Objective

Repeat an exact EID query for the four B1 records that had changed position under Date (oldest). Determine whether Scopus exposes a stable secondary ordering pattern before relaxing strict completion from ordered-sequence equality to complete stable-ID-set equality.

The [predeclared plan](searches/event-plan.json) ran six independent one-owner events. Every event used Documents, years 2011-2026, the exact visible `English` facet, Date (oldest), page size 10, no abstract expansion, and both mandatory screenshots.

## Result

All six events returned exactly the same four IDs. Every event preserved monotonic retained years, with both 2022 records before both 2025 records. Two full source orders occurred:

- five events placed `105005251801` before `85137554950`
- one event reversed that 2022 pair

The 2025 pair retained one order in all six events. Earlier B1 runs had reversed that pair, so this bounded result does not establish a permanent rule for either pair.

The [assessment](searches/assessment.json) records two unique full orders, equal stable-ID sets, and 12 verified screenshots. Exact publication dates were unavailable in the retained rows. No stable secondary tie-break pattern was observed.

## Decision

Relax strict cross-pass reconciliation to require identical complete unique stable-ID sets. Continue to require exact totals, complete page accounting, contiguous ranges, controls, and per-pass uniqueness. Retain both ordered hashes, whether order matched, and the changed-position count as audit evidence.
