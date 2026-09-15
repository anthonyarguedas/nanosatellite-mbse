# Pilot 004: current schedule, screenshots, and population wildcards

**Status:** passed diagnostic. This is not a final search.

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_web_of_science.py` version 2.

## Objective

Test all nine main partitions from protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`. Use no proximity operator or pair expansion. Compare each complete literal result set with Pilot 002's ten trailing-wildcard population candidates. Verify the adapter's mandatory configured-search and first-results screenshots.

## Method

The [event plan](searches/event-plan.json) fixed 18 literal and wildcard events before execution. Every event used:

- Web of Science Core Collection and every currently exposed edition
- `TS` Topic atoms
- raw `PY=(2011-2026) AND LA=(English)` controls
- Date: oldest first and native page size 50
- strict two-pass ordered WOS-ID and total reconciliation
- native RIS export for every positive first pass
- no publication type, subject, access, full-text, or controlled-term restriction
- two automatic sibling PNGs with no screenshot opt-out

The wildcard candidate replaces 22 population literals with ten quoted trailing-`*` atoms. Four population literals remain unchanged. Each candidate query is 255 characters shorter than its literal comparison.

## Results

| Partition | Literal total | Wildcard total | Complete sets equal | Complete order equal |
|---|---:|---:|---|---|
| `A1` | 1 | 1 | yes | yes |
| `A2` | 11 | 11 | yes | yes |
| `A3` | 2 | 2 | yes | yes |
| `B1` | 93 | 93 | yes | yes |
| `B2` | 78 | 78 | yes | yes |
| `BG1` | 3 | 3 | yes | yes |
| `BG2` | 7 | 7 | yes | yes |
| `BC1` | 17 | 17 | yes | yes |
| `BT2` | 3 | 3 | yes | yes |

Every wildcard event retained every literal WOS ID. No wildcard-only ID occurred. The literal and wildcard main unions each contain 154 IDs. The literal Stream A union contains 12 IDs, core Stream B contains 144, and expanded Stream B contains 29.

All 18 successful source events retained both required screenshots. The [assessment](searches/assessment.json) verifies 36 unique PNGs beside their JSON files, including filenames, hashes, dimensions, and privacy flags.

## Retained failures and recovery

The first `wildcard-BG1` attempt failed at browser connection before query execution. It retains `total: null`, no screenshots, and no source query claim. The [recovery plan](searches/recovery-plan.json) predeclared two unchanged retries. Attempt 2 completed with total 3, so attempt 3 did not run. The [recovery receipt](searches/recovery-run-receipt.json) also records completion of the remaining six original events.

The first runner stopped after a successful `literal-A1` event because its local validator expected source-private strict fields that the shared public-output compactor removes. The retained [local validation receipt](searches/run-receipt-initial-local-validation-failure.json) records adapter exit 0 and source status success. The corrected validator uses the public report-ready, source-accounting, native-artifact, and screenshot receipts. It reused the unchanged marker-bound `literal-A1` artifact without a second source search.

## Decision

Accept and prefer the ten-wildcard population block in all nine main Web of Science partitions. Use the current compound Boolean definitions for `BG1`, `BG2`, and `BC1`, and use `T_precise` directly in `BT2`. Use no proximity operator, pair expansion, or local pair filter.

This diagnostic does not authorize a final search. `PY` remains year-level. Final collection must apply the common exact cutoff rule to records in the cutoff year. PSR queries were outside this pilot and retain literal `P` and `X` blocks until separately piloted.

Offline checks are reproducible with:

```text
python3 SLR/SLR1/source-specific/web-of-science-core-collection/scripts/wos_pilot004/test_queries.py
python3 SLR/SLR1/source-specific/web-of-science-core-collection/scripts/wos_pilot004/build_plan.py --check
python3 SLR/SLR1/source-specific/web-of-science-core-collection/scripts/wos_pilot004/validate_pilot.py
```
