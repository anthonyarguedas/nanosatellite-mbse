# Protocol for a Systematic Review of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems

- **Review run ID:** `eps-mbse-slr-2026`
- **Protocol version:** `1.5` (frozen)
- **Initial scope-decision approval date:** 2026-08-06
- **Version-1.2 interface/consistency review:** PRESS revisions and fresh validation completed 2026-08-07
- **Version-1.3 genericity amendment and freeze/search authorization:** 2026-08-10
- **Version-1.4 source-coverage amendment and freeze/search authorization:** 2026-08-10
- **Version-1.5 source/completeness amendment and final freeze/search authorization:** 2026-08-10

## Review status and restart policy

This protocol defines a **new systematic review run** (branch `slr1-1.1-restart`) focused on nanosatellite electrical power system (EPS) MBSE. It is not an amendment to, or an update of, the earlier whole-nanosatellite/EPS review (`main` branch).

The earlier searches, screening decisions, corpus, extractions, codebook, synthesis, and manuscript are treated as legacy or pilot artifacts. A failed attempt under version 1.0 was abandoned and its search outputs were removed; it supplies no discovery events, records, decisions, or evidence to this run. In particular:

- no previously identified report is automatically included;
- all records must be found through a documented latest-version search or citation-chasing route and screened against this protocol;
- previous reports may be used only as known-item recall checks when refining the search;
- every included report must be newly extracted from its full text against a new run-specific codebook; prior extraction may be consulted only during a later discrepancy audit and may not supply new-run evidence;
- prior counts and classifications must not be carried into the new synthesis; and
- DOI/title matching may retain a prior corpus ID only as a `legacy_corpus_id`; new-run report-family, report, EPS-thread, reusable-artifact-lineage, tailoring-application, outcome/burden, and V&V-record identifiers must be run-specific.

Version 1.5 prospectively supersedes version 1.4. No valid new-run discovery search was executed under versions 1.3 or 1.4. The dated version-1.2 source-interface diagnostics, version-1.3 genericity/search diagnostics, version-1.4 source-addition/interface gates, and pre-authorization IAF gate are pilots only: they do not create the independent candidate set, and their records, opaque identifiers, or aggregate observations cannot determine evidence membership. Every final discovery method must start in a clean version-1.5 final-run artifact set. Any later deviation must be recorded prospectively in the new run's search or decision log.

## Reporting framework

PRISMA-P (2015) guides this protocol and its amendment history; PRISMA-S (2021) guides the design, execution, preservation, and reporting of every search in [`query-search-plan.md`](query-search-plan.md); and PRISMA 2020 will guide the completed review, abstract, checklist, and flow diagram. These are reporting guidelines, not evidence-validity instruments. Health-review terminology is adapted to this engineering evidence map without inventing clinical effect measures, risk-of-bias tools, or GRADE ratings.

This is a new review, not an update. The completed review will use the PRISMA 2020 flow template for a new systematic review using databases and other sources. Identification and selection are counted at record/report level; report families, EPS threads, reusable-artifact lineages, tailoring applications, outcome/burden records, and V&V records are linked analytic units reported with separate denominators.

Official guidance to use at the applicable stage:

