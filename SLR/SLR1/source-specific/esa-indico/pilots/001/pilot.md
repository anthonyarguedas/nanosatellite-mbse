# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py`

## Objective

Validate full deterministic local A1 and BG1 materialization and parsing, same-field `NEAR/5`, and a trailing wildcard candidate.

## Runs

- [`local-translation-audit.json`](searches/local-translation-audit.json)

## Result

- [x] Document a source limitation
- [x] Change the source translation

The offline audit is explicitly not a source search. Exact A1 (`26 P`, `38 E_H`, `54 M_H`) and BG1 (`14` fixed literals, `16` pairs) parsed successfully. Same-field `NEAR/5` passed in both orders and rejected cross-field and six-gap cases. Every one of `146` wildcard coverage checks passed. The candidate reduced A1 by `1,025` characters and BG1 by `725` characters. Keep exact expressions normative because wildcard completions broaden recall and no result-set evidence supports adoption.
