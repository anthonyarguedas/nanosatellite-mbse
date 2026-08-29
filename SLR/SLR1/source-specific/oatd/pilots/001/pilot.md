# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`

## Objective

Validate complete source-native `A1` and `BG1` count-only translations in OATD with the 2011-2026 source year window and source-rendered relevance order.

The deterministic audit used `P: 26`, `E_H: 38`, and `M_H: 54` literal members for `A1`. `BG1` used `P: 26`, `G_model: 14` fixed literals, and `16` declared pairs. Each pair expanded to `12` named-field clauses, both orders in `title`, `author`, `abstract`, `publisher`, `subject`, and `discipline`, for `192` pair clauses. No wildcards or controlled vocabulary terms were added.

## Runs

- [`A1.json`](searches/A1.json)
- [`BG1.json`](searches/BG1.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

The complete A1 expression reached the normal OATD route with an exact total of `1`, no retained records, and source-rendered `relevance` order. The complete BG1 expression used the required named-field, both-order `~5` union, but the page did not become ready within the 60-second request bound. Its artifact records `OATDMetadataRequestError`, no total, and no records. This is a route/readiness failure, not a zero or syntax result. The stop rule prevented a retry. These are diagnostic artifacts, not final searches.
