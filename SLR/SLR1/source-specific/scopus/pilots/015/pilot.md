# Pilot 015: isolated 200-row PSR retry

**Status:** failed diagnostic. This is not a final search.

The [predeclared plan](searches/event-plan.json) reran all four current literal PSR partitions with one fresh authorized target per event and the native 200-row page size. This reduced PSR2 to two pages per pass without changing the query or adding a source restriction.

PSR3 completed with one ID and a strict v2 receipt. PSR2 and PSR4 traversed complete first-pass source ledgers of 237 and 68 records, then failed closed. PSR1 stopped at editor focus before source execution. The [run receipt](searches/run-receipt.json) and all captured artifacts are retained.

The 200-row route did not provide a clean four-partition result. Pilots 016 through 020 isolated the final-page parser fault, and Pilot 021 returned to the validated 50-row setting.
