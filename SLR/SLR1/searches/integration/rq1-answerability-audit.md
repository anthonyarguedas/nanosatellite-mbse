# RQ1 Answerability and Search-Coverage Audit

**Review run:** `eps-mbse-slr-2026`
**Authoritative protocol:** `SLR/SLR1/protocol.md`, version 1.0
**Audit timestamp:** `2026-08-06T17:51:45Z`
**Scope:** metadata-only evidence-sufficiency/search-coverage audit; not full-text eligibility screening or extraction.

## Executive verdict

The frozen new-run retrieval corpus is **adequate to begin an exploratory RQ1 evidence map, but at risk for a complete comparative RQ1 synthesis until full-text eligibility and source-located extraction are done**. Direct primary-database coverage is strong for EPS/MBSE discovery and now directly tested for inputs/assumptions, reuse/tailoring, and abstraction/fidelity. Yet visible metadata is too sparse to establish protocol-qualifying EPS threads or detailed input reporting.

| RQ1 component | Verdict | Basis |
|---|---|---|
| Model representation and qualifying EPS-thread relations | **probably sufficient but full-text dependent** | Both primary sources used explicit EPS Stream-A routes; 14/92 kept records are A-tagged and 78/92 are B-only embedded-thread leads. The audit finds direct metadata relation signals in only two kept records, so metadata cannot establish the full protocol bridge. |
| Stated purposes, decisions, and lifecycle use | **probably sufficient but full-text dependent** | Task/lifecycle language is broadly visible across the kept set and the primary query set explicitly covers requirements, behavior, architecture, interfaces, traceability, parametrics, verification/validation, analysis, and concurrent/conceptual design. |
| Material input/assumption types | **probably sufficient but full-text dependent** | Original Stream-A functional EPS/budget/component queries plus the new direct inputs/assumptions probes are redundant with frozen candidates. Candidate leads include budgets, energy, power consumption, resources, operational scenarios, batteries/solar content, and constraints. |
| Input values/units/time basis, provenance, uncertainty/margins, rationale, trace location, and effect | **at risk** | The targeted assumptions/margins/orbit/environment probe found no new plausible candidate, so direct discoverability is tested. However, saved metadata almost never discloses these extraction-level details; the audit detects no visible EPS value/unit and no source-locatable input trace. |
| Abstraction/fidelity choices | **probably sufficient but full-text dependent** | Reference-model, conceptual, logical/functional architecture, black-box, parametric, and fidelity vocabulary occurs in kept metadata; the direct abstraction/fidelity probes returned only frozen records. |
| Deliberate omissions and explicit boundary exclusions | **at risk** | No saved metadata directly identifies a deliberately omitted phenomenon or an explicit EPS model-boundary exclusion under the strict rule. |
| Reuse/tailoring mechanisms, assets, and target/context | **probably sufficient but full-text dependent** | The newly direct reuse/tailoring probes returned 90 fully retrieved source occurrences across Scopus/IEEE, overwhelmingly frozen duplicates and no new plausible candidate. Kept metadata contains reference-model, template, profile, open-source, tailored, and standardization signals. |
| Demonstrated versus intended reuse/tailoring | **at risk** | Metadata more often describes an asset, intended starting point, template, or mechanism than an independently demonstrated reuse instance. The reference-model title family contributes a concentrated share of the reuse signals. |

### What the verdict does and does not say

- **Search discoverability:** the candidate set has direct Stream-A and deliberately EPS-free Stream-B coverage; the isolated gap probes found no new plausible candidate outside the frozen 174.
- **Metadata-level evidence:** only visible title/abstract/snippet terms are counted below. A query match is never treated as a reported fact.
- **Synthesis answerability:** remains indeterminate for any report until full text confirms eligibility and supplies source-located data. No Route A/B decision, input record, abstraction choice, or reuse claim was inferred here.

## Compliance and boundaries

- Read and applied protocol v1.0 first; did not alter canonical search, screening, corpus, merge, freeze, or deduplication artifacts.
- Used only Scopus and IEEE Xplore metadata/provenance for audit analysis and probes. **Semantic Scholar and Google Scholar were not used, queried, browsed, fetched, or inspected as sources.** No regular web search was used.
- Did not inspect `SLR/SLR1/markdown/`, `SLR/SLR1/pdfs/`, Git history, or legacy/deleted artifacts.
- Validated 223 retained-corpus Scopus/IEEE provenance events against 17 raw primary-metadata files; all matched by DOI or normalized title+year at the recorded source rank.

