# Pilot 020: final-page Next-control diagnosis

**Status:** diagnostic passed. This is not a final search.

The [predeclared bounded diagnostic](searches/event-plan.json) found two Next candidates after all 237 PSR2 records were traversed. One was the disabled final paginator. The other was an enabled article-title link, “Lessons Learned from Training the Next Generation of Space Software Engineers.” The article title caused the false positive because the parser accepted any link text containing `next`.

The [run receipt](searches/run-receipt.json) retains the bounded candidate attributes without hrefs, source rows, stable IDs, query text, or browser targets. The adapter now recognizes exact Next controls and the disabled paginator's screen-reader suffix. It excludes arbitrary result-title links.
