# PRESS-corrected Scopus and IEEE query validation

**Status:** completed `pilot_not_candidate_search`; no record was screened, retained as a candidate, or used as evidence. Final discovery remains unauthorized.

- **Run date:** 2026-08-07, 11:13–11:28 EDT (15:13–15:28 UTC)
- **Raw private workspace:** `.searches/eps-mbse-slr-2026/press-fix-pilots/2026-08-07/`
- **API-validation manifest:** 113 files, SHA-256 `fda7a1ab5a373b4ab8cd25835fe2f5f5a1d1cda31ea66378ab0a8318844f2217`
- **Exact strings:** final `S-*` and `I-*` blocks in `SLR/SLR1/query-search-plan.md`
- **Source clients:** `search_scopus.py` SHA-256 `1c92dde7a62b43d8003767eb0b2c7c262d35ef12ac09da430da65b642def6d9d`; `search_ieee_xplore.py` SHA-256 `7d09758723b759f03d5db95264bfce4c749f43022dd6b2d9c51a1d0be033ab77`; strict reconciler SHA-256 `be9fd8a5202ddb8ef5fec96855d119d840a8c9fbcbbb1f8393836df594d6801e`.

## Corrected syntax/count results

All Scopus strings include `LANGUAGE(english) AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027` and no `DOCTYPE`. All IEEE requests use years 2011–2026, `Language:English`, and no ContentType refinement.

| Source | A1 | A2 | B1 | B2 | V1 | O1 |
|---|---:|---:|---:|---:|---:|---:|
| Scopus `COMPLETE` | 3 | 10 | 85 | 68 | 1 | 4 |
| IEEE Xplore | 4 | 6 | 39 | 47 | 1 | 4 |

The revised A1/A2/B1/B2 strings therefore accepted the corrected population, EPS, model/modeling, object-oriented-model, and explicit IEEE relation variants. V1/O1 remain selected, non-exhaustive sensitivity probes.

## Population and type-filter comparisons

- Adding spaced plural `"nano satellites"` to otherwise matched final Scopus B1 produced 85→85.
- Adding standalone `nanosat` and spaced plural `"nano satellites"` to otherwise matched final IEEE B1 produced 39→39.
- Removing the old Scopus `DOCTYPE(ar|cp|ch)` restriction changed final B1 from 80 to 85 (+5).
- Removing IEEE `ContentType:Journals/Conferences/Books` changed final B1 from 38 to 39 (+1).

Equal population-variant totals do not prove set equivalence. The unrestricted gains confirm that the old type controls were retrieval restrictions and are superseded.

## Complete unrestricted pagination and merge preflight

The delegated MAJOR-06 reconciler was rerun on the corrected no-type-filter requests with fixed page size 25, explicit source ordering, two complete passes, stable totals, unique source IDs, global ranks, missing/duplicate-page checks, and the hard `retrieved == source total` rule.

| Pilot | Pages per pass | Total | Retrieved per pass | Ordered IDs | Merge smoke test | Private manifest SHA-256 |
|---|---|---:|---:|---|---|---|
| Scopus final S-B1 | 25/25/25/10 | 85 | 85/85 | identical; 85 unique EIDs; sequence `d133619ebb55d0cb40e68a1781e0fbd738092f3a3c49056a6666cf61b95bf8cd` | 85 raw / 84 bibliographically unique / 1 duplicate manifestation | `e89596345c9da44c09807b71ba205dd6a350e7de515251b443fdaad045c0a3f9` |
| IEEE final I-B2 | 25/22 | 47 | 47/47 | identical; 47 unique article numbers; sequence `66b71e0afa32cd9c337b6d5946b76bfc4f22b2ad7c2b3726414447e534001f39` | 47 raw / 47 unique / 0 removed | `1d475b5e8fd562459c011fc8fc678f8d374b9dc87435b6c50e1a0e0b8b998934` |

Neither strict run had a retry, total change, missing page, repeated page sequence, duplicate source ID, or short nonterminal page. The current non-secret request-template SHA-256 is `15087ec37cf4c510fae78583df248c28703a3257365e8e1dea6d73cd4b48a66a`; its `prospective_final_execution` object separates these corrected requests from the preserved historical type-filter pilots.

The generic academic Scopus client failed during attempted full normalization because one source author had a null given name. This was a client exception, not a source failure or zero result; the strict reconciler safely normalized the same source and completed 85/85 twice.

## Expansion and exact-day controls

Neither validated API request exposes a separate automatic stemming, lemmatization, or term-expansion parameter. No singular/plural or US/UK equivalence is inferred; explicit forms remain frozen. Both source date controls admit all of 2026, so a final run must preserve the source total and separately log records removed after the exact run-day first-formal-publication cutoff.
