# Pilot 019: PSR2 internal failure trace

**Status:** diagnostic completed. This is not a final search.

The [predeclared trace](searches/event-plan.json) retained no browser target, query text, source row, or stable ID in its debug output. After all 237 PSR2 entries were traversed, the adapter raised `Scopus exposed an enabled next-page control after its reported final record`. The bounded [trace](searches/debug-stderr.txt) established the failing branch. Pilot 020 inspected its candidate controls.
