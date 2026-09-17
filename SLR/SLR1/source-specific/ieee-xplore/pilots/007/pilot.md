# Pilot 007: native pagination investigation

Required changes were applied in commit: ce6a8ce6716e6b9a0e4fdeb6b2b6ad1ffd2f1452

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

Pilot 007 is diagnostic. It is not a final search. It uses native inclusive Publication Year `2011_2026_Year`. Every event skips full document pages to isolate rendered controls, pagination, and stable Article Numbers.

## Objective

Test the Pilot 006 diagnosis that strict setup failed by forcing a preferred Items Per Page transition. Retain the current valid native page size when it can exhaust the exact source total within `--max-pages`. Reconcile two complete passes without changing any query, date, scope, access, sort, or refinement.

## Repair under test

The adapter treats `--page-size 100` as a preference. It keeps the validated current native size when strict pagination fits the declared page bound. It still requires contiguous pages, exact source totals, unique ordered Article Numbers, equal semantic controls, and equal normalized exports in both passes.

Adapter v9 also persists a compact strict completion receipt. Each pass records its total, pages, native page size, Year representation, stable-ID hashes, export hashes, and completion state.

The [predeclared plan](searches/event-plan.json) contains three strict events. No event was retried.

## Results

All three events completed:

| Partition | Total | Native pages per pass | Page size | Year readback, pass 1 / pass 2 |
|---|---:|---:|---:|---|
| `BG2` | 11 | 1 / 1 | 25 / 25 | contained `2014_2026_Year` / exact `2011_2026_Year` |
| `BC1` | 28 | 2 / 2 | 25 / 25 | contained `2011_2026_Year` / exact `2011_2026_Year` |
| `B2` | 131 | 6 / 6 | 25 / 25 | exact / exact `2011_2026_Year` |

`BG2` and `BC1` recovered the Pilot 006 null strict events. Their equal totals, ordered Article Number hashes, and exports reconciled across different valid Year representations. This confirms the semantic year-control repair with live source evidence.

`B2` captured all 131 Article Numbers through contiguous rows 1 through 131 in each pass. Both passes used six native pages and produced the same ordered hash `60e900c04c118045330c037c71c286cec4c398827ddf9fac1ab76ce8fec154b6`. This resolves the historical over-100 rendered pagination blocker for current adapter behavior. It does not reinterpret the Pilot 004 artifact.

The complete `BG2` and `BC1` Article Number lists are in the [assessment](searches/assessment.json). The B2 list remains in its source artifact because it contains 131 records.

## Artifact status

All three JSON files have valid adapter-generated `IEEE_COMMIT` sidecars and complete compact strict receipts. The source artifacts report technical merge eligibility because the adapter completed its contract. Their location, predeclared purpose, and [assessment](searches/assessment.json) declare them diagnostic only. Do not merge them into the review baseline.

The [adapter validation](searches/adapter-validation.json) records 139 passing tests, 102 passing subtests, and a clean Ruff check. It also records the adapter hashes used for Pilots 006 and 007. A later metadata-only key rename did not change a source event or historical artifact.

## Result

Change the strict page-size policy.

Keep current valid native pagination when it fits `--max-pages`. Use the preferred page-size control only when current paging cannot fit the caller's bound. Require the same complete two-pass reconciliation in either case.

The native Year and rendered-state failures requested for investigation now have bounded causes:

- Pilot 005 Year resets and disabled Apply were unnecessary interactions with contained result intervals.
- Pilot 005 `BG1` strict failure came from comparing equivalent Year representations as different controls.
- The A1 `rendered_state` failures occurred during browser-page acquisition before source navigation.
- Pilot 006 `BG2` and `BC1` failures came from forcing an unnecessary page-size transition.

IEEE Xplore still lacks final-search authorization. Pilot 007 used year precision, skipped document details, and did not test the exact publication-day cutoff. The separate A2 initial form readiness failure also remains unresolved.

## Validation and reproduction

The [validation report](searches/validation-report.json) checks all Pilot 006 and 007 artifacts, source totals, contained intervals, strict receipts, native pages, stable-ID hashes, terminal markers, documentation, and adapter test evidence.

```bash
python3 SLR/SLR1/source-specific/ieee-xplore/scripts/ieee_xplore_pilot007/build_plan.py \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/007/searches/event-plan.json

python3 SLR/SLR1/source-specific/ieee-xplore/scripts/ieee_xplore_pilot007/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/ieee-xplore/pilots/007/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/007 \
  --receipt SLR/SLR1/source-specific/ieee-xplore/pilots/007/searches/run-receipt.json

python3 SLR/SLR1/source-specific/ieee-xplore/scripts/ieee_xplore_pilot007/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/007 \
  --pilot006-root SLR/SLR1/source-specific/ieee-xplore/pilots/006 \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/007/searches/assessment.json

python3 SLR/SLR1/source-specific/ieee-xplore/scripts/ieee_xplore_pilot007/validate_pilot.py \
  --pilot006-root SLR/SLR1/source-specific/ieee-xplore/pilots/006 \
  --pilot007-root SLR/SLR1/source-specific/ieee-xplore/pilots/007 \
  --guideline SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/007/searches/validation-report.json
```
