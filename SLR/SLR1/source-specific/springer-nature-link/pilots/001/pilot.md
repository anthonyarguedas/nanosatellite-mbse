# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_springer_link.py`

## Objective

Validate the complete source-native `A1` translation in count-only mode with unrestricted language, native `oldestFirst`, and the diagnostic upper bound 2026-08-29. Proceed to `BG1` only if the two-pass identity check succeeds.

## Runs

- [`A1.NON_MERGEABLE_DIAGNOSTIC.json`](searches/A1.NON_MERGEABLE_DIAGNOSTIC.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

The deterministic audit used `P: 26`, `E_H: 38`, and `M_H: 54`. The A1 count-only attempt reached the two-pass canonical identity check, then the verification pass returned a different canonical-path order. The script saved a non-mergeable failure artifact with no total. It is an explicit source order or pagination failure, not zero. The stop rule prevented a BG1 request. Retain the strict identity and native oldest-first checks. This is a diagnostic artifact, not a final search.
