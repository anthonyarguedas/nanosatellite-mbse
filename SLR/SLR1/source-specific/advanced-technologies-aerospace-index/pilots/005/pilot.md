# Pilot 005: adapter stability repair

Pilot 005 is a diagnostic adapter check. It is not a final search. It uses the labelled 2011-01-01 through 2026-08-29 pilot window, and all retained artifacts are non-mergeable.

## Objective

Repair and validate three adapter defects exposed by earlier ATAI pilots:

1. A transient terminal `More` token changed otherwise identical abstract strings.
2. The exact restore-session modal could cover normal database-selection controls.
3. The ATAI lease lacked the inventory-proven target ID required by the current shared-browser cleanup helper.

## Adapter v4 repairs

The strict repair checks ran with adapter version 4. Current adapter version 5 retains these repairs and adds automatic sibling search-page and results-page screenshots for every CLI JSON output.

- Abstract extraction removes only a terminal standalone `More` after sentence punctuation. Normal prose such as `learn more` remains unchanged. The JavaScript extractor and Python payload parser apply the same canonical rule.
- The adapter recognizes only the exact `#restoresession_confirm` dialog with the expected “Restore your last ProQuest session” text. It clicks the exact `Dismiss` action on its owned page before blocked source actions. Cookie consent remains separate.
- Attached pages are allocated through the shared target-inventory helper. The resulting opaque target ID is carried in the ATAI lease, reasserted before source actions, and used by verified cleanup.
- The local Pilot 004 monkeypatches were removed. Its runners now use adapter v4 directly.

## Abstract truncation audit

The [repair validation](searches/adapter-repair-validation.json) compares both historical ordinary passes with fresh adapter v4 output.

- A3 had one record whose historical passes differed only by terminal `More`.
- B1 had seven of 19 records whose historical passes differed only by terminal `More`.
- Removing that token made every historical A3 and B1 abstract exactly equal to fresh adapter v4 text.
- No fresh canonical abstract ended in an ellipsis.
- The saved JSON contains the full canonical abstract strings. Ellipses shown by the adapter's console preview are display caps only.

No abstract truncation was observed. The unstable `More` text was a presentation token.

## Strict live checks

Fresh adapter v4 runs used ATAI alone, `LA(English)`, the inclusive publication-date range, no document-type, peer-review, full-text, or access filter, frozen variant controls, and `DateAsc`.

| Partition | Source total | Full records | Strict passes | Cleanup page count |
|---|---:|---:|---:|---:|
| A3 | 1 | 1 | 2 stable | 10 → 10 |
| B1 | 19 | 19 | 2 stable | 10 → 10 |

The retained [A3](searches/A3.strict-v4.json) and [B1](searches/B1.strict-v4.json) artifacts passed the two-full-record-pass contract. Both owned pages disappeared while shared Chrome remained open.

These successes supersede the prospective adapter limitation caused by Pilot 003's strict A3 and B1 failures. The historical failure artifacts remain unchanged as evidence of adapter v3 behavior.

## Validation

Focused offline command:

```bash
cd "$HOME/agent-tools/academic-api-search/skills/academic-api-search/tests"
uv run --with playwright python test_search_proquest_aerospace.py
```

Result: 22 tests passed.

The live checks used the normal adapter through `run_with_browser.py`. The non-mergeable artifacts and abstract audit were built with:

```bash
python3 SLR/SLR1/source-specific/advanced-technologies-aerospace-index/scripts/atai_pilot005/build_repair_validation.py \
  --a3 /tmp/atai-v4-a3.json \
  --b1 /tmp/atai-v4-b1.json \
  --a3-before /tmp/atai-v4-a3-before.json \
  --a3-after /tmp/atai-v4-a3-after.json \
  --b1-before /tmp/atai-v4-browser-before.json \
  --b1-after /tmp/atai-v4-browser-after.json \
  --historical-a3-pass1 SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/003/searches/A3-repaired-pass1.json \
  --historical-a3-pass2 SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/003/searches/A3-repaired-pass2.json \
  --historical-b1-pass1 SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/003/searches/B1-stable-id-pass1.json \
  --historical-b1-pass2 SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/003/searches/B1-stable-id-pass2.json \
  --output-dir SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/005/searches

python3 SLR/SLR1/source-specific/advanced-technologies-aerospace-index/scripts/atai_pilot005/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/005 \
  --guideline SLR/SLR1/source-specific/advanced-technologies-aerospace-index/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/005/searches/validation-report.json
```
