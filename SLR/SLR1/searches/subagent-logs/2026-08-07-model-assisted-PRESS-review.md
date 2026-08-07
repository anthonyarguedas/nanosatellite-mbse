# model-assisted PRESS-style review

**Review label:** `model-assisted PRESS-style review`<br>
**Review run:** `eps-mbse-slr-2026`<br>
**Strategy reviewed:** protocol version 1.1 and the current pre-freeze source translations<br>
**Prepared:** 2026-08-07 10:06:01 EDT (UTC−04:00)<br>
**Reviewer status:** model-assisted search-methods review; no human information specialist participated<br>
**Overall disposition:** `revise before execution`

## Finding count

| Classification | Count |
|---|---:|
| CRITICAL | 0 |
| MAJOR | 7 |
| MINOR | 4 |
| SUGGESTION | 1 |

## Review boundary and method

All ten files specified in the review request were read in full. The assessment applies the PRESS 2015 Evidence-Based Checklist domains to the strategy as it now stands: translation of the research question; Boolean/proximity operators; subject headings/controlled vocabulary where applicable; text words and variants; syntax/field codes; and limits/filters. Superseded pilot strings were used only as source-syntax and interface evidence, not as the strategy under review.

No discovery search was run. No candidate record was inspected or screened; no retained source PDF or Markdown was used as evidence; and no deleted history was inspected. Aggregate pilot counts and interface behavior in the required logs were used only to assess syntax, controls, and reproducibility. The user-confirmed indexing of AIAA and IAC content in Scopus is accepted; this review does **not** recommend separate venue databases merely for those venues.

## Overall assessment

The conceptual architecture is strong. Population, EPS, and structured-system-model concepts map appropriately to the objective and RQs; no comparator is made mandatory; outcome direction is not an inclusion condition; and the broad `P AND M` Stream B is an appropriate safeguard for embedded EPS threads absent from metadata. The generic SmallSat exclusion is a documented scope decision, not a search error. Bare `EPS`, `MBSE`, `MIL`, `SIL`, `PIL`, and `HIL` are intersected with narrower concepts rather than searched alone.

Boolean grouping is sound in the query-based sources. NTRS appropriately avoids unsupported `OR`/parentheses, and no unsupported proximity syntax should be introduced. Source restrictions to WoS Core Collection with all editions, Compendex only, unrestricted Wiley, the whole ESA Indico instance, and the whole NTRS collection are well specified. Backward reference checking and dual-platform Scopus/WoSCC forward chasing are also well designed.

The strategy is not ready to freeze, however. Some frozen P/E/M terms are absent from source implementations; the NTRS matrix is large but still omits much of M; the ESA matcher is not yet an executable frozen strategy and is metadata-gated; Scopus and IEEE lack a validated multi-page request specification; and three discovery filters are not demonstrably aligned with the protocol's eligible report types.

## PRESS-domain assessment

| PRESS domain | Assessment |
|---|---|
| Translation of the research question | **Conceptually appropriate, implementation revision required.** P/E/M and optional O/V preserve the RQs without mandatory outcome terms. Source-level omissions are addressed in MAJOR-01 through MAJOR-05. |
| Boolean/proximity operators | **Acceptable.** Parentheses and `AND`/`OR` grouping are correct. NTRS's cell approach is justified by its failed Boolean pilots. No proximity operator is required merely for checklist conformity, and none has source validation in the logs. |
| Subject headings/controlled vocabulary | **Acceptable for the documented routes.** Compendex `KY` includes Subject/Title/Abstract, so the terms also search its indexed subject text. No separate controlled-vocabulary syntax was validated for the other routes. Lack of a dedicated heading block is not, by itself, an error here. |
| Text words, spelling, truncation, and ambiguity | **Revise.** The main acronym controls are defensible, but population, structured-model, relation, and EPS variants are not consistently translated. |
| Syntax, field codes, phrase handling, and line/query identification | **Mostly sound, but incomplete for two APIs and ESA.** `TITLE-ABS-KEY`, WoS Topic, Compendex `KY`, Wiley `AllField`, and NTRS cell syntax are supported by the logs. Stable query IDs are adequate in place of numbered lines. Exact API pagination and the ESA matching implementation still need to be frozen. |
| Limits and filters | **Revise.** Date and English limits reflect eligibility, with justified post-search screening where source filters are unavailable. Document-type controls in Scopus, WoS, and IEEE are not yet shown to preserve every eligible indexed report type. |

