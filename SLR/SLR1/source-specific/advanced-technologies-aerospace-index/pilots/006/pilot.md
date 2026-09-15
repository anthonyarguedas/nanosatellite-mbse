# Pilot 006: field, pair, indexed-term, and language validation

Pilot 006 is diagnostic. It is not a final search. It uses the labelled 2011-01-01 through 2026-08-29 pilot window unless a known-item contrast explicitly states All dates. All source artifacts are non-mergeable.

## Objective

Resolve two remaining ATAI translation questions:

1. Determine which protocol-relevant metadata fields `NOFT` covers and whether `NOFT NEAR/5` retains source-located pair positives without joining separate fields.
2. Determine whether `LA(English)` removes any source record that the final prospective translation should retain.

The [assessment](searches/assessment.json) records the resulting source decisions.

## `NOFT` field coverage

The initial [event plan](searches/event-plan.json) declared paired explicit-field and `NOFT` known-item checks.

| Known-item field | Explicit result | `NOFT` result | Finding |
|---|---:|---:|---|
| `TI` title | 1 | 1 | Same ATAI ID `3371247439` |
| `AB` abstract | 1 | 1 | Same ATAI ID `3097792411` |
| `MAINSUBJECT` | 1 | 1 | Same ATAI ID `3181339955` |
| `IF` indexed keyword | 1 | 0 | `NOFT` omitted ATAI ID `2438984228` |

The first `IF` cells both returned zero because the known item fell outside the diagnostic date window. A no-date strict retry then encountered a source row without the adapter's required Abstract/Details link. Both outcomes remain preserved under [`cells/`](searches/cells/) and [`retry1/`](searches/retry1/). Retry 2 used two exact AN-bounded count passes. `IF.EXACT("Aerospace engineering")` returned `1` twice and `NOFT("Aerospace engineering")` returned `0` twice.

`NOFT` therefore covers the bounded title, abstract, and controlled-subject examples, while it does not cover every exact `IF` assignment.

## Pair gate

Two records had the declared `adapted` and `model` pair in their retained abstracts:

| ATAI ID | Minimum intervening words | `AB NEAR/5` | `NOFT NEAR/5` |
|---|---:|---:|---:|
| `1825532815` | 3 | retrieved | retrieved |
| `2728408177` | 4 | retrieved | retrieved |

The cross-field control used `BOREALIS` from the title or abstract and assigned subject `Moon` on ATAI ID `3181339955`. `NOFT("BOREALIS" NEAR/5 "Moon")` returned zero. The bounded gate retained every source-located abstract positive and did not join the separate captured fields.

Keep unordered `NOFT NEAR/5` for every declared pair. Do not emulate lexical distance in `IF`.

## Exact `IF` supplement

Retry 3 compared every literal partition with a no-loss indexed-keyword augmentation twice. Every ordinary literal atom became:

```text
(NOFT("literal") OR IF.EXACT("literal"))
```

Declared `NEAR/5` pair atoms remained unchanged. Every augmented expression was below the validated 50,000-character limit.

| Partition | Literal | `NOFT OR IF.EXACT` | Delta |
|---|---:|---:|---:|
| A1 | 0 | 0 | 0 |
| A2 | 5 | 5 | 0 |
| A3 | 1 | 1 | 0 |
| B1 | 19 | 25 | +6 |
| B2 | 29 | 34 | +5 |
| BG1 | 2 | 2 | 0 |
| BG2 | 7 | 7 | 0 |
| BC1 | 1 | 2 | +1 |
| BT2 | 2 | 3 | +1 |

Both count passes were identical. The [two-pass card-ID reconciliation](searches/if-stable-id-reconciliation.json) retained nine candidate-only IDs. None appeared in Pilot 003's 49-ID literal union. The [two-pass detail harvest](searches/candidate-detail-harvest.json) found six plausible review candidates and three likely search-noise records. These method labels are not final screening decisions.

Plausible additions include:

- *Intersatellite Communication: An MBSE Operational Concept for a Multiorbit Disaggregated System*
- *Preliminary Design of Satellite Systems through the Integration of Model-Based System Engineering and Agile Methodologies: Application to the 3ColStar Mission*
- *Micro-Satellite Systems Design, Integration, and Flight*
- *The Spacecraft Early Analysis Model: An MBSE Framework for Early Analysis of Spacecraft Behavior*
- *Hierarchical Planning Applied to the Preliminary Design of CubeSats: Nanospace Study*
- *Towards a Unified Modeling and Simulation Framework for Space Systems: Integrating Model-Based Systems Engineering with Open Source Multi-Domain Simulation Environments*

