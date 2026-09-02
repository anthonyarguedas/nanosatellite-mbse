# Pilot 018: direct PSR2 predicate diagnostic

**Status:** completed source traversal, diagnostic unresolved. This is not a final search.

A [predeclared direct diagnostic adapter](searches/event-plan.json) traversed all 237 PSR2 records over five pages and failed closed. The strict predicate hook produced no output because the exception occurred before strict-pass construction. The [run receipt](searches/run-receipt.json) preserves this result. Pilot 019 traced the earlier exception site.