# Findings requiring action

## MAJOR-01 — A frozen population term is dropped in IEEE and NTRS, and the spaced plural nanosatellite variant is absent

**PRESS domains:** translation; text words/spelling; source translation.<br>
**Affected IDs:** `I-A1`, `I-A2`, `I-B1`, `I-B2`, `I-V1`, `I-O1`; all `N-B` and `N-A` cells through `P_N`; `ESA-A1`/`ESA-B1` dictionary specification; and the P blocks in `S-*`, `WS-*`, `C-*`, and `W-*` for the spaced plural.

**Actual error versus scope choice:** The protocol explicitly names `nanosat` as a Population term, and the common plan uses `nanosat*`. IEEE has neither wildcard nor explicit `nanosat`; NTRS's eight-form audit did not test bare `nanosat`. Those implementations silently drop a frozen concept. In addition, the strategy has singular `"nano satellite"` and plural hyphenated `"nano-satellites"`, but not spaced plural `"nano satellites"`. Compendex has autostemming off, so singular phrase equivalence cannot be assumed.

**Why it matters:** A report using the abbreviation `nanosat` in searchable metadata can be missed in two source routes. A spaced plural is an ordinary number/hyphenation variant and is not matched by contiguous `nanosat*`.

**Precise replacement/decision:**

1. Add unquoted `nanosat` to every IEEE P block.
2. Replace `P_N` with at least `{CubeSat, CubeSats, nanosatellite, "nano-satellite", nanosat, "nano satellites"}`; each remains a separate NTRS cell term.
3. Add `"nano satellites"` to the canonical P block and every Boolean-source translation, and encode it explicitly in the ESA dictionary.
4. Do not add generic `SmallSat`, `small satellite`, PocketQube, or CanSat terms; their omission remains a defensible population decision.

**Syntax evidence:** IEEE accepted simple tokens and quoted phrases; NTRS accepted simple space-delimited terms and materially restrictive quoted phrases but not Boolean OR; Scopus, WoS, Compendex, and Wiley accepted quoted phrases. No new operator is proposed.

**Fresh pilot needed:** **Yes.** Run revised count/syntax pilots for all IEEE strings, test the two added NTRS P terms against every final `M_N` term, and run matched old/new P checks in the Boolean sources. Re-freeze the NTRS matrix size afterward.

## MAJOR-02 — Structured-system-model spelling and relation variants are incomplete

**PRESS domains:** translation; text words/spelling/truncation; phrase handling.<br>
**Affected IDs:** `S-A2`, `S-B2`; `WS-A2`, `WS-B2`; `I-A2`, `I-B2`; `C-A2`, `C-B2`; `W-A2`, `W-B2`; and the planned `ESA-A1`/`ESA-B1` M dictionary. NTRS is addressed separately in MAJOR-03.

**Actual error versus scope choice:** The common M block includes US singular `"system modeling"` and UK plural `"systems modelling"`, but omits the crossed variants `"systems modeling"` and `"system modelling"`. With Compendex autostemming off and quoted phrases, equivalence cannot be assumed. IEEE and Wiley B2 also omit the frozen phrase `"object-oriented systems model"`. Their relation blocks mix singular and plural forms without a documented stemming control: IEEE has `requirements/functions/interfaces` but not the singulars, while Wiley has `requirement/function/interface` but not the plurals.

**Why it matters:** B2 is the principal expansion for reports that do not say MBSE or SysML. Missing orthographic/number variants can therefore suppress the exact records Stream B was created to recover.

**Precise replacement/decision:**

- Add `"systems modeling"` and `"system modelling"` wherever the broad model/modeling phrases are used. Add `"object-oriented systems model"` to every A2/B2 broad-M block where it is absent.
- In `W-B2`, replace the relation block with the Wiley-supported unquoted wildcard form:

```text
(requirement* OR function* OR behavio* OR architectur* OR interface* OR traceab* OR parametric* OR verification OR validation)
```

- In `I-B2`, do **not** invent wildcard behavior. Use explicit accepted tokens:

```text
(requirement OR requirements OR function OR functions OR behavior OR behaviors OR behaviour OR behaviours OR architecture OR architectures OR interface OR interfaces OR traceability OR parametric OR parametrics OR verification OR validation)
```

- Add all four phrases `"system modeling"`, `"systems modeling"`, `"system modelling"`, and `"systems modelling"` to `I-A2` and `W-A2`, which currently omit some or all of them.

