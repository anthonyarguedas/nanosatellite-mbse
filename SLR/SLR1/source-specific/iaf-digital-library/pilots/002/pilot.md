# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`

## Objective

Record the indexed Language field and unavailable type vocabulary, and test documented trailing `*` in one representative `A1` cell below the 500-character limit. This is diagnostic only, using 2011-01-01 through 2026-08-29.

## Runs

- [Pilot 001 exact cell](../001/searches/test1.json)
- [`test1.json`](searches/test1.json): `CubeSat*` candidate cell

## Result

- [x] Document a source limitation

The exact and wildcard cells both reported zero. They are count-only cells, not a full partition or stable-ID comparison. The candidate changed only quoted `CubeSat` to bare `CubeSat*`, shortening the raw cell from 69 to 68 characters and remaining below 500. No other punctuation, spacing, phrase, or spelling form was replaced. Possible suffix completions were not enumerated, so the wildcard is **unaccepted** and is not adopted from the equal zero totals.

`language:English` is an indexed wizard field, but the receipt records no enumerated language vocabulary or missing-assignment behavior. It is a known source field, not an accepted exhaustive eligibility filter. English remains a full-text screening decision. IAF is already bounded to conference-paper records, and its wizard exposes no searchable publication-type vocabulary. No additional type, access, full-text-availability, or peer-review filter was used.
