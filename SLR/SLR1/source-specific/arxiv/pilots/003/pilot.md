# Pilot 003: Atom API lossless cell route

Required changes were applied in commit: NA

## Objective

Test a practical source-native route for all nine direct partitions without changing the protocol concepts. The diagnostic window was 2011-01-01 through 2026-08-29. This is a pilot, not a final search.

## Route and validation

The rendered Advanced Search Cartesian plan would require many cells. Pilot 003 instead tested the documented Atom API with [`atom_pilot.py`](../../../../scripts/arxiv_pilot003/atom_pilot.py). It used parenthesized `all:` expressions, `submittedDate:[201101010000 TO 202608292359]`, and ascending `submittedDate` order. The API User's Manual and live controls were separately checked for fields, grouping, phrases, dates, ordering, pagination, stable IDs, and the broader pair fallback:

- [`transport-validation.json`](searches/transport-validation.json): all seven controls passed. Its Atom Boolean observation is explicitly separate from browser Advanced Search semantics.
- [`pagination-capture.json`](searches/pagination-capture.json): two 25-record-page traversals of the bounded 2024 `CubeSat` control reconciled 72 source records, total, order, bare IDs, and versioned IDs.
- Declared `reusable`/`model` fallback control retained `1102.2933`; its abstract had the pair in order with two intervening lexical tokens. This validates a no-loss broader candidate fallback, not API proximity.

Full Atom expressions for `A2`, `BC1`, and `BT2` failed before a source total because the live request line was too long. The preserved failures are [`A2-full.NON_MERGEABLE_FAILURE.json`](searches/A2-full.NON_MERGEABLE_FAILURE.json) (HTTP 400), [`BC1-full.NON_MERGEABLE_FAILURE.json`](searches/BC1-full.NON_MERGEABLE_FAILURE.json) (HTTP 400), and [`BT2-full.NON_MERGEABLE_FAILURE.json`](searches/BT2-full.NON_MERGEABLE_FAILURE.json) (HTTP 414). Each has `total: null`, not zero.

The repaired union split only one parenthesized OR factor at a time: `A2` into `M_H`/`M_B`, `BC1`'s 62 alternatives into two 31-alternative cells, and `BT2`'s 224 pairs into six disjoint 38/34-pair cells. Every replacement URI was at most 3,791 encoded characters. The runner imports the exact concepts and pairs from `pilot_schedule`; its offline checks prove no literal, pair, wildcard, or Boolean factor was changed.

## Complete partition unions

Every retained source cell was exhausted twice. The [union receipt](searches/partition-unions.json) deduplicates on bare arXiv ID while retaining returned versioned manifestations and source-cell membership.

| ID | Complete cells | Source events | Deduplicated arXiv-ID union |
|---|---:|---:|---:|
| [A1](searches/A1.json) | 1 | 0 | 0 |
| [A2](searches/A2.json) | 2 | 0 | 0 |
| [A3](searches/A3.json) | 1 | 0 | 0 |
| [B1](searches/B1.json) | 1 | 6 | 6 |
| [B2](searches/B2.json) | 1 | 4 | 4 |
| [BG1](searches/BG1.json) | 1 | 8 | 8 |
| [BG2](searches/BG2.json) | 1 | 1 | 1 |
| [BC1](searches/BC1.json) | 2 | 0 | 0 |
| [BT2](searches/BT2.json) | 6 | 1 | 1 |

No deduplicated partition union exceeded 100 records, so the required [threshold investigation](searches/threshold-investigation.json) was not triggered. No precision filter was added. The exact Boolean expression, bounded date clause, and lossless cell unions were the only controls; language, type, category, proximity, local visible-metadata checks, and wildcard compression could not be shown no-loss.

The one `BT2` candidate (`2507.22198`) had no locally verifiable declared pair in its retained title/abstract. It remains in the broad fallback candidate union rather than being silently discarded. This is a source-field/proximity limitation, not a match or screening decision.

## Result

- Change the source translation or schedule
- Document a source limitation

The prospective source translation is the documented Atom API route and its lossless cell plan in the [source guideline](../../source-specific-guidelines.md). It produced complete, low-volume diagnostic candidate unions for all nine partitions. No wildcard, language, type, category, access, peer-review, proximity, controlled-vocabulary, or API-side export filter was used. All artifacts are non-mergeable pilot evidence; no final search or screening decision was made.
