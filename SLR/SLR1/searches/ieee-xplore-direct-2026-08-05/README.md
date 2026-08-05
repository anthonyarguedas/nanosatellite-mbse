# Controlled direct IEEE Xplore update — 2026-08-05

This directory is the reproducible direct-IEEE Xplore parity update for `SLR/SLR1`.

## Method

- Source: IEEE Xplore's direct metadata endpoint, through
  `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts/search_ieee_xplore.py`.
- Applied uniformly: publication years 2013–2026, English, journals and
  conferences.
- The Scopus-only `TITLE-ABS-KEY(...)` wrapper was removed; the contained
  Boolean concepts were sent in IEEE Xplore syntax.
- Each line has a count artifact and, where non-zero, a full JSON/CSV result
  artifact. A count-only zero is a valid IEEE result, not a failed search.
- Q3 and Q18 have identical concept logic, so one shared direct search was
  used and explicitly mapped to both IDs.
- Q12's original generic-space query returned 75 records and remains the
  direct parity/audit artifact. A population-constrained 11-record refinement
  was run in addition for focused protocol screening; it did not replace the
  broad result, and overlapping records were deduplicated.

## Q1–Q28 Scopus → IEEE parity matrix

All artifact names below end in `_2026-08-05`; `count` and `full` identify
count-only and screened retrieval artifacts. The same matrix is available for
programmatic use in `q1_q28_parity_matrix_2026-08-05.json`.

| Scopus ID | Direct IEEE artifact stem | IEEE total / retrieved | Result |
|---|---|---:|---|
| Q1 | `ieee_q01_eps_exact_count` | 0 / 0 | Valid zero-result direct parity check. |
| Q2 | `ieee_q02_verification_mbse_{count,full}` | 13 / 13 | Full retrieval screened. |
| Q3 | `ieee_q03_q18_mission_arch_design_{count,full}` | 35 / 35 | Shared with Q18; full retrieval screened. |
| Q4 | `ieee_q04_eps_power_{count,full}` | 10 / 10 | Full retrieval screened. |
| Q5 | `ieee_q05_reference_model_{count,full}` | 26 / 26 | Full retrieval screened. |
| Q6 | `ieee_q06_vv_traceability_{count,full}` | 23 / 23 | Full retrieval screened. |
| Q7 | `ieee_q07_outcomes_integration_{count,full}` | 17 / 17 | Full retrieval screened. |
| Q8 | `ieee_q08_vv_power_crosscut_{count,full}` | 15 / 15 | Full retrieval screened. |
| Q9 | `ieee_q09_exact_requirements_verification_title_count` | 0 / 0 | Valid zero; non-IEEE title not inferred absent elsewhere. |
| Q10 | `ieee_q10_exact_enterprise_modeling_title_{count,full}` | 1 / 1 | Existing core record matched by DOI. |
| Q11 | `ieee_q11_exact_budget_title_{count,full}` | 1 / 1 | Existing supporting record matched by DOI. |
| Q12 | `ieee_q12_requirements_verification_concept_{count,full}` | 75 / 75 | Broad audit line; population refinement below. |
| Q12 refinement | `ieee_q12_requirements_verification_concept_population_refined_{count,full}` | 11 / 11 | Screening refinement, not a replacement query ID. |
| Q13 | `ieee_q13_enterprise_modeling_concept_{count,full}` | 3 / 3 | Full retrieval screened. |
| Q14 | `ieee_q14_budget_concept_{count,full}` | 6 / 6 | Full retrieval screened. |
| Q15 | `ieee_q15_exact_rapid_model_based_title_count` | 0 / 0 | Valid zero for the non-IEEE title. |
| Q16 | `ieee_q16_exact_sparc1_title_{count,full}` | 1 / 1 | Existing rejected candidate matched by DOI. |
| Q17 | `ieee_q17_exact_floripasat2_title_{count,full}` | 1 / 1 | Existing rejected candidate matched by DOI. |
| Q18 | `ieee_q03_q18_mission_arch_design_{count,full}` | 35 / 35 | Same direct logic/results as Q3. |
| Q19 | `ieee_q19_eps_alt_terms_{count,full}` | 2 / 2 | Both records were existing matches. |
| Q20 | `ieee_q20_requirements_vv_traceability_{count,full}` | 14 / 14 | Full retrieval screened. |
| Q21 | `ieee_q21_capella_arcadia_cps_{count,full}` | 30 / 30 | Full retrieval screened. |
| Q22 | `ieee_q22_requirements_testing_count` | 0 / 0 | Valid zero result. |
| Q23 | `ieee_q23_capella_arcadia_exact_{count,full}` | 5 / 5 | Full retrieval screened. |
| Q24 | `ieee_q24_test_evaluation_{count,full}` | 13 / 13 | Full retrieval screened. |
| Q25 | `ieee_q25_exact_rvsat1_title_{count,full}` | 1 / 1 | Existing supporting record matched by DOI. |
| Q26 | `ieee_q26_exact_interim_status_5_title_count` and `_en_dash_count` | 0 / 0; 0 / 0 | Both punctuation variants validly returned zero; the citation-chasing promotion is preserved unchanged. |
| Q27 | `ieee_q27_exact_3colstar_title_count` | 0 / 0 | Valid zero for the MDPI title. |
| Q28 | `ieee_q28_exact_guo2014_title_count` | 0 / 0 | Valid zero for the IAC title. |

Q29–Q31 remain **Google Scholar-only citation-chasing items**. They are not
Scopus Q1–Q28 parity rows and were not recast as IEEE searches.

## Additional required direct checks

- Q32 CSRM title check: `ieee_q32_csrm_metamodel_title_{count,full}` → 1 / 1.
- Q32 CSRM DOI check: `ieee_q32_csrm_metamodel_doi_{count,full}` → 1 / 1.
  Both identify DOI `10.1109/AERO66936.2026.11519791`, already retained as
  `paper-0082`; no duplicate was created.
- Post-2026-04-24 update check:
  `ieee_update_2025_2026_post_2026-04-24_{count,full}` → 4 / 4. Three were
  already retained (budget-calculation, CSRM metamodel-quality, and
  standardized New Space functional modeling); the generic spacecraft SEAM
  record was screened out for population scope.

## Reconciliation outcome

`reconcile_direct_ieee_update.py` produces the machine-readable manifest and
screening/deduplication audit. Its controlled result is:

- 298 primary direct identifications; 133 unique records after internal
  DOI/normalized-title deduplication.
- 29 matched existing merged candidates; fresh direct provenance was appended
  without changing their identifiers or decisions.
- All 104 genuinely new direct records were excluded/not added under the
  unchanged protocol. Most were generic spacecraft/non-nanosatellite records,
  non-MBSE technology/process studies, or subsystem-only studies. The three
  CubeSat/OpenOrbiter requirements-engineering records were explicitly excluded
  as requirements elicitation/tool-support contributions outside the target
  system/EPS MBSE architecture and model-integrated IVV focus.
- No new merged candidate, corpus paper, tier change, override change, or
  citation-chasing decision was warranted. The candidate set remains 82 and
  the kept corpus remains 45 (23 core, 22 supporting).

## Supplemental retained-record metadata check

An exact DOI check for `10.1109/MAES.2017.180230` returned zero under the
journal/conference parity facets, then 1/1 when the content-type facet was
removed. IEEE classifies this user-retained record as a Magazine Article. The
saved all-content result supplies direct publisher metadata but is excluded
from Q1–Q28 parity counts.
