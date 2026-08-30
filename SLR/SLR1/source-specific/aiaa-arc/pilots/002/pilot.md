# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py`

## Objective

Record unavailable or unaccepted Language/type controls and test one supported trailing-wildcard compression of complete `A1`, without changing the Anywhere field. This is diagnostic only, using 2011-01-01 through 2026-08-29.

## Runs

- [Pilot 001 literal `A1`](../001/searches/A1.json)
- [Pilot 001 `BG1`](../001/searches/BG1.json)
- [`test1.json`](searches/test1.json): full-`A1` wildcard candidate

## Result

- [x] Document a source limitation

The literal and wildcard `A1` totals were both `492` count-only. `BG1` remains `8,088` from Pilot 001 for the later field/noise investigation. The candidate changed only the listed `nanosatellite` and `nanosatellites` literals to unquoted `nanosatellit*`, shortening the full query from 2,762 to 2,740 characters (`22`). All other punctuation, spacing, phrase, and spelling forms remained literal. Count-only retained no stable-ID ledger, so extra completions and equality/superset are unproved: the wildcard is **unaccepted**. Equal totals are not a precision finding, and no narrower field was tested or adopted.

ARC exposes no usable Language control. Its visible Publication Types facets are not a proved lossless eligible-type union, and journal records can lack a visible facet. No type restriction is applied. No access, full-text-availability, or peer-review filter was used.
