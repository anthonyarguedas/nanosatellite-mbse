# Supporting protocol for identifying and assessing prior secondary reviews

> **Main review protocol:** [1 — Scope and definitions](protocol.md) · [2 — Discovery and appraisal](protocol-discovery-and-appraisal.md) · [3 — Extraction and synthesis](protocol-extraction-and-synthesis.md)
>
> This is a bounded supporting search used to establish the need for the main systematic review. It is not a tertiary review and does not answer RQ1–RQ3 from secondary-review findings.

## Purpose and relationship to the main review

Before the first final primary-evidence search, identify prior secondary reviews that could overlap the main review and assess whether they already answer all or a material part of its questions. Use the assessment to state why a new systematic review of primary evidence is needed, whether its scope should change, or whether proceeding would be redundant.

This supporting search does only the work needed for that decision. It will:

- identify potentially overlapping completed secondary reviews;
- describe their scope, currency, and methods;
- answer the CRD questions reproduced by Kitchenham and Charters and the four DARE questions at review level;
- compare their coverage with the main review's population, MBSE and EPS boundaries, and RQ1–RQ3; and
- produce a source-located need-for-review assessment.

It will not:

- synthesize findings across reviews;
- treat a review's conclusions as evidence for RQ1–RQ3;
- reconstruct or extract every primary study included by a review;
- pool review results or correct for overlap among their primary-study sets; or
- insert a primary report into the main review merely because a prior review cited it.

Complete this supporting assessment under tasks [`PR-001`](TASKS.md) and [`PR-002`](TASKS.md) before task [`R-002`](TASKS.md). If it identifies a review that may make the main review redundant, do not begin `R-002` until the rationale and, where necessary, the main protocol have been reconsidered and committed.

## Supporting questions

1. **PRQ1 — prior-review coverage.** Which completed secondary reviews identified in Scopus or Web of Science Core Collection have a scope that overlaps space-system MBSE and could include or answer questions about nanosatellite or CubeSat EPS evidence?
2. **PRQ2 — methods and adequacy.** What objectives, sources, restrictions, eligibility criteria, appraisal, extraction, synthesis, study descriptions, treatment of differences, and evidence windows do those reviews report, and how do they answer the CRD and DARE questions?
3. **PRQ3 — need for the main review.** To what extent does each prior review cover the main review's population, intervention and EPS boundary, and RQ1–RQ3, and what uncovered scope, methodological limitation, or currency gap remains?

## Provisions reused from the main protocol

Unless this supporting protocol states otherwise, reuse the following provisions rather than defining parallel rules:

