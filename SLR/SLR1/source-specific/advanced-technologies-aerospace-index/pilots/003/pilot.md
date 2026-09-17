# Pilot 003

Commit reference: this pilot commit (no completion status is changed).

Export method: `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

## Objective

Run the complete nine-partition ATAI schedule as a **pilot-only** stable-ID diagnostic. `P-001` is unset. The inclusive 2011-01-01 through 2026-08-29 Publication-date window is only a labelled diagnostic window, not the review cutoff or a final search.

## Method

The [predeclared event plan](searches/event-plan.json) uses the shared [pilot schedule helper](../../../../scripts/pilot_schedule/queries.py). Every literal, declared pair, parenthesis, and Boolean relation is retained as an ATAI `NOFT` atom. Pairs are unordered `NEAR/5`. The nine full expressions are 1,494–10,923 characters, below the adapter's validated 50,000-character limit, so no query cell was split and no wildcard was used.

Every run requested ATAI alone, `LA(English)`, the endpoint-inclusive Publication-date range, no type/peer-review/full-text/access filter, frozen spelling/form/display variants, and `DateAsc`/Oldest first. The source receipts record Full text and Access as unavailable. The English field is metadata only. Full-text screening remains authoritative.

`A1` and `A2` passed the adapter's strict two-full-record-pass contract. The same strict contract returned null-total full-record-signature failures for `A3` and `B1`. Both failures are retained. The same literal query and controls were then traversed twice with `limit=10000` and `max-pages=500`. Each pair had a matching source total, every rendered row, canonical numeric ATAI ID, and identical ordered ID list. The observed strict-signature instability motivated the same two-pass stable-ID route for `B2`, `BG1`, `BG2`, `BC1`, and `BT2`. This is a capture repair, not a query refinement or final-search acceptance.

## Runs and unions

| ID | Active complete-ID artifact | Source total / partition ID union | Capture note |
|---|---|---:|---|
| A1 | [A1](searches/A1.json) | 0 / 0 | Strict two-pass |
| A2 | [A2](searches/A2.json) | 5 / 5 | Strict two-pass |
| A3 | [pass 2](searches/A3-repaired-pass2.json) | 1 / 1 | [strict failure](searches/A3.strict-complete.NON_MERGEABLE_FAILURE.json) and [ID repair](searches/A3-repair-reconciliation.json) |
| B1 | [pass 2](searches/B1-stable-id-pass2.json) | 19 / 19 | [strict failure](searches/B1.strict-complete.NON_MERGEABLE_FAILURE.json) and [ID pair](searches/B1-stable-id-reconciliation.json) |
| B2 | [pass 2](searches/B2-stable-id-pass2.json) | 28 / 28 | [ID pair](searches/B2-stable-id-reconciliation.json) |
| BG1 | [pass 2](searches/BG1-stable-id-pass2.json) | 2 / 2 | [ID pair](searches/BG1-stable-id-reconciliation.json) |
| BG2 | [pass 2](searches/BG2-stable-id-pass2.json) | 7 / 7 | [ID pair](searches/BG2-stable-id-reconciliation.json) |
| BC1 | [pass 2](searches/BC1-stable-id-pass2.json) | 1 / 1 | [ID pair](searches/BC1-stable-id-reconciliation.json) |
| BT2 | [pass 2](searches/BT2-stable-id-pass2.json) | 2 / 2 | [ID pair](searches/BT2-stable-id-reconciliation.json) |

The [stable-ID union reconciliation](searches/stable-id-union-reconciliation.json) retains every ID in source order for every active cell and every partition union. It reports 65 source record occurrences and 49 deduplicated ATAI document IDs: Stream A 5, core Stream B 41, expanded Stream B 11. Stream-only/intersection counts remain in that artifact. No partition, stream, or all-schedule deduplicated union exceeded 100.

## Noise, refinements, and limitations

The [noise investigation](searches/noise-investigation.json) records that the threshold was not reached, so no threshold-triggered metadata sample was required. No source refinement was applied: ATAI does not prove a lossless eligible-type or result-facet union, no protocol-block Technology Thesaurus supplement was validated, and Full text/Access cannot be emulated. The literal schedule therefore remains unchanged.

These artifacts are non-mergeable pilots. They do not finalize a translation, controlled-vocabulary supplement, type control, noise filter, source coverage, or evidence window. The 10,000-record source cap remains a hard limitation. The retained `A3` and `B1` null-total strict failures mean later final work must resolve or explicitly handle full-record-signature stability rather than treating this pilot's stable-ID repair as final validation.

## Checks

- [Shared query membership, source controls, JSON, receipt, stable-ID union, and threshold checks](searches/validation-report.json)
- [Offline ATAI source-documentation verification](searches/source-documentation-verification.json)
- Reproducible runners: [strict schedule](../../scripts/atai_pilot003/run_schedule.py), [A3 repair](../../scripts/atai_pilot003/repair_a3_stable_ids.py), and [stable-ID pair route](../../scripts/atai_pilot003/run_stable_id_pair.py)
