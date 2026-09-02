# Pilot 008: unchanged direct A2 readiness retest

Required changes were applied in commit: c16192b4b347eae0aba5ee47bfafade9daccbc5a

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

Pilot 008 is diagnostic. It is not a final search.

## Objective

Retest the exact unchanged direct A2 expression twice:

```text
F(P) AND F(E_F) AND (F(M_H) OR F(M_B))
```

The 5,947-character query has SHA-256 `c089612db91c2dcecacc21f5c6d2aafad7ca54b13725c1e3eecc4baa6cd7f934`. It is byte-identical to Pilot 005. The [predeclared plan](searches/event-plan.json) uses one source expression and introduces no split, wildcard, filter, or term change.

Both events requested Documents, All Results, oldest-first ordering, and native Publication Year `2011_2026_Year`. The adapter could reach Year handling only after the initial result page became ready.

## Result

Both unchanged attempts failed at `initial_form_readiness` with `total: null`.

| Evidence | Pass 1 | Pass 2 |
|---|---|---|
| Exact query echo | yes | yes |
| Expected IEEE route | yes | yes |
| Access or syntax state | none | none |
| Initial form ready | no | no |
| Stable summary | no | no |
| Cards | 0 | 0 |
| Sort control | not observed | not observed |
| Year attempts | 0 | 0 |
| Source total | `null` | `null` |

The two [source artifacts](searches/counts/) have the same structural failure signature. They also match both Pilot 005 A2 attempts. The direct unchanged expression has therefore failed four independent times after exact query echo.

IEEE accepts the query text on its public route, then leaves the result shell unready. No source total is available. Publication Year handling is not involved.

## Decision

Document a source limitation.

The direct A2 expression is not currently executable through a stable rendered result page. Keep every direct A2 total null. Pilot 008 does not authorize a split or any narrower source query.

A future exact Boolean distribution into source cells requires a separately predeclared pilot. It must retain the identity:

```text
P AND E_F AND (M_H OR M_B)
=
(P AND E_F AND M_H) OR (P AND E_F AND M_B)
```

IEEE Xplore remains unauthorized for final search execution.

## Later adapter reclassification

[Pilot 009](../009/pilot.md) identified this repeated state as an adapter v9 transport failure. The 9,319-byte request target received HTTP 414 before IEEE loaded its result application. Adapter v9 ignored that status and treated the failed route's query parameter as an exact source echo. Adapter v10 preserved the byte-identical literal query in a 7,477-byte request target and completed two count events with the same total.

The Pilot 008 artifacts remain immutable failure evidence. Their direct-A2 source-limitation diagnosis is superseded. No Pilot 009 count is a final search result.

## Validation and reproduction

The [assessment](searches/assessment.json) hashes both failures and verifies the Pilot 005 query identity. The [validation report](searches/validation-report.json) checks the predeclared plan, query bytes, controls, failure signatures, null totals, and source guideline.

```bash
python3 SLR/SLR1/scripts/ieee_xplore_pilot008/build_plan.py \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/008/searches/event-plan.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot008/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/ieee-xplore/pilots/008/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/008 \
  --receipt SLR/SLR1/source-specific/ieee-xplore/pilots/008/searches/run-receipt.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot008/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/008 \
  --pilot005-root SLR/SLR1/source-specific/ieee-xplore/pilots/005 \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/008/searches/assessment.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot008/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/008 \
  --pilot005-root SLR/SLR1/source-specific/ieee-xplore/pilots/005 \
  --guideline SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/008/searches/validation-report.json
```
