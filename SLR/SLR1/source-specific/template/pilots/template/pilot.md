# Pilot Consecutive Number

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_template.py`

Pilot searches are saved to `source-specific/template/pilots/template/searches/`.
Name each search artifact with the cross-source query schedule ID being piloted (`A1.json`, `PSR1.json`), or seed paperID in the case of citation chasing pilots (`paperID.json`). For pilot searches that intentionally deviate from the query schedule and citation chasing strategy for testing purposes, name them with a consecutive test number (`test1.json`). The script will automatically record the exact query and filters you tested.

The script above automatically saves the required search event metadata, including failures. A single search event failure does not warrant excluding the source from the review, only systematic failures that conflict with inclusion/exclusion criteria.

## Objective

Write the objective in one sentence.

## Result

One or more of:
- No protocol changes needed
- Document source-specific limitation
- Change source-specific filters or controlled vocabulary
- Change source-specific concept blocks translations
- Change source specific query schedule
- Change cross-source concept blocks
- Change cross-source query schedule
- Change cross-source inclusion/exclusion criteria
- Exclude source from review due to failure

Justify the result with an evidence-based paragraph that references the results of all tests.

(mark this pilot done in `SLR/SLR1/source-specific/template/source-specific-guidelines.md` when the changes resulting from the pilot are commited, or if it ends without changes needed)
