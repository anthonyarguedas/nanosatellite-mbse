# Pilot 005: compact-receipt runner stop

**Status:** stopped diagnostic. This is not a final search.

Pilot 005 repeated the [18-event plan](searches/event-plan.json) after the long-query editor repair. The literal A1 source event completed two strict passes with six records. It saved the mandatory [configured-search](searches/literal/A1.search-page.png) and [first-results](searches/literal/A1.results-page.png) screenshots beside its [JSON](searches/literal/A1.json).

The local runner then stopped because it expected verbose strict fields that the shared output compactor correctly retains inside `strict_two_pass_receipt`. The source event was valid. The local validation was wrong. The [run receipt](searches/run-receipt.json) preserves that distinction. No wildcard event ran, and this A1 result is excluded from the combined Pilot 009 decision.

Pilot 006 prospectively validated the compact strict receipt grammar and reran the paired events without reusing this source result.