**Syntax evidence:** Wiley's log validates non-leading unquoted `*`, parentheses, uppercase Boolean, and quoted phrases. IEEE validates explicit Boolean tokens and quoted phrases but not wildcard semantics, hence the explicit IEEE replacement. Scopus/WoS/Compendex logs validate the phrase forms; Compendex validates explicit wildcards with autostemming off.

**Fresh pilot needed:** **Yes.** Rerun revised A2/B2 count/syntax pilots in all five query-based source families and synthetic ESA matcher tests before freezing the exact blocks.

## MAJOR-03 — The NTRS 136-cell matrix is arithmetically correct but does not implement the frozen M concept

**PRESS domains:** translation; text words; source-specific syntax; Stream A/B complementarity.<br>
**Affected IDs:** all 28 current `N-B` cells, all 108 current `N-A` cells, optional `N-V`/`N-O` parent-cell selection, and the `136 mandatory cells` stopping rule.

**Actual error versus scope choice:** The matrix correctly computes `4×7 + 4×9×3 = 136`, and using cells rather than Boolean OR is supported by the NTRS diagnostics. The problem is term coverage, not arithmetic. Current `M_N` omits frozen high-specificity terms including the singular long forms of model-based system engineering, `systems modeling language`, `systems model`, modeling/modelling variants, Arcadia, Capella, and `object-oriented systems model`.

**Why it matters:** NTRS is the dedicated institutional-report route. A technical report that names a tool or a structured system model but not one of the seven current `M_N` terms can be absent from the NTRS union, and other bibliographic sources cannot be assumed to repair repository-specific under-retrieval.

**Precise replacement/decision:** Expand `M_N` to the complete source-representable M set, using a separate simple-token or quoted-phrase cell for each:

```text
MBSE
"model-based systems engineering"
"model based systems engineering"
"model-based system engineering"
"model based system engineering"
SysML
"systems modeling language"
"system model"
"systems model"
"system modeling"
"systems modeling"
"system modelling"
"systems modelling"
"reference model"
"digital engineering"
Arcadia
Capella
"object-oriented systems model"
```

At minimum, make the expanded `P_N × M_N` N-B matrix the complete NTRS discovery baseline. The current N-A cells may be retained as source-level EPS tags, but they must not be described as compensating for an incomplete N-B matrix. Retire the fixed number `136` and recompute the mandatory-cell total after MAJOR-01 and this change.

**Syntax evidence:** Every proposed item is either a simple token or a quoted phrase. Those are the two NTRS forms validated in the log; no OR, parentheses, truncation, or unsupported field syntax is introduced.

**Fresh pilot needed:** **Yes.** Test every newly introduced `M_N` cell with representative P terms, cross-check representative cells in the UI, then execute and reconcile the complete revised matrix after authorization.

## MAJOR-04 — Frozen EPS terms are absent from exact Stream A source translations

**PRESS domains:** translation; text words; exact source translation.<br>
**Affected IDs:** `S-A2`, `WS-A2`, `C-A2`; `I-A1`, `I-A2`; `W-A1`, `W-A2`; current `N-A`/`E_N`; and the future `ESA-A1` dictionary.

**Actual error versus scope choice:** Section 4 freezes `power mode`, but it appears in none of the five A2 Boolean queries. IEEE and Wiley A2 omit `power generation`; both use singular `battery` without a validated stemming rule; and IEEE/Wiley A1 omit `"electric power subsystem"`. Current NTRS `E_N` is a selected nine-term subset, not the full frozen E concept.

**Why it matters:** Stream B does not completely neutralize these omissions. B2 adds a relation block and uses a different M partition, so an EPS-explicit record using a broad model phrase but no relation word in metadata can depend on A2's E×M cross-product.

**Precise replacement/decision:**

- Add `"power mode" OR "power modes"` to `S-A2`, `WS-A2`, `C-A2`, `I-A2`, and `W-A2`.
- Add `"power generation"` to `I-A2` and `W-A2`.
- In `I-A2` and `W-A2`, use explicit `battery OR batteries` rather than assuming stemming.
- Add `"electric power subsystem"` to `I-A1` and `W-A1`.
- If N-A remains a claimed complete Stream A search, expand `E_N` to the full Section 4 E set as one term/phrase per cell. Otherwise relabel N-A as a selected high-specificity EPS-tag matrix and apply the complete E dictionary to the full N-B union for Stream A classification.
- The frozen ESA E dictionary must contain the full corrected E set.

