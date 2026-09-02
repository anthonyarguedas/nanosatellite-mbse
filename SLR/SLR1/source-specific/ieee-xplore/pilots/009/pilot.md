# Pilot 009: literal A2 adapter transport repair

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

Pilot 009 is diagnostic. It is not a final search.

## Objective

Validate the adapter repair with two executions of the unchanged direct A2 expression:

```text
F(P) AND F(E_F) AND (F(M_H) OR F(M_B))
```

The 5,947-character query has SHA-256 `c089612db91c2dcecacc21f5c6d2aafad7ca54b13725c1e3eecc4baa6cd7f934`. It is byte-identical to Pilots 005 and 008. The [predeclared plan](searches/event-plan.json) uses one literal source expression. It contains no wildcard, split, proximity operator, filter change, or Boolean change.

## Adapter diagnosis and repair

The bounded [transport investigation](searches/transport-investigation.json) found that adapter v9 encoded the initial A2 request target into 9,319 bytes. IEEE returned HTTP 414 before its result application loaded. The old adapter ignored the response status and read the query from the failed page URL, so Pilot 008 recorded an exact URL echo as source-observed query evidence.

Adapter v10 retains percent-component encoding for request targets through 7,800 bytes. Longer routes use `+` for spaces and retain RFC-safe parentheses. The ordered decoded parameters remain identical. The repaired A2 request target is 7,477 bytes.

Adapter v10 also:

- rejects explicit HTTP errors;
- recognizes rendered request-rejection pages; and
- records query echo only from a ready result state.

The repair changes no search term. IEEE's ten-wildcard limit is not used as a query-shortening mechanism. Wildcards remain excluded from this source translation.

## Result

Both predeclared events completed with the same source total of 33.

| Evidence | Pass 1 | Pass 2 |
|---|---:|---:|
| Exact rendered query echo | yes | yes |
| Native Publication Year | exact `2011_2026_Year` | exact `2011_2026_Year` |
| Oldest sort | yes | yes |
| Source total | 33 | 33 |
| Valid terminal marker | yes | yes |

The [assessment](searches/assessment.json) binds both events to adapter v10 and confirms byte identity with Pilot 008. The [adapter validation](searches/adapter-validation.json) records 24 focused passing tests, a clean Ruff check, and both live events. Pilot 008 remains immutable evidence of adapter v9 failure. Its direct-A2 source-limitation diagnosis is superseded by this transport repair.

## Decision

Retain the complete literal A2 expression and prohibit wildcards. Use the bounded compact route representation when the equivalent percent-component request target exceeds the validated envelope.

Pilot 009 resolves direct A2 initial readiness. IEEE Xplore remains unauthorized for final execution because this pilot used year precision and count-only mode. It does not validate the exact publication-day cutoff or a complete two-pass record capture.

## Reproduction

```bash
python3 SLR/SLR1/scripts/ieee_xplore_pilot009/build_plan.py \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/009/searches/event-plan.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot009/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/ieee-xplore/pilots/009/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/009 \
  --receipt SLR/SLR1/source-specific/ieee-xplore/pilots/009/searches/run-receipt.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot009/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/009 \
  --pilot008-root SLR/SLR1/source-specific/ieee-xplore/pilots/008 \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/009/searches/assessment.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot009/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/009 \
  --pilot008-root SLR/SLR1/source-specific/ieee-xplore/pilots/008 \
  --guideline SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/009/searches/validation-report.json
```
