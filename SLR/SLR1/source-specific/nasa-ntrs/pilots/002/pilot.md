# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ntrs.py`

## Objective

Record the unavailable Language and non-lossless Type controls, and test one supported trailing-wildcard compression of complete `A1`. This is diagnostic only, using NTRS's exact publication-date window 2011-01-01 through 2026-08-29.

## Runs

- [Pilot 001 literal `A1`](../001/searches/A1.json)
- [`test1.json`](searches/test1.json): full-`A1` wildcard candidate

## Result

- [x] Document a source limitation

The literal and wildcard `A1` totals were both zero count-only. The candidate changed only the listed `nanosatellite` and `nanosatellites` literals to `nanosatellit*`, shortening the full query from 2,762 to 2,740 characters (`22`). All other punctuation, spacing, phrase, and spelling forms remained literal. Count-only retained no stable-ID comparison, so extra completions and equality/superset are unproved: the wildcard is **unaccepted** and is not adopted from zero totals.

NTRS exposes no usable Language control. Its Type selector accepts one exact option per run, but neither the vocabulary nor missing-assignment behavior proves a lossless OR of articles, conference papers, and technical reports. No type restriction is applied. No access, full-text-availability, or peer-review filter was used. The general `q` still searches indexed full text. That is source scope, not an access or full-text filter.