**Syntax evidence:** All additions use simple tokens or quoted phrases already supported in the applicable logs. No unvalidated proximity or wildcard syntax is required.

**Fresh pilot needed:** **Yes.** Rerun the revised A1/A2 strings and pilot whichever complete NTRS E-tag implementation is selected.

## MAJOR-05 — ESA-A1/ESA-B1 are not yet an executable frozen strategy and can miss report attachments behind nonmatching metadata

**PRESS domains:** source translation; text-word matching; fields; syntax/reproducibility.<br>
**Affected IDs:** `ESA-A1`, `ESA-B1`, the ESA stopping rule, and planned artifact `searches/search-concept-dictionary.json`.

**Actual error versus scope choice:** At review time, `SLR/SLR1/searches/search-concept-dictionary.json` is absent. The plan defers the exact dictionary, field implementation, token boundaries, wildcard behavior, and matcher tests until before the valid harvest, although the strategy is described as ready to freeze. More importantly, attachments are inventoried/retrieved only **after** a contribution is a metadata candidate. A substantive attached report whose event/contribution/material metadata lacks P or M will never reach matching or screening.

**Why it matters:** ESA's candidate set is created entirely by this local matcher. An unfrozen matcher prevents exact peer review and reproducibility; metadata-gated attachment retrieval creates a plausible false-negative route in a source specifically included for weakly indexed event material.

**Precise replacement/decision:** Before authorization:

1. Create and freeze the actual dictionary with the corrected P/E/M terms, case-folding, Unicode-dash and hyphen/space normalization, phrase rules, explicit wildcard expansions, and standalone token boundaries for acronyms such as `EPS`, `MBSE`, `MIL`, `SIL`, `PIL`, and `HIL`.
2. Freeze the exact searched fields, matcher code/version/checksum, and positive/negative synthetic regression fixtures with field-level expected hits.
3. Inventory every material attachment for every in-window contribution before candidate gating. For every accessible document-like attachment, match extractable normalized text as well as the joined event/contribution/material metadata; union metadata and attachment-text candidates. Record inaccessible or unparseable materials as coverage failures. Slides/posters may remain lead-only at screening, but should not be discarded solely because the surrounding metadata fails P/M.
4. Treat `ESA-A1` as an EPS-explicit tag within `ESA-B1`'s union; preserve both field-level match routes.

**Syntax evidence:** This is a local deterministic matcher, not a proposal for unsupported Indico query syntax. The existing root and contribution-export endpoints and response shape are well validated.

**Fresh pilot needed:** **Yes.** Run synthetic unit tests plus a complete no-screening census/matcher dry run that reconciles events, contributions, materials, parse failures, A/B overlap, and union counts. Do not reuse its candidates as final-run discovery output.

## MAJOR-06 — Scopus and IEEE multi-page API execution is not yet reproducibly specified or validated

**PRESS domains:** syntax/field codes; pagination; export reproducibility.<br>
**Affected IDs:** `S-A1`, `S-A2`, `S-B1`, `S-B2`, `S-V1`, `S-O1`; `I-A1`, `I-A2`, `I-B1`, `I-B2`, `I-V1`, `I-O1`.

**Actual error versus scope choice:** The logs validate only complete retrievals of three Scopus records (`S-A1`) and four IEEE records (`I-A1`). Larger pilot totals reach 80 and 42, but the plan does not freeze a complete non-secret request template, page size/offset or cursor behavior, declared ordering, retry behavior, and duplicate/missing-page reconciliation for either API. The Scopus displayed query blocks also omit the year clauses that prose says will be appended.

**Why it matters:** A count-only success does not establish complete retrieval. Default page limits or unstable ordering can silently truncate or duplicate the two broadest electronic-source sets.

**Precise replacement/decision:**

- Append the already validated `AND PUBYEAR AFT 2010 AND PUBYEAR BEF 2027` clauses to each displayed final Scopus strategy, rather than leaving them only in prose.
- Before freeze, add one redacted, source-native request template per API containing every non-secret query, field/view, filter, sort, and pagination parameter; identify the exact client version/checksum and the stop/retry/total-change rules. Keep credentials out of artifacts.
- Require ordered page-ID reconciliation, global ranks, duplicate-page detection, and `retrieved == source total` (or a logged source failure) for every final query.
- Because the required pagination parameter names and behavior are not present in the reviewed logs, observe and freeze them in a pilot rather than inventing them in the plan.

