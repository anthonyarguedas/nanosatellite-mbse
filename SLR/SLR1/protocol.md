# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems

- **Working branch:** `slr1-1.1-restart`
- **Common evidence cutoff:** 2026-08-24
- **Final searches merged and deduplicated in commit:** NA
- **Citation chasing finished in commit:** NA
- **Full-text screening completed in commit**: NA

## Review type and terminology

This work is a **systematic review with an evidence-map synthesis**. Throughout the protocol, *systematic review* names the overall method of identifying, selecting, appraising, and synthesizing evidence; *evidence map* names the structured descriptive output. Do not call the work a *systematic mapping study*: Kitchenham and Charters use that term for broad, high-level classification with deliberately limited extraction, whereas this review performs in-depth extraction and appraisal of linked evidence units.

## Review status and restart policy

This protocol defines a **new systematic review run** on model-based systems engineering (MBSE) for nanosatellite electrical power systems (EPSs). The work is on branch `slr1-1.1-restart`. It is not an amendment to or update of the earlier whole-nanosatellite/EPS review on the `main` branch.

Treat all material from the earlier review as legacy or pilot material. This includes searches, screening decisions, the report set, extractions, the codebook, the synthesis, and the manuscript.

## Reporting framework

Use the following guidance:

- [PRISMA-P (2015) protocols and checklist](https://www.prisma-statement.org/protocols) for this protocol;
- [PRISMA-S (2021) search reporting](https://www.prisma-statement.org/prisma-search) and [Rethlefsen et al. (2021)](https://doi.org/10.1186/s13643-020-01542-z) to design the strategy in [Part 2](protocol-discovery-and-screening.md#search-strategy) and to run, save, and report every search in a search log;
- Kitchenham and Charters (2007), *Guidelines for performing Systematic Literature Reviews in Software Engineering*, as complementary engineering conduct guidance for PICOC framing, heterogeneous evidence, protocol and form piloting, selection and extraction consistency, duplicate-report handling, and descriptive or narrative synthesis; and
- the [PRISMA 2020 statement](https://www.prisma-statement.org/prisma-2020-statement), [checklist](https://www.prisma-statement.org/prisma-2020-checklist), [abstract guidance](https://www.prisma-statement.org/abstracts), and [flow templates](https://www.prisma-statement.org/prisma-2020-flow-diagram) for the completed review.

PRISMA supplies reporting guidance; Kitchenham and Charters supply complementary engineering-review conduct guidance. Neither proves that evidence is valid. This systematic review produces an engineering evidence map, so do not invent clinical effect measures, clinical risk-of-bias tools, or GRADE ratings.

Use the PRISMA 2020 flow diagram for a new systematic review that uses databases and other sources.

 [ ] Registration and contact details, contributor and guarantor details, and declarations about funding, sponsors, and competing interests will be completed later. State clearly when any of these details are still absent. Do not claim that this protocol is administratively complete under PRISMA-P until the above are reported.

## Need for this review

Before the first final primary-evidence search, conduct the bounded [prior-secondary-review search and CRD/DARE assessment](protocol-prior-secondary-reviews.md). This supporting process uses only Scopus and Web of Science Core Collection, has separate records and counts, and is not a tertiary review. It will determine whether an existing review already covers the nanosatellite-EPS population, direct MBSE relationship, and RQ1–RQ3; identify scope, currency, or methodological gaps; and provide the justification for proceeding.

## Review objective

The review will map how MBSE represents and supports nanosatellite EPS work, including typed EPS elements and requirements, dedicated use-case, operational, feared-event, failure, recovery, and V&V test-case records, ordered modeled behavior and test steps, structured model representations and relationships among views, exchanges, dependencies, boundaries, scenario and model coverage, viewpoints and abstraction, tools and equipment, model generation methods, engineering workflows with linked lifecycle phases and activities, procedural reporting detail, inputs and assumptions, implementation, artifact, method, and workflow reuse or tailoring, reported outcomes and burdens, and links to V&V before physical integration or testing.

## PICOC

| Population | Intervention | Comparison | Outcome | Context | Related RQ(s) |
|---|---|---|---|---|---|
| EPSs for orbital CubeSat or nanosatellite-class missions | EPS-primary MBSE or a clear embedded EPS model thread | Not required | EPS functions, behaviors, external actors and systems/subsystems, logical and physical components, interfaces, states or modes, scenarios, use cases, feared events, faults or failures, and requirements; scenario and V&V test-case definitions and records; structured representations of organizational or mission context, requirements, use-cases, scenarios, sequences, states or modes, structure or architecture, interfaces, data-/resource-flows, V&V activities or test cases; dependencies, coverage, viewpoints, boundaries, abstraction; model generation/reuse/tailoring method, modeling language, and modeling tools; why the model is used; method and model inputs and assumptions; artifact identity and lineage; artifact, method, and workflow applicability, reusable core, variation points, tailoring or adaptation rules and steps, demonstrated uses and checks, reuse levels, and required roles and resources | Nanosatellite systems engineering throughout the lifecycle | RQ1 |
| EPSs for orbital CubeSat or nanosatellite-class missions | EPS-linked MBSE artifacts, analyses, and model-enabled work | When reported: document-based practice, manual analysis, another toolchain, an earlier mission or model, or another clear comparator | Beneficial, null, mixed, or adverse EPS-linked technical and process outcomes, plus implementation burdens. Priority topics are reliability and mission assurance, reproducibility and reuse, and integration and interoperability | Nanosatellite development and decision-making | RQ2 |
| EPSs for orbital CubeSat or nanosatellite-class missions | EPS-specific or system-wide but EPS-linked model-based V&V before physical integration or test | When reported: separate or document-based V&V, manual checking, another method, or no comparator | V&V scope and object, links to V&V artifacts, executable checks, results, virtual integration, and continuity from model to test | Analysis and V&V before physical work, with later physical links recorded separately | RQ3 |

## Research questions

1. **RQ1** How are nanosatellite EPSs represented and used in MBSE approaches, how are generic or reference models constructed, and what model generation methods, engineering workflows, inputs, assumptions, implementation needs and footprint, and bounded artifact, method, or workflow reuse and tailoring practices are reported? What evidence supports these characterizations?

2. **RQ2** What technical or process outcomes and implementation burdens do sources attribute to EPS-linked MBSE? For each attribution, how does the source say the MBSE artifact or activity led to the outcome or burden, and what evidence supports that claimed link?

3. **RQ3** How is EPS-linked MBSE connected to V&V before physical integration or testing, and what evidence is reported for its pass/fail criteria, execution, results, and model-to-test continuity?

### Report eligibility versus question contribution

An outcome, burden, V&V activity, reuse claim, reuse or tailoring application, evidence-basis code, or support judgment is never an additional report-level inclusion test. Every eligible report contributes to RQ1 through its report-level extraction. Create direct RQ2 findings and RQ3 activities only when their respective definitions are met. A question-contribution or support code cannot make an otherwise ineligible report eligible.

Within RQ2, reliability and mission assurance, reproducibility and reuse, and integration and interoperability are priority categories for presentation. Code all eligible outcomes and burdens without favoring a direction or hiding other categories after seeing the results.

## Operational definitions

### Nanosatellite population

An eligible platform is an actual or planned orbital spacecraft that the source calls a CubeSat or nanosatellite. Recognized CubeSat form factors are eligible even if a particular spacecraft is outside the strict 1–10 kg nanosatellite range. A reference, template, or early design model can be eligible without a named or built mission if it clearly targets orbital CubeSat or nanosatellite development.

Exclude:

- CanSats and other educational demonstrators that are not orbital;
- studies only about PocketQubes or picosatellites, unless they also report a separate CubeSat or nanosatellite case;
- generic SmallSat studies, larger small satellites, and conventional spacecraft, unless the source also identifies a CubeSat or nanosatellite-class case and reports its results separately; and
- mixed-platform evidence when the nanosatellite findings cannot be separated.

### EPS boundary and elements

EPS content can include:

- power generation and solar arrays;
- energy storage and battery management;
- conversion, conditioning, regulation, and distribution;
- protection, monitoring, and control;
- electrical buses and harnesses;
- power interfaces;
- operating modes and load or energy profiles;
- power and energy budgets and margins;
- degradation;
- hazards, feared events, faults or failures, fault propagation, risk controls, and recovery; and
- related requirements.
- another subsystem only when it is clearly an EPS load, interface, environmental dependency, operating-mode driver, or source of an EPS requirement. Do not synthesize that subsystem's internal design.

### MBSE qualification

A report does not have to use the term “MBSE.” It must, however, describe a structured system model used for a systems-engineering purpose. The report must show modeled elements and explicit relationships across at least two systems-engineering concerns. Examples of concerns are requirements, function or behavior, architecture, interfaces, parametric analysis, design decisions, and V&V.

The relationships must involve the same EPS entity or thread that makes the report eligible. Whole-report MBSE work that is unrelated to isolated EPS content does not qualify that EPS content.

Qualifying approaches may use SysML, Arcadia or Capella, object-oriented system models, reference models, or connected digital-engineering environments. A stand-alone circuit or battery model, SPICE/MATLAB/Simulink simulation, optimization, power-budget spreadsheet, or component-sizing calculation is not MBSE by itself. It qualifies only if the source explicitly binds, traces, transforms, or otherwise connects its inputs or outputs to a structured system model.

### Eligible EPS evidence routes

Assign each full-text report to one of two routes. The routes are mutually exclusive. Use Route A only when the report's objective, modeled viewpoint or boundary, and substantial methods or results focus on the EPS. Otherwise, use Route B if it has a qualifying embedded thread. A report can contain several EPS threads, but its report-level route does not change.

- **Route A — EPS-primary MBSE:** The EPS, electrical-power viewpoint, or a defined EPS function or architecture is the main modeled boundary. The report identifies an EPS model artifact and at least one explicit relationship between that EPS content and another systems-engineering concern.
- **Route B — embedded EPS model thread:** A wider nanosatellite MBSE report contains at least one EPS thread with an [EPS anchor, model anchor, and EPS-to-model bridge](protocol-extraction.md#eps-representation).

External repositories, evolving models, and author-provided artifacts are not independently retrieved or inspected.

## Inclusion and exclusion criteria

| Criterion | Plain-English rule | RQ(s) |
|---|---|---|
| Publication date | Include a report only when an eligible version is dated from 2011-01-01 through the common evidence cutoff. | 1–3 |
| Language | The full report must be in English. English metadata does not prove that the report itself is in English. If the full text cannot be obtained, use `not_retrieved` instead of making a language assumption. | 1–3 |
| Publication type | Include a full primary-research journal article; conference, proceedings, or workshop paper; workshop presentation (for ESA Indico only); research chapter in an edited scholarly book; institutional technical report; arXiv preprint; master's thesis; or doctoral thesis or dissertation. | 1–3 |
| Degree completion | Include a thesis or dissertation only when full-text screening establishes `completion_status` as `completed`. Use `exclude_wrong_completion_status` when it is `in_progress_or_incomplete` or `unclear`. | 1–3 |
| Scientific scope | The work must satisfy the canonical [nanosatellite population](protocol.md#nanosatellite-population), [EPS boundary](protocol.md#eps-boundary), [MBSE qualification](protocol.md#mbse-qualification), and [Route A or Route B](protocol.md#eligible-eps-evidence-routes) rules. | 1–3 |
| Secondary studies | Exclude secondary studies. | 1–3 |
| Abstract-only or non-research material | Exclude posters or abstracts without full papers; thesis or dissertation metadata and abstract stubs without the completed substantial report; proposals and prospectuses; undergraduate, bachelor's, or non-degree projects; advertisements; and non-scholarly web material. | 1–3 |
| Retrieval status | Scientific eligibility does not depend on open access. If the report is not obtained after the required retrieval attempts, including a restricted or embargoed thesis, record `not_retrieved`. Do not silently exclude it for scientific reasons. | 1–3 |
