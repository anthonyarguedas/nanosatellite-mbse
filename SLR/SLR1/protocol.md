# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems

- **Working branch:** `slr1-1.1-restart`
- **Common evidence cutoff:** 2026-08-24

## Review type and terminology

This work is a systematic review with an evidence-map synthesis. Throughout the protocol, systematic review names the overall method of identifying, selecting, appraising, and synthesizing evidence. Evidence map names the structured descriptive output. Do not call the work a systematic mapping study, as Kitchenham and Charters use that term for broad, high-level classification with deliberately limited extraction, whereas this review performs in-depth extraction and appraisal of linked evidence units.

## Reporting framework

Use the following guidance:

- [PRISMA-P (2015) protocols and checklist](https://www.prisma-statement.org/protocols) for this protocol;
- [PRISMA-S (2021) search reporting](https://www.prisma-statement.org/prisma-search) and [Rethlefsen et al. (2021)](https://doi.org/10.1186/s13643-020-01542-z) to design the strategy in [Part 2](protocol-discovery-and-screening.md#search-strategy) and to run, save, and report every search in a search log;
- Kitchenham and Charters (2007), *Guidelines for performing Systematic Literature Reviews in Software Engineering*, as complementary engineering conduct guidance for PICOC framing, heterogeneous evidence, protocol and form piloting, selection and extraction consistency, duplicate-report handling, and descriptive or narrative synthesis; and
- the [PRISMA 2020 statement](https://www.prisma-statement.org/prisma-2020-statement), [checklist](https://www.prisma-statement.org/prisma-2020-checklist), [abstract guidance](https://www.prisma-statement.org/abstracts), and [flow templates](https://www.prisma-statement.org/prisma-2020-flow-diagram) for the completed review.

PRISMA supplies reporting guidance, while Kitchenham and Charters supply complementary engineering-review conduct guidance.

Use the PRISMA 2020 flow diagram for a new systematic review that uses databases and other sources.

## Need for this review

Before the first final primary-evidence search, conduct the bounded [prior-secondary-review search and CRD/DARE assessment](protocol-prior-secondary-reviews.md). This supporting process uses only Scopus and Web of Science Core Collection, has separate records and counts, and is not a tertiary review. It will determine whether an existing review already covers the nanosatellite-EPS population, direct MBSE relationship, and RQ1–RQ3; identify scope, currency, or methodological gaps; and provide the justification for proceeding.

## PICO

Population: EPSs for orbital CubeSat or nanosatellite-class missions

### RQ1

Intervention: EPS-linked MBSE artifacts, analyses, and model-enabled work
Comparison: When reported: document-based practice, manual analysis, another toolchain, an earlier mission or model, or another explicit comparator
Outcome: Beneficial, null, mixed, or adverse EPS-linked technical and process outcomes, plus implementation burdens. Priority topics are reliability and mission assurance, reproducibility and reuse, and integration and interoperability

### RQ2

Intervention: EPS-primary MBSE or a clear embedded EPS model thread
Comparison: Not required
Outcome:
- structured representations (models) of organizational or mission context, requirements, scenarios, sequences, states or modes, structure or architecture, interfaces, data-/resource-flows, noting coverage of engineering viewpoints (electronics, electrical, software, mechanical), and level of abstraction;
- modeled EPS functions/behaviors, data/resource flows and exchanges, interfaces, ports, logical and physical components, connections/links between logical and physical components, states or modes, state or mode transitions, scenarios, use cases, feared events/faults/failures, and requirements, noting which ones belong to the EPS and which to external actors and systems/subsystems, where external actors and systems/subsystems can also be a standalone model element, and noting executable properties (mathematical expressions, numeric values, algorithms, simulators, physical executability) assigned to the modeled elements;
- what the EPS models are used for;
- EPS model generation/reuse/tailoring methods, modeling language/ontology/metamodel, modeling/reuse/tailoring tools;
- model and method inputs and assumptions, applicability, reusable core, variation points, tailoring or adaptation rules and steps, tools, demonstrated uses and post hoc checks, distinguishing which of these elements are novel/tailored and which are reused from another method (i.e. ARCADIA, OOSEM);
- if a method has a structured representation, the structured representation and its modeled elements;
- if the model or method is called generic, why;
- model or method lineage, if reported

### RQ3

Intervention: EPS-specific or system-wide but EPS-linked model-based V&V
Comparison: When reported: separate or document-based V&V, manual checking, another method, or another explicit comparator
Outcome:
- structured representations (models) of V&V requirements, objectives, pass/fail criteria, scenarios/test cases, sequences, states or modes, structure or architecture, interfaces, data-/resource-flows that are modeled separately from the EPS, noting coverage of engineering viewpoints (electronics, electrical, software, mechanical), and level of abstraction;
- modeled V&V functions/behaviors, data/resource flows and exchanges, external actors and systems/subsystems, interfaces, ports, logical and physical components, connections/links between logical and physical components, states or modes, state or mode transitions, scenarios, use cases, feared events, faults or failures, requirements, objectives, pass/fail criteria that are modeled separately from the EPS, noting executable properties (mathematical expressions, numeric values, algorithms, simulators, physical executability) assigned to the modeled elements;
- definitions of setup and equipment, requirements, objectives, and pass/fail criteria for V&V test cases/scenarios that are not modeled;
- links between V&V models, modeled elements or definitions; and EPS models or modeled elements;
- V&V model or V&V test case/scenario definition generation/reuse/tailoring methods, noting specifically if an EPS model or modeled element is an input to the method;
- methods for EPS or V&V model/definition update from test results;
- methods for V&V test case/scenario execution from V&V or EPS model and its type (check/computation, simulation, SIL, HIL, physical execution);
- model and method method inputs and assumptions, applicability, reusable core, variation points, tailoring or adaptation rules and steps, tools, demonstrated uses and post hoc checks, distinguishing which of these elements are novel/tailored and which are reused from another method (i.e. ARCADIA, OOSEM, V-Model);
- if a method has a structured representation, the structured representation and its modeled elements;
- if the V&V model or method is called generic, why;
- model or method lineage, if reported

## Research questions

**RQ1** What technical or process outcomes and implementation burdens do sources attribute to EPS-linked MBSE? For each attribution, how does the source say the MBSE artifact or activity led to the outcome or burden, and what evidence supports that claimed link?

**RQ2** How are nanosatellite EPSs represented and used in MBSE approaches? How are EPS MBSE models generated, reused, tailored, verified, or validated? What evidence supports these characterizations?

**RQ3** How is EPS-linked MBSE connected to V&V before physical integration or testing, and how is model-to-test continuity performed?

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

| Criterion | Plain-English rule |
|---|---|
| Publication date | Include a report only when an eligible version is dated from 2011-01-01 through the common evidence cutoff. |
| Language | The full report must be in English. English metadata does not prove that the report itself is in English. If the full text cannot be obtained, use `not_retrieved` instead of making a language assumption. |
| Publication type | Include a full primary-research journal article; conference, proceedings, or workshop paper; workshop presentation (for ESA Indico only); research chapter in an edited scholarly book; institutional technical report; arXiv preprint; master's thesis; or doctoral thesis or dissertation. |
| Degree completion | Include a thesis or dissertation only when full-text screening establishes `completion_status` as `completed`. Use `exclude_wrong_completion_status` when it is `in_progress_or_incomplete` or `unclear`. |
| Scientific scope | The work must satisfy the canonical [nanosatellite population](protocol.md#nanosatellite-population), [EPS boundary](protocol.md#eps-boundary), [MBSE qualification](protocol.md#mbse-qualification), and [Route A or Route B](protocol.md#eligible-eps-evidence-routes) rules. |
| Secondary studies | Exclude secondary studies. |
| Abstract-only or non-research material | Exclude posters or abstracts without full papers; thesis or dissertation metadata and abstract stubs without the completed substantial report; proposals and prospectuses; undergraduate, bachelor's, or non-degree projects; advertisements; and non-scholarly web material. |
| Retrieval status | Scientific eligibility does not depend on open access. If the report is not obtained after the required retrieval attempts, including a restricted or embargoed thesis, record `not_retrieved`. Do not silently exclude it for scientific reasons. |
