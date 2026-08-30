# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py`

## Objective

Compare complete literal and source-native wildcard-compressed A1 under identical Articles & Chapters, date, and sort controls.

## Runs

- [`A1.json`](searches/A1.json): literal A1.
- [`A1.wildcard.json`](searches/A1.wildcard.json): wildcard candidate.

## Result

- [x] Change the source translation or schedule
- [x] Document a source limitation

Both diagnostics returned 21 Articles & Chapters records, retained all 21, and had the same ordered DOI ledger (`aa37f90bd324493e79e0875355abdfd68be1c920260525efa76f83a4632ee6c8`). There were no candidate-only IDs. The literal is 2,770 characters and the candidate 2,685 (-85). The accepted A1-only replacements are `CubeSat/CubeSats` → `CubeSat*`, `nanosat/nanosats/nanosatellite/nanosatellites` → `nanosat*`, and `SmallSat/SmallSats` → `SmallSat*`. Each `*` can also admit other suffix tokens (notably joined `CubeSatellite(s)` or `SmallSatellite(s)` and other matching prefixes). None produced a candidate-only A1 ID. All uncovered punctuation, spacing, phrase, and spelling forms remain literal.

`articlesChapters` is the source type boundary. No `PubType`, peer-review, access, or full-text filter was applied. Wiley exposes no Language field or facet, so English remains a full-text decision. These are pilot diagnostics, not final searches.