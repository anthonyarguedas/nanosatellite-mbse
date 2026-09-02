# Pilot 007

Required changes were applied in commit: 61efaed6dee07616a3ca33bf30078098878e5eb8

Export method: read-only execution with `~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py`, adapter v8, over the marker-bound Pilot 006 metadata ledger.

## Objective

Execute all nine current direct-query expressions over the complete Pilot 006 category-0 corpus. Verify the current compound Boolean translation and quantify the partition and stream sets without refreshing ESA or requesting attachment bodies.

## Runs

- [`schedule-plan.json`](searches/schedule-plan.json): fixed nine-event plan, exact expressions, controls, matcher identity, and source-corpus binding.
- Partition receipts: [`A1`](searches/A1.json), [`A2`](searches/A2.json), [`A3`](searches/A3.json), [`B1`](searches/B1.json), [`B2`](searches/B2.json), [`BG1`](searches/BG1.json), [`BG2`](searches/BG2.json), [`BC1`](searches/BC1.json), and [`BT2`](searches/BT2.json).
- [`run-receipt.json`](searches/run-receipt.json): artifact hashes, per-event completion, and the stable-ID schedule union.
- [`assessment.json`](searches/assessment.json): partition totals, intersections, stream sets, and the 24-record candidate ledger.
- [`validation-report.json`](searches/validation-report.json): independent corpus-gate, query, matcher, artifact, accounting, and prose checks.
- [Pilot 006 compact artifact](../006/searches/A1-r15.json), [full metadata ledger](../006/searches/.A1-r15.json.ESA_INDICO_METADATA_LEDGER.json), and [terminal marker](../006/searches/.A1-r15.json.ESA_INDICO_HARVEST_COMMIT.json): fixed source evidence.

## Result

- Change the source translation or schedule
- Document a source limitation

The shared ESA v8 gate revalidated the Pilot 006 transaction before execution. Its two root snapshots still contained the same ordered 440 events. All 440 event witnesses and 16,517 normalized metadata records reconciled. The local matcher file had the same SHA-256 digest recorded by the source artifact. The A1 expression exactly reproduced the Pilot 006 expression and its zero result.

All nine current expressions completed one bounded pass over every record. A1 returned 0, A2 returned 0, A3 returned 0, B1 returned 22, B2 returned 2, BG1 returned 0, BG2 returned 1, BC1 returned 2, and BT2 returned 0. The union contained 24 distinct metadata candidates from eight parent events. It comprised 12 Contributions and 12 Materials. No Event or Subcontribution matched. No partition exceeded the 100-record investigation threshold.

Stream A returned 0 records. Core Stream B returned 23, and expanded Stream B returned 3. Their intersection contained 2 records, so the complete Stream B union contained all 24 candidates. B1 and B2 shared one record. B1 and BC1 shared that same record. B2 and BC1 contained the same two records. BG2 contributed the one expanded-only record.

The current cross-source strategy uses ordinary phrases and compound `AND` and `OR` definitions. Pilot 007 therefore replaces the historical pair-expanded BG1, BG2, BC1, and BT2 translations with the current definitions. It uses no wildcard, proximity operator, or pair expansion. Source controls and matcher fields remain unchanged.

No source or attachment body request was made. The 24 records are unscreened metadata candidates. Date, language, report type, full-text access, eligibility, and contribution-to-attachment deduplication remain downstream tasks. Notes and Categories remain outside the complete route. The derivative receipts are pilot-only and cannot enter the merger as new source harvests. The final search was not executed.
