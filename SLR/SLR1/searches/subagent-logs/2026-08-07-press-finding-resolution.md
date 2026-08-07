# Resolution of model-assisted PRESS findings

**Review run:** `eps-mbse-slr-2026`<br>
**Resolution date:** 2026-08-07 EDT<br>
**Boundary:** pre-freeze implementation and `pilot_not_candidate_search` validation only; no valid discovery search, screening, candidate retention, or evidence use occurred.<br>
**Human information-specialist review:** none.

## Major findings

| Finding | Resolution | Validation |
|---|---|---|
| **MAJOR-01** population omissions | Added bare IEEE `nanosat`; added spaced plural `"nano satellites"` to every Boolean translation and deterministic dictionary; replaced NTRS P with six separate forms. | All corrected API/browser strings accepted; matched plural comparisons logged; all 36 cells for the two added NTRS P forms were included in the complete 108-cell pilot. |
| **MAJOR-02** structured-model/relation variants | Added `systems modeling`, `system modelling`, all four modeling/modelling phrases, and `object-oriented systems model` to every A2/B2 broad block. IEEE B2 now uses all explicit singular/plural US/UK relation forms; Wiley B2 uses validated wildcards. | Corrected A2/B2 count pilots completed in Scopus, WoS, IEEE, Compendex, and Wiley; 30-query static strategy lint passed. |
| **MAJOR-03** incomplete NTRS M matrix | Replaced the incomplete matrix with 6 P × 18 complete M = **108 mandatory P×M cells**. Removed mandatory N-A discovery cells; the full-E deterministic tag is applied to the complete union. | 108/108 cells completed/reopened/reconciled; 39 overlapping events, six-ID unscreened union; no failures. Full-E tag gave A∩B=1, B-only=5, A-only=0. |
| **MAJOR-04** missing EPS terms | Added power mode(s) to all A2 strings; added IEEE/Wiley power generation and battery/batteries; added electric power subsystem to IEEE/Wiley A1; froze the complete 25-form E dictionary. | Revised A1/A2 pilots completed in all five Boolean source families; full-E self-test passed 25/25 forms. |
| **MAJOR-05** unfrozen/metadata-gated ESA | Added a versioned dictionary, deterministic field matcher, positive/negative fixtures, exact field/normalization rules, attachment-first whole-instance harvester, and no-network rematcher. Every material is inventoried before gating; joined metadata and each attachment text are separate routes. | 408/408 in-window event exports; 8,394 contributions; 6,770 material associations; all 5,690 document-like URLs received outcomes. Corrected rematch: metadata B=17, attachment B=62, overlap=5, union=74, attachment-only=57; A∩B=23, B-only=51, A-only=0. Four retrieval and 22 parse failures are explicit coverage failures. |
| **MAJOR-06** API pagination | **Delegated** to a Pi subagent launched with `-e ~/agent-tools/academic-research`. Frozen source-native Scopus offsets and IEEE page numbers, explicit ordering, retries/stops/total-change rules, two-pass ordered IDs/ranks, missing/duplicate checks, secret handling, and hard total reconciliation. | Delegated historical pilots completed 80/80 and 42/42 twice. Parent integration reran corrected unrestricted final shapes: Scopus 85/85 twice over four pages; IEEE 47/47 twice over two pages. |
| **MAJOR-07** unproven type filters | Removed Scopus `DOCTYPE`, WoS Document Type, and IEEE ContentType restrictions; publication type is screened later. Prospective API templates explicitly contain no type filter. | Unrestricted versus old B1: Scopus 85 vs 80; IEEE 39 vs 38; WoS 43 vs 43. Corrected unrestricted API pagination/export and WoS ordinary RIS preflight succeeded. |

## Minor findings and suggestion

| Finding | Resolution |
|---|---|
| **MINOR-01** O/V heading overclaim | Relabelled O/V as selected, non-exhaustive sensitivity probes and documented selection rationale; baseline A/B remains outcome-independent. |
| **MINOR-02** expansion state | Final log contract records expansion state/absence. Scopus/IEEE API templates expose no separate expansion parameter; Compendex autostemming is OFF; WoS Exact Search was observed unchanged at `false` without inferring semantics; deterministic matching performs no implicit expansion. |
| **MINOR-03** structural A subsets | ESA and NTRS now report A∩B, B-only, union, and enforce A-only=0; A is explicitly an EPS tag, not a source-unique discovery stream. |
| **MINOR-04** exact-day cutoff | Scopus, IEEE, Compendex, and Wiley preserve source totals and log a post-search first-formal-publication-date cutoff and removals after the exact run day. |
| **SUGGESTION-01** redundant NTRS A cells | Adopted after securing the complete P×M union: no mandatory N-A cells; full-E local metadata tagging plus optional logged source-equivalence checks. |

## Frozen implementation checksums

| Artifact | SHA-256 |
|---|---|
| `searches/search-concept-dictionary.json` | `1b2416c22840bd780d9b47f3ff81c6fd6466f13d52ee9d2ca7b429161a4232ab` |
| `searches/api-pagination-request-templates.json` | `15087ec37cf4c510fae78583df248c28703a3257365e8e1dea6d73cd4b48a66a` |
| `searches/tools/api_pagination_reconcile.py` | `be9fd8a5202ddb8ef5fec96855d119d840a8c9fbcbbb1f8393836df594d6801e` |
| `searches/tools/concept_matcher.py` | `895d7e8fb333d1ce684cda02e6ca795f6fbc29ee70a16cc894c5d8eaaa0203eb` |
| `searches/tools/esa_indico_harvest_match.py` | `78ff39c67371b4948bbae14b9cdbdf2b9b92f54bcd67858a8c35b5ef41e04d2b` |
| `searches/tools/esa_indico_rematch.py` | `ff2d71659089b18c935c636c6ce09bd3b5ae5c6887c247b2dc864e01ff1ada39` |
| `searches/tools/search_strategy_lint.py` | `edf5b81dba2f8f4e5273b7043639e5df03f6a4b5ecade039c295179b2d3b001d` |

Static lint passed all 30 Boolean query blocks. Ten deterministic matcher fixtures passed, including positive/negative field-level and attachment-only cases. Exact source observations and private-manifest checksums are in:

- [`2026-08-07-press-api-query-validation.md`](2026-08-07-press-api-query-validation.md)
- [`2026-08-07-press-browser-source-validation.md`](2026-08-07-press-browser-source-validation.md)
- [`2026-08-07-ntrs-revised-matrix-validation.md`](2026-08-07-ntrs-revised-matrix-validation.md)
- [`2026-08-07-esa-attachment-first-validation.md`](2026-08-07-esa-attachment-first-validation.md)
- [`2026-08-07-scopus-ieee-multipage-api-validation.md`](2026-08-07-scopus-ieee-multipage-api-validation.md)

## Disposition after correction

All seven MAJOR and four MINOR findings are implemented and pre-freeze validated. Version 1.1 may be presented to the researcher for freeze/search authorization. Every pilot output remains superseded; all final source strategies, 108 NTRS cells, the complete ESA census, and final API snapshots must be rerun after authorization.
