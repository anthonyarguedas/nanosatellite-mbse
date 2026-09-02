# Pilot 014: first clean current literal PSR attempt

**Status:** failed diagnostic. This is not a final search.

The [predeclared plan](searches/event-plan.json) attempted all four current literal PSR partitions. It ran PSR2 and PSR4 first. Every event used only the 2026 upper year bound, Documents scope, Date (oldest), and the strict v2 two-pass contract. No language, document type, subject, access, peer-review, lower-year, or Search within restriction was applied. Wildcard comparisons were omitted.

PSR4 completed with 68 IDs and PSR1 completed with 53 IDs. PSR1 retrieved Buruso et al. as `SCOPUS-PUBLICATION:105032155734`. PSR2 traversed a 237-record first-pass ledger and then failed closed. PSR3 failed before a query execution was confirmed. All captured JSON and PNG files remain under [`searches/`](searches/), and the [run receipt](searches/run-receipt.json) records every outcome.

Later diagnostics found that a PSR2 result title containing “Next” caused a false enabled-paginator state. Pilot 021 reran all four partitions after the parser repair.
