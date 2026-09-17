# Pilot 004: literal schedule and native-year control

Export method: the fixed read-only `search_ieee_xplore.py` adapter, exercised through the local shared browser. Pilot-local runners under [`../../scripts/ieee_xplore_pilot004/`](../../scripts/ieee_xplore_pilot004/) only preserve adapter-generated normal rendered URLs with percent-encoded components when IEEE rejected the equivalent form-style route. They do not change a query, field, pair, Boolean relation, filter, or use an API.

## Objective

Run all nine direct partitions with the `pilot_schedule` IEEE renderer, every literal and declared unordered pair, and the native inclusive Publication Year `2011`–`2026` Apply control. Preserve failed controls as `total: null`. Make no final search or unbounded/local-date substitute.

## Controls and boundaries

- **Requested search window:** native Publication Year `2011_2026_Year`, inclusive. The diagnostic evidence cutoff is **2026-08-29**. It is recorded separately because this pilot used the source's year-precision control, not an invented native day filter.
- **Result-page interval:** a sidebar interval is a possible *further refinement*, not a replacement for the requested window. For example, [`A1-full.json`](searches/preflight/A1-full.json) records requested `2011_2026_Year` and the contained result-refinement interval `2013_2024_Year`. The local two-pass receipts retain both surfaces.
- **Date Added:** not applied. It remains a distinct indexing-date control and is never used as Date of Publication.
- **No language, type, access, peer-review, or full-text filter** was applied. Language and a lossless eligible-report type union remain unavailable. Access remains All Results.
- **No controlled-vocabulary supplement** was applied: no descriptor mapping was validated for these normative blocks.
- **No wildcard** was used or accepted. Any future comparison is partition-specific and must compare stable Article Numbers under identical controls.

The linked [`year-boundary-receipt.json`](searches/year-boundary-receipt.json) is the concise boundary check. Its strict known-item artifact requests `[2022,2023]`, retains `10398967` (2022) and `10436175` (2023), and excludes `9438156` (2021). The literal `]min,max[` form was not reproduced and remains fixture-only.

## Schedule, cells, and outcomes

[`schedule.json`](searches/schedule.json) is generated from `pilot_schedule/queries.py`. It keeps every literal atom and native `NEAR/6` pair. Expressions over the conservative 5,000-character pilot ceiling are a lossless Cartesian union of source cells. The ceiling is not claimed as an IEEE maximum. Stable identity is the numeric IEEE Article Number.

[`union-receipt.json`](searches/union-receipt.json) is authoritative for cell coverage, source events, stable-ID unions, and nulls. A complete union exists only when every required cell has two reconciled, fresh native-Year-Apply captures.

| Partition | Outcome | Deduplicated stable Article Number union |
|---|---|---:|
| A1 | complete | 5 (`6496894`, `7500564`, `9172748`, `10131054`, `10516429`) |
| A2 | all three cells failed the native control/readback | `null` |
| A3 | complete | 6 (`6496894`, `6836209`, `9172748`, `10516429`, `11436987`, `11513211`) |
| B1 | native control/readback failure | `null` |
| B2 | native count was 131, stable full capture failed closed | `null` |
| BG1 | complete | 1 (`6161179`) |
| BG2 | native control/readback failure | `null` |
| BC1 | one of two cells failed, two IDs are only a partial capture | `null` |
| BT2 | cells 0002 and 0008 failed, 15 IDs are only a partial capture | `null` |

The two-pass pass artifacts are retained in `searches/two-pass-*`. Each successful pair has a linked `*-two-pass-receipt.json`. Cards, rather than full abstracts, supply the stable Article Numbers. The adapter's built-in strict A1 attempt is separately preserved in `searches/strict/A1-full.json`: it failed only because the first native Apply exposed a contained refinement interval and its verification route exposed the requested token. The fresh two-pass receipt does not collapse those representations and reconciles the same ordered IDs.

## Over-100 investigation

[`over-100-investigation.json`](searches/over-100-investigation.json) links the B2 native-Year count of 131 and the failed stable-ID capture. IEEE omitted page-size evidence outside a complete small page. A subsequent explicit normal result route was inconsistent. No first-100 prefix, local date filtering, or count-only total was promoted to a deduplicated union. B2 therefore remains `null` and is not mergeable.

## Limitations and stop boundary

- Source failures are retained as source artifacts with `total: null`. They are not zeros.
- The fixed adapter was not edited. The pilot-local percent-component transport was used only after the decoded rendered query echo was observed. Its use and the strict-readback representation limitation are recorded in each successful pass artifact.
- The incomplete partitions do not authorize a narrower query, a wildcard, a local date filter, a language/type/access restriction, or a final search.
- This is a pilot-only diagnostic. Nothing here belongs in `final-searches/`, and IEEE Xplore remains unresolved for the review baseline.

## Validation

Run from the repository root:

```bash
python3 source-specific/ieee-xplore/scripts/ieee_xplore_pilot004/build_schedule.py --validate
python3 source-specific/ieee-xplore/scripts/ieee_xplore_pilot004/build_receipts.py --write
python3 source-specific/ieee-xplore/scripts/ieee_xplore_pilot004/validate_pilot.py
```