- [PRISMA-P protocols and checklist](https://www.prisma-statement.org/protocols);
- [PRISMA-S search reporting](https://www.prisma-statement.org/prisma-search) and [Rethlefsen et al. (2021)](https://doi.org/10.1186/s13643-020-01542-z); and
- [PRISMA 2020 statement](https://www.prisma-statement.org/prisma-2020-statement), [checklist](https://www.prisma-statement.org/prisma-2020-checklist), [abstract guidance](https://www.prisma-statement.org/abstracts), and [flow templates](https://www.prisma-statement.org/prisma-2020-flow-diagram).

Registration/contact declarations, contributor and guarantor details, and funding/sponsor and competing-interest declarations are intentionally deferred at this stage. Their absence must be stated accurately; this frozen protocol is not represented as administratively PRISMA-P-complete.

## Approval, amendment, and pre-search decision record

- **Initial scope-decision approval date:** 2026-08-06
- **Version-1.2 freeze/search authorization date:** 2026-08-07
- **Version-1.3 amendment approval and freeze/search authorization date:** 2026-08-10
- **Version-1.4 source-coverage amendment approval and freeze/search authorization date:** 2026-08-10
- **Version-1.5 source/completeness amendment approval and freeze/search authorization date:** 2026-08-10
- **Frozen protocol:** `1.5`, retaining the bounded-genericity methodology, authorizing IAF, and incorporating the complete source/query plan
- **Search state at version-1.5 freeze:** prior interface/source/genericity gates complete; version-1.5 amendment pilots remain to be run; no valid new-run discovery search executed
- **Working branch:** `slr1-1.1-restart`

The researcher reviewed the failed version-1.0 run and prospectively approved the methodological scope decisions incorporated into versions 1.1 and 1.2. On 2026-08-10, before any valid final discovery search, the researcher directed version 1.3 so the review could define bounded genericity, map tailoring, and grade the strength of evidence for reusable EPS MBSE artifacts. The researcher then directed version 1.4 to add Inspec through the paired Engineering Village route and to add Springer Nature Link, Advanced Technologies & Aerospace Index on ProQuest, and AIAA Aerospace Research Central. Still before any valid final discovery search, the researcher directed version 1.5 to authorize IAF, include every permitted scripted academic source, complete Stream A and NTRS C1, correct finite T2 and sensitivity terms, and freeze a common evidence cutoff. Versions 1.0 through 1.4 remain superseded pre-search protocols in version control. Version 1.5 is the governing protocol for all valid searches and later review activity from its authorization on 2026-08-10.

| Change | Date | Timing | Rationale and consequence |
|---|---|---|---|
| `1.0` to `1.1` | 2026-08-06 | Before freeze and any valid new-run search | Remove stale search-start claims; extend the evidence window to 2011; expand information sources and admit substantive institutional technical reports; define Buruso (2026) as a secondary-review seed and recall benchmark; make the generic SmallSat exclusion explicit; extract outcome direction and implementation burdens; distinguish V&V scope and object; formalize the study/implementation report-family unit; and clarify that all reported model reuse/tailoring is in scope, with lightweight status only a possible synthesis characterization and never a filter. These decisions were retained in the frozen version 1.2. |
| `1.1` pre-freeze refinement | 2026-08-07 | Before freeze and any valid new-run search | Add Web of Science Core Collection as a seventh independent electronic source after live Topic-search, Core Collection edition, ordinary RIS-export, normalization, and merge-interface validation; harmonize source-supported CubeSat/nanosatellite spellings after logged count/syntax pilots; add `CubeSats` to the NTRS matrix after unique-yield testing; and prespecify Scopus plus Web of Science Core Collection for forward citation chasing. These changes update source, stopping, and reconciliation rules without changing eligibility or the RQs. |
| `1.1` pre-freeze API-pagination refinement | 2026-08-07 | Before freeze and any valid new-run search | Empirically validate the over-one-page current revised-population Scopus S-B1 and IEEE I-B2 API requests; freeze non-secret request templates, source-native ordering and page parameters, two-pass ordered-ID/global-rank reconciliation, retry/stop/total-change behavior, merge preflight, and the hard `retrieved == source total` failure rule. Pilot outputs remain superseded/no-screening artifacts. This changes retrieval reproducibility controls only, not eligibility, concept scope, or other source decisions. |
| `1.1` model-assisted PRESS revision | 2026-08-07 | Before freeze and any valid new-run search | Correct population, structured-model, relation, and EPS variants in every source translation; replace the incomplete NTRS strategy with a complete 108-cell P×M baseline and full-E local Stream-A tag; freeze an attachment-first ESA dictionary/matcher/fixture implementation; remove unproven Scopus, WoS, and IEEE discovery type filters; document automatic-expansion and exact-day controls; clarify selected O/V probes and structural Stream-A subsets; and run fresh no-screening pilots. MAJOR-06 API pagination was delegated to a subagent with the academic-research package. Eligibility and RQs are unchanged. |
| `1.1` to `1.2` | 2026-08-07 | Final pre-search freeze, before any valid new-run search | Incorporate the completed PRESS corrections and related pre-freeze validations; record researcher authorization; and establish version 1.2 as the governing protocol. All pilot outputs remain superseded/no-screening artifacts and every final discovery method must start from a clean post-authorization artifact set. |
| `1.2` to `1.3` | 2026-08-10 | Prospective post-freeze amendment, but still before any valid new-run discovery search, screening, codebook creation, or extraction | Add nested RQ1-G; define genericity as bounded, artifact-specific transferability relative to a declared applicability envelope; distinguish artifact reuse from method/workflow reuse and author claims from demonstrated transfer; add reusable-artifact-lineage and tailoring-application units; prescribe a non-compensatory A/E/C/T/P/I profile and `NA`, `G0`--`G4` evidence tiers; and add separately provenance-coded precise-artifact (`B-G`), conservative central-asset (`B-C1`), and model-coupled tailoring (`B-T2`) recall partitions to Stream B after model-assisted no-screening pilots found opaque source-ID yield outside the version-1.2 B1/B2 union. It rejects an unsplit G×relation formula because architecture could self-satisfy the relation, preserves relation-free exact-artifact recall, expands the NTRS final matrix to 660 finite cells after preserving all ten source-representable population forms, and versions the ESA route matcher/fixtures. The amendment also records the empirically observed Scopus terminal-page and IEEE zero-result conventions without weakening total/ID/two-pass reconciliation. Eligibility, Route A/B, RQ2, RQ3, and the seven information sources are unchanged. Affected artifacts are this protocol, the query plan, search log/dictionary and API reconciler, the not-yet-created extraction codebook, and planned registries; no candidate, screening, or evidence record existed to revise. |
| `1.3` to `1.4` | 2026-08-10 | Prospective source-coverage amendment, still before any valid new-run discovery search, screening, codebook creation, or extraction | Expand the independent electronic baseline from seven sources to eleven databases/collections searched through ten interfaces: add Inspec alongside Compendex in every simultaneous Engineering Village event, and add the full Springer Nature Link publisher platform, the exact Advanced Technologies & Aerospace Index on ProQuest, and source-wide AIAA Aerospace Research Central. These additions reduce dependence on the original indexes, strengthen engineering/aerospace and publisher-hosted coverage, and retain cross-source overlap as provenance rather than deduplicating at discovery. Freeze source boundaries, normal-interface controls, complete pagination/ordered-ID reconciliation, native export and merge preflights, exact-day handling, source-overlap provenance, and fail-closed access/identifier behavior described in the query plan. The no-screening source pilots and off-topic AIAA adapter gates remain non-candidate diagnostics. Eligibility, RQs, evidence routes, extraction fields, and the version-1.3 genericity methodology are unchanged. Affected artifacts are this protocol, the query plan, search log, search-strategy linter, browser adapters/domain notes, source aliases, and final-run manifests; no candidate, screening, codebook, extraction, or evidence record existed to revise. |
| `1.4` to `1.5` | 2026-08-10 | Prospective source/completeness amendment, still before any valid new-run discovery search, screening, codebook creation, or extraction | Authorize IAF Digital Library as an IAC-proceedings-only twelfth collection and eleventh interface, ensuring that every permitted source adapter in the academic-search scripts directory maps to an authorized source while arXiv, Semantic Scholar, and Google Scholar remain forbidden. Complete direct-source Stream A with `A3 = P ∧ E_high ∧ M_broad`; complete IEEE T2 finite inflections; expand NTRS C1 from 23 to 51 atoms and the matrix from 660 to 940 cells; standardize finite V1/O1 queries and local tags; freeze 2026-08-10 as one evidence cutoff for all electronic and citation sources; and extend lint to all eight direct interfaces and 88 query blocks. Prior pilots remain non-candidates, and the mandatory pre-final amendment pilots are listed separately. Eligibility, RQs, evidence routes, and extraction rules are unchanged. |

The identified choices were reviewed and retained or amended as follows:

1. **CubeSat/nanosatellite population.** PocketQube/picosatellite-only, CanSat, and generic `SmallSat`/small-satellite studies are excluded. Mixed studies remain eligible only when the source identifies a CubeSat/nanosatellite-class case and its evidence is separable; searches do not deliberately target excluded platforms.
2. **Evidence window.** The common first-formal-publication window is 2011-01-01 through 2026-08-10 for every electronic source and citation route, regardless of execution date. Source controls that admit later 2026 records retain their raw totals and apply the same exact-day cutoff. Any update requires a prospective amendment and complete reruns to one new common cutoff.
3. **Expanded source coverage.** The electronic baseline comprises twelve databases/collections searched through eleven interfaces: Scopus; Web of Science Core Collection; IEEE Xplore; Compendex and Inspec searched simultaneously on Engineering Village; the full Wiley Online Library and Springer Nature Link publisher platforms; the exact Advanced Technologies & Aerospace Index on ProQuest; source-wide AIAA Aerospace Research Central; IAF Digital Library restricted to IAC proceedings; the full public ESA Indico event database; and the NASA Technical Reports Server (NTRS). This includes every permitted source-specific adapter in `/Users/antho/agent-tools/academic-research/skills/academic-search/scripts`; Web of Science is additionally retained through its normal interface. Each source uses the boundary and method below and in the query plan.
4. **Open, direction-neutral RQ2 set.** This avoids directional outcome-reporting bias. Beneficial, null, mixed, and adverse outcomes and implementation burdens are extracted when explicitly attributed to a qualifying EPS thread. Reliability/mission assurance, reproducibility/reuse, and integrability/interoperability remain priority domains; all domains and directions use the same attribution and evidence rules.
5. **Tiered and differentiated V&V records.** A named EPS target, or a system-wide target explicitly linked to EPS, together with a model-to-V&V bridge and reported V&V method/intent/artifact establishes the lowest linked tier. EPS-specific versus system-wide EPS-linked scope and the object of V&V are coded separately. Missing criterion, execution, verdict, or timing remains missing evidence and cannot support a higher tier.
6. **Broad Stream B.** This is necessary because embedded EPS threads may be absent from metadata. Query partitioning, count pilots, conservative title/abstract retention, and separate unique-yield accounting control workload without imposing an EPS keyword.
7. **Buruso (2026) as secondary evidence only.** The review is used for positioning, a deferred recall benchmark, and logged citation chasing. It does not supply primary evidence or bypass independent discovery and new screening.
8. **New extraction for every included report.** Legacy extraction and synthesis files were removed. Retained source Markdown/PDF files may be reused only after independent rediscovery and new screening.
9. **All model tailoring is in scope.** Eligibility and discovery do not require a lightweight implementation. Extract every reported reuse/tailoring approach and its implementation footprint; discuss lightweight, scalable, comprehensive, or resource-intensive characteristics only where the source or extracted evidence supports them.
10. **Genericity is bounded and artifact-specific.** The review grades evidence for transferability of an identifiable EPS-linked model artifact only within its declared applicability envelope. A source label such as generic, reference, template, reusable, configurable, modular, scalable, or open is not itself demonstrated genericity. Method/workflow reuse is mapped separately and cannot establish artifact genericity without persistent EPS model content and source-supported lineage.
11. **Reusable-artifact and tailoring terms expand recall but never gate eligibility or grading.** Source-adapted precise-artifact, conservative central-asset, and model-coupled tailoring partitions are added within Stream B because no-screening pilots found opaque-ID additions beyond existing B1/B2 retrieval. G/C1/T2 words are not mandatory across core searches, and discovery through an expansion is not evidence that a model is reusable or tailored. Every included artifact is assessed from full text under the same profile regardless of discovery route.

Pre-search anti-anchoring controls are part of this approval:

- legacy and failed-run search results, screening, corpora, codebook, extractions, scoping review, and manuscript were removed before the valid version-1.5 search;
- `markdown/` and `pdfs/` were retained only as a source-file cache outside the search evidence base;
- retained files cannot supply candidates, eligibility decisions, IDs, or extracted data;
- matching against retained files is deferred until the complete successful-source candidate set and explicit failure register for all twelve planned electronic databases/collections are frozen, and matches serve only as recall and retrieval checks; and
- old corpus or extraction data may not be reconstructed from Git history during new search or screening.

Any change after final freeze requires a prospective entry stating its date, exact decision or wording change, rationale, affected artifacts and records, consequences for synthesis, and protocol version.

## Review objective

To synthesize how nanosatellite EPSs are represented through MBSE, why those models are constructed, which inputs and assumptions they depend on, how they are reused or tailored, what bounded genericity is specified or demonstrated for identifiable EPS-linked artifacts, which beneficial, null, mixed, or adverse EPS-linked outcomes and implementation burdens are reported, and how EPS verification and validation (V&V) are integrated before physical integration or test.

For reusable artifacts, the review will map the declared applicability envelope, reusable core, variation points, tailoring pathway and footprint, demonstrated target contexts, post-tailoring assurance, dependence, and genericity evidence tier. It will not certify context-free, universal, or “true” genericity.

The analytic scope includes both:

1. **EPS-primary MBSE**, where the EPS is the principal modeled system or viewpoint; and
2. **embedded EPS model threads**, where a broader nanosatellite model contains an explicit, extractable chain linking EPS content to systems-engineering artifacts or activities.

Generic whole-spacecraft MBSE evidence does not answer the research questions merely because EPS and another artifact occur in the same report.

## PICOC

| Population | Intervention | Comparison | Outcome | Context | Related RQ(s) |
|---|---|---|---|---|---|
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-primary MBSE or an explicit embedded EPS model thread | Not required | EPS representation, model purpose, required inputs and assumptions, abstraction, artifact identity/lineage, declared applicability envelope, reusable core, variation points, tailoring and its footprint, demonstrated coverage and assurance, bounded-genericity evidence tier, and required roles/resources | Nanosatellite systems engineering across the lifecycle | RQ1, including RQ1-G |
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-linked MBSE artifacts, analyses, and model-enabled activities | When reported: document-centric practice, manual analysis, alternative toolchain, previous mission/model, or other explicit comparator | Beneficial, null, mixed, or adverse EPS-linked technical and engineering-process outcomes and implementation burdens, especially reliability/mission assurance, reproducibility/reuse, and integrability/interoperability | Nanosatellite development and decision making | RQ2 |
| EPSs of orbital CubeSat/nanosatellite-class missions | EPS-specific or system-wide EPS-linked model-based V&V before physical integration or test | Separate or document-based V&V, manual checking, another method, or no comparator when reported | V&V scope and object, traceability to V&V artifacts, executable checks, verdicts, virtual integration, and model-to-test continuity | Pre-physical analysis and V&V, with downstream physical links recorded separately | RQ3 |

## Research questions

1. **RQ1 — representation, purpose, and prerequisites.** How are nanosatellite EPSs represented in EPS-primary MBSE models and embedded EPS model threads; for what stated purposes; what inputs, assumptions, abstraction choices, roles, skills, and resources are reported; and how are the models reused or tailored?

   **RQ1-G — bounded reuse and tailoring.** For each eligible EPS model thread, what, if any, reusable EPS MBSE artifact and artifact lineage is reported; what declared applicability envelope, reusable core, variation points, dependencies, and tailoring pathway does it have; which materially distinct target-context applications and post-tailoring assurances are reported; and at what non-compensatory evidence tier is bounded reuse supported?

2. **RQ2 — EPS-linked outcomes, burdens, and evidence.** Which beneficial, null, mixed, or adverse EPS-specific technical or engineering-process outcomes, and which implementation burdens, are explicitly attributed to EPS MBSE artifacts or model-enabled activities; through what mechanisms; and with what supporting evidence?

3. **RQ3 — EPS-linked pre-physical V&V.** How are EPS-specific or system-wide EPS-linked pre-physical V&V activities connected to EPS requirements, model elements, analyses, or interfaces; what is the object of verification or validation; and what level of preparation, execution, result reporting, and model-to-test continuity is demonstrated?

RQ1–RQ3 are co-primary mapping questions. RQ1-G is a prespecified analytic stratum nested within RQ1, not a fourth eligibility question: an eligible report need not claim genericity or report reuse. Within RQ2, reliability/mission assurance, reproducibility/reuse, and integrability/interoperability are prespecified priority presentation strata, not eligibility filters; the open outcome/burden set is coded and reported direction-neutrally without post-hoc suppression of other domains.

## Operational definitions

### Nanosatellite population

An eligible platform is an actual or intended orbital spacecraft that the source identifies as a CubeSat or nanosatellite, including recognized CubeSat form factors even when a particular implementation falls outside a strict 1--10 kg mass definition. A reference, template, or early-phase design model may qualify without a named or realized mission when its stated target population is orbital CubeSat/nanosatellite development.

`SmallSat` and “small satellite” are not treated as synonyms for the eligible population. A generic SmallSat/small-satellite label alone does not establish CubeSat/nanosatellite-class eligibility, even when the report may be relevant to broader small-spacecraft engineering.

Exclude:

- CanSats and other non-orbital educational demonstrators;
- PocketQube/picosatellite-only studies unless a separable CubeSat/nanosatellite case is also reported;
- generic SmallSat/small-satellite studies, larger small satellites, or conventional spacecraft unless the source also identifies a CubeSat/nanosatellite-class case and its results can be extracted separately; and
- mixed-platform evidence when nanosatellite-specific findings cannot be separated.

### EPS boundary

EPS content may include power generation; solar arrays; storage and battery management; conversion, conditioning, regulation, and distribution; protection, monitoring, and control; electrical buses and harnesses; power interfaces; operational modes; load and energy profiles; power/energy budgets and margins; degradation; faults and fault management; and relevant requirements.

Other subsystems are in scope only as explicit EPS loads, interfaces, environmental dependencies, operating-mode drivers, or sources of EPS requirements. Their internal design is not synthesized.

### MBSE qualification

A report need not use the acronym “MBSE,” but it must describe a structured system model used for a systems-engineering purpose and provide extractable evidence of modeled elements and relationships across at least two systems-engineering concerns, such as requirements, functions/behavior, architecture, interfaces, parametrics/analysis, design decisions, or V&V. For report eligibility, those relationships must involve the same EPS entity or thread used to justify inclusion; unrelated report-level MBSE does not qualify otherwise isolated EPS content.

Examples may include SysML, Arcadia/Capella, object-oriented systems models, reference models, or connected digital-engineering environments. A stand-alone circuit model, battery model, SPICE/MATLAB/Simulink simulation, optimization, power-budget spreadsheet, or component-sizing calculation is not MBSE by itself. It qualifies only when its inputs or outputs are explicitly bound, traced, transformed, or otherwise linked to a structured system model.

### Bounded genericity, reusable artifacts, and tailoring

For RQ1-G, **genericity means bounded transferability**: the extent to which the documented core of an identifiable EPS-linked MBSE artifact can be adopted or tailored for stated target contexts within a declared applicability envelope. Genericity is not an intrinsic or context-free property of a paper, diagram, language, tool, repository, workflow, or model merely because it is called generic, reference, standard, template, reusable, configurable, modular, scalable, lightweight, open, or mission-agnostic. The review assesses the support for a claim, not metaphysical or universal “true genericity.”

A **reusable EPS MBSE artifact** is a source-identifiable structured-model asset or documented package of assets that contains, or is explicitly bound to, a qualifying EPS thread and its modeled relations. It may be a reference/template model, metamodel or profile carrying EPS semantics, model library or pattern, interface contract, parametric-model package, transformation/generator with persistent model content, or a larger reusable spacecraft model with a separately reconstructable EPS portion. Public availability is recorded but is not required. A reusable method, workflow, toolchain, transformation procedure, or guidance document is coded as **method/workflow reuse** unless persistent EPS model content and its lineage are identified; a specific-mission artifact does not become generic merely because its method might be reused.

An **artifact lineage** links a base artifact and any versions or derived instances for which identity and continuity are source-supported by a name/version, repository or package identifier, explicit derivation, transformation record, shared model identifiers, or a reconstructable retained core. Shared authors, organization, tool, topic, terminology, or diagrams alone are insufficient. Materially changed cores or unresolved identity are kept as separate/uncertain lineages rather than merged.

A **declared applicability envelope (DAE)** is the source-locatable intended scope for reuse: target platform or mission context, intended lifecycle use or decision, EPS/model boundary and abstraction, material dependencies and required inputs, applicable architecture/interface/tool assumptions, and stated exclusions or limits. At minimum for the genericity profile, the source must report the intended target class/context, intended lifecycle use or decision, EPS/model boundary and abstraction, and at least one material condition, dependency, required input, or exclusion. Evidence may be assembled across explicitly linked reports while preserving the provenance of each field, but an observed mission, a broad “for CubeSats” label, or reviewer expertise cannot fill a missing envelope.

A **reusable core** comprises the model elements, relations, constraints, interfaces, semantics, or packaged assets stated or reconstructably shown to persist across applications. A **variation point** is a source-described location, option, range, rule, or dependency by which the core may vary. **Tailoring** is a source-described configuration, parameterization, selection, specialization, extension, deletion/substitution, interface mapping, transformation/generation, or explicitly justified unchanged adoption that produces or selects a target-specific instance. A parameter sweep or scenario run in one unchanged mission model is analysis, not a cross-context tailoring application. Unstructured reconstruction may demonstrate reuse of a method, but it supports artifact reuse only when lineage and retained core are established.

A **tailoring application** is one artifact-lineage-to-target-context application. The artifact's originating development case counts only when the source identifies it as an adoption/configuration of the same reusable core and reports the retained-core/change or justified-as-is evidence; merely being the mission in which the artifact was created does not count as transfer. Its context tuple records the mission/platform, lifecycle purpose, EPS architecture and interfaces, environment/operations, tool/model configuration, relevant envelope dimensions, what core remained, what changed or was intentionally unchanged, rationale, implementation footprint, and result. Two applications are materially distinct only when they differ on at least one DAE dimension that exercises or tests the claimed reuse; two reports, scenarios, revisions, or names for the same underlying implementation are not distinct applications.

**Demonstrated coverage** is the subset of the DAE represented by reported tailoring applications. It is never assumed to equal the claimed envelope. **Post-tailoring assurance** requires an identifiable tailored configuration, an intended-use-relevant criterion or oracle, an executed check after tailoring, and a reported result or verdict. A syntax, import, or build check alone is insufficient unless that is itself the stated intended use. Assurance may cross-link to RQ3, but it becomes a direct RQ3 V&V record only when the existing EPS target–model-to-V&V bridge–method/intent rule is also met; validation of a base model does not transfer automatically to a derived instance.

Every eligible EPS thread receives an RQ1-G disposition of `not_an_artifact_or_method_only`, `artifact_no_reuse_indication`, `genericity_or_reuse_claim`, `reported_reuse_without_bounded_specification`, `bounded_reuse_candidate`, or `unclear`. Where an EPS-linked artifact is identifiable, the following non-compensatory profile is coded at artifact-lineage/version/scope level; method/workflow-only cases receive `NA` without inventing an artifact lineage. The letters are local profile labels, not the Population block used in searching:

| Gate | Minimum source-supported evidence |
|---|---|
| **A — artifact/lineage** | Identifiable EPS-relevant artifact and source-locatable lineage across any claimed instances. |
| **E — envelope** | Minimum DAE, with each component and source location retained. |
| **C — core and variation design** | Identified reusable core plus variation points, tailoring rules, and prerequisites; alternatively, an explicit bounded reuse-as-is rule. |
| **T — transfer/tailoring** | Actual target-context applications with the retained core, changes or justified unchanged adoption, and rationale reported; credited contexts must be materially distinct. |
| **P — post-tailoring assurance** | For every context credited toward demonstrated reuse, an intended-use-relevant criterion, executed post-tailoring check, and result/verdict. |
| **I — independent transfer** | At least one credited context is separately adopted or tailored and post-tailoring assured by an adopter team independent of the artifact's originating implementation family, with the adoption and result corroborated in a report, artifact, or data record attributable to that independent adopter/evaluator rather than only asserted by the originator. An external organization/team normally qualifies when lineage continuity is established; a same-organization separate team qualifies only when the source supports separate implementation control, no material participation by the originating implementation team, and a distinct assured application. Independent review of the originator's unchanged instance, disjoint author lists, companion reports, a shared underlying implementation, and unclear relationships do not qualify. |

Code each gate as `demonstrated`, `partial`, `not_reported`, `uncertain`, `none`, or narrowly justified `not_applicable`, with source locations and confidence. **Only `demonstrated` satisfies a gate required by a tier.** `not_applicable` may describe a gate not required at the assigned lower tier but never substitutes for a required gate; `none` means the source affirmatively indicates that the condition was absent or failed, whereas `not_reported` means it cannot be assessed. `partial`, `not_reported`, `uncertain`, `none`, `not_applicable`, and reviewer-inference-only evidence fail a required gate but—apart from source-supported `none`—are not evidence that the underlying capability is absent. Explicit unchanged adoption may satisfy T only when its conditions, target context, retained core, and rationale are reported; it never waives E, C, or P.

Assign the highest cumulative **genericity evidence tier** supported:

| Tier | Minimum conditions | Interpretation |
|---|---|---|
| **`NA`** | No identifiable EPS model artifact, or method/workflow reuse only | Artifact genericity is not rated; method/workflow reuse remains in RQ1. |
| **`G0_artifact_only`** | An EPS-linked artifact is identified, but no genericity/reuse claim or application is reported | No genericity evidence reported; not evidence of non-reusability. |
| **`G1_claimed_or_unbounded`** | A is supported and the source makes a genericity/reuse claim or reports a traceable but unbounded reuse indication | Claim or indication only; bounded reuse is not established. |
| **`G2_bounded_reuse_specified`** | A ∧ E ∧ C | Prospective bounded reuse is specified; actual transfer need not have been demonstrated. |
| **`G3_bounded_reuse_demonstrated`** | G2 ∧ T for at least two materially distinct target contexts ∧ P for every credited context | Bounded reuse is demonstrated, potentially within one dependent implementation family. |
| **`G4_independently_corroborated`** | G3 ∧ I, with the independent application itself meeting T and P | Bounded transfer is independently adopted and assured, still only for the demonstrated subset of the DAE. |

The cumulative caps are explicit: missing A yields `NA`; A without E∧C cannot exceed G1; one assured application, multiple unassured applications, the uninstantiated originating development case, or repeated reports of one application cannot exceed G2; two materially distinct assured applications of the reusable core can reach G3; and only an independently adopted/tailored, independently corroborated, and assured credited application can reach G4. A wider claimed envelope, a larger model, more parameters, public artifact availability, a higher report-quality score, or strength on another gate cannot compensate for a missing gate or produce a higher tier. Tiers are ordinal evidence classes, not numeric scores, model-quality rankings, maturity levels, benefit measures, prevalence estimates, or guarantees of suitability for untested contexts. Assign one highest tier only after checking every lower-tier prerequisite; retain the gate vector alongside it so artifacts tied at a tier are not implied to be equivalent. Claim concordance (`not_evaluated`, `supported_in_tested_contexts`, `partially_supported`, `mixed`, `not_supported`, or `unclear`) and envelope breadth are reported separately. Failed tailoring, out-of-envelope applications, burdens, and contradictory evidence are retained rather than netted into the tier.

The phrase **generic whole-spacecraft MBSE** in the exclusion rule means whole-spacecraft evidence with no qualifying EPS thread; it is not a judgment about the model's genericity. A whole-spacecraft reusable artifact may receive an RQ1-G profile only for its EPS-linked content and only after normal Route A/B eligibility is established. Genericity status and tier never determine report eligibility.

### Eligible EPS evidence routes

A full-text report is assigned one of two mutually exclusive eligibility routes. Route A takes precedence only when the stated objective, modeled viewpoint/boundary, and substantive method or results center on EPS. Otherwise, a qualifying report is Route B. A report may contain multiple EPS threads, but its report-level route remains fixed.

- **Route A — EPS-primary MBSE:** the EPS, electrical-power viewpoint, or a defined EPS function/architecture is the principal modeled boundary, and the report provides an identifiable EPS model artifact plus at least one explicit relation involving that EPS content and a second systems-engineering concern.
- **Route B — embedded EPS model thread:** a broader nanosatellite MBSE report contains at least one qualifying EPS thread meeting all three conditions below.

A qualifying embedded EPS model thread requires:

1. an **EPS anchor**: a named EPS requirement, function, behavior, component, interface, mode, load/profile, budget, parameter, constraint, or hazard;
2. a **model anchor**: an identifiable representation of that EPS content in a structured system-model artifact or explicitly connected analysis model; and
3. an **explicit bridge**: a reported, source-locatable relation connecting the EPS anchor to a second concern such as a requirement, behavior, architecture/interface, analysis, decision, output, or V&V artifact. Eligible bridges include allocation, trace, satisfy/refine/verify relations, interface/flow, parametric binding, transformation, and data mapping.

Containment in a generic spacecraft breakdown, an EPS label, or an equipment-list entry may establish where an anchor appears but is not a sufficient bridge by itself. The source need not name a formal relation type, but the relation's endpoints and meaning must be reconstructable. The anchors and bridge must be supported by text, a figure/table, a model extract, a trace record, or another locatable source. Keyword presence, reviewer inference, or report-level co-occurrence is insufficient.

### MBSE-enabled outcomes and implementation burdens versus EPS engineering outputs

An **EPS engineering/model output** is a result such as minimum state of charge, power margin, battery capacity, solar-array area, voltage/current, energy balance, or a selected architecture. Such outputs are extracted for RQ1 and may support RQ2 or RQ3, but they are not automatically evidence of MBSE value.

An **RQ2-eligible outcome or implementation-burden record** must provide:

1. an eligible EPS model thread or named EPS-linked model artifact/activity;
2. a reported beneficial, null, mixed, or adverse technical or engineering-process outcome, or an implementation burden, explicitly attributed to that EPS artifact/activity rather than to an EPS technology choice; and
3. extractable result or claim wording and the evidence, if any, offered for it.

The proposed model-enabled mechanism is extracted when stated and coded `not_reported` when absent; missing mechanism reporting lowers interpretability but does not erase an otherwise explicit EPS-attributed record. A generic claim about MBSE in a report containing EPS material is not EPS-specific evidence. Assertion-only claims may be retained but must be classified as unsupported rather than as demonstrated effects.

A null outcome requires an evaluated result indicating no observed effect or difference; it is not synonymous with `not_reported`, missing evidence, or absence of a claim. Split separable benefits, adverse effects, null findings, and burdens into atomic records. Use `mixed/conditional` only when direction varies inseparably by scenario, metric, actor, or condition. An implementation burden may coexist with a beneficial outcome and must not be netted against it by reviewer inference. Generic project- or report-level MBSE burdens may be retained as RQ1 context, but they enter direct RQ2 synthesis only when explicitly attributed to the qualifying EPS thread.

A power or energy margin alone is not an EPS-reliability result. Reliability coding requires an explicit connection to failure, fault tolerance, availability, risk, assurance, or another defined reliability construct. Reproducibility/reuse and integrability/interoperability claims must likewise be kept distinct from mere model availability or diagram co-occurrence.

### Direct EPS-linked pre-physical V&V

An **EPS-linked RQ3 V&V record** requires:

1. an **EPS target**: a named EPS requirement, model element, parameter, mode, interface, behavior, function, or hazard, or a system-wide target explicitly decomposed, allocated, or traced to such EPS content;
2. an **explicit model-to-V&V bridge**: a trace, shared identifier, binding, port/data mapping, transformation, generated artifact, allocation, or other reported link; and
3. a **V&V method, intent, or artifact**: the source presents the activity as verification, validation, compliance/requirement checking, virtual integration, a model-derived test activity, or another V&V function.

Classify each candidate record independently by **linkage scope**:

- **`eps_specific`:** the V&V target and activity are explicitly EPS-specific;
- **`system_wide_eps_linked`:** a broader system-level activity contains a named, reconstructable EPS target and bridge;
- **`system_wide_cooccurrence`:** system-wide V&V and EPS content occur in the same report without the required direct link; or
- **`unclear`:** the scope cannot be resolved from the report.

Both `eps_specific` and `system_wide_eps_linked` records may enter direct RQ3 synthesis, but they are always reported separately and the scope of any result or verdict is retained. `system_wide_cooccurrence` is a near miss and cannot support an EPS-specific conclusion.

Classify the **object of V&V** separately from scope and execution environment:

- **model verification:** whether a model, transformation, or executable representation was implemented correctly against its specification or formulation;
- **model validation:** whether a model is adequate or credible for its stated intended use against an authoritative reference, data, or expected behavior;
- **system/design verification:** whether the EPS or wider system design satisfies specified requirements or criteria;
- **system/design validation:** whether the design supports intended stakeholder, operational, or mission needs;
- **multiple:** more than one of these objects is explicitly demonstrated; or
- **unclear.**

Preserve the source's terminology separately from the reviewer's normalized code and rationale. Executing a method in a model does not automatically make the activity model verification or model validation; for example, a virtual requirement check may be system/design verification. MIL, SIL, PIL, HIL, virtual testbeds, and other execution environments are likewise coded separately from the object of V&V.

Criterion, execution, and result completeness are then stratified rather than used to suppress an otherwise explicit linked record:

- **EPS-linked V&V:** the target, bridge, and V&V method/intent/artifact are reported;
- **criterion-complete EPS-linked V&V:** the record additionally reports a requirement, threshold, expected behavior, formal property, acceptance criterion, or pass/fail oracle;
- **executed pre-physical V&V:** the linked method is executed before physical integration or test of the target EPS and a result or verdict is reported; and
- **model-to-test continuity/closure:** a downstream physical artifact or activity is linked, with closure reserved for reported comparison and disposition of results.

A simulation or trade study with no stated V&V/checking intent and no criterion is analysis rather than V&V. A source-claimed verification activity with an unreported criterion remains an EPS-linked record but is not criterion-complete. Generic system V&V and EPS content appearing in the same report without an explicit bridge are co-occurrence only and do not answer RQ3.

For this review, **pre-physical V&V** means a model-based V&V artifact or activity prepared or executed before physical integration or physical testing of the target EPS design. Model-derived preparation for a later physical test is included as preparation. MIL and SIL may qualify when the target EPS hardware remains virtual. PIL and HIL are classified by the hardware actually present: they are not counted as wholly pre-physical when target EPS hardware participates, but representative or non-target hardware does not by itself convert a still-virtual target EPS into a physical EPS test. Bench, environmental, integration, operational, and flight evidence are recorded as downstream model-to-test continuity. When timing or target-relative physicality is unclear, it is coded uncertain and is not counted as demonstrated pre-physical execution.

## Information sources

### Electronic databases and collections

The independent baseline comprises twelve databases/collections searched through eleven interfaces; Engineering Village is one simultaneous interface for two separately preserved databases:

- Scopus, bibliographic database
- Web of Science Core Collection on the Clarivate Web of Science platform, bibliographic and citation database
- IEEE Xplore, bibliographic/full-text database
- Compendex and Inspec, selected and searched simultaneously on the Engineering Village platform, with database-level provenance retained
- Wiley Online Library, searched as a general publisher database across the full platform
- Springer Nature Link, searched across the full publisher platform
- Advanced Technologies & Aerospace Index on ProQuest, with only that exact index selected
- AIAA Aerospace Research Central (ARC), searched source-wide across its publisher-hosted collection
- IAF Digital Library, restricted to canonical IAC proceedings from 2011 through 2026 with population harvest and deterministic local classification
- ESA Indico, searched as a general event/contribution database across the full public instance
- NASA Technical Reports Server (NTRS), searched across the full public technical-report database

Wiley, Springer Nature Link, and AIAA ARC are source-wide publisher-platform searches for this review, not named-venue searches; ARC is not claimed to cover AIAA material outside the content indexed by ARC. ProQuest is restricted to Advanced Technologies & Aerospace Index, not its parent collection, full-text sibling, computer-science sibling, or all databases. IAF is restricted to canonical `IAC-YYYY` events; GLEX, Spring Meetings, other events, manuscript/full-text routes, and the robots-disallowed API are outside its source boundary. Every Engineering Village event retains Compendex and Inspec as separate discovery instances until common record-level deduplication. ESA Indico and NTRS remain whole-collection searches. INCOSE International Symposium content in Wiley and ESA MBSE workshop content in Indico are prespecified coverage checks, not source boundaries. PRISMA-S and PRISMA identification accounting preserves totals for all twelve databases/collections; Engineering Village additionally preserves its simultaneous combined total and the separate Compendex and Inspec counts before common deduplication.

### Supplementary discovery and citation searching

- Backward chasing from the complete reference lists of included reports and relevant secondary reviews, and forward citation chasing in both Scopus and Web of Science Core Collection
- Buruso et al. (2026), *Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review* (https://doi.org/10.1002/sys.70051), as a named secondary-review seed and deferred recall benchmark

Buruso et al. (2026) is excluded from primary evidence. A report cited by it may enter the corpus only through a logged version-1.5 database/additional-source discovery event or protocol-compliant citation-chasing event followed by new screening. Its overlap, source-specific rediscovery, citation-chasing yield, and exclusions of apparently relevant reports will be reported separately.

arXiv, Semantic Scholar, and Google Scholar searches CANNOT be used.

## Search strategy

Use two complementary search streams so that embedded EPS threads absent from titles or abstracts are not systematically lost:

- **Stream A — EPS-explicit:** combine Population × EPS × MBSE/system-model concepts to identify EPS-primary reports and explicit embedded threads. In the eight direct-query interfaces, the complete implementation is `A1 ∪ A2 ∪ A3`, where A3 restores high-specificity EPS × broad-model combinations; in IAF, ESA, and NTRS it is the equivalent local `P AND E AND M` tag.
- **Stream B — embedded-thread recall:** combine Population with structured-model/MBSE, precise reusable-artifact, conservative central-asset, or model-coupled tailoring concepts without requiring an EPS term, then screen full texts for a qualifying EPS thread. Stream B is intentionally broader and its unique yield is reported separately. The governing version-1.5 implementation retains the version-1.3 core routes and separately provenance-coded `B-G`, `B-C1`, and, where not structurally contained in core B, `B-T2` partitions.

For the eight query-based bibliographic/publisher interfaces—covering nine databases/collections because Engineering Village searches Compendex and Inspec together—**core B means the retained union B1∪B2**: B1 is population plus high-specificity MBSE terms, while B2 combines population and broader structured-model terms with the established systems-engineering relation/concern block needed to control those broader terms. IAF, ESA, and NTRS instead implement local core B as `P AND M` within one route/record. Accordingly, an optional R tag for exact G/C1 artifacts does not make R optional in bibliographic B2.

The concept blocks, adapted to each source's syntax and searchable metadata, are:

1. **Population:** CubeSat/CubeSats, `cube sat`, nanosat, nanosatellite/nanosatellites, singular/plural hyphenated and spaced `nano satellite` variants, or an explicitly nanosatellite-class mission. Generic `SmallSat`/“small satellite” is neither a positive search concept nor sufficient eligibility evidence;
2. **EPS:** electrical/electric power system or subsystem, EPS, power subsystem, electrical/power architecture, power/energy budget, energy balance, battery/batteries or storage, solar array/power generation, power conditioning/distribution/management/interface, power mode(s), load profile, PCDU, or PMAD;
3. **MBSE/system model (`M`):** singular/plural model-based system(s) engineering, MBSE, SysML/systems modeling language, singular/plural US/UK system(s) modeling/modelling, reference or object-oriented systems model, digital engineering, Arcadia, Capella, or another validated structured-system-model term;
4. **Precise reusable-artifact (`G`):** complete generic/reusable/configurable model or system-model phrases; model template; mission-agnostic or mission-independent model/architecture; reference architecture; domain model; metamodel/meta-model; product-line/product-family model; or a variation point coupled to model/architecture. The preferred query-source form is relation-free `P AND G`, because exact phrases bound the expansion and an R requirement can both self-satisfy through `architecture` and suppress records whose metadata omit relation words;
5. **Conservative central asset (`C1`):** reference/system-reference model, model-library, model-pattern, model-profile, or SysML-profile phrases, plus a domain-specific modeling/modelling-language phrase only when coupled to an MBSE/system-model anchor. Bare `library`, `pattern`, `profile`, or language terms are prohibited; and
6. **Model-coupled tailoring (`T2`):** a B2 structured-model block plus explicit reuse, tailoring, customization, configuration, parameterization, instantiation, variability/variation-point, specialization, or adaptation forms coupled to model(s) or architecture(s). Source-supported wildcards or finite inflections are required.

`B-G`, `B-C1`, and `B-T2` are candidate-generating terminology partitions only where their source adaptation is not structurally contained in core B and complete no-screening pilots support or prospectively preserve possible unique yield. They do not require EPS terms and never replace core B. For G/C1 expansion records, R may be retained as an optional precision/provenance tag; an architecture-bearing artifact cannot qualify that tag through its own overlapping token. Genericity/tailoring terminology is not required for eligibility or grading, and retrieval through any expansion is no evidence that an artifact is reusable.

Targeted RQ2 and RQ3 sensitivity probes may add benefit, null/adverse outcome, burden, effort, cost, training, traceability, verification, validation, model verification/validation, system/design verification/validation, simulation, model checking, requirements-in-the-loop, MIL, SIL, PIL, HIL, or test terms. Every direct `V1`/`O1` query and IAF/ESA/NTRS local tag uses the same exact finite subsets in the query plan and dictionary; no source may rely on wildcard or implicit expansion equivalence. These terms are not mandatory in every query because doing so could suppress relevant RQ1 and embedded-thread reports. The old T1 probe was a logical subset of core B and added no IDs; the later `T2` design replaces the bibliographic B2 relation gate with a tightly model/architecture-coupled tailoring block and did add opaque IDs in Scopus/IEEE, so the T1 result does not justify dropping T2.

Searches will be piloted in small, targeted sets. The new search log must record, as applicable, exact strings or request bodies, fields, filters, platform/interface, dates and time zone, source-reported totals, retrieved totals, pagination or event-harvest coverage, automatic stemming/lemmatization/term-expansion state or absence, refinements, failed or overbroad queries, deduplication, coverage checks, and stopping rationale. Refining source-specific syntax or precision within these fixed concept streams is search implementation, not a change to review eligibility; every version and the final used set must remain in the log.

For every final Scopus or IEEE Xplore API query, preserve the non-secret request template, client/version checksum, page requests, ordered source IDs, global ranks, retry events, page/response checksums, and normalization/merge preflight. A logical API result is valid only if the source total is stable throughout the snapshot, every expected page is present, source IDs and page-ID sequences are nonduplicated, a second complete ordered-ID pass agrees, and `retrieved == source total`; otherwise record a source failure and do not merge or screen a partial result. The reconciler accepts the empirically observed Scopus convention in which a one-page terminal result can advertise its actual count rather than the requested 25 and the IEEE convention in which a valid zero result reports one empty page; it still requires exact terminal count, empty-zero reconciliation, and identical complete passes. Credentials, cookies, tokens, and pilot records remain outside the candidate corpus. The validated source-specific implementation is in [`searches/api-pagination-request-templates.json`](searches/api-pagination-request-templates.json) and [`searches/tools/api_pagination_reconcile.py`](searches/tools/api_pagination_reconcile.py).

Every final browser-backed query must use the frozen source-native strings and controls in [`query-search-plan.md`](query-search-plan.md), preserve the exact interface and source/database selection, reconcile a stable source total to complete pagination and source IDs, and complete two identical ordered-ID passes where the source exposes an ordered record ledger. A partial prefix, challenge, login/access state, query rewrite, stale/short page, changed total, duplicate/missing identifier, export mismatch, or timeout is a documented source failure with total `null`, never a zero or a partial candidate import. Use only an authorized normal browser session; never serialize credentials, cookies, challenge state, or access tokens. Preserve source overlap as separate discovery events and deduplicate only after each source event has been retrieved and normalized.

The version-1.5 source-specific controls are mandatory:

- **Engineering Village:** run every `C-*` query once with Compendex and Inspec selected simultaneously, All and Knovel clear, `KY` concept fields, Published 2011–Latest plus literal year/English clauses, autostemming off, Relevance, 100/page, no discovery document-type filter, and source-side duplicate removal off. Preserve the combined total, separate database totals, row-level database label, global rank, and both database instances through later deduplication; a Compendex-only or Inspec-only troubleshooting run cannot replace the paired final event.
- **Wiley Online Library:** search the full platform with the frozen Anywhere/`AllField` expressions, 20-record Articles & Chapters pages, the separately logged Collections coverage route, and no discovery venue, content-type, access, or language filter unsupported by the interface. Preserve the source total, exact-day cutoff, ordered DOI ledger, native page-scoped RIS with abstracts, and normalized merge provenance.
- **Springer Nature Link:** search the full Link platform through unrestricted Keywords with English, custom 2011–2026 dates followed by the common 2026-08-10 cutoff, Relevance, 20/page, and no content-type, brand, discipline, venue, or access facet. Reconcile the complete ordered DOI/canonical-URL ledger twice. Use and preserve the normal native CSV where an authorized account and the 1,000-record source ceiling permit it; otherwise use complete normal-page retrieval. Partition prospectively into disjoint date cells when a source ceiling would truncate a final set.
- **Advanced Technologies & Aerospace Index on ProQuest:** select only that exact Index; use the frozen `NOFT` expressions with year and English clauses, Relevance, 20/page, spelling/form expansion in its recorded final state, no full-text/peer-review/source-type/document-type limiter, and source duplicate exclusion off. Preserve selected-database proof, complete page/rank/source-ID ledgers, a normal native RIS preflight and batches where available, and normalized source provenance; never substitute the broader parent or sibling databases.
- **AIAA Aerospace Research Central:** search source-wide All content through Anywhere/`AllField` with `access=on`, January 2011 through August 2026, Relevance, fixed 20-record pages, and no language, publication-type, venue, topic, or open-access discovery facet. Preserve the month-granular source total and apply the common 2026-08-10 cutoff. Require complete two-pass DOI pagination and the visible per-record Tools → Download citation RIS route with exact-byte native preservation and DOI reconciliation. A DOI-less row, challenge, or changed interface stops the run with total `null` pending a prospectively validated source-native fallback; do not discard the row or substitute another index.
- **IAF Digital Library:** harvest the complete population query separately for every canonical `IAC-2011` through `IAC-2026` event year, retrieve all public landing-page title/abstract metadata twice, and apply deterministic local P/M/G/C1 plus E/R/T2/V1/O1 classification. Use no manuscript/full-text/API/authentication route, retain missing-abstract leads, and apply the common 2026-08-10 first-formal-publication cutoff during screening.

Previously identified reports may be listed before searching in a read-only known-item register. They may guide query refinement if missed, but they enter the corpus only through a logged search or citation-chasing event followed by new screening. Known-item recall and unique inclusions from each stream and source are reported separately.

No query-based source uses a discovery publication/content-type filter unless the final log prospectively records a source-mandated implementation change; publication type is verified during screening. Apply English in Scopus, Web of Science Core Collection, IEEE Xplore, paired Engineering Village, Springer Nature Link, and ProQuest where the planned interface exposes a reliable control; Wiley, AIAA ARC, IAF, ESA, and NTRS language is screened because no reliable discovery control was validated. Every source and citation route uses the common 2026-08-10 evidence cutoff. Source year/month controls that admit later records—including Scopus, IEEE, paired Engineering Village, Wiley, Springer, ProQuest, AIAA ARC, and IAF—retain their unaltered source totals and receive a logged first-formal-publication-date cutoff with the number removed or left unresolved.

For ESA Indico, inventory every event/contribution material through the common cutoff before candidate gating and union deterministic core P×M with relation-free complete P×G/C1 artifact matches from joined metadata and each individual extractable attachment; retain independent-R, T2, V1, and O1 as separate tags; inaccessible/unparseable materials are coverage failures and terms may not be combined across metadata and attachment routes. For NTRS, exhaust 940 separate cells: ten population terms × eighteen core model terms, the same ten × twenty-five exact G terms, and the same ten × fifty-one exact C1 atoms. The C1 set includes every four-language-spelling × nine-model-anchor combination. Apply the full deterministic E/T dictionaries and exact finite V1/O1 subsets to the deduplicated core-B∪B-G∪B-C1 union. Preserve Stream A as the E-explicit tag within core B and label E-explicit expansion records separately rather than converting a G-only record into Stream A. In ESA and NTRS, Stream A is structurally contained in core B; report core/G/C1 intersections and exclusive yields, total B, A∩core-B, core-B-only, expansion-E and T2/V1/O1 tags, and the union, and do not treat expected `A-only = 0` as a performance defect.

Freeze the independent baseline only after each of the twelve electronic databases/collections has either a complete, reconciled version-1.5 final run or an explicitly documented final source/interface failure. Merge only successful complete-source results, including separate Compendex and Inspec discovery instances from each successful paired Engineering Village event; retain every failed-source status and reason in the manifest and PRISMA-S/PRISMA accounting, and never import a failed source's partial prefix. Only after that successful-source baseline and the failed-source register are frozen will Buruso et al. (2026) and the retained-file cache be used for deferred recall audits. A missed Buruso-cited report can prompt a logged concept-level probe or enter through a logged citation-chasing route; it is never inserted directly.

Backward and forward citation chasing starts from every full-text-included report and relevant secondary review. Backward chasing inspects the complete source reference list; forward chasing searches both Scopus and Web of Science Core Collection. A zero result or indexing failure in one forward-citation platform does not waive the other. Newly found eligible reports are chased in the next numbered cycle; iteration stops when one complete backward and dual-platform forward cycle yields no new eligible report. Every seed, platform, direction, exact route, cycle, source/retrieved total, candidate, duplicate, decision, failure, and stopping result is logged. Citation records retain `discovery_route=citation_chasing` separately from their bibliographic source and never bypass normal eligibility screening.

Searching stops only when both streams, direct-source A1/A2/A3, every core, B-G, B-C1, and source-applicable B-T2 partition, every mandatory local V1/O1 tag, and all sixteen IAF annual harvests have completed at every planned source—or the affected final source/interface has failed explicitly without partial candidate import—every source-specific coverage check and prespecified concept cluster has completed or failed explicitly, relevant report families/artifact lineages discovered during the new run have been tested, citation chasing is complete, and additional searches are predominantly redundant rather than merely convenient or precise. The execution date for every source and strategy is reported, but the review's evidence window closes uniformly on 2026-08-10.

## Data management and audit trail

Manage review methods, logs, controlled dictionaries, derived data, and analysis code in the version-controlled `SLR/SLR1/` workspace. Preserve raw source artifacts as read-only files where licensing permits and index every artifact in a manifest with path, query/event ID, source, timestamp, byte size, SHA-256 checksum, access/rights status, and creating software/version. Record the actual database interface and software versions at execution rather than assuming the draft environment remains unchanged.

Use UTF-8 JSON/JSONL or CSV for derived machine-readable data and RIS/BibTeX/CSV or source-native structured exports for bibliographic transfer as available. Validate schemas, identifiers, controlled values, and referential integrity before each merge or synthesis. Deduplication is reproducible but manually adjudicated where identifiers conflict; preserve both the original metadata and the preferred normalized value with rationale. Git history supplies the audit trail for text, code, schemas, and derived non-sensitive data; raw licensed exports and full texts remain in access-controlled storage with the repository/search manifest recording their durable location and backup status. Do not publicly redistribute licensed exports, copyrighted abstracts, or full texts merely for checklist compliance.

## Inclusion and exclusion criteria

| Criterion | Rule | Applicable RQ(s) |
|---|---|---|
| Publication date | First formal publication date from 2011-01-01 through the common 2026-08-10 evidence cutoff; online-first and issue versions of the same report are one work | 1--3 |
| Language | Report written in English; inability to retrieve the full text is handled separately as `not_retrieved` | 1--3 |
| Publication type | Full primary-research journal article, conference/proceedings or workshop paper, research chapter in an edited scholarly volume, or institutional technical report with stable provenance and substantive methods/results; empirical comparison and experience reports are eligible when they meet all other criteria. Document type, provenance, and reported review status are verified where possible | 1--3 |
| Population | Actual or intended orbital CubeSat/nanosatellite-class mission or a nanosatellite-tailored model; a generic SmallSat/small-satellite label alone is excluded, and separable CubeSat/nanosatellite evidence is required in mixed-platform reports | 1--3 |
| MBSE threshold | Must meet the structured-system-model definition above | 1--3 |
| EPS threshold | Must meet Route A or Route B at full text | 1--3 |
| RQ1 contribution | Every eligible EPS thread contributes its reported representation, purpose, inputs/assumptions, abstraction, and reuse/tailoring information and receives an RQ1-G disposition; identifiable EPS-linked artifacts receive artifact-lineage profiles and tailoring applications where applicable; missing fields remain `not_reported` | 1, including RQ1-G |
| RQ2 contribution | Only atomic outcome or implementation-burden records explicitly attributed to a qualifying EPS thread enter direct RQ2 synthesis; direction, mechanism, and evidence completeness are coded separately | 2 |
| RQ3 contribution | Only `eps_specific` or `system_wide_eps_linked` records with the required target, explicit bridge, and reported V&V method/intent/artifact enter direct RQ3 synthesis; scope, object, criterion completeness, and execution are reported separately | 3 |
| Mixed system scope | Include only when an EPS thread is separately extractable; synthesize other subsystems only as EPS dependencies/interfaces | 1--3 |
| Secondary studies | Exclude from primary evidence, including Buruso et al. (2026); retain separately for positioning, terminology, deferred recall checking, and citation chasing | 1--3 |
| Non-MBSE EPS studies | Exclude stand-alone component, circuit, control, optimization, sizing, simulation, or hardware-performance studies without an explicit structured-system-model link | 1--3 |
| Generic whole-spacecraft MBSE | Exclude reports lacking a qualifying EPS thread, even if they mention EPS or a power budget | 1--3 |
| Other subsystem studies | Exclude unless they contain a qualifying EPS thread; a subsystem's power consumption alone is insufficient | 1--3 |
| Abstract-only/non-research material | Exclude posters/abstracts without full papers, presentation- or slide-only records, recordings, editorials, tutorials, advertisements, patents, and non-scholarly web material. Such records from ESA Indico or NTRS may be logged as discovery leads to a distinct eligible full report but cannot themselves supply primary evidence | 1--3 |
| Retrieval status | Scientific eligibility is independent of open-access status. Reports not obtained after the defined retrieval process are logged as `not retrieved`, not silently excluded on scientific grounds | 1--3 |

Outcome, V&V, reuse, genericity-claim, or demonstrated-tailoring presence is not a report-level inclusion criterion. A Route A or B report may answer only the non-genericity portions of RQ1 and still be included. Genericity dispositions, profiles, and tiers are assigned only after scientific eligibility and cannot rescue an ineligible report.

Retrieval follows the run's PDF workflow: DOI/open-access and publisher/repository routes are attempted first, followed by one documented institutional/manual-download pass where needed. Unresolved reports remain in the PRISMA and retrieval records as `not_retrieved`; they do not enter full-text evidence synthesis, but lack of access is not presented as a scientific exclusion reason.

## Screening and eligibility procedure

### Title and abstract screening

Use screening tiers only to prioritize retrieval; they are not final evidence classes:

- **core candidate:** title/abstract gives clear evidence of EPS-primary MBSE or a likely embedded EPS thread;
- **supporting candidate:** the record meets the nanosatellite and possible MBSE threshold, but a qualifying embedded thread cannot be confirmed without full text; and
- **rejected candidate:** clearly fails population, publication, or MBSE scope, or an EPS-explicit record clearly lacks a qualifying model link.

Because embedded threads may not appear in abstracts, Stream B records do not require a power/EPS term at this stage. Uncertainty is resolved toward retrieval when nanosatellite MBSE is plausible; the EPS anchor and bridge are tested at full text.

### Full-text decision

Assign one final decision with a source-located rationale:

- `include_route_A_eps_primary`;
- `include_route_B_embedded_eps`;
- `exclude_no_qualifying_eps_thread`;
- `exclude_not_mbse`;
- `exclude_wrong_population`;
- `exclude_wrong_publication_type`;
- `exclude_wrong_date`;
- `exclude_wrong_language`;
- `exclude_secondary_study`;
- `exclude_insufficient_primary_report`;
- `not_retrieved`.

For every Route B inclusion, screening must record the EPS anchor, model anchor, explicit bridge, and supporting location. These data are rechecked during extraction.

Secondary reviews and generic MBSE sources used for background or citation chasing are maintained outside the analytic denominator.

## Units of evidence and identifiers

The review distinguishes seven linked analytic units. Report-family and artifact-lineage relations can cross reports and implementations, so the units are not assumed to form a strictly nested hierarchy:

1. **Study/implementation report family:** one underlying investigation, evaluation, mission/design implementation, reference-model release, or materially shared model/toolchain application represented by one or more reports. Family membership requires documented overlap; shared topic, organization, or tool alone is insufficient, and evidence does not transfer silently between family members.
2. **Report:** one distinct publication or institutional technical report. Online-first and issue manifestations of the same work are collapsed, while substantively distinct companion reports remain separately citable and are linked to their family.
3. **EPS model thread:** one qualifying EPS-primary or embedded chain within a report. A report may contain more than one thread.
4. **Reusable EPS artifact lineage and genericity profile:** one identifiable base artifact and its source-supported versions/derived instances, linked to every contributing report, family, and EPS thread. Create separate lineages when the retained core or derivation identity is materially different or uncertain. One lineage receives one profile per materially distinct artifact version/scope when a combined profile would conceal changed claims or gates.
5. **Tailoring application:** one artifact-lineage-to-target-context application, including a justified reuse-as-is case. Multiple reports of the same underlying application are collapsed for context and assurance counts while retaining all report provenance.
6. **Outcome or implementation-burden record:** one atomic outcome direction or burden linked or potentially linked to a thread. When one statement reports several outcomes, directions, or burdens, create separate records that may share the same quotation.
7. **V&V record:** one target–method–scenario activity or artifact linked or potentially linked to a thread. Multiple targets, methods, or scenarios use linked atomic records rather than one aggregate record.

Assign a report-family ID, report-to-family relationship type, membership rationale, evidence location, and overlap confidence. A report may map to more than one family when it genuinely reports distinct underlying implementations or evaluations. Reports from the same family are not treated as independent replications. An artifact lineage may span multiple implementation families, but this does not establish independent reuse unless the I gate is source-supported. Conversely, shared organization or artifact name does not justify merging lineages. Each integrated artifact-level field retains report provenance; linking reports must not attribute an unreported fact or result to another report/version. Families and lineages are analytic dependence/identity units, not PRISMA flow-diagram units: PRISMA identification and selection counts remain at record/report level.

New-run IDs must qualify linked records, for example `family_id`, `artifact_lineage_id:genericity_profile_id`, `artifact_lineage_id:tailoring_application_id`, `report_id:thread_id:outcome_burden_id`, and `report_id:thread_id:vnv_id`. A normalized DOI is the preferred cross-run report identity key; NTRS/report numbers and source IDs supplement it, and title–author–year matching requires manual confirmation. Artifact identity requires the lineage evidence defined above. Legacy IDs and prior discovery paths are provenance only.

## Quality checklist

All applicable items use:

- No = 0
- Insufficiently = 0.5
- Yes = 1
- Not applicable = excluded from that score's denominator

Quality scores contextualize confidence and sensitivity analyses; they are not automatic exclusion thresholds and cannot make an ineligible report, genericity profile, outcome/burden record, or V&V record eligible. The A/E/C/T/P/I genericity profile and `NA`/`G0`--`G4` tier are not included in this numerical checklist and must not be averaged with it.

### Report and EPS-thread quality

1. Was the primary research published in a credible scholarly venue or identifiable institutional technical-report series, with report type, provenance, and review status verifiable?
2. Is the CubeSat/nanosatellite mission context and lifecycle stage described clearly enough to assess applicability?
3. Are the MBSE method, model boundary, language/toolchain, artifacts, and modeled relations described clearly enough to verify MBSE qualification?
4. Are the EPS anchor, model anchor, explicit bridge, and EPS boundary reported clearly enough to reconstruct the qualifying thread?
5. Are the model's stated purpose, intended decisions, users/roles, and lifecycle use reported?
6. Are material inputs and assumptions reported with sufficient detail about value/range, units or time basis, provenance, uncertainty/margin, and rationale?
7. Are model/tool/data availability, configurations, interfaces, and reusable assets reported sufficiently to assess reproducibility?
8. Do the authors discuss limitations, scope boundaries, uncertainty, threats to validity, or alternative explanations?

### RQ1-G genericity-evidence audit, when applicable

Apply the A/E/C/T/P/I gates and tier rules above without numerical scoring. In addition to the source location and status for every gate, audit whether:

- the claim object is an EPS-linked model artifact rather than a method, tool, workflow, or generic whole-spacecraft assertion;
- artifact/version lineage and every credited tailoring application are identifiable without transferring evidence across uncertain versions or duplicate reports;
- the DAE is distinguished from demonstrated coverage and from reviewer-inferred applicability;
- retained core, variation points, actual changes, footprint, and any reuse-as-is rationale are reported;
- each context credited to G3/G4 has a post-tailoring criterion, executed check, and result relevant to intended use;
- G4 independence reflects an independently adopted/tailored and assured application corroborated by an independent-adopter/evaluator source, not merely the originator's assertion, an independent reviewer, publication, author list, or repeat evaluation of the originator's instance; and
- failed, mixed, out-of-envelope, or contradictory applications are retained in claim-concordance reporting.

A genericity tier grades the completeness and independence of evidence for bounded transfer; it is not a finding that the artifact is high quality, beneficial, broadly applicable, or superior.

### RQ2 outcome/burden quality, when applicable

9. Is the outcome or implementation burden explicitly linked to a qualifying EPS thread and a stated MBSE mechanism rather than to EPS technology choice or generic MBSE?
10. Is its reported direction or burden supported by an appropriate metric, traceable case result, comparator, stakeholder assessment, reuse, integration/test result, or operational evidence?

### RQ3 V&V quality, when applicable

11. Are the EPS target, linkage scope, model-to-V&V bridge, source terminology, normalized V&V object, method/artifact, criterion, lifecycle timing, and execution status explicitly reported?
12. When execution or closure is claimed, are the result/verdict and any downstream software, hardware, integration, test, operational, or flight link evidenced?

Items 1--3 and 8 are scored at report level; items 4--7 at EPS-thread level; items 9--10 for each direct RQ2 outcome/burden record; and items 11--12 for each EPS-linked RQ3 record. The separate genericity audit is reported at artifact-lineage/profile and tailoring-application level without a numerical roll-up. Any checklist roll-up is descriptive and retains its unit and applicable-item denominator. Linkage, lineage, and tier confidence are also retained separately from quality score.

### Appraisal meaning, reporting-bias assessment, and conclusion confidence

The checklist assesses reporting completeness, direct EPS linkage, and strength of support in heterogeneous engineering evidence; it is not presented as a validated clinical risk-of-bias instrument. Report checklist domains and record-level evidence confidence at their actual units rather than collapsing them into an unqualified “study quality” label.

No funnel plot or statistical publication-bias test is planned because there is no common effect estimate and the evidence types are heterogeneous. Instead, assess and report, for each RQ synthesis:

- coverage/interface limitations and unique yield across the twelve electronic databases/collections, eleven interfaces, and citation routes;
- effects of the English, date, population, publication-type, retrieval, and source-access limits;
- unavailable full reports and lead-only material;
- selective or missing genericity claims, applicability boundaries, tailoring failures/burdens, outcome/burden, criteria, results, and limitations;
- dependence created by shared study/implementation report families and repeated reporting of the same artifact lineage/application; and
- protocol deviations, search refinements, or review-process limitations that could change interpretation.

Assign conclusion-level confidence narratively as `higher`, `moderate`, `lower`, or `insufficient`, with a source-locatable rationale. Consider directness to a qualifying EPS thread, report and record quality, the genericity profile/tier where relevant, evidence type and comparator, maturity/independent or physical validation, consistency including null/adverse or failed-transfer evidence, report-family and tailoring-application independence, and review-process limitations. A genericity tier never maps mechanically to a conclusion-confidence label. No numerical quality cutoff or mechanical averaging determines confidence. `Higher` requires multiple materially independent, directly linked and well-supported records with no major unexplained inconsistency; `moderate` permits limited independence, maturity, or comparators but still requires directly supporting evidence; `lower` denotes sparse, weak, indirect, dependent, or materially inconsistent support; and `insufficient` denotes no eligible direct evidence for the conclusion. These labels are an engineering-review framework, not GRADE.

## Extraction fields

A new run-specific `extraction_codebook.json` must be created from this protocol before per-report extraction. Earlier codebooks and extraction forms are not authoritative for this run and may not be copied into new-run fields.

Every synthesis-critical controlled code requires a rationale, a direct quote or source location where possible, and a confidence rating. Preserve `not_reported`, `not_applicable`, `none`, and `uncertain` as distinct statuses. Distinguish author-reported facts from extractor inference.

### Report-level bibliographic and review-management fields

- New-run report ID; optional legacy corpus ID; extraction file path.
- Citation, title, authors, year, venue or institutional report series, publication type, DOI/URL, publisher/issuing organization, source/report identifier, and reported peer/technical-review status.
- Every discovery event: run ID, database/source, exact query or citation route, date, source record ID, rank when available, and raw-search artifact.
- Title/abstract screening tier and rationale.
- Full-text eligibility decision and exclusion rationale, if applicable.
- Route A/Route B classification and evidence.
- RQ contribution status: RQ1; RQ1-G genericity dispositions and counts of linked artifact-lineage profiles/tailoring applications; count of eligible RQ2 outcome/burden records; count of direct and near-miss RQ3 records.
- Study/implementation report-family ID(s), linked artifact-lineage ID(s), report-to-family/artifact relationship, membership or identity rationale/evidence, overlap confidence, and shared-result notes.
- Extraction confidence and assessor/review-pass provenance.

### Study context and MBSE qualification

- Mission/platform, form factor/mass if reported, mission name/domain, organization type, and project maturity.
- Demonstrated lifecycle stage, separated from asserted or future lifecycle applicability.
- Development context: academic/student, agency, industry/NewSpace, distributed team, agile/concurrent design, rapid prototyping, resource-constrained mission, or not reported.
- Reported MBSE implementation requirements and burdens: roles, skills, training, staffing, time/effort, licensing/infrastructure, model/data preparation, computation, integration, governance, maintenance/configuration, cost, schedule, or not reported.
- Author's stated objective, pain point, intended decision, and rationale for using MBSE.
- MBSE qualification evidence: method/language, tools, system-model artifacts, modeled concerns, explicit relations, and system boundary.
- Model maturity: conceptual framework, reference/template, prototype, executable, project-applied, physically validated, operational/flight, or not reported. These may co-occur and are not assumed ordinal unless the paper supports an ordering.
- Toolchain architecture, data flow, interoperability mechanism, ownership/handoff, and reported limitations.
- Availability of models, profiles, libraries, scripts, data, configurations, and documentation.

### EPS-model-thread record

Create one record per qualifying thread:

- Thread ID and report ID.
- Thread route/role: EPS-primary or embedded EPS.
- Host-model anchor for embedded threads.
- EPS model anchor and EPS system boundary.
- Explicit bridge(s), relation type, and source location.
- EPS concerns represented: requirements, function, behavior, architecture, components, ports/interfaces, modes/operations, parametrics/budgets, decisions/trades, risks/faults, V&V, or other.
- EPS elements: generation/solar array, storage/battery management, conversion/regulation, conditioning/distribution, protection, monitoring/control, bus/harness, loads/interfaces, modes, margins, degradation, fault management, or other.
- Model artifacts and tools carrying the thread.
- Level of abstraction/fidelity and phenomena deliberately omitted.
- Purpose and decisions supported: definition/sizing, requirements/traceability, trade study, interface management, executable analysis, V&V, reuse/tailoring, communication, lifecycle continuity, or other.
- Reuse/tailoring mechanism: template, reference model, profile, library, pattern, transformation, reusable workflow, open package, method guidance, mission-agnostic architecture, interface-focused model, specific-mission model with reusable method, or other.
- Tailoring choices and implementation footprint: model/artifact scope, retained or omitted content, roles, tooling, automation, governance, required resources, rationale, and reported trade-offs. Preserve any author characterization such as lightweight, scalable, comprehensive, or resource-intensive, but do not impose a lightweight threshold or infer one from mission class.
- Linked artifact-lineage/profile and tailoring-application IDs; genericity disposition; method/workflow-only status where applicable.
- Thread-level maturity, lifecycle stage, availability, evidence confidence, and limitations.

### Reusable EPS artifact-lineage and genericity-profile record

Register every identifiable EPS-linked artifact and create one profile for each lineage/version/scope that can be assessed without concealing material change:

- Artifact-lineage ID, genericity-profile ID, linked report-family/report/thread IDs, and every source-supported base/derived or version relationship.
- Artifact object/type: structured system model; reference/template model; metamodel; modeling profile; library/pattern; interface contract; parametric package; transformation/generator with persistent content; larger model with separable EPS content; method/workflow only; toolchain only; other; or unclear.
- Artifact name, version, repository/package/model identifiers, owner/developer, availability, license where reported, and lineage confidence/rationale. Shared tool, organization, terminology, or topic is not lineage evidence.
- Exact source terminology and claim text; claim object and actor; claimed reuse/genericity scope; whether the claim concerns the artifact, a method/workflow, toolchain, language/profile, whole spacecraft, or is unclear.
- Genericity disposition: `not_an_artifact_or_method_only`; `artifact_no_reuse_indication`; `genericity_or_reuse_claim`; `reported_reuse_without_bounded_specification`; `bounded_reuse_candidate`; or `unclear`.
- DAE fields: intended target platform/mission/form factor; mission/domain/orbit/environment; lifecycle use, purpose, and decision; EPS boundary/architecture/interfaces; abstraction/fidelity; required inputs/data; modeling language/tool/version; organizational/process assumptions; prerequisites; stated exclusions and failure boundaries. Preserve `not_reported` by dimension and record whether the minimum DAE is met.
- Reusable core/invariants: retained elements, relations, constraints, semantics, interfaces, libraries/packages, identifiers, and source locations.
- Variation design: variation-point identifier/location; permitted range/options; default; dependencies/constraints; operation type; rationale; and whether the point is source-declared or only reconstructable from an explicit base/derived mapping.
- Tailoring rules/pathway, required inputs and roles, governance/configuration control, automation, and any bounded reuse-as-is rule.
- Linked tailoring-application IDs; claimed envelope versus demonstrated-context tuples; number of materially distinct applications after collapsing duplicate reporting; and evidence used to judge distinctness.
- A/E/C/T/P/I gate status, rationale, evidence location, and confidence for every gate; failed condition(s); highest genericity tier (`NA`, `G0_artifact_only`, `G1_claimed_or_unbounded`, `G2_bounded_reuse_specified`, `G3_bounded_reuse_demonstrated`, or `G4_independently_corroborated`) with a source-locatable cumulative rationale.
- Claim concordance: `not_evaluated`; `supported_in_tested_contexts`; `partially_supported`; `mixed`; `not_supported`; or `unclear`, preserving failed/out-of-envelope applications and alternative explanations.
- Profile-level limitations, model/data availability, report-family and lineage dependence, evidence source, extraction confidence, and first/second-check provenance.

Do not award a gate from source silence, source labels alone, a single observed mission, model openness, maturity, or reviewer knowledge. Integrate complementary reports only after lineage is established and retain which report supports each field; do not transfer results between versions or applications.

### Tailoring-application record

Create one record per artifact-lineage-to-target-context application, including a justified unchanged adoption:

- Tailoring-application ID, artifact-lineage/profile ID, linked family/report/thread IDs, target model/configuration identifier, and application identity/duplicate-report rationale.
- Target-context tuple: mission/platform/form factor; mission purpose/domain; orbit/environment; lifecycle use/decision; EPS architecture/components/interfaces; modes/load profile; model fidelity; language/tool/version; organization/team; and other material DAE dimensions.
- Relationship to the DAE: inside; boundary case; outside; unclear; or DAE not reported, with rationale. Record the material dimension(s) that distinguish this context from other credited applications.
- Base/core content retained and evidence; content configured, parameterized, selected, specialized, extended, deleted, substituted, mapped, transformed/generated, rebuilt, or intentionally unchanged; affected variation-point IDs; before/after or base/derived trace; and rationale.
- Tailoring inputs/assumptions, procedure, roles/skills, automation, tools/licenses/infrastructure, governance, effort/time/cost, maintenance, and other implementation footprint or burden. Do not infer low effort from parameterization or mission class.
- Resulting artifact/use, decisions or analyses supported, availability/configuration identifier, reported failures/rework/trade-offs, and whether the record demonstrates artifact reuse, method/workflow reuse only, or is unclear.
- Post-tailoring assurance: intended-use criterion/oracle and provenance; method; execution timing; result/verdict; discrepancies/disposition; and whether all P-gate conditions are met. Link an RQ3 record only when its independent eligibility rule is satisfied.
- Adopter/evaluator relationship: originating/same team; same organization but operationally separate team; external organization/team; independent evaluation of the originator's instance only; or unclear. Record personnel/implementation-control overlap, the independent adopter/evaluator's own report/artifact/data provenance, report-family evidence, separate adoption/tailoring and assurance evidence, and whether the I gate is met.
- Evidence source, confidence, limitations, and extraction/second-check provenance.

A single application may inform RQ1-G and also link to RQ2 burden/outcome or RQ3 V&V records, but it does not enter those direct syntheses unless their separate attribution/linkage rules are met.

### Input and assumption record

Create one record for each material reported input or assumption linked to its EPS thread. “Material” means that the input or assumption defines the EPS boundary, parameterizes behavior or a scenario, supplies a criterion, affects a reported output/decision, or limits claimed applicability:

- Input/assumption ID and thread ID.
- Type: mission requirement; orbit/environment; operational mode or load profile; architecture/interface; generation; storage; conversion/distribution; component performance/loss; degradation/lifecycle; margin/uncertainty; control/fault; model-fidelity/tool assumption; V&V configuration; or other.
- Parameter/construct, reported value or description, units, time basis, and nominal/worst-case/range/distribution status.
- Provenance: mission requirement; standard/handbook; vendor data; test/flight data; heritage/previous mission; literature; tool default; analyst assumption; calculated/derived; or not reported.
- Treatment of uncertainty, variability, margin, sensitivity, and degradation.
- Stated rationale: mission/environment constraint; early-phase uncertainty or unavailable data; conservatism/safety; reuse/tailoring; computational/tool limitation; interface standard; decision need; V&V need; or not stated.
- Trace location in a requirement, model element, parameter, figure/table, data file, or external-tool binding.
- Effect on model outputs or decisions, if reported.
- Evidence source and extraction confidence.

Do not infer that an input is unnecessary because it is not reported. Source silence is coded `not_reported`.

### EPS engineering outputs

Extract technical outputs separately from MBSE outcome/burden records:

- Output ID and thread ID.
- Quantity/result and units/time basis.
- Scenario/configuration and input set.
- Whether it is calculated, simulated, checked against a criterion, compared, or physically validated.
- Decision or model artifact informed.
- Evidence source and confidence.

### RQ2 outcome and implementation-burden evidence record

Create one atomic record for each candidate outcome or burden that is explicitly or plausibly linked to a qualifying EPS thread. Do not exhaustively extract generic MBSE claims merely because they occur in an eligible report. Split multi-outcome statements into atomic records and connect shared evidence through source IDs:

- Record ID and linked thread ID.
- Exact result/claim text or conservative paraphrase.
- Record role: outcome; implementation burden; mixed trade-off; or other.
- Claim scope and target.
- Outcome category: EPS reliability; system/mission assurance; defect/error reduction; risk reduction; reproducibility/rerunnability; reuse/replication; integrability/interoperability; interface consistency; traceability/requirements quality; completeness; lifecycle continuity; decision/trade support; cost; schedule; effort/automation; communication/knowledge; governance/value realization; or other.
- Reported direction: beneficial; null/no observed effect; mixed/conditional; adverse; unclear/not reported. Preserve author-claimed direction separately from evidence-supported direction.
- Direction basis: metric polarity, comparator or criterion, time horizon, magnitude/value/units, conditions, and whether the result is observed or anticipated.
- Implementation-burden category, when applicable: time/effort; skills/training; staffing; tooling/licensing/infrastructure; model/data preparation; computation; integration/interoperability; maintenance/configuration/governance; schedule; cost/resource use; other; none reported; or not reported. Record affected actor, adoption versus ongoing phase, mitigation, and any linked benefit/trade-off.
- Reliability subtype where relevant: EPS reliability, system/mission reliability, process reliability, model consistency/reliability, mission assurance, defect/error reduction, generic reliability claim, or not applicable.
- MBSE mechanism: artifact traceability, requirements linkage, executable simulation, parametric analysis, reference-model reuse, automated generation, transformation, shared repository, tool integration, interface management, lifecycle-gate support, model-derived V&V, or other.
- Artifact/process linked to the record and lifecycle stage.
- Attribution status: explicit EPS-thread attribution; ambiguous attribution; generic/not eligible. Only explicit EPS-thread attribution enters direct RQ2 synthesis.
- Evidence type: assertion only; conceptual/illustrative; single-case demonstration; executable result; trade/requirements-check result; quantitative metric without comparator; quantitative comparison; stakeholder/expert evaluation; reuse/replication; integration/test/operational/flight evidence.
- Metric or value indicator; baseline/comparator; observed effect, result, or burden.
- Evidence source, alternative explanations, and report-family/nesting notes.
- Evidence confidence:
  - **Unsupported:** assertion without extractable support;
  - **Weak:** plausible explanation or illustrative/single-case evidence without a result adequate to support the claimed direction or burden;
  - **Moderate:** traceable within-case evidence, executable/checking result, or metric, but limited comparator or independent validation;
  - **Strong:** appropriate comparative, repeated-reuse, independent, integration/test, operational, or flight evidence directly supporting the reported direction or burden.

### RQ3 V&V record

Create one atomic target–method–scenario record per candidate activity or artifact. Retain plausible linkage near misses so exclusion from EPS-linked RQ3 synthesis is auditable, but do not exhaustively extract unrelated generic system V&V:

- V&V record ID and linked thread ID.
- EPS target or system-wide target explicitly linked to EPS; target type and requirement/criterion identifier when reported.
- Model element/artifact and explicit model-to-V&V bridge.
- Source terminology for verification, validation, V&V, checking, or analysis.
- Linkage scope: `eps_specific`; `system_wide_eps_linked`; `system_wide_cooccurrence`; or `unclear`, with source evidence and rationale.
- Normalized V&V object: model verification; model validation; system/design verification; system/design validation; multiple; or unclear, with coding rationale.
- Eligibility disposition: analysis only; direct EPS-linked V&V; system-wide co-occurrence near miss; or unclear.
- Method/artifact: requirements-in-the-loop, parametric/constraint check, simulation scenario, model checking, trade verification, virtual integration, verification matrix, test case/procedure, generated test artifact, automated test, MIL, SIL, PIL, HIL, or other.
- Execution environment and hardware present; physicality relative to the target EPS.
- Criterion/oracle and its provenance.
- Timing relative to physical realization, integration, and test; lifecycle stage.
- Status: proposed only; prepared/generated; executed virtually; verdict/result reported; downstream physical link demonstrated; model-to-test closure demonstrated.
- Result/verdict, result scope (EPS-specific, system-wide, or not reported), and discrepancy handling, if reported.
- Downstream link: software integration, hardware integration, flat-sat/bench, PIL/HIL, environmental test, operational validation, or flight evidence.
- EPS-linked RQ3 eligibility: yes/no/uncertain for the target–bridge–V&V-method/intent rule, with the failed condition recorded when not eligible.
- Criterion-complete status: yes/no/uncertain, with criterion evidence.
- Demonstrated pre-physical execution status: yes/no/uncertain, with timing, target-relative physicality, and result evidence.
- Evidence source, confidence, limitations, and report-family/nesting notes.

### Limitations and open extraction

- Author-stated limitations, assumptions, and scope boundaries.
- Extractor-identified evidence gaps, with absence-based explanations only after completing the relevant fields.
- Narrow controlled limitation flags, including prototype/future work, single case, no comparator, no independent validation, no physical/model-to-test evidence, unavailable model/data, assumptions/data-quality limits, tool dependency, interoperability limits, incomplete lifecycle coverage, ambiguous EPS linkage, generic outcome attribution, missing V&V criterion, method/artifact conflation, missing or inferred DAE, unidentified reusable core, no explicit variation rule, tailoring claim without a reconstructable application, ambiguous artifact lineage, duplicate/same-family reuse only, no post-tailoring assurance, or unreported failed/out-of-envelope reuse.
- Emergent codes for unexpected findings that do not fit the controlled vocabulary; do not silently expand controlled categories during extraction.

## Calibration, consistency, and validation

Before full screening and extraction:

1. pilot the full-text eligibility rule on clear Route A, clear Route B, generic whole-spacecraft MBSE, and non-MBSE EPS examples;
2. pilot the thread, input/assumption, artifact-lineage/genericity-profile, tailoring-application, RQ2 outcome/burden, and RQ3 V&V forms on a deliberately varied sample, including method-only versus artifact reuse, claim-only, bounded specification, one versus multiple materially distinct contexts, same-family duplication, reuse-as-is, failed transfer, and post-tailoring assurance cases;
3. revise and then freeze the run-specific codebook before full extraction; and
4. document all calibration decisions and examples.

Use isolated assessment passes to reduce context carryover. All final Route B inclusions, artifact-lineage merges/splits, G3/G4 tier assignments, and direct RQ2/RQ3 linkage decisions must receive a second check. Calibrate the distinction between a DAE and an observed case, a scenario sweep and tailoring, a model artifact and method/workflow, separate reports and separate applications, and post-tailoring assurance and direct RQ3 V&V. Record whether each check was performed by another human assessor or by a model-assisted validation pass. Do not describe model-assisted validation as independent human review, and calculate an agreement statistic only when the assessment design genuinely supports it.

Validate all extraction JSON against the codebook, exact controlled labels, record IDs, required evidence/rationales, status distinctions, and report-family/report/thread/artifact-lineage/genericity-profile/tailoring-application/outcome-burden/V&V referential integrity before synthesis.

## Planned synthesis

The synthesis is a structured evidence map and narrative synthesis; no pooled effect estimate is planned because models, outcomes, and evidence designs are expected to be heterogeneous.

### Relationship to Buruso et al. (2026)

Buruso et al. (2026) is a broad secondary review of 126 selected space-MBSE studies and reports published from 2011 to 2023, mapping methods, languages, tools, five MBSE phases, and general challenges across heterogeneous space applications. It is used here for positioning, terminology, a deferred recall benchmark, and logged citation chasing, not as primary evidence.

This review is neither an update nor a replication of Buruso et al. It is restricted to orbital CubeSat/nanosatellite EPSs; requires a source-locatable EPS anchor, model anchor, and explicit bridge; and synthesizes material inputs and assumptions, all reported reuse and tailoring approaches, bounded artifact genericity and its evidential support, implementation footprint, direct EPS-attributed outcome direction and implementation burdens, and direct EPS target–model–V&V chains. It therefore addresses broader gaps concerning model tailoring and scalability, predominantly anecdotal value claims, and poor visibility of later integration, test, and V&V. System-wide MBSE or V&V is not treated as EPS evidence without the protocol's direct link. Cross-review counts are not compared as effectiveness evidence.

For descriptive currency and overlap, publication patterns may be shown separately for 2011--2023, corresponding to Buruso et al.'s evidence window, and 2024 through the common 2026-08-10 evidence cutoff. This temporal split does not change eligibility or imply that reports within either period are independent.

### RQ1

- Map EPS boundaries, model concerns, artifacts, purposes, abstraction levels, inputs/assumptions, provenance, uncertainty/margin handling, all reported reuse/tailoring approaches, implementation footprint, required roles/skills/resources, trade-offs, and lifecycle use.
- Distinguish reported inputs and implementation requirements from reviewer-inferred dependencies and from source silence.
- Where evidence permits, describe how authors characterize implementations as lightweight, scalable, comprehensive, or resource-intensive and compare those characterizations with the reported implementation footprint; lightweight status is not an eligibility filter or required tailoring category.
- Compare Route A and Route B without assuming either is more mature.

### RQ1-G

- Register identifiable EPS-linked artifact lineages and report method/workflow reuse separately from artifact reuse.
- Map source terminology and claims, DAE dimensions and missingness, reusable cores, variation points, tailoring pathways, implementation footprints, demonstrated target-context tuples, post-tailoring assurance, failures/boundaries, claim concordance, and A/E/C/T/P/I gates.
- Present `NA`, G0, G1, G2, G3, and G4 separately at artifact-lineage/profile level. Treat G1 as a claim/indication, G2 as specified bounded reuse, G3 as demonstrated bounded reuse in at least two materially distinct assured contexts, and G4 as independently corroborated bounded reuse.
- Report DAE breadth separately from evidence tier and show demonstrated coverage as a subset; never rank a broader claim above a narrower but better-supported artifact merely because of scope.
- Collapse duplicate reports of one tailoring application and distinguish same-family, same-organization/separate-team, and external/independent reuse. Use artifact identity and application denominators rather than publication counts as transfer evidence.
- Retain one-context tailoring, partial gates, missing assurance, failed/out-of-envelope use, burdens, and contradictory evidence in the profile even when they cannot support G3/G4.
- Use wording such as “G3 evidence supports bounded reuse of [artifact scope] in [demonstrated contexts], within the stated DAE.” Do not report a model as proven, universally, truly, or context-free generic.
- A post-tailoring assurance record or tailoring burden enters direct RQ3 or RQ2 synthesis only when its separate linkage/attribution rule is satisfied; genericity tier alone demonstrates neither V&V integration nor benefit.

### RQ2

- Synthesize only explicitly EPS-thread-attributed outcomes and implementation burdens.
- Keep EPS engineering outputs separate from records of MBSE-enabled value or burden.
- Present record role, outcome category, author-claimed and evidence-supported direction, burden category, proposed mechanism, evidence type, comparator, confidence, and lifecycle stage together.
- Treat unsupported claims as evidence about claim prevalence, not demonstrated effects; do not equate `not_reported` with a null result or infer net benefit from record counts.

### RQ3

- Map EPS target-to-model-to-V&V chains and stratify linkage scope (`eps_specific` versus `system_wide_eps_linked`), V&V object, criterion completeness, executed pre-physical evidence, and downstream model-to-test continuity.
- Report analysis-only, system-wide co-occurrence, and missing-link near misses separately; report a missing criterion as an evidence-completeness limitation rather than silently discarding an otherwise explicit EPS-linked V&V record.
- Do not infer EPS-specific V&V integration or an EPS-specific verdict from a system-wide activity or report-level co-occurrence.

### Cross-cutting safeguards

- Report separate denominators for study/implementation report families, reports, EPS model threads, reusable-artifact lineages/profiles, tailoring applications, input/assumption records, outcome/burden records, and V&V records. PRISMA flow counts remain record/report based.
- Treat tailoring applications, outcome/burden records, and V&V records as linked to reports and dependent within report families; do not treat report counts as independent artifact reuse.
- Stratify Route A and Route B before presenting combined totals.
- Identify recurring reports from the same study/implementation family; do not count them as independent replication.
- Stratify institutional technical reports and other gray literature from peer-reviewed scholarly reports and include publication-provenance sensitivity views where informative.
- Use quality, linkage/lineage confidence, and genericity-gate sensitivity views, including Route-A-only, high-confidence, G3/G4, and artifact-available subsets where informative; do not convert the genericity tier into a numerical quality score.
- Interpret cross-tabs only as descriptive co-reporting unless a direct extracted link supports a relationship.
- Retain `not_reported`, `none`, `not_applicable`, `uncertain`, and invalid/unmapped values distinctly.
- Treat sparse direct evidence as a review finding rather than filling gaps with generic whole-spacecraft MBSE claims.

## Required new-run artifacts

After protocol approval, the restarted review must generate or regenerate, with run provenance:

- integrated protocol approval/version/amendment record, study/implementation report-family registry, reusable EPS artifact-lineage registry, tailoring-application table, and read-only legacy and Buruso-recall known-item registers;
- completed version-1.5 pre-final pilot register from [`pilots-to-run-v1.5.md`](pilots-to-run-v1.5.md), exact PRISMA-S-compatible search log, versioned source-matching dictionary/code, and raw source-specific search results;
- search manifest with file checksums, source dates, interface details, restrictions, and rights/access status;
- merged/deduplicated candidate set and deduplication report;
- title/abstract and full-text screening log, retrieval log, accessible corpus, and cited full-text exclusion table with one primary reason per report;
- run-specific corpus, identifiers, and extraction codebook;
- per-report extraction files with thread, artifact-lineage/profile and tailoring-application links, outcome/burden, and V&V records, plus an artifact-level claim-to-evidence table;
- compiled extraction dataset, bibliography, validation report, and analysis code; and
- machine-readable PRISMA count reconciliation, official PRISMA 2020 flow diagram, synthesis outputs, and completed PRISMA-S/PRISMA 2020 checklists.

Licensed exports, copyrighted abstracts, and full texts need not be made public where rights prohibit it. Preserve them securely where permitted and publish or archive the exact methods, dates, manifests, derived counts/decisions, codebook, code, and a rights-aware availability statement.

## Completed-review reporting

The final report will identify itself as a systematic review and use the PRISMA 2020 checklist and 12-item abstract guidance. It will:

- report every information source actually used, its execution date, and the common 2026-08-10 evidence cutoff, with failed/planned-but-unused sources distinguished;
- link to verbatim final source-native strategies and PRISMA-S logs rather than a cleaned representative query;
- describe screening, extraction, second checks, conflict handling, and model assistance exactly as performed, never calling model-assisted checking independent human review;
- explain that no pooled effect estimate is planned and label every descriptive count/proportion by its report-family, report, thread, artifact-lineage/profile, tailoring-application, outcome/burden, or V&V denominator;
- use the new-review databases-and-other-sources flow diagram with records/reports—not linked analytic units—in its boxes;
- cite apparently eligible full reports excluded at full text with source-locatable reasons;
- present appraisal, reporting-bias, and conclusion-confidence results using the framework above; and
- report protocol access/version, every amendment/deviation, review-process and evidence limitations, and data/code/material availability.

The exact administrative declarations intentionally deferred above must be completed or explicitly reported as absent before publication; they are not silently implied by methodological freeze.

The version-1.2 PRESS-corrected source-interface pilots, version-1.3 bounded-genericity/search pilots, version-1.4 source-addition/interface gates, and pre-authorization IAF gate are logged as no-screening diagnostics. This model-assisted protocol and search review involved no human information specialist; model-assisted checks are not represented as independent human peer review. Version 1.5 was frozen and authorized on 2026-08-10 before any valid final discovery search, codebook creation, screening, or extraction. Its mandatory remaining pilots are listed in [`pilots-to-run-v1.5.md`](pilots-to-run-v1.5.md). No pilot output, calibration record, or opaque source identifier is a candidate, and every final discovery method authorized here—including IAF—must use clean version-1.5 post-authorization artifacts. Subsequent changes require a prospective, versioned deviation record.