## RQ1 answerability rubric

| Label | Predeclared meaning |
|---|---|
| **Direct metadata signal** | Saved title/abstract visibly contains the specified RQ1 terms or relation. It is a retrieval lead, not proof of the protocol full-text threshold. |
| **Plausible full-text lead** | Metadata/provenance makes the dimension worth checking, but the required detail or relationship is not visible. |
| **No visible evidence** | Metadata silence only—not proof that the full text lacks the fact. |

Dimension rules applied:

1. **Representation/relations:** direct representation requires co-visible EPS and structured-system-model/MBSE language. Direct relation additionally needs a visible relation/analysis/traceability term. Full text must still show the same EPS anchor, model anchor, endpoints, and bridge meaning.
2. **Purpose:** direct purpose requires task/decision/lifecycle language; it is EPS-specific only when EPS content is also visible.
3. **Inputs/assumptions:** a named power/energy/resource topic is not assumed to be a model input. Input type, explicit input/assumption wording, value/unit/time basis, provenance, uncertainty/margin, rationale, trace location, and effect were scored separately.
4. **Abstraction:** conceptual/logical/functional/black-box/fidelity/parametric/reference/template/metamodel wording is a signal. Generic constraints do not prove deliberate omissions.
5. **Reuse/tailoring:** mechanism, asset, target/context, and applied versus intended status are separate. A reference model or template is not assumed to have been reused, and generic reuse is not EPS-specific reuse.

## Corpus and metadata basis

- Kept corpus: **92** records: **6 core**, **86 supporting**.
- Stream provenance: **2 A-only**, **12 A+B**, **78 B-only**; A-tagged = **14**.
- Source provenance: **61 Scopus-only**, **8 IEEE Xplore-only**, **23 in both**.
- Metadata constraint: **61** records have no saved abstract; the other **31** have truncated abstracts. This includes **2** core records with none and **4** core records with truncated abstracts.

## Candidate-level signal matrix

Counts are **direct / plausible / no visible evidence**. `A-tagged` combines A-only and A+B; `B-only` is separate. Full candidate IDs and term-level explanations for every one of the 92 records are in the companion JSON.

