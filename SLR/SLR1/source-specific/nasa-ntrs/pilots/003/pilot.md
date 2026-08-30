# Pilot 003: complete literal schedule and canonical-ID unions

Required changes were applied in commit: NA. This is a diagnostic pilot only; it does not change the source guideline's completion state or create final searches.

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ntrs.py` through the shared browser wrapper.

## Objective

Run all nine direct schedule partitions with the exact inclusive publication-date window **2011-01-01 through 2026-08-29**, retain complete canonical NTRS citation-ID sets, and reconcile each semantic partition's union. All literals, declared pairs, and Boolean relations come from the shared [pilot schedule renderer](../../../../scripts/pilot_schedule/queries.py).

## Method

Each terminal cell used literal NTRS `q`, `--require-complete`, `Publication Date (Oldest)`, page size 100, and capacity for 10,000 records/100 pages. The adapter reconciled two exhaustive rendered canonical-ID passes. No wildcard, language, Type, access, collection, Source, distribution, center, subject, or controlled-term restriction was applied.

- [`plan.json`](searches/plan.json) records the complete unsplit schedule before execution.
- [`schedule-assessment.json`](searches/schedule-assessment.json) binds each terminal artifact hash, source total, canonical-ID union, cell proof, and null-total failure record.
- [`pair-checks.json`](searches/pair-checks.json) checks declared pairs in retained title/list-snippet fields without treating a missing visible match as a false source hit.

`BC1`'s 5,511-character full literal query failed twice before source query readback. It was replaced by four lossless `P AND C1` OR cells (largest 1,903 characters). `BT2`'s 14,027-character full literal query failed before readback. Its seven prospective `T2` cells were run; failed parents were replaced only by disjoint literal children. The ten terminal cells cover `T2` pair positions 1–224 exactly once and retain complete `P` and `M_B` blocks. These are prospective lossless execution cells, not narrowing filters or a claimed NTRS hard length limit.

## Results

| ID | Terminal cells | Successful source events | Deduplicated canonical-ID union |
|---|---:|---:|---:|
| A1 | 1 | 0 | 0 |
| A2 | 1 | 1 | 1 |
| A3 | 1 | 0 | 0 |
| B1 | 1 | 10 | 10 |
| B2 | 1 | 4 | 4 |
| BG1 | 1 | 0 | 0 |
| BG2 | 1 (retry 1) | 4 | 4 |
| BC1 | 4 | 0 | 0 |
| BT2 | 10 | 0 | 0 |

The schedule produced 19 successful source events and a **15-ID** cross-partition canonical union. No partition union exceeded 10 IDs, so the 100-record investigation threshold did not trigger. No metadata, controlled-vocabulary, language, eligible-type, access, or other narrowing refinement was attempted.

The retained-field pair check found four `BG2` snippet hits: both `product-line/model` spelling variants for citations `20180001888` and `20180001738`, each with one intervening lexical token. This is only a local confirmation of retained visible text. NTRS general `q` also searches document full text. Two exact `BG2 --full-abstracts` diagnostic attempts failed before usable complete results, so full-text uncertainty remains explicit and every related failure total is `null`, not zero.

## Limitations

- NTRS exposes no usable Language control. English remains a full-text screening decision.
- Its one-value Type control is not a proved lossless eligible-type union, so no type filter was used.
- NTRS exposes no proved NASA Thesaurus term/explosion route. No descriptor supplement was applied.
- The preserved pre-readback errors do not establish source zeros or a fixed query-length ceiling. The successful literal cell unions are pilot evidence only.
- These pilot records stay under `pilots/003`; they are not final-search events or a final corpus.

## Checks

Run the shared query tests and the [Pilot 003 validator](../../../../scripts/ntrs_pilot003/validate_pilot.py):

```bash
python3 SLR/SLR1/scripts/pilot_schedule/test_queries.py
python3 SLR/SLR1/scripts/ntrs_pilot003/validate_pilot.py
```

The validator parses all JSON, validates exact dates/controls/query construction, verifies the NTRS commit markers and hashes, confirms null failure totals, confirms complete terminal ID sets and cell unions, checks all 224 `BT2` pair positions, and replays the retained-field pair check.
