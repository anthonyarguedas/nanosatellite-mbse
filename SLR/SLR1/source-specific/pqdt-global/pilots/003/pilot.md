# Pilot 003

Required changes were applied in commit: this pilot commit. This remains a pilot. It does not set a final-search or source-completion state.

Export method: `~/agent-tools/internet/skills/browser/scripts/search_pqdt.py`

## Objective

Run the complete nine-partition literal PQDT Global schedule as a pilot-only, two-pass canonical document-ID diagnostic.

## Method

The [standard event plan](searches/event-plan.json) uses the shared [pilot schedule helper](../../../../scripts/pilot_schedule/queries.py). Every literal, Boolean relation, and declared unordered `NEAR/5` pair is retained as a `NOFT` atom. No wildcard or controlled term was used. The full expressions are 1,494–10,923 characters, below the adapter's documented 50,000-character limit, so each partition has one lossless full-expression cell.

Every event used `YR(2011-2026)`, `LA(English)`, frozen spelling/form/display variants and duplicate exclusion off, Full text off, and `DateAsc`/Oldest first. The adapter selected the PQDT Global scope alone and restored the prior ProQuest selection on each owned-tab event. Compact marker-bound artifacts retain the source-scope readback `PQDT Global` rather than pre/post checkbox labels. The 2026-08-29 date is a diagnostic screening cutoff only: PQDT's `YR` control is year precision. No degree, completion, document-type, access, or full-text filter was applied. English report language and degree/completion status remain screening decisions.

Each source artifact is a marker-bound strict run: the adapter completed two full rendered passes with reconciled ordered numeric PQDT document IDs, and every cell stayed at or below the fixed 10,000-result complete boundary.

## Runs and unions

| ID | Cell | Source total / ID union |
|---|---|---:|
| A1 | [A1](searches/A1.json) | 1 / 1 |
| A2 | [A2](searches/A2.json) | 3 / 3 |
| A3 | [A3](searches/A3.json) | 1 / 1 |
| B1 | [B1](searches/B1.json) | 21 / 21 |
| B2 | [B2](searches/B2.json) | 13 / 13 |
| BG1 | [BG1](searches/BG1.json) | 1 / 1 |
| BG2 | [BG2](searches/BG2.json) | 3 / 3 |
| BC1 | [BC1](searches/BC1.json) | 3 / 3 |
| BT2 | [BT2](searches/BT2.json) | 2 / 2 |

The [execution ledger](searches/event-execution-ledger.json) and [stable-ID union reconciliation](searches/stable-id-union-reconciliation.json) retain all cell IDs and source order. There were 48 source occurrences and 29 deduplicated PQDT document IDs: Stream A 4, core Stream B 27, expanded Stream B 7. No strict failure occurred.

## Volume check and limitations

No partition, stream, or all-schedule union exceeded 100 records. The [noise investigation](searches/noise-investigation.json) therefore applied no refinement. It explicitly retains the reasons not to use degree/completion/type/full-text/access filters or unvalidated PQ subject/index-term restrictions.

The 10,000-result boundary remains hard. A later strict failure must retain a null total, not be treated as zero or replaced by an unrecorded narrower query. These artifacts are non-final pilots and are not inputs to a final-search merge.

## Checks

- [Source documentation verification](searches/source-documentation-verification.json)
- [JSON, standard-plan, exact-membership, controls, union, and diff validation](searches/validation-report.json)
- Reproducible runners: [schedule](../../scripts/pqdt_pilot003/run_schedule.py), [assessment](../../scripts/pqdt_pilot003/build_assessment.py), and [validator](../../scripts/pqdt_pilot003/validate_pilot.py)
