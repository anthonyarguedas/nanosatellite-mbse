# Pilot 007: smaller-page strict B1 attempt

**Status:** stopped diagnostic. This is not a final search.

Pilot 007 predeclared the six comparisons left after Pilot 006 and reduced the native page size from 200 to 50. The [literal B1 event](searches/literal/B1.json) again failed during strict result reconciliation with candidate total 165. It retained `total: null` and a configured-search screenshot. The [run receipt](searches/run-receipt.json) stopped before the wildcard or other partitions.

A bounded one-owner diagnostic then exhausted all 165 B1 records across four pages. This showed that current traversal can complete when one adapter-owned page runs at a time. Pilot 008 therefore predeclared two separate complete one-owner events per query and reconciled them locally. Pilot 007 contributes no accepted wildcard set.
