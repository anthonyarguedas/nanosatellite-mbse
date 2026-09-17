# Pilot 005: broader wildcard boundary

**Status:** completed stopped diagnostic. The broad schedule candidate is not accepted.

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_web_of_science.py` version 2.

## Objective

Test a stronger interpretation of “use wildcards whenever possible.” The [event plan](searches/event-plan.json) mapped 128 ordinary variant families covering 292 declared term occurrences. It used Web of Science `$` for zero or one trailing character and `*` only for families that require a longer suffix. Singleton terms and families without one reviewed common stem stayed literal.

The planned controls matched Pilot 004. Every query used Topic, all current Core Collection editions, `PY=(2011-2026)`, `LA=(English)`, Date: oldest first, strict two-pass capture, native RIS, and mandatory screenshots. No query used proximity or pair expansion.

## Results

The first broad `A1` attempt failed before source execution at browser connection. Its unchanged retry completed with one WOS ID. The ID equals the Pilot 004 literal `A1` set.

The 2,743-character direct broad `A2` query contains 48 wildcard operators. Three unchanged attempts saved the configured-search screenshot, then timed out at submit with `total: null`. The [recovery plan](searches/recovery-plan.json) split only the planned `M_H OR M_B` factor:

- `P AND E_F AND M_H` completed with five WOS IDs and both screenshots.
- `P AND E_F AND M_B` timed out at submit in three unchanged attempts. Each failure retains `total: null` and its configured-search screenshot.

The pilot stopped before `A3`, `B1`, `B2`, `BG1`, `BG2`, `BC1`, or `BT2`. Nine source attempts produced two successful events, one connection failure, and six submit failures. The [assessment](searches/assessment.json) verifies ten retained screenshots. Successful events have both sibling PNGs. Submit failures have only the pre-submit PNG because no results page became available.

## Decision

Reject the broad 128-family map for schedule use. The repeated A2 failures leave no complete A2 union and no full schedule comparison. They do not identify one invalid wildcard token or prove a source wildcard limit.

Keep Pilot 004's ten population wildcards. That smaller candidate completed all nine partitions, retained every literal ID, and added no record. Do not adopt Pilot 005's additional `$` or `*` patterns from its isolated A1 result.

Pilot 005 is diagnostic only. No result enters screening or a final search.
