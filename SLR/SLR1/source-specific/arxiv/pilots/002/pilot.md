# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_arxiv.py`

## Objective

Record the unavailable Language and type controls, and test documented trailing `*` in one representative structured-row `A1` cell. This is diagnostic only, using 2011-01-01 through 2026-08-29.

## Runs

- [Pilot 001 exact cell](../001/searches/test1.json)
- [`test1.json`](searches/test1.json): `CubeSat*` candidate cell

## Result

- [x] Document a source limitation

Both the exact and wildcard cells reported zero. They are count-only cells, not a full partition or stable-ID comparison. The candidate changed only `CubeSat` to `CubeSat*`. The source-rendered query length grew from 93 to 94 characters (reduction `-1`). No other punctuation, spacing, phrase, or spelling form was replaced. Possible suffix completions were not enumerated, so the wildcard is **unaccepted** and is not adopted from the equal zero totals.

The current receipt records no usable Language or document-type control. arXiv remains bounded to submissions/e-prints (preprints), so no additional type restriction is applied. No access, full-text-availability, or peer-review filter was used. English remains a full-text screening decision.