| Dimension | All (n=92) | Core (n=6) | Supporting (n=86) | A-tagged (n=14) | B-only (n=78) | Direct-signal IDs |
|---|---:|---:|---:|---:|---:|---|
| Model representation | 3 / 60 / 29 | 2 / 4 / 0 | 1 / 56 / 29 | 2 / 12 / 0 | 1 / 48 / 29 | `eps-mbse-slr-2026-r0019, eps-mbse-slr-2026-r0045, eps-mbse-slr-2026-r0085` |
| Qualifying EPS-thread relation lead | 2 / 61 / 29 | 2 / 4 / 0 | 0 / 57 / 29 | 2 / 12 / 0 | 0 / 49 / 29 | `eps-mbse-slr-2026-r0045, eps-mbse-slr-2026-r0085` |
| Stated purpose/decision/lifecycle | 76 / 10 / 6 | 6 / 0 / 0 | 70 / 10 / 6 | 14 / 0 / 0 | 62 / 10 / 6 | `see JSON (n=76; examples: eps-mbse-slr-2026-r0002, eps-mbse-slr-2026-r0003, eps-mbse-slr-2026-r0004, eps-mbse-slr-2026-r0005, eps-mbse-slr-2026-r0007)` |
| EPS-specific purpose lead | 9 / 78 / 5 | 5 / 1 / 0 | 4 / 77 / 5 | 7 / 7 / 0 | 2 / 71 / 5 | `eps-mbse-slr-2026-r0019, eps-mbse-slr-2026-r0045, eps-mbse-slr-2026-r0063, eps-mbse-slr-2026-r0071, eps-mbse-slr-2026-r0085, eps-mbse-slr-2026-r0093, eps-mbse-slr-2026-r0125, eps-mbse-slr-2026-r0134, eps-mbse-slr-2026-r0144` |
| Input type/topic | 9 / 54 / 29 | 4 / 2 / 0 | 5 / 52 / 29 | 6 / 4 / 4 | 3 / 50 / 25 | `eps-mbse-slr-2026-r0019, eps-mbse-slr-2026-r0045, eps-mbse-slr-2026-r0063, eps-mbse-slr-2026-r0071, eps-mbse-slr-2026-r0085, eps-mbse-slr-2026-r0106, eps-mbse-slr-2026-r0125, eps-mbse-slr-2026-r0134, eps-mbse-slr-2026-r0144` |
| Explicit model input/assumption | 1 / 8 / 83 | 1 / 3 / 2 | 0 / 5 / 81 | 1 / 5 / 8 | 0 / 3 / 75 | `eps-mbse-slr-2026-r0045` |
| Values/units/time basis | 0 / 2 / 90 | 0 / 1 / 5 | 0 / 1 / 85 | 0 / 1 / 13 | 0 / 1 / 77 | `none` |
| Input provenance | 0 / 9 / 83 | 0 / 4 / 2 | 0 / 5 / 81 | 0 / 6 / 8 | 0 / 3 / 75 | `none` |
| Uncertainty/margin | 0 / 9 / 83 | 0 / 4 / 2 | 0 / 5 / 81 | 0 / 6 / 8 | 0 / 3 / 75 | `none` |
| Input rationale | 1 / 8 / 83 | 1 / 3 / 2 | 0 / 5 / 81 | 1 / 5 / 8 | 0 / 3 / 75 | `eps-mbse-slr-2026-r0045` |
| Input trace location | 0 / 1 / 91 | 0 / 1 / 5 | 0 / 0 / 86 | 0 / 1 / 13 | 0 / 0 / 78 | `none` |
| Input effect on output/decision | 1 / 3 / 88 | 1 / 1 / 4 | 0 / 2 / 84 | 1 / 2 / 11 | 0 / 1 / 77 | `eps-mbse-slr-2026-r0045` |
| Abstraction/fidelity | 21 / 65 / 6 | 0 / 6 / 0 | 21 / 59 / 6 | 1 / 13 / 0 | 20 / 52 / 6 | `see JSON (n=21; examples: eps-mbse-slr-2026-r0003, eps-mbse-slr-2026-r0004, eps-mbse-slr-2026-r0007, eps-mbse-slr-2026-r0022, eps-mbse-slr-2026-r0026)` |
| Deliberate omissions/boundary exclusions | 0 / 9 / 83 | 0 / 3 / 3 | 0 / 6 / 80 | 0 / 3 / 11 | 0 / 6 / 72 | `none` |
| Reuse/tailoring mechanism | 21 / 36 / 35 | 2 / 1 / 3 | 19 / 35 / 32 | 5 / 2 / 7 | 16 / 34 / 28 | `see JSON (n=21; examples: eps-mbse-slr-2026-r0007, eps-mbse-slr-2026-r0018, eps-mbse-slr-2026-r0022, eps-mbse-slr-2026-r0025, eps-mbse-slr-2026-r0026)` |
| Reusable asset | 19 / 2 / 71 | 1 / 1 / 4 | 18 / 1 / 67 | 3 / 2 / 9 | 16 / 0 / 62 | `see JSON (n=19; examples: eps-mbse-slr-2026-r0007, eps-mbse-slr-2026-r0022, eps-mbse-slr-2026-r0025, eps-mbse-slr-2026-r0026, eps-mbse-slr-2026-r0028)` |
| Reuse target/context | 18 / 39 / 35 | 2 / 1 / 3 | 16 / 38 / 32 | 5 / 2 / 7 | 13 / 37 / 28 | `see JSON (n=18; examples: eps-mbse-slr-2026-r0007, eps-mbse-slr-2026-r0018, eps-mbse-slr-2026-r0022, eps-mbse-slr-2026-r0025, eps-mbse-slr-2026-r0026)` |
| Applied/demonstrated reuse signal | 2 / 19 / 71 | 0 / 2 / 4 | 2 / 17 / 67 | 0 / 5 / 9 | 2 / 14 / 62 | `eps-mbse-slr-2026-r0035, eps-mbse-slr-2026-r0145` |
| EPS-specific reuse/tailoring | 2 / 62 / 28 | 2 / 4 / 0 | 0 / 58 / 28 | 2 / 10 / 2 | 0 / 52 / 26 | `eps-mbse-slr-2026-r0045, eps-mbse-slr-2026-r0085` |

### Interpretation of the matrix