**Fresh pilot needed:** **Yes.** Use revised `S-B1` and `I-B2` (or another set demonstrably exceeding one page) for full multi-page retrieval and merge preflights, then rerun every final strategy after authorization.

## MAJOR-07 — Scopus, WoS, and IEEE publication-type filters are not proven to preserve the protocol's eligible report types

**PRESS domain:** limits/filters.<br>
**Affected IDs:** all `S-*`, `WS-*`, and `I-*` searches.

**Actual error versus scope choice:** English and date restrictions directly reflect eligibility and are defensible. The discovery type restrictions are different: Scopus keeps only `ar/cp/ch`; WoS keeps Article, Book Chapter, and Proceedings Paper; IEEE keeps Journals, Conferences, and Books. The protocol also admits substantive institutional technical reports and retains relevant secondary reviews for recall/citation chasing. The reviewed interface evidence does not establish that every eligible indexed manifestation maps to the selected categories. Compendex appropriately avoided this same risk by removing its type filter.

**Why it matters:** An otherwise eligible technical/experience report, an atypically classified workshop or early manifestation, or a relevant secondary review can be excluded before screening. NTRS cannot substitute for non-NASA institutional reports, and the existence of other sources does not validate a source-level filter.

**Precise replacement/decision:** Remove the discovery document/content-type restriction from Scopus, WoS, and IEEE and apply publication type during screening. Concretely: remove the Scopus `DOCTYPE` clause, select no WoS Document Type restriction, and omit the IEEE content-type facet. Retain English and date controls. If the researcher prefers a type filter, first document a source-native category-mapping audit that demonstrates complete coverage of every eligible type; do not add unobserved source codes by guesswork.

**Fresh pilot needed:** **Yes.** Compare unrestricted and currently restricted `S-B1`, `WS-B1`, and `I-B1`, validate export/pagination under the broader sets, then freeze and rerun all final strings. No record screening is required for the syntax/count pilot.

# Lower-severity findings

## MINOR-01 — The O/V headings imply a fuller translation than the exact sensitivity probes contain

Section 4 lists, among other terms, `design verification`, `design validation`, `model-to-test`, `interface consistency`, `lifecycle continuity`, `no effect`, `adverse`, `time`, `skill`, `resource`, `maintenance`, and `governance`; the exact `S/WS/I/C/W-V1` and `-O1` probes use selected subsets. This is not an outcome-reporting-bias error because A/B remain the baseline and outcome terms are never mandatory. Either label the lists and IDs explicitly as **selected, non-exhaustive sensitivity probes** with the selection rationale, or align the exact probes with the frozen list. Any expansion should receive a syntax/count pilot.

## MINOR-02 — Automatic stemming/lemmatization state is not consistently reported

Compendex correctly freezes autostemming **off**, and ESA is intended to use explicit deterministic matching. Wiley documents wildcard/phrase behavior, and NTRS documents restrictive phrase quoting. For Scopus, WoS Basic Search, and IEEE, record whether an automatic term-expansion setting exists and its state/default at final execution; do not infer singular/plural or spelling equivalence from equal counts. The explicit variants required above should remain even if a platform also expands terms.

## MINOR-03 — Stream A cannot have source-unique yield in ESA and current NTRS

By construction, `ESA-A1 = P AND E AND M` is a subset of `ESA-B1 = P AND M`. Each current N-A cell is likewise a subset of its corresponding P×M N-B cell. Report `A∩B`, `B-only`, and the union; label A as an EPS-explicit tag in these two sources and do not interpret an expected `A-only = 0` as poor performance. This is a reporting clarification, not a recall defect.

## MINOR-04 — Exact-day upper-date screening should be explicit for all year/month-only sources

Scopus and IEEE use the whole 2026 publication year, Compendex uses `Latest`, and Wiley normalizes through month-end. Wiley already requires screening after the run date. Apply and log the same first-formal-publication-date check to Scopus, IEEE, and Compendex, preserving the source total and the number removed after the exact run-date cutoff.

## SUGGESTION-01 — Collapse redundant NTRS A cells after the complete B matrix is secured

