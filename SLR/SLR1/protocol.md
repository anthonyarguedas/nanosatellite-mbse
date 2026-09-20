# [ABANDONED] Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems

- **Note**: This SLR has been **abandoned**. It's only purpose now is a traceability archive for the chunks used in `embeddings/search.py`.
- **Final included reports:** `SLR/SLR1/included_reports.json`
- **Common evidence cutoff:** 2026-08-24

## Review type and terminology

This work is a systematic review with an evidence-map synthesis. Throughout the protocol, systematic review names the overall method of identifying, selecting, appraising, and synthesizing evidence. Evidence map names the structured descriptive output. Do not call the work a systematic mapping study, as Kitchenham and Charters use that term for broad, high-level classification with deliberately limited extraction, whereas this review performs in-depth extraction and appraisal of linked evidence units.

## Reporting framework

Use the following guidance:

- [PRISMA-P (2015) protocols and checklist](https://www.prisma-statement.org/protocols) for this protocol;
- [PRISMA-S (2021) search reporting](https://www.prisma-statement.org/prisma-search) and [Rethlefsen et al. (2021)](https://doi.org/10.1186/s13643-020-01542-z) to design the discovery and screening strategy and to run, save, and report every search in a search log;
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
1. Source-reported types for EPS model artifacts (such as MBSE models, digital twins, repositories, packages, or simulation environments), with links to their presented representations when reported;
1.2. modeling language/ontology/metamodel/theory if stated (could be more than one for different representations);
1.3. what the EPS model artifacts are used for;
1.4. if the model artifact is called generic, record any justification with the original wording;
1.5. if the model artifact is explicitly stated to be part of a lineage, record it with the original wording.

2. Structured model representations (views, diagrams, matrices, tables, or model excerpts presented in the source) of organizational or mission context, requirements, scenarios, sequences, states or modes, structure or architecture, interfaces, and data-/resource-flows, recording:
2.1. each representation's source-reported name and type; if no name or type is reported, classify it with a type of electrical diagram, informal architectue/structure diagram, simulation/digital twin diagram, sequence diagram, or black box diagram;
2.2. containing model artifacts when reported;
2.3. modeling language/ontology/metamodel/theory (only one per representation);
2.3. coverage of engineering viewpoints (electronics, electrical, software, mechanical, thermal, chemical);
2.4 source-reported names and types for modeled EPS elements and relationships, and annotations carried by relationships, plus the endpoints and direction of each relationship when reported, before language-neutral semantic classification;
2.5 language-neutral semantic classifications of modeled EPS content and relationships, including external actors and systems/subsystems, capabilities, functions/behaviors, activities/actions, data/resource flows and exchanges, exchanged items/signals, interfaces, ports/connectors, blocks/components/parts/instances and any source-reported or evident (i.e. explicitly named hardware or software) logical or physical classification, allocations/mappings and other connections/links, states or modes, state or mode transitions, scenarios, sequences, use cases, hazards/feared events/faults/failures, and requirements, noting whether each element is inside or outside the EPS boundary and identifying the external actor or system/subsystem for outside elements when reported. classify any annotations carried by relationships as guard, cost, parameter, exchanged item/data/resource or other formal or executable content described in 2.6;
2.6. formal or executable content (equations, guards, constraints, parameters, algorithms, simulators, or explicitly-stated physically-implemented behavior), with links from this content to the corresponding model elements, relationships, and structured representations recorded above;
2.7. elements labelled as reusable core or variation points of the model (with links to existing model elements).

3. EPS model generation/reuse/tailoring methods (which could be implicitly or explicitly used to generate/reuse/tailor the models already extracted);
3.1. modeling language/ontology/metamodel/theory if stated;
3.2. inputs and assumptions;
3.3. applicability;
3.4. reusable core and variation points of the model generated/reused/tailored (with links to existing model elements and their containing representations if applicable, and avoiding duplication if this has already been extracted for the model itself),
3.5. tailoring or adaptation phases, rules and steps, tools, and post hoc checks (only extract as text if not modeled, see 3.6);
3.6. if the method itself has a structured representation:
3.6.1. the representation's source-reported name and type;
3.6.2. each represented method element's source-reported name and native type before semantic classification;
3.6.3. represented phases, activities or steps, stakeholders or roles, inputs, outputs, assumptions, requirements, applicability conditions, rules, decisions, models, model elements, reusable cores and variation points involved in the steps, tools, checks, and the other element types also used for EPS element representations;
3.6.4. source-reported name and native type of each represented relationship between method elements, its endpoints and direction when reported, and its carried annotations with source name and language-neutral type;
3.7. demonstrated reuses of the method, distinguishing if the report generates and reuses its own method or if the report reuses a method introduced elsewhere.
3.8. demonstrated tailorings of the method (that is, one report tailoring another report's method and explicitly stating it).
3.9. If the method is called generic, record any justification with the original wording.
3.10. If the method is explicitly stated to be part of a lineage, record it with the original wording.

### RQ3

Intervention: EPS-specific or system-wide but EPS-linked model-based V&V
Comparison: When reported: separate or document-based V&V, manual checking, another method, or another explicit comparator
Outcome:
1. source-reported types for V&V strategy artifacts (such as MBSE models, repositories, packages, simulation environments, executable scripts, or document-based definitions), with links to their presented representations when reported. An EPS model artifact that does not include any V&V content must not be duplicated as a V&V strategy artifact.
1.2. modeling language/ontology/metamodel/theory if stated (could be more than one for different representations);
1.3. whether the strategy artifact is integrated into an EPS model artifact of interest or is separate but linked, or separate and unlinked.
1.4. If the strategy artifact is called generic, record any justification with the original wording.
1.5. If the strategy artifact is explicitly stated to be part of a lineage, record it with the original wording.

2. strategy artifact representations (views, diagrams, matrices, tables, model excerpts or text-based definitions presented in the source) of V&V requirements, objectives, pass/fail criteria, scenarios/test cases, sequences, states or modes, structure or architecture, interfaces, and data-/resource-flows, recording each representation's source-reported name and type (including "text-based");
2.2. modeling language/ontology/metamodel/theory (or text-based, only one per representation);
2.1. containing strategy artifacts when reported,
2.3. whether the representation is integrated into a representation of the EPS model artifact of interest or is separate but linked, or separate and unlinked, or unknown.
2.4. coverage of engineering viewpoints (electronics, electrical, software, mechanical, thermal, chemical);
2.5. execution type (check/computation, simulation, co-simulation, SIL, HIL, physical execution, or deployed/operational execution);
2.6 source-reported names and types for modeled V&V elements and relationships, and annotations carried by relationships, plus the endpoints and direction of each relationship when reported, before language-neutral semantic classification;
2.7. language-neutral semantic classifications of modeled V&V content and relationships, including external actors and systems/subsystems, functions/behaviors, activities/actions, data/resource flows and exchanges, exchanged items/signals, interfaces, ports/connectors, blocks/components/parts/instances and any source-reported logical or physical classification, test setups/equipment, properties/parameters/constraints, allocations/mappings and other connections/links, states or modes, state or mode transitions, scenarios, sequences, use cases, hazards/feared events/faults/failures, requirements, objectives, and pass/fail criteria. classify any annotations carried by relationships as guard, cost, parameter, exchanged item/data/resource or other formal or executable content described in 2.6;
2.6. formal or executable content (equations, guards, constraints, parameters, algorithms, simulators, or explicitly-stated physically-implemented behavior), with links from this content to the corresponding model elements, relationships, and structured representations recorded above.
2.7. elements labelled as reusable core or variation points of the V&V strategy artifact (with links to existing model elements).

3. methods for: V&V strategy artifact generation/reuse/tailoring, and executing V&V test cases/scenarios from a V&V or EPS model, and updating an EPS model or V&V strategy based on test results (which could all be a single method covering these 3 phases and more):
3.1. modeling language/ontology/metamodel/theory if stated;
3.2. inputs and assumptions, for generation/reuse/tailoring, noting specifically if an EPS model or modeled element is an input to the method (for the other two it's an obvious yes);
3.3. applicability (for V&V test cases/scenarios execution methods, note whether it is applicable to check/computation, simulation, co-simulation, SIL, HIL, physical execution, or deployed/operational execution);
3.4. phases, rules and steps, tools, and post hoc checks (only extract as text if not modeled, see 3.6), noting if the 3 phases from 3 are covered;
3.5. reusable core and variation points of the V&V strategy artifact generated/reused/tailored (for generation/reuse/tailoring methods only, with links to existing model elements and their containing representations if applicable, and avoiding duplication if this has already been extracted for the V&V strategy artifact itself),
3.6. if the method itself has a structured representation:
3.6.1. the representation's source-reported name and type;
3.6.2. each represented method element's source-reported name and native type before semantic classification;
3.6.3. represented phases, activities or steps, stakeholders or roles, inputs, outputs, assumptions, requirements, applicability conditions, rules, decisions, models, model elements, reusable cores and variation points involved in the steps, tools, checks, and the other element types also used for EPS element representations;
3.6.4. source-reported name and native type of each represented relationship between method elements, its endpoints and direction when reported, and its carried annotations with source name and language-neutral type;
3.7. demonstrated reuses of the method, distinguishing if the report generates and reuses its own method or if the report reuses a method introduced elsewhere.
3.8. demonstrated tailorings of the method (that is, one report tailoring another report's method and explicitly stating it).
3.9. If the method is called generic, record any justification with the original wording.
3.10. If the method is explicitly stated to be part of a lineage, record it with the original wording.

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

Some hand-picked reports may be included as Route C even if excluded as per the above criteria.