- Direct representation signals: `eps-mbse-slr-2026-r0019, eps-mbse-slr-2026-r0045, eps-mbse-slr-2026-r0085`. Direct qualifying-relation leads: `eps-mbse-slr-2026-r0045, eps-mbse-slr-2026-r0085`. These are not final EPS-thread inclusions.
- The only direct explicit model-input/assumption signal under the rubric is `eps-mbse-slr-2026-r0045`; it does not supply a corpus-wide comparison of values, provenance, margins, or source locations.
- Direct abstraction/fidelity signals: `see JSON (n=21; examples: eps-mbse-slr-2026-r0003, eps-mbse-slr-2026-r0004, eps-mbse-slr-2026-r0007, eps-mbse-slr-2026-r0022, eps-mbse-slr-2026-r0026)`. No saved metadata directly identifies a deliberate omitted phenomenon/model-boundary exclusion under the strict rule.
- Direct reuse/tailoring mechanisms: `see JSON (n=21; examples: eps-mbse-slr-2026-r0007, eps-mbse-slr-2026-r0018, eps-mbse-slr-2026-r0022, eps-mbse-slr-2026-r0025, eps-mbse-slr-2026-r0026)`. EPS-specific reuse/tailoring signals: `eps-mbse-slr-2026-r0045, eps-mbse-slr-2026-r0085`. Application wording is a metadata lead only, not independent reuse evidence.

## Primary-query coverage audit

| RQ1 concept | Existing Scopus/IEEE coverage | Assessment before probe | Audit conclusion |
|---|---|---|---|
| Representation / EPS relations | Explicit EPS names, functional EPS/budget, components, structured-model/engineering-relation Stream B, direct EPS digital-twin and control/interface sensitivities | Direct | Strong discoverability coverage; eligibility relation remains full-text dependent. |
| Purpose / lifecycle | Requirements, functions/behavior, architecture, interfaces, traceability, parametrics, V&V, conceptual/concurrent routes | Not a single purpose gate by design | Appropriate: making purpose mandatory would create recall loss; metadata gives broad task coverage. |
| Inputs / assumptions | Power/energy budgets, generation/storage, conditioning/distribution, load profile; E1 added margins/modes/control/interface | Types direct; detailed reporting incidental | Material detailed-input gap justified the IA probe. It returned frozen records only. |
| Abstraction / fidelity | Reference-model and conceptual-design language | Fidelity/abstraction/omission vocabulary incidental | Material gap justified AF probe. It returned frozen records only. |
| Reuse / tailoring | `reference model`; reuse/reusable in outcome sensitivity only | Tailoring assets/mechanisms incidental | Material gap justified RT probe. It yielded no new plausible candidate. |

## Isolated RQ1 gap probes

The gap probes were run only because the existing primary query set had the material direct-term gaps above. They are isolated audit artifacts under `SLR/SLR1/searches/rq1-answerability-audit/`; they were **not** merged into the frozen 174 candidates or the 92-record corpus. All used 2013–2026 inclusive, English, eligible scholarly source types, and no open-access filter. IEEE Xplore ran count-only first.

| Query ID | Source / concept | Source total | Retrieved | Frozen duplicate occurrences | New plausible | New irrelevant |
|---|---|---:|---:|---:|---:|---:|
| `S-RQ1-IA-P1` | Scopus / inputs_assumptions | 6 | 6 | 6 | 0 | 0 |
| `S-RQ1-RT-P1` | Scopus / reuse_tailoring | 53 | 53 | 48 | 0 | 5 |
| `S-RQ1-AF-P1` | Scopus / abstraction_fidelity | 1 | 1 | 1 | 0 | 0 |
| `I-RQ1-IA-F1` | IEEE Xplore / inputs_assumptions | 8 | 8 | 8 | 0 | 0 |
| `I-RQ1-RT-F1` | IEEE Xplore / reuse_tailoring | 37 | 37 | 30 | 0 | 7 |
| `I-RQ1-AF-F1` | IEEE Xplore / abstraction_fidelity | 2 | 2 | 2 | 0 | 0 |

| IEEE count-only ID | Concept | Total | Retrieved by count-only | Full successor |
|---|---|---:|---:|---|
| `I-RQ1-IA-C1` | inputs_assumptions | 8 | 0 | `I-RQ1-IA-F1` |
| `I-RQ1-RT-C1` | reuse_tailoring | 37 | 0 | `I-RQ1-RT-F1` |
| `I-RQ1-AF-C1` | abstraction_fidelity | 2 | 0 | `I-RQ1-AF-F1` |

Full probes retrieved **107** raw occurrences: **95** frozen duplicates, **0** new plausible candidates, and **12** new irrelevant raw occurrences (10 unique probe identities). Totals were manageable (1–53 Scopus; 2–37 IEEE) and fully retrieved, so no refinement was needed.

New source-novel records were all metadata-irrelevant (payload/data studies, ADCS/control, generic indices, or communications/physical analyses), not candidates to add. Exact query strings, hashes, source totals, raw JSON, and every DOI/source-ID/title comparison are in the JSON and `worklog.md` in the probe directory.

