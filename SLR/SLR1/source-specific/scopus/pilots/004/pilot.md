# Pilot 004: first post-proximity wildcard attempt

**Status:** stopped diagnostic. This is not a final search.

The [predeclared plan](searches/event-plan.json) paired fresh literal and ten-wildcard stable-ID captures for all nine main partitions. It used the schedule from protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`, main years 2011-2026, the visible `English` facet, Documents, Date (oldest), no type limiter, and strict two-pass capture.

The first literal A1 event stopped before source submission. Thousands of individual Monaco key events did not produce exact editor readback. The [failure artifact](searches/literal/A1.json) has `total: null`, `error_stage: editor_readback`, and no result or screenshot claim. The [run receipt](searches/run-receipt.json) records the stop. No wildcard event ran.

The adapter was repaired prospectively. Long expressions now use one target-scoped browser text-entry event and still require exact Monaco `EditContext` readback before the single Search click. Pilot 005 used a new plan and adapter hash.
