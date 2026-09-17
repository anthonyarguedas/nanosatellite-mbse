# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`

## Objective

Retry Pilot 001's unchanged complete `BG1` count-only request once before any wildcard conclusion: 2011–2026, source-rendered relevance order, one page, and the same 60-second readiness bound.

## Runs

- [`BG1.json`](searches/BG1.json): unchanged complete `BG1` retry.

## Result

- [x] Document a source limitation

The retry used the unchanged Pilot 001 query and requested 2011–2026, source-rendered relevance order, one 30-record page, zero busy retries, and the 60-second bound. OATD again returned `OATDMetadataRequestError` because the page did not become ready. It has no query echo, total, or records. This is a terminal route/readiness failure, **not zero**. Per the stop rule, no English `A1` check or wildcard candidate was issued.

The source-native English metadata control remains a proposal for a later successful event: display option `English`, source value `(en OR eng OR english)`, with route-query readback required. It is not accepted by this pilot. Full-text screening would remain authoritative. OATD remains an ETD source without a lossless degree/level union proved for completed master's and doctoral reports, so no degree, level, completion, availability, access, or full-text restriction is accepted. No wildcard conclusion is drawn.