## Lineage/dependence risk

Named clusters below are based only on repeated title wording; they are not assumed to be independent studies, shared implementations, or qualifying EPS threads.

| Named title cluster | Records | Consequence |
|---|---|---|
| BOREALIS_title_family | 2: `eps-mbse-slr-2026-r0108, eps-mbse-slr-2026-r0115` | Contributes 0 direct reuse-mechanism and 0 direct abstraction/fidelity signals; do not count as independent reuse replications. |
| CubeSat_reference_model_title_family | 10: `eps-mbse-slr-2026-r0007, eps-mbse-slr-2026-r0022, eps-mbse-slr-2026-r0026, eps-mbse-slr-2026-r0028, eps-mbse-slr-2026-r0035, eps-mbse-slr-2026-r0037, eps-mbse-slr-2026-r0047, eps-mbse-slr-2026-r0102, eps-mbse-slr-2026-r0145, eps-mbse-slr-2026-r0146` | Contributes 10 direct reuse-mechanism and 10 direct abstraction/fidelity signals; do not count as independent reuse replications. |
| Nanospace_title_family | 2: `eps-mbse-slr-2026-r0002, eps-mbse-slr-2026-r0086` | Contributes 1 direct reuse-mechanism and 0 direct abstraction/fidelity signals; do not count as independent reuse replications. |
| Team_Xc_title_family | 2: `eps-mbse-slr-2026-r0024, eps-mbse-slr-2026-r0034` | Contributes 0 direct reuse-mechanism and 0 direct abstraction/fidelity signals; do not count as independent reuse replications. |

The CubeSat reference-model title family is the main visible reuse/abstraction concentration. It supports breadth of terminology but risks dominance of conclusions about reusable assets, lifecycle intent, and model abstraction. Separate it from other mission/toolchain contexts during full-text synthesis; do not treat a sequence of interim/model-family reports as independent demonstrations.

## Limits and precise recommendations

### Limits

- 61/92 abstracts are absent and every available abstract is truncated, especially constraining direct metadata inference.
- Scopus provides sparse title-level metadata; IEEE Xplore matching is unfielded and snippets are truncated. Source query matching does not disclose a protocol-qualifying relation.
- Core/supporting are retrieval priorities only. All six core and 86 supporting reports remain pending full-text Route A/B eligibility.
- Candidate counts do not establish detailed RQ1 reporting, independent evidence, or robust comparison. The corpus may map diverse approaches but could have too few independent EPS threads for quantitative or strong comparative conclusions.
- Citation chasing is protocol-required later; it was not performed in this audit.

### Recommendations

1. Proceed to the protocol-defined full-text eligibility pilot, starting with all six core candidates and the direct-signal supporting leads. For every retained Route A/B thread, source-locate EPS anchor, model anchor, and bridge before counting it as RQ1 evidence.
2. Use the protocol input/assumption form verbatim for values/units/time basis, provenance, uncertainty/margin, rationale, trace location, and effect. Preserve not_reported rather than inferring these fields from a budget, simulation, or model label.
3. Separate generic CubeSat/system-model reuse from EPS-thread reuse. Treat the CubeSat reference-model title family as a clustered lineage, not independent replications, and distinguish intended assets from applied/reused instances.
4. Use the audit-probe files only as isolated coverage evidence; do not merge them. Their zero new-plausible yield does not justify changing the frozen corpus or eligibility criteria.
5. After full-text inclusions exist, perform the protocol-required iterative citation chasing and document any evidence-window update separately. That future step, not metadata-only auditing, is the appropriate route for residual recall risk.

## Validation

- JSON parsing and all audit count reconciliations passed.
- All 92 kept records are classified exactly once; 6 core + 86 supporting = 92; 2 A-only + 12 A+B + 78 B-only = 92.
- Each per-record classification retains its candidate ID, tier, primary-database provenance, stream, metadata basis, exact matched terms, and source restriction context in `rq1-answerability-audit.json`.
- Probe full retrieval reconciles: 107 raw occurrences = 95 frozen duplicates + 0 new plausible + 12 new irrelevant occurrences.
- No canonical artifact was modified. Semantic Scholar and Google Scholar were not used.

## Companion machine-readable record

`SLR/SLR1/searches/integration/rq1-answerability-audit.json` contains input hashes, the rubric, all 92 candidate-level classifications, stratified counts and ID lists, query coverage, probe inventory/comparisons, verdicts, recommendations, and validation assertions.