Accept the `IF.EXACT` OR supplement for every ordinary literal. Screening will resolve all nine added records.

## Language audit

The first complete literal-schedule union full-record run retained a detail-readiness failure in [`language-schedule-union-unfiltered.json`](searches/cells/language-schedule-union-unfiltered.json). Retry 2 replaced it with two repeated exact source-total comparisons:

- Unfiltered union: `52` and `52`
- `LA(English)` union: `50` and `50`
- Union `NOT LA(English)`: `2` and `2`

The [two-pass excluded-ID capture](searches/language-exclusion-id-reconciliation.json) identified ATAI IDs `896198854` and `2621176457`.

The accepted `IF` supplement changed the prospective translation, so Retry 7 repeated unfiltered and English counts for every augmented partition. Only B2 differed:

| Partition | Unfiltered | `LA(English)` | Excluded |
|---|---:|---:|---:|
| A1 | 0 | 0 | 0 |
| A2 | 5 | 5 | 0 |
| A3 | 1 | 1 | 0 |
| B1 | 25 | 25 | 0 |
| B2 | 36 | 34 | 2 |
| BG1 | 2 | 2 | 0 |
| BG2 | 7 | 7 | 0 |
| BC1 | 2 | 2 | 0 |
| BT2 | 3 | 3 | 0 |

Both passes were identical. The [final excluded-ID reconciliation](searches/final-language-exclusion-id-reconciliation.json) returned the same two records. Their source detail pages state `Language of publication: Chinese`:

- `896198854`, *Star-sensor-based attitude estimation fusing improved particle filter and predictive filter*. Its summary languages are `Chinese; English`.
- `2621176457`, *Bureau of Quality Solid Propulsion Design for That Surname Adaptive Breeding Control Law*.

Retain `LA(English)`. English titles or abstracts do not make these source-labelled Chinese publications English reports. Source metadata remains a bounded search control. Full-text screening remains authoritative for retrieved candidates.

## Decisions

- Use `(NOFT(L(s)) OR IF.EXACT(L(s)))` for every ordinary literal.
- Keep `LA(English)`.
- Keep all existing no-type, no-peer-review, no-access, and no-full-text filter decisions.

The pair decision applied to the earlier cross-source schedule. Commit `3194156e90497186664260a8e86435e78d2e2aa1` removed every declared pair. [Pilot 007](../007/pilot.md) supersedes that translation decision while retaining this pilot's field, indexed-term, language, and filter evidence.

## Retained failures and repair path

The [initial run receipt](searches/run-receipt.json) preserves the full-union detail failure after eleven successful field and pair cells. [Retry 1](searches/run-receipt-retry1.json) preserves the non-exportable indexed-keyword row failure. [Retry 2](searches/run-receipt-retry2.json) completed the repeated index and literal-language totals. [Retry 3](searches/run-receipt-retry3.json) completed all indexed-keyword count comparisons. Retry 4 reconciled affected stable IDs. Retry 5 captured the first language-excluded IDs. Retry 6 harvested candidate details. [Retry 7](searches/run-receipt-retry7.json) completed the final per-partition language comparisons. Retry 8 confirmed the same final excluded IDs.

The [validation report](searches/validation-report.json) checks every active decision and preserved failure.

## Reproduction

Review-specific scripts are under [`SLR/SLR1/source-specific/advanced-technologies-aerospace-index/scripts/atai_pilot006`](../../scripts/atai_pilot006). Run live scripts through the shared browser launcher. The offline decision and validation commands are:

```bash
python3 SLR/SLR1/source-specific/advanced-technologies-aerospace-index/scripts/atai_pilot006/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/006 \
  --if-reconciliation SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/006/searches/if-stable-id-reconciliation.json \
  --detail-harvest SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/006/searches/candidate-detail-harvest.json \
  --pilot003-union SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/003/searches/stable-id-union-reconciliation.json \
  --final-language-exclusions SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/006/searches/final-language-exclusion-id-reconciliation.json \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/006/searches/assessment.json

python3 SLR/SLR1/source-specific/advanced-technologies-aerospace-index/scripts/atai_pilot006/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/006 \
  --guideline SLR/SLR1/source-specific/advanced-technologies-aerospace-index/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/006/searches/validation-report.json
```