- the common evidence cutoff, restart rules, change recording, and legacy-material policy in [Part 1](protocol.md#review-status-and-restart-policy);
- the definitions of `P`, `E_H`, `E_F`, `E`, `M_H`, `M_B`, `M`, `R`, `G_model`, `G_structure`, and `C1` in the [main search strategy](protocol-discovery-and-appraisal.md#search-streams-and-set-construction);
- the Scopus and Web of Science Core Collection boundaries and the interface behavior validated under `S-D01` and `S-D02`;
- the pilot-versus-final-event distinction, event documentation, retrieval-completeness, source-failure, zero-versus-null, and no-partial-import rules in [Pilots and final search events](protocol-discovery-and-appraisal.md#pilots-and-final-search-events);
- the UTF-8 JSON, bibliographic transfer, reproducible deduplication, manifest, normalized-versus-original metadata, and Git audit-trail rules in [Data management and audit trail](protocol-discovery-and-appraisal.md#data-management-and-audit-trail);
- the main review's full-text retrieval sequence and its treatment of `not_retrieved`, adapted only to the secondary-review eligibility criteria below;
- the report-versus-record distinction and version-handling principles in [Units of evidence and counting](protocol.md#units-of-evidence-and-counting); and
- coding confidence, evidence references, model-use safeguards, human adjudication, discrepancy recording, and rights-sensitive fallback principles in [Sole-reviewer extraction and verification](protocol-extraction-and-synthesis.md#sole-reviewer-extraction-and-verification).

The supporting search has separate event IDs, records, reports, decisions, extractions, counts, and outputs. Common schemas and a common log file may be reused, but every row must carry a separate supporting-search namespace and supporting records must never be merged into the main primary-evidence candidate set, denominator, PRISMA flow, or analytic units. A DOI may be cross-referenced between the two processes without sharing a decision or extraction.

## Information sources and limits

Search only:

- **Scopus**; and
- **Web of Science Core Collection** on the Clarivate Web of Science platform.

These multidisciplinary citation databases are used because the target objects are completed secondary reviews, which are expected to be more widely indexed than individual technical reports and embedded EPS applications. Using two broad, partly overlapping indexes is proportionate to a bounded need assessment, but it is not evidence that every secondary review has been found. Report the source restriction as a limitation and phrase the result as reviews *identified by this search*, not as proof that no other review exists. Apply the main protocol's PRISMA-S search-reporting requirements to these two database searches without presenting the supporting process as a tertiary review.

Search each database from its available inception through the common evidence cutoff in [Part 1](protocol.md). Do not apply the main review's 2011 lower bound: an earlier review could still be relevant to the decision that a new review is needed. Use only report versions available by the common cutoff.

Do not apply a database document-type, subject-area, peer-review, open-access, or language filter during discovery. The full report must be in English for CRD/DARE extraction. Record rather than silently discard a plausible non-English or unretrieved review.

Do not use another database, website search, backward citation search, forward citation search, author contact, or retained-file cache to add supporting-search records. Buruso et al. (2026) is a known item for query validation, not a manually inserted report. It enters the supporting assessment only if a successful final Scopus or Web of Science event retrieves it and it passes normal screening.

## Search strategy

### Additional concept blocks

Reuse the main search blocks named above exactly. Add these two blocks for this supporting search:

- **Broad space context (`X`):** all terms in the main Population block `P`, plus `spacecraft`, `space system`, `space systems`, `space mission`, `space missions`, `space engineering`, `space systems engineering`, `space application`, `space applications`, `space sector`, `space industry`, `satellite`, `satellites`, `SmallSat`, `SmallSats`, `small satellite`, and `small satellites`. These broader terms are discovery terms only. They do not change the main review's nanosatellite population definition.
- **Secondary-review signal (`Q`):** `systematic review`, `systematic literature review`, `systematic mapping`, `systematic mapping study`, `mapping study`, `scoping review`, `literature review`, `literature survey`, `bibliometric review`, `bibliometric analysis`, `evidence synthesis`, `secondary study`, `state-of-the-art review`, `state of the art review`, `survey paper`, and `survey`. The broad `survey` term protects recall for engineering review papers; an empirical questionnaire survey remains ineligible.

Source-native translations may change syntax, phrase delimiters, field wrappers, and validated wildcard use, but not the intended terms or Boolean relationships. Search title, abstract, and author-keyword or equivalent topic fields. Do not require a review document-type tag because conference reviews, mapping studies, and bibliometric studies may be classified differently by the databases.

### Query schedule

Run all four semantic partitions in both sources:

| ID | Boolean form | Purpose |
|---|---|---|
| `PSR1` | `X AND M_H AND Q` | Explicit MBSE reviews in the broad space context |
| `PSR2` | `X AND M_B AND R AND Q` | Reviews using broader structured-system-model terminology |
| `PSR3` | `P AND E AND M AND Q` | Nanosatellite-EPS sensitivity partition without requiring `R` for `M_B` |
| `PSR4` | `X AND (G_model OR G_structure OR C1) AND Q` | Reviews centered on reusable models, reference architectures, or persistent model assets |

The supporting candidate set is `PSR1 ∪ PSR2 ∪ PSR3 ∪ PSR4` across Scopus and Web of Science Core Collection. Retain every record returned by a successful final partition and preserve all source and partition discovery events until cross-source deduplication.

### Piloting and final execution

Under [`PR-001`](TASKS.md), validate the four source-native translations after the relevant Scopus and Web of Science interface behavior has been established under `S-D01` and `S-D02`. Record exact fields, phrase and Boolean behavior, automatic expansion, limits, date handling, result totals, export method, stable identifiers, and completeness checks in a clearly separated supporting-search section of the new-run search log.

Use Buruso et al. as a read-only known item. For each source in which it is indexed and exposes searchable metadata containing the required concepts, the accepted query union must retrieve it. A source that does not index the report is not a query failure. A missed indexed known item requires prospective diagnosis and, if justified, a protocol-consistent translation correction before final execution; it cannot be inserted manually.

Pilot records are diagnostic only. Execute clean final events after the translations are accepted. Apply the main protocol's final-event completeness and failure rules. The electronic search is complete when all four partitions have either completed successfully or failed explicitly in both sources, with no partial import.

## Eligibility criteria

Eligibility assesses whether a report is a potentially overlapping secondary review. It does not apply the main review's primary-study Route A or Route B test to the review report itself.

Include a report when all of the following hold:

1. **Completed secondary report:** its main purpose is to review, map, classify, bibliometrically analyze, or otherwise synthesize a defined body of prior reports. It reports at least one identifiable search or source-selection route. Explicit eligibility criteria, primary-study appraisal, or study-level extraction are not required for inclusion because their absence must remain visible in the CRD/DARE assessment.
2. **Potential scope overlap:** it addresses MBSE or structured systems models in spacecraft, space systems, space missions, satellites, SmallSats, CubeSats, or nanosatellites. A broad space-MBSE review can qualify without EPS-specific findings because determining that omission is part of the need assessment.
3. **Full report:** enough methods and results are available to assess its scope and the CRD/DARE questions.
4. **Date:** an eligible version was available by the common evidence cutoff; there is no lower date limit.
5. **Language:** the full report is in English.

Include weakly reported or methodologically limited reviews if they meet this threshold. CRD/DARE appraisal is not an eligibility filter.

Exclude:

- primary empirical reports, including questionnaire surveys of practitioners;
- review protocols with no completed results;
- narrative background sections, tutorials, opinions, and state-of-practice discussions that report no identifiable literature search or source-selection route;
- reviews of remote sensing, satellite imagery, communications algorithms, payload science, or other application domains with no MBSE or structured-system-model scope;
- general MBSE reviews with no space, spacecraft, satellite, SmallSat, CubeSat, or nanosatellite scope and no separately reported space subset;
- abstracts, posters, slides, metadata stubs, and other insufficient completed reports;
- reports published after the cutoff; and
- non-English full reports.

A review does not need to identify a qualifying EPS thread to enter this supporting assessment. EPS coverage is extracted as an overlap finding rather than used as an inclusion requirement.

## Screening, retrieval, and decisions

Deduplicate Scopus and Web of Science records using the main protocol's identifier and metadata rules. Preserve both discovery events. Treat preprint, online-first, conference, and journal versions according to the main report-identity principles; use all materially informative versions but count one report when no relevant substantive difference exists.

At title and abstract screening, interpret eligibility liberally. Retrieve the full text when the record plausibly describes a review of space-related MBSE, SysML, digital engineering, structured system models, reference models, or reference architectures. Do not require CubeSat, nanosatellite, or EPS terms in metadata.

Assign one source-located full-text decision:

- `include_prior_secondary_review`;
- `exclude_not_secondary_review`;
- `exclude_narrative_or_no_identifiable_search`;
- `exclude_no_space_or_satellite_scope`;
- `exclude_no_mbse_or_structured_system_model_scope`;
- `exclude_insufficient_completed_report`;
- `exclude_wrong_date`;
- `exclude_wrong_language`; or
- `not_retrieved`.

Use one main exclusion reason. Preserve review-like excluded reports in a contextual list, but do not appraise or count them as included prior reviews.

The sole human reviewer makes every final screening decision. Run a blind LLM screen of all normalized title-and-abstract records using the same criteria, followed by a source-based human adjudication of every disagreement. At full text, obtain a blind LLM eligibility decision and a separate audit of the human decision for every model-permitted candidate; otherwise use a delayed human recheck. Apply the authorization, document-coverage, technical-failure, rights, discrepancy, and no-independent-human-review language from the main verification protocol. Model output never determines eligibility automatically.

## Extraction form

Create one compact extraction for each included prior-review report. Do not use the primary-evidence extraction form. Record:

### Identity and provenance

- supporting-search report ID;
- full citation, DOI and other stable identifiers;
- report version and date used;
- review type as stated by the authors and as normalized by the reviewer;
- every Scopus and Web of Science discovery-event and source-record ID;
- duplicate or companion-report relationship and the version chosen for assessment; and
- extractor, verification passes, evidence references, and coding confidence.

### Scope and currency

- stated objective and research questions;
- populations, systems, mission classes, and application domains;
- whether space systems, SmallSats, CubeSats, nanosatellites, and EPS are included and whether their findings are separable;
- MBSE, structured-model, language, tool, artifact, lifecycle, outcome, burden, reuse, and V&V scope;
- review search dates and evidence-window start and end;
- number of records, included reports, and underlying studies as reported, keeping their labels and denominators distinct; and
- author-stated limitations and update status.

### Review methods

- every database, collection, website, manual source, citation route, and expert-contact route searched;
- exact-search availability, search dates, date and language limits, publication-type limits, and other restrictions;
- inclusion and exclusion criteria and how they were applied;
- number of screeners, independence, disagreement resolution, and reported agreement;
- appraisal or validity criteria and how appraisal was used;
- data-extraction fields, number of extractors or checkers, and disagreement handling;
- duplicate-publication handling;
- synthesis method, treatment of qualitative and quantitative evidence, and any pooling;
- investigation of differences, heterogeneity, sensitivity, and publication or reporting bias; and
- availability of protocol, data, extraction forms, code, and excluded-report lists.

### Findings needed only for overlap

- which main-review RQ1, RQ2, and RQ3 dimensions the review explicitly sought or reported;
- whether nanosatellite-EPS evidence was directly extractable, only embedded in broader counts, mentioned without separable results, or absent;
- whether the review used an MBSE and EPS relationship at least as specific as the main review's definitions;
- findings or author conclusions needed solely to understand claimed coverage, without treating them as primary evidence; and
- author-identified and reviewer-identified gaps relevant to the need for the main review, kept separate.

Do not extract every included primary report, recompute the prior review's synthesis, or use its report count as a main-review denominator.

## CRD and DARE assessment

For each included review, answer the following CRD questions with a source-located response and coding confidence:

1. What are the review's objectives?
2. What sources were searched, and what restrictions were applied?
3. What inclusion and exclusion criteria were used, and how were they applied?
4. What criteria were used to assess primary-evidence quality or validity?
5. How were those appraisal criteria applied and used?
6. How were data extracted?
7. How were data synthesized?
8. How were differences among the included evidence investigated?
9. How were data combined, and was that combination reasonable for the evidence?
10. Do the conclusions flow from the evidence presented?

Also code the four DARE questions:

1. Are the inclusion and exclusion criteria described and appropriate?
2. Is the literature search likely to have covered the evidence relevant to the review's own stated scope?
3. Did the reviewers assess the quality or validity of included evidence?
4. Are the included reports or underlying studies adequately described?

Use `yes`, `partly`, `no`, or `unclear`, with a reason and evidence reference for each DARE answer. Judge appropriateness relative to the prior review's stated objective rather than by database count alone. Keep methodological conduct distinct from missing reporting: use `unclear` when the available report does not permit a judgment. Do not calculate an aggregate DARE score, rank the reviews, or use a numerical threshold to decide whether the main review is needed.

## Overlap and need assessment

For each included review, create an overlap matrix containing:

- **population overlap:** `broad_space_only`, `smallsat_in_scope`, `cubesat_or_nanosatellite_in_scope`, `separable_nanosatellite_evidence`, or `none`;
- **EPS overlap:** `direct_and_separable`, `embedded_but_separable`, `mentioned_not_separable`, `absent`, or `unclear`;
- **MBSE-definition overlap:** `at_least_as_specific`, `broader_than_main_review`, `adjacent_only`, or `unclear`;
- **RQ1, RQ2, and RQ3 coverage:** independently code `substantial`, `partial`, `adjacent`, `none`, or `unclear`, with reasons;
- **currency:** last search date, evidence-window end, and the unsearched interval to the common cutoff; and
- **methodological and reporting limitations relevant to relying on that review.**

Then assign one supporting-search disposition, with a narrative justification rather than a mechanical rule:

- `no_substantial_overlap_identified`;
- `partial_overlap_main_review_still_needed`;
- `substantial_overlap_but_scope_or_update_gap_remains`;
- `potential_redundancy_requires_protocol_reconsideration`; or
- `insufficient_information_to_decide`.

A prior review is potentially redundant only when its actual methods and extractable results substantially cover the main nanosatellite population, direct EPS–MBSE relationship, and all three current research questions with adequate currency. A broad space-MBSE review, a shared keyword, or a high DARE profile alone is not enough. Conversely, poor reporting alone does not prove that no overlap exists; preserve uncertainty.

The final need statement must distinguish:

- no review identified by the bounded two-database search;
- reviews identified but outside the direct scope;
- partial or outdated coverage;
- methodological inability to rely on otherwise overlapping coverage; and
- genuinely unresolved possible redundancy.

## Verification and consistency

The sole human reviewer performs the canonical extraction and all final CRD/DARE and overlap judgments. For every included model-permitted review, apply the complete blind LLM extraction, separate canonical-extraction audit, frozen-output reconciliation, human adjudication, rights assessment, and technical-failure rules from the main [sole-reviewer workflow](protocol-extraction-and-synthesis.md#sole-reviewer-extraction-and-verification), using this supporting extraction form rather than the primary-evidence codebook.

Treat these as high-consequence supporting judgments:

- full-text inclusion;
- each DARE answer;
- nanosatellite and EPS separability;
- RQ1–RQ3 coverage;
- the unsearched interval to the main cutoff; and
- the final supporting-search disposition.

Ask the supervisor to audit `min(2, N)` included prior reviews, where `N` is the number included, blind to the canonical extraction and model outputs where feasible. If `N = 0`, ask the supervisor to audit the search strategy and a reproducible sample of full-text exclusions rather than inventing an included-review check. Preserve requested and completed scope and never call an LLM pass independent human review. Supporting-search verification records and discrepancies remain separate from primary-review verification counts.

## Required artifacts and reporting

Create under a distinct supporting-search namespace:

- the accepted Scopus and Web of Science source-native translations and pilot evidence;
- a supporting-search section of the search log and manifest with `PSR*` event IDs;
- the read-only Buruso known-item entry;
- raw final exports and retrieval-completeness evidence;
- normalized and deduplicated records with preserved discovery events;
- title-and-abstract and full-text screening decisions;
- the retrieval log and full-text exclusion table;
- the supporting extraction codebook and per-review extractions;
- model, supervisor, discrepancy, and adjudication records;
- the CRD answer table, DARE question matrix, and scope-overlap matrix; and
- a dated need-for-review statement and methods limitation statement.

Report this supporting process separately from the main review. At minimum report:

- both databases and platforms;
- exact final queries and search dates;
- common evidence cutoff and absence of a lower date limit;
- source-reported, retrieved, deduplicated, screened, full-text, included, excluded, and not-retrieved counts;
- one main reason for each full-text exclusion;
- each included review's CRD/DARE and overlap assessment;
- verification actually performed;
- the final disposition and its effect on the main protocol; and
- limitations arising from using only Scopus and Web of Science, English full text, and no supplementary discovery.

Do not add supporting-search records to the main PRISMA 2020 flow diagram. A compact separate flow table is sufficient because this is a need assessment rather than a tertiary review. In the main review report, summarize the method and conclusion and link to the complete supporting artifacts.
