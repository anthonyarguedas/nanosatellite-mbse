# Pilot 004: controlled vocabulary value test

Pilot 004 is a diagnostic pilot. It is not a final search and all artifacts are non-mergeable. The set comparison uses the labelled 2011-01-01 through 2026-08-29 diagnostic window.

## Objective

Harvest the indexing terms assigned to seven user-selected Pilot 003 records. Validate candidate labels against the ProQuest Technology Thesaurus. Test whether an exact controlled vocabulary supplement adds stable ATAI records beyond the literal `B1` translation.

The selected records are relevant known items for this vocabulary test only. This selection is not a final review screening decision.

## Assigned terms

The active [two-pass assignment harvest](searches/assigned-indexing-terms-retry2.json) read the canonical ATAI detail page for each selected stable ID twice. Every page proved the exact ATAI product and exposed one `SUBJECT` indexing group. The two passes returned identical ordered assignments.

| Former reading-aid entry | ATAI ID | Assigned `SUBJECT` terms |
|---|---:|---:|
| 02 | `3371247439` | 11 |
| 03 | `3062738113` | 10 |
| 07 | `2035264195` | 7 |
| 11 | `1825532815` | 8 |
| 14 | `3110716244` | 11 |
| 18 | `3181339955` | 25 |
| 37 | `1709719593` | 8 |

The records supplied 58 distinct assigned terms. `Model-based systems` and `Systems engineering` each appeared on six records. `Cubesat` appeared on three. `Small satellites`, `Modelling`, `Mathematical models`, `Satellite design`, and several general engineering terms appeared on two.

The first harvest attempt retained a [capitalization-parser failure](searches/assigned-indexing-terms.NON_MERGEABLE_FAILURE.json). Retry 1 retained a [multiple-indexing-group parser failure](searches/assigned-indexing-terms-retry1.NON_MERGEABLE_FAILURE.json). Both were local parser failures. Retry 2 accepts `Subject` case-insensitively and separates `SUBJECT` from `COMPANY/ORGANIZATION`.

## Technology Thesaurus validation

The [candidate validation](searches/technology-thesaurus-candidates.json) tested six assigned labels twice through the live Technology Thesaurus selection surface:

- Population candidates: `Cubesat`, `Nanosatellites`, and `Small satellites`.
- MBSE candidates: `Model-based systems`, `Systems engineering`, and `Modelling`.

All six were exact selectable descriptors. Each read back as `MAINSUBJECT.EXACT("...")` in both passes. The source exposed no stable term ID, vocabulary release, hierarchy export, or explosion state.

The three population labels duplicate existing population literals modulo case. The protocol does not allow generic `Systems engineering` to satisfy `M_H` alone. The tested MBSE supplement therefore used:

```text
MAINSUBJECT.EXACT("Systems engineering")
AND
(
  MAINSUBJECT.EXACT("Model-based systems")
  OR MAINSUBJECT.EXACT("Modelling")
)
```

Every descriptor supplement was joined to its corresponding free-text block with `OR`.

## Stable-ID value comparison

The first set-comparison event retained a [restore-session-overlay failure](searches/set-comparison.NON_MERGEABLE_FAILURE.json) before any cell completed. Retry 1 dismissed that exact blocking prompt on the owned page and retained six successful source artifacts under [`set-passes-retry1/`](searches/set-passes-retry1/). [Pilot 005](../005/pilot.md) moves this handling and the current verified-cleanup contract into adapter v4. The local runner no longer monkeypatches either behavior.

The active [set reconciliation](searches/set-comparison-retry1.json) used two ordinary complete traversals per cell. Each cell had equal source totals and identical ordered stable IDs across its two passes. These same-query stable-ID pairs do not replace the adapter's strict full-record-signature contract.

| Cell | Stable IDs | Result |
|---|---:|---|
| Seven known IDs × candidate MBSE descriptors | 5 | Two selected records lacked the complete descriptor construction |
| Fresh literal `B1` | 19 | Retrieved all seven selected records |
| Fresh augmented `B1` | 19 | Same ordered IDs as literal `B1` |

Literal and augmented `B1` shared ordered-ID SHA-256 `7cc40c0121f6bbf1d4d6e6bd8d83860a3b25c989c126bdc1f745cbfb6693b275`. The augmentation produced zero candidate-only IDs.

## Decision

The [inclusion assessment](searches/inclusion-assessment.json) records `do_not_add_controlled_vocabulary_supplement`.

- The descriptors have bounded source mapping and assignment evidence.
- The population descriptors repeat existing literals.
- The context-qualified MBSE descriptors added no stable ID. `B1` is the broad `P × M_H` partition, so the same M_H supplement cannot add an ID to narrower `A1` or the M_H arm of `A2` under these controls.
- Literal `B1` retrieved all seven selected records. The controlled MBSE construction matched only five.
- Controlled terms cannot replace free text, and the tested `OR` supplement showed no marginal recall value.

Retain the literal `NOFT` schedule with no Technology Thesaurus supplement. This decision applies to the descriptors and B1 construction tested here. It does not prove that every possible future descriptor lacks value.

## Reproduction

```bash
caffeinate -dims python3 "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/scripts/atai_pilot004/harvest_assigned_terms.py \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/assigned-indexing-terms-retry2.json \
  --failure-output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/assigned-indexing-terms-retry2.NON_MERGEABLE_FAILURE.json

caffeinate -dims python3 "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/scripts/atai_pilot004/validate_thesaurus_candidates.py \
  --harvest SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/assigned-indexing-terms-retry2.json \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/technology-thesaurus-candidates.json \
  --failure-output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/technology-thesaurus-candidates.NON_MERGEABLE_FAILURE.json

caffeinate -dims python3 "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/scripts/atai_pilot004/run_set_comparisons.py \
  --event-plan SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/003/searches/event-plan.json \
  --candidate-receipt SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/technology-thesaurus-candidates.json \
  --output-dir SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/set-passes-retry1 \
  --reconciliation SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/set-comparison-retry1.json \
  --failure-output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/set-comparison-retry1.NON_MERGEABLE_FAILURE.json

python3 SLR/SLR1/scripts/atai_pilot004/build_assessment.py \
  --harvest SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/assigned-indexing-terms-retry2.json \
  --candidates SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/technology-thesaurus-candidates.json \
  --comparison SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/set-comparison-retry1.json \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/inclusion-assessment.json

python3 SLR/SLR1/scripts/atai_pilot004/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004 \
  --guideline SLR/SLR1/source-specific/advanced-technologies-aerospace-index/source-specific-guidelines.md \
  --reading-aid SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/003/controlled-vocabulary-seed-candidates.md \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/004/searches/validation-report.json
```
