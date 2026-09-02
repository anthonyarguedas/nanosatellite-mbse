# Pilot 006: PSR population wildcards

**Status:** passed diagnostic. This is not a PSR final search.

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_web_of_science.py` version 2.

## Objective

Test the ten population wildcard atoms accepted by Pilot 004 in all four current prior-secondary-review partitions. In `PSR1`, `PSR2`, and `PSR4`, replace only the main `P` members nested inside `X`. In `PSR3`, replace `P`. Keep every additional `X` term and every other concept term literal.

## Method

The [event plan](searches/event-plan.json) fixed eight adjacent literal and wildcard events before source execution. Every event used:

- Web of Science Core Collection and all currently exposed editions
- `TS` Topic atoms
- `PY=(1900-2026)` as the current source-inception through upper-year control
- all languages
- Date: oldest first and native page size 50
- strict two-pass ordered WOS-ID and total reconciliation
- native RIS export for positive results
- no publication type, subject, access, full-text, or controlled-term restriction
- no proximity operator or pair expansion
- mandatory configured-search and first-results screenshots

The wildcard version replaces 22 explicit population literals with ten quoted trailing-`*` atoms. It shortens every PSR query by 255 characters. No retry was required.

## Results

| Partition | Literal total | Wildcard total | Complete set | Complete order |
|---|---:|---:|---|---|
| `PSR1` | 22 | 22 | equal | equal |
| `PSR2` | 60 | 60 | equal | equal |
| `PSR3` | 0 | 0 | equal | equal |
| `PSR4` | 27 | 27 | equal | equal |

Every wildcard partition retained every literal WOS ID. No wildcard-only ID occurred. The literal and wildcard unions each contain the same 102 WOS IDs in the same order.

Buruso et al. (`10.1002/sys.70051`) was retrieved as `WOS:001705529700001` by both versions of `PSR1` and `PSR2`. It was not inserted manually.

All eight events completed on their first attempt. The [assessment](searches/assessment.json) verifies 16 mandatory sibling screenshots and all source receipts.

## Decision

Accept and prefer the ten population wildcard atoms in all four Web of Science PSR partitions. Use the wildcard population rendering for `P` and for the `P` members nested in `X`. Keep every additional `X` term literal.

Pilot 005's broader 128-family map remains rejected. Pilot 006 does not authorize PSR final execution or change the source date limitation. Final PSR collection must apply the common exact cutoff to records from the cutoff year.

Offline checks are reproducible with:

```text
python3 SLR/SLR1/scripts/wos_pilot006/test_queries.py
python3 SLR/SLR1/scripts/wos_pilot006/validate_pilot.py
```