Once MAJOR-01 and MAJOR-03 produce a complete P×M N-B union, the N-A queries cannot add candidates. For efficiency, the researcher may replace the N-A search cells with a versioned full-E matcher over the retrieved N-B metadata and retain a small set of N-A cells only as matcher/source-equivalence checks. Adopt this only after a pilot confirms the desired Stream A tagging behavior; retaining the cells is defensible if source-level A discovery-event provenance is valued.

# Source-by-source pre-execution checklist

| Source | Concepts and Boolean | Fields/syntax | Limits/database | Pagination/export | Pre-execution status |
|---|---|---|---|---|---|
| Scopus | P/E/M grouping sound; revise P, broad M, and A2 E terms (MAJOR-01/02/04) | `TITLE-ABS-KEY` accepted; add year clauses to displayed exact strings | English/date sound; remove or validate `DOCTYPE` filter | `COMPLETE` merge path works; multi-page API route not validated | **REVISE + fresh pilot** |
| WoS Core Collection | Grouping sound; revise P/M/A2 E terms | Topic field, phrases/wildcards, all ten editions, ordinary RIS and CR sidecar validated | Exact date/English sound; remove or validate Document Type filter | Page size/sort and ≤1,000 ordinary export documented | **REVISE + fresh pilot** |
| IEEE Xplore | Add `nanosat`, explicit relation inflections, complete broad M, and missing E terms | Boolean/phrases accepted; use explicit variants rather than unvalidated wildcards | English/year sound; remove or validate content-type facet | Count/full merge works only for four-record set; freeze multi-page request | **REVISE + fresh pilot** |
| Compendex | Grouping sound; add M variants and power mode(s) | `KY`, phrases, wildcards, Compendex-only, autostemming off validated | Year/language sound; no type filter is appropriate | Relevance, 100/page, Detailed CSV normalization validated | **REVISE strings + fresh pilot** |
| Wiley Online Library | Grouping sound; add P/M/relation/E variants | Whole-platform `AllField`, explicit Boolean, phrases, unquoted wildcards validated | Month overshoot and post-screening documented; no unsupported language/type filter | 20/page, stale-DOM check, page-scoped RIS and normalization validated | **REVISE strings + fresh pilot** |
| ESA Indico | A/B logic sound, but dictionary absent and metadata gating can miss attachments | Root/child census and contribution JSON shape validated; local matcher not frozen | Whole public instance and event-date handling sound | Event/access reconciliation strong; add all-material inventory/text-matching coverage | **REVISE before freeze** |
| NASA NTRS | Cell method justified; P and M incomplete; 136 is not a complete frozen matrix | Use only simple terms and quoted phrases; no OR/parentheses | Exact date; language/type screened later | 100-record exhaustion and total-change rerun rule documented | **REVISE matrix + fresh pilot** |

# Citation searching assessment

The citation-search component is acceptable without revision:

- complete source reference lists, rather than indexed-reference exports alone, are used for backward checking;
- every included report and relevant secondary review is a seed;
- forward citations are searched independently in both Scopus and WoS Core Collection;
- a zero result or indexing failure in one platform does not waive the other;
- DOI/title/cited-reference routes are logged for unindexed seeds;
- newly included reports enter the next cycle; and
- stopping requires a complete backward and dual-platform forward cycle with no new eligible report.

The separation of `discovery_route=citation_chasing` from bibliographic source and the deferred Buruso benchmark are internally consistent. No additional citation index or venue database is required solely because AIAA or IAC are not standalone planned sources.

# Internal consistency assessment

The protocol, plan, and log are consistent on the seven-source set, the 2011 lower bound, English eligibility, the no-valid-search-yet boundary, the superseded status of pilots, the broad Stream B rule, deferred retained-file/Buruso checks, and dual-platform forward citation chasing. Pilot authentication/export failures are correctly distinguished from zero results.

The material inconsistencies are the common P/E/M dictionaries versus exact source strings (MAJOR-01/02/04), the claim that a search unit is an exact request/matching operation versus the unfrozen ESA and API implementations (MAJOR-05/06), and eligible report types versus pre-search filters (MAJOR-07). Consequently, the statements that interface validation is complete and version 1.1 is ready for authorization are premature until the major findings are resolved and the resulting exact strategies are re-frozen.

# Disposition

`revise before execution`

The research-question translation, Boolean architecture, source selection, Stream B safeguard, and citation-chasing design should be retained. Resolve all seven MAJOR findings, rerun only the necessary syntax/interface pilots without treating pilot outputs as candidates, update the exact pre-freeze strategy artifacts prospectively, and then obtain search authorization.