# Pilot 011: first set-reconciled strict attempt

**Status:** stopped diagnostic. This is not a final search.

The [plan](searches/event-plan.json) first applied the v2 complete-set strict contract to the four Pilot 010 EIDs, then scheduled the accepted wildcard B1 query.

The first event stopped before Search with `error_stage: editor_readback` and `total: null`. Strict mode owned two fresh pages, and the short EID expression lost individual Monaco key events on the first page. No screenshot state was reached. The [run receipt](searches/run-receipt.json) stopped before B1.

The adapter was repaired prospectively to use one target-scoped `Input.insertText` browser event for every nonempty query. Exact Monaco readback remains mandatory before the single Search click. Pilot 012 reran both events under a new plan and adapter hash.
