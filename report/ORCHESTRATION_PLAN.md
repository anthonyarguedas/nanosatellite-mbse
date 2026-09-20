# OOSEM Orchestration Plan for a Nanosatellite EPS Framework

**Working title:** *An MBSE-Based Framework for the Design and Analysis of Nanosatellite Electrical Power Systems*

This project applies OOSEM to the architecture of a socio-technical engineering framework. The working title does not narrow the planned lifecycle coverage.

Three framing decisions govern the work:

1. **The system of interest is the nanosatellite EPS engineering framework.** Its physical architecture contains modeling tools, analysis services, repositories, integration mechanisms, compute nodes, data stores, and operating procedures.
2. **Nanosatellite EPS engineering is the reference domain.** Parameterized requirements, designs, analyses, FMEA, test data, and telemetry scenarios exercise the proposed architecture without tying it to one mission.
3. **The architecture study has three sprints, each ending with human review.** Sprint 1 defines the framework's measures, requirements, and use cases. Sprint 2 develops the logical architecture and physical alternatives. Sprint 3 evaluates alternatives and selects a preferred architecture. Framework construction and later OOSEM development activities remain in the overall roadmap beyond these three sprints.

The primary users are university teams. Commercial teams are also in scope when they accept the same lightweight operating assumptions. Cloud dependence, real-time collaborative editing, and enterprise permissions management are outside the required scope. Asynchronous review and local operation remain relevant capabilities.

Buruso et al. present Requirements Management (RM), Model Development (MD), Simulation and Analysis (SA), Configuration Management (CM), and Collaboration and Communication (CC) as overlapping lifecycle processes. Figure 16 shows CM and CC spanning the lifecycle. Model them first as capabilities and activities. OOSEM then derives logical components and allocates them to physical components.

The research addresses a reusable framework for nanosatellite EPS engineering. It does not seek merely to demonstrate a toolchain for one mission. The three-sprint study's claim is an evidence backed architecture selection with explicit uncertainty. Operational proof across the full lifecycle belongs to later implementation and verification.

## Review contract and research priorities

The primary human review artifact is one self-contained LaTeX report, with citations, narrative reasoning, SysML diagrams, and supporting tables and figures. The reader must be able to examine every important requirement, use case, architectural choice, and selection argument without opening auxiliary JSON or Markdown files.

Requirements and use case definition form a major research workstream, comparable in effort and importance to developing all three candidate architectures. Allocate substantial research, synthesis, modeling, and independent review effort before candidate synthesis. Revisit this work when evidence exposes gaps.

The evidence base includes Buruso et al. and the author's corpus of 129 papers, many focused on CubeSats, EPS, and MBSE. The author began an SLR under `SLR/SLR1/protocol.md`, then stopped after judging that it would likely reproduce Buruso et al.'s insights for a narrower population. Its contribution to this study is the collected, chunked, embedded, searchable corpus exposed through `embeddings/search.py`. Describe this history accurately. Do not present the abandoned review as a completed SLR or imply that all protocol steps were completed.

Use corpus mining to discover themes, requirements, use cases, standard scenarios, and existing partial frameworks. Follow retrieval and clustering with source reading and cited narrative synthesis. The report should explain how relevant papers contribute, where their approaches stop, and which parts can be reused or extended.

All non-SysML graphics must be monochrome and tightly packed while retaining legible labels. Use shapes, line styles, hatching, and direct labels where distinctions are needed.

## Initial candidate ingredients

| Ingredient | Architectural role | Decisions still needed |
|---|---|---|
| SysML v2 | Modeling language | Authoring tool, semantic validator, model ownership, repository, interchange mechanism |
| Python | Programming and analysis language | Runtime, packages, orchestration, schemas, result publication |
| Git | Configuration mechanism | Local workflow, artifact storage, baseline and change practices |
| NVIDIA Omniverse | Platform family | Relevant components, USD, connectors, local deployment, GPU needs, source authority, review value |
| CSRM | Reusable model content | Availability, provenance, licence, SysML v1 to v2 transformation, tailoring and validation |
| Automated FMEA | Required capability | Failure library, extraction rules, propagation model, criticality method, validation, human approval |

A complete candidate adds deployment nodes, data ownership, interface contracts, orchestration, artifact storage, proportionate security and recovery, operating procedures, and configuration baseline semantics. Complexity must be justified by user needs.

## Three-sprint structure

| Sprint | Steps | Reviewable outcome |
|---|---|---|
| **1. Define the framework** | 1–22 | Corpus synthesis, stakeholders, measures, mission-independent scenarios, use cases, and black-box requirements. Complete the tailored MCR and SRR. Stop before logical architecture definition. |
| **2. Develop architectural alternatives** | 23–32 | Logical architecture and at least three comparable physical candidates, with walkthroughs, assumptions, and planned feasibility tests. Review these work products in preparation for SDR. |
| **3. Evaluate and select** | 33–39 | Trade analysis, sensitivity, preferred architecture or conditional recommendation, and completed tailored SDR. |

At each sprint boundary, compile the cumulative self-contained LaTeX report with the completed work products and native SysML views. Pause for human review before starting the next sprint. Sprint 1 includes steps 17–22 so its requirements baseline includes black-box requirements rather than only high-level needs. Later architecture trace links remain explicitly pending until their sprint.

Measures and scoring anchors are established in Sprint 1. Sprint 2 uses them to develop comparable candidates. Sprint 3 formalizes the analysis cases and evaluates the candidates without changing criteria to favor a candidate. Any necessary requirements or criteria revision returns for human review.

All three sprints remain design work. Implementation and integration experiments require a separate decision after this study.

# Numbered execution plan

## A. Frame and prepare the study

### 1. State the architecture decision question

Use:

> Which physical architecture best enables a traceable, reproducible, affordable, and reusable framework for nanosatellite EPS engineering across concept, design, assembly and test, and operations?

Target university teams and commercial teams willing to use the same lightweight framework. Define the nanosatellite domain and lifecycle coverage. Require operation without cloud services. Do not make enterprise collaboration or permissions management acceptance criteria.

### 2. Define the system boundary

Create separate namespaces for:

- `FrameworkSOI`
- `EPSReferenceDomain`
- `PhysicalCandidates`
- `Analyses`
- `Traceability`
- `Evidence`
- `Views`

Framework components satisfy framework requirements. EPS components satisfy EPS requirements. Tool components do not satisfy spacecraft power requirements.

### 3. Tailor OOSEM and define the sprint boundary

Allocate OOSEM activities across the three sprints:

- **Sprint 1:** Setup model, analyze stakeholder needs, and analyze system requirements, including measures and use cases.
- **Sprint 2:** Define logical architecture and synthesize candidate physical architectures.
- **Sprint 3:** Optimize and evaluate alternatives and select the preferred architecture.
- **Every sprint:** Manage requirements traceability and conduct technical reviews appropriate to the completed work.

Retain in the later roadmap:

- Develop database
- Develop hardware where applicable
- Develop software
- Develop operator procedures
- Integrate and verify system

All three sprints stop short of building the framework or candidate integration prototypes. Research scripts, SysML study models, diagrams, and report generation support the design study. They do not implement the proposed framework.

Treat the OOSEM geometric model task as conditional. A traditional CAD model of the framework adds little value. A proposed SysML to USD correspondence may still matter when assessing Omniverse.

### 4. Use NASA technical reviews and tailored exit criteria

Use NASA review names and purposes, with the NASA Systems Engineering Handbook and applicable NASA review guidance as the source. Buruso et al. also acknowledge NASA lifecycle reviews. Cite the relevant sources in the report.

Use this provisional mapping, then confirm the detailed entry and success criteria against NASA guidance:

- **Mission Concept Review (MCR):** Review the framework purpose, intended users, scope, stakeholder needs, concept of use, and OOSEM tailoring.
- **System Requirements Review (SRR):** Review the framework requirements, use cases, measures, verification approach, and supporting evidence.
- **System Definition Review (SDR):** Review the logical definition, comparable physical alternatives, trade results, and preferred architecture.

Explain tailoring for a university framework study. These are study reviews using NASA guidance, without a claim of formal NASA approval. Logical architecture and candidate completeness checks feed SDR. They do not introduce a second set of invented gates.

Do not claim PDR or CDR maturity merely because a physical architecture has been selected. Retain later applicable NASA reviews in the development roadmap. A failed review returns work to the relevant OOSEM activity.

Distinguish reviews of this framework study from the mission lifecycle reviews that the future framework must help its users prepare for.

### 5. Develop a cited narrative evidence synthesis

Use LaTeX prose as the authoritative review format. For each substantive claim, explain the source contribution, applicability to nanosatellite EPS, limitations, and consequence for a need, requirement, use case, or architectural criterion. Use bibliography citations with page or section locators where appropriate.

Organize the synthesis around engineering problems and lifecycle continuity. Discuss existing frameworks and environments, including approaches that cover only some lifecycle stages. Explain complementary contributions, conflicting findings, and remaining gaps. Give relevant studies enough attention to make their contribution reviewable.

Use Buruso et al. to establish the broader gap and design space. Use the 129-paper corpus to deepen domain evidence. Verify product claims through primary papers and current documentation. The space robotics digital twin review can inform coupling, synchronization, assurance, and lifecycle principles. Its tool findings need EPS specific confirmation.

Plan corpus mining as follows:

1. Inspect corpus coverage and available embeddings. Establish the unit of analysis and distinguish papers from chunks and multiple reports of one study.
2. Combine targeted searches through `embeddings/search.py` with exploratory clustering of available embeddings. Add a small analysis script if needed. Do not assume the search interface already provides clustering.
3. Inspect representative, boundary, and outlier papers. Label themes from source content and search for evidence that challenges the emerging interpretation.
4. Produce cluster plots, theme frequencies, lifecycle coverage summaries, and other statistical analyses when they answer a research question. Report denominators and avoid giving long papers extra weight merely because they contain more chunks.
5. Explain preprocessing, embedding and clustering choices, parameter sensitivity, ambiguous assignments, and projection limitations in the report. A two-dimensional cluster plot is an exploratory view rather than proof of distinct research categories.
6. Translate source supported findings into proposed needs and use cases. Distinguish reported practice, author recommendations, and this study's engineering judgments.

Corpus frequency is evidence of coverage within this collection. It is not a direct measure of stakeholder priority or prevalence across the whole field. Preserve rare but important assurance needs. Document retrieval and corpus limitations.

Internal working data are permitted. No separate evidence ledger is required for human review. Put the complete decision-relevant reasoning in the report and its appendices.

### 6. Establish modeling and reporting conventions

Define naming and identifiers, units, requirement patterns, rationale, candidate naming, viewpoints, and required views.

Explicitly map the OOSEM baseline's SysML v1 work products to SysML v2 concepts. Cover requirements, behavior, structure, interfaces, allocations, variation, analysis, verification, and views. Document semantic differences and work products that need adaptation. OOSEM predates SysML v2, and OOSEM guidance for v2 remains under development. Do not assume a diagram-for-diagram translation.

Follow the NASA Systems Engineering Handbook guidance for writing requirements. Cite that guidance and state its use. Explain any deviations rather than reproducing an elaborate requirement-writing method.

Use native SysML views in the report. Apply the monochrome, compact graphic convention to corpus plots and all other non-SysML figures.

### 7. Create a lightweight study structure

Maintain:

- SysML v2 sources
- LaTeX report and bibliography
- Generated figures and tables
- Small research and report scripts where useful
- Inputs and results needed to understand and rerun the study's analyses

Do not require dependency locks, release manifests, a CI workflow, or a Python test suite for this design study. Record essential commands and tool versions in a short report appendix. Check calculations in proportion to their influence on the decision.

Validate SysML syntax and semantics and render the required native views. A focused suite of model checks may be useful. Apply the SysML tooling skill when modeling starts.

Distinguish study tooling from the proposed framework. Candidate architectures may include automated tests, configuration manifests, and stronger reproducibility mechanisms where their requirements justify them.

## B. Establish the mission-independent EPS reference domain

### 8. Define a parameterized EPS domain

Describe reusable variation points for:

- Orbit and eclipse profile
- Attitude assumptions
- Solar array configuration
- Battery configuration
- Power conditioning and distribution architecture
- Nominal and peak loads
- Operating modes
- Degradation assumptions
- Test data and telemetry availability

Use parameterized examples and bounded ranges with cited rationale. Evaluate more than one configuration so the framework supports reuse. Avoid adopting one mission's choices as general requirements. Reference BIRDS-4 only if a concrete mission example becomes necessary, and identify its illustrative role.

### 9. Define standard EPS benchmark scenarios

Use corpus evidence to ground scenarios such as:

- Nominal sunlit operation
- Worst case eclipse
- Peak payload load
- Safe mode
- Solar array degradation
- Battery aging
- Converter or switch failure
- AIT measurement import
- Delayed or incomplete telemetry replay

Specify inputs, outputs, assumptions, and expected engineering decisions. Mine recurring scenario families from the corpus and explain their selection in prose. These are reusable architecture evaluation scenarios, with execution deferred where it would require building the framework.

### 10. Assess CSRM availability and plan adaptation

Assign a CSRM sub-orchestrator two focused investigations:

- Locate the original CSRM distribution, versions, licence, provenance, and tool dependencies.
- Search the corpus for the thesis that reportedly reconstructed CSRM and published a repository. Follow its source references and compare the reconstruction with the original where available.

Treat both availability and the reported repository as questions to verify. Distinguish an original distribution, a reconstruction, and a local adaptation.

Assess reusable EPS elements, transformation risks, and separation of local extensions from source content. Specify the proposed SysML v2 adaptation and relationship checks. Preserve source provenance. Full migration and integration belong to development after the three-sprint study.

Report findings and reuse recommendations in the LaTeX narrative. A repository link alone is insufficient evidence of semantic equivalence or permission to reuse.

## C. Analyze stakeholder needs

### 11. Characterize current engineering practice

Use the corpus to describe current frameworks and workflows at the level needed to explain problems:

- Documents and spreadsheets
- Existing models and analysis scripts
- Manual transformations
- Review and approval flow
- Configuration practices
- Test and telemetry handling
- Repeated data entry
- Broken or missing trace links

Separate observed practices from inferred problems. Identify useful existing solutions and the lifecycle boundaries they reach.

### 12. Perform causal analysis

Analyze causes of lifecycle fragmentation, such as:

- Incompatible semantics
- Missing stable identifiers
- Multiple uncontrolled sources
- Manual conversion
- Stale analysis inputs
- Weak provenance
- Binary artifacts outside configuration control
- Phase local digital twins
- Missing interface contracts

Explain evidence and uncertainty for each causal interpretation. Avoid inferring causation from cluster membership or frequency alone.

### 13. Identify stakeholders and define the future domain

Include systems, EPS, requirements, analysis, reliability, AIT, and operations engineers, alongside configuration managers, reviewers, project managers, suppliers, and independent reproducers.

Model roles separately from headcount. A university team member may hold several roles. Capture concerns, learning needs, resource limits, and required views.

### 14. Specify mission requirements for the framework

Here, OOSEM mission requirements express the framework's purpose. They are independent of a particular spacecraft mission.

Develop and justify needs such as:

- Preserve traceability across lifecycle stages.
- Reproduce an EPS analysis from an approved baseline.
- Propagate requirement and configuration changes.
- Help users assess requirement quality and completeness.
- Help users verify model syntax, semantics, consistency, and traceability.
- Generate reviewable FMEA candidates from the system model.
- Maintain distinct as-designed, as-analyzed, as-built, as-tested, and as-operated configurations.
- Support controlled multidisciplinary review without requiring simultaneous editing.
- Produce a self-contained technical baseline.

Develop these through iterative corpus synthesis and stakeholder reasoning. For each proposed requirement, provide cited rationale, applicability, priority, assumptions, and a proposed verification approach. Clearly identify requirements that arise from the study's scope decisions.

### 15. Define framework use cases

Core use cases should include:

- Reuse and specialize the EPS reference model
- Capture, assess, and change a requirement
- Check a model's correctness and consistency
- Create an EPS design
- Execute power and energy analyses
- Generate and review an FMEA
- Compare EPS design variants
- Process a controlled change
- Create and restore a baseline
- Review a model asynchronously
- Import test or telemetry data
- Recalibrate an analysis model
- Generate a technical report

Decompose **Create an EPS design** to cover solar array sizing, battery pack sizing, power conditioning and distribution choices, controller selection such as MPPT, and interfaces and constraints. CSRM tailoring supplies reusable model content and variation points for this use case. Link sizing and selection decisions to analysis and variant comparison.

Separate verification of requirements and models from V&V of the modeled EPS. Specify which checks can be automated, which are advisory, and which require engineering judgment. Automated checks cannot guarantee that a model is an adequate representation of the intended system.

For every use case, define actors, trigger, preconditions, main and alternative flows, outputs, failure paths, and links to needs and requirements. Use corpus themes to discover missing cases. Provide full reviewable descriptions in the report or its appendices.

### 16. Define measures of effectiveness

Organize measures under:

- **Continuity:** lifecycle and trace coverage
- **Trustworthiness:** semantic correctness, provenance, uncertainty, reproducibility
- **Efficiency:** elapsed time, manual steps, analysis runtime
- **Automation:** supported transitions between lifecycle activities, manual handoffs, automatic trace and consistency checks, and required human intervention
- **Adoptability:** cost, training, administration, portability
- **Interoperability:** data loss, interface coverage, adapter effort
- **Review:** review effort, conflict handling, decision closure

Assess automation beyond individual analysis scripts. Compare how methods and frameworks transfer artifacts between lifecycle activities. Establish the baseline from evidence rather than assuming all MBSE methods offer the same automation.

Set targets and scoring anchors before candidate scoring. Throughout the study, distinguish measured study properties from literature supported estimates and unverified predictions.

## D. Analyze black-box requirements

### 17. Define lifecycle scenarios and the system context

Use end-to-end scenarios:

1. Requirement change to model update to analysis to decision
2. Requirement or model quality issue to diagnostic to correction to review
3. Failure identification to FMEA to mitigation to verification case
4. Change request to impact analysis to approved baseline
5. Test or telemetry data to calibration to updated analysis
6. Architecture review to visualization to decision report

Include nominal, stressing, alternative, and failure paths. Relate outputs to applicable NASA mission reviews without making any one mission the reference architecture.

### 18. Specify black-box behavior and interfaces

Define what the framework must do without naming products. Specify inputs and outputs, external actors, model and data exchanges, required services, timing and quality constraints, local data protection, and recovery behavior.

Keep requirements proportionate to university teams. Enterprise identity management and cloud operation are outside the mandatory scope.

### 19. Define framework states

Useful states include Initialized, In work, Under analysis, Under review, Baselined, Released, Superseded, Degraded, and Recovering.

Define permitted transitions and approval conditions. Lightweight human review can provide approval without a dedicated permissions platform.

### 20. Analyze variation and design constraints

Consider mission and satellite size, team size, asynchronous distributed work, connectivity, tool versions, supplier participation, model fidelity, digital twin coupling, and data sensitivity.

Treat SysML v2, Python, Git, and Omniverse as candidate ingredients unless explicitly fixed by a validated study constraint. A fixed choice narrows the study claim. Cloud independence is a scope constraint. Local repositories and locally hosted services remain options.

### 21. Analyze potential failures at two levels

**Framework failures:** malformed or ambiguous requirements, incorrect model relationships, stale traces, unit mismatch, schema drift, nonreproducible analysis, edit conflicts, lost provenance, failed synchronization, corrupted baselines, unintended changes, and telemetry delay or loss.

**EPS failures used as benchmark inputs:** solar string open circuit, battery degradation, converter failure, sensor bias, switch stuck open or closed, and unexpected load growth.

Keep framework assurance distinct from EPS assurance. Include detection and review of requirements and modeling errors before downstream system V&V.

### 22. Baseline requirements and close traceability gaps

Maintain this framework trace:

> Need -> framework mission requirement -> use case -> scenario -> black-box requirement -> logical behavior -> logical component -> candidate physical component -> analysis evidence -> decision

Provide readable traceability tables alongside the rationale in the report. At the end of Sprint 1, complete the trace through black-box requirements. Mark downstream architecture and decision links as pending work for Sprints 2 and 3. Conduct the tailored SRR and require substantive review of evidence coverage, measures, requirement quality, use case completeness, and unresolved stakeholder assumptions.

Compile the Sprint 1 LaTeX report and pause for human review. Do not begin logical architecture definition until this baseline is approved. Requirements work must not become a short preliminary task overshadowed by tool selection.

## E. Define the logical architecture

### 23. Derive logical behavior from scenarios

Allocate actions such as managing requirements, checking requirement quality, authoring and querying models, checking model consistency, executing analyses, generating safety analyses, exchanging data, managing variants and baselines, reviewing results, ingesting lifecycle data, and generating reports.

### 24. Derive the logical decomposition

RM, MD, SA, CM, and CC provide a starting taxonomy. Evaluate an explicit integration capability:

- Requirements and Traceability Service
- Model and Knowledge Service
- Analysis and Assurance Service
- Configuration and Provenance Service
- Review and Presentation Service
- Integration and Orchestration Service

CM and CC remain cross-cutting. Integration may be a component or an allocated responsibility with owned interfaces. Logical services need not become separate deployed services.

### 25. Define logical interactions and contracts

Model flows for requirements and rationale, stable identifiers, parameter sets and units, analysis requests and results, diagnostics, FMEA records, baseline descriptions, review decisions, test and telemetry data, visualization data, and report evidence.

Specify invariants such as preserved analysis inputs and traceable transformations. Make ownership and error handling explicit.

### 26. Specify logical components and review the baseline

Define inputs, outputs, operations, persistent data, quality properties, and failure behavior for every component. Review the logical baseline before naming tools. Carry findings into SDR preparation.

## F. Synthesize physical alternatives

### 27. Define partitioning criteria and the design space

Include model authority, SysML v2 implementation, file or API integration, analysis execution, artifact storage, configuration strategy, asynchronous review, local deployment, proportionate security, CSRM reuse, FMEA implementation, digital twin coupling, synchronization, automation, and reporting.

### 28. Screen candidate components using available evidence

Check documented semantics, API maturity, stable identifiers, queries, merge behavior, formats, automation, licensing, operating systems, GPU and storage needs, recovery, and current maintenance.

Verify claims using primary documentation and available published demonstrations. Record evidence dates and unresolved questions. Defer integration experiments until after the three-sprint design study.

Omniverse appearing in a review does not establish its suitability for EPS configuration management. Assess relevant components and local deployment options directly. Remove unnecessary components rather than forcing them into a candidate.

### 29. Create at least three coherent candidate families

| Candidate | Architecture concept |
|---|---|
| **A. Text and Git centered workbench** | Textual SysML v2, Python analyses, local Git, controlled artifact storage, generated review views, optional Omniverse visualization |
| **B. Model repository centered framework** | Locally hosted SysML v2 repository and API as model authority, Python workers, metadata store, Git for code, asynchronous review views |
| **C. Federated lifecycle framework** | Locally deployable model, analysis, FMEA, telemetry, configuration, and visualization components connected through contracts, identifiers, and workflow orchestration |

The proposed stack seeds Candidate A. Candidates must differ in architecture and satisfy the same scope constraints. A locally deployable COTS suite can be a fourth comparison if cost, licence, and current SysML v2 support permit it. Explain any administrative burden introduced by repositories or federation.

### 30. Complete every candidate physical architecture

Specify named products and relevant versions, licences, logical allocations, deployment nodes, software components, data stores, schemas, interfaces, failure handling, artifact authority, local protection, backup, recovery, migration, operating procedures, costs, and residual risks.

Describe how each candidate binds model, code, data, analysis configuration, reusable libraries, and results into a recoverable baseline. A manifest or test suite may be part of the future framework when justified. It is not mandatory infrastructure for this study.

### 31. Make digital twin choices explicit

For each candidate define the twin subject, intended decision, coupling level, model type, fidelity, uncertainty, deployment, synchronization, telemetry quality, authority, and degraded behavior.

An offline model and replay shadow provide initial comparison points. Bidirectional command paths require separate justification and carry a larger assurance burden.

### 32. Conduct equivalent architecture walkthroughs and plan feasibility tests

Apply the same standard scenarios to all candidates. Trace inputs, responsibilities, interfaces, outputs, manual work, and failure handling for:

- CSRM to SysML v2 EPS specialization
- Requirement and model quality checks
- Requirement change propagated to analysis and report
- Solar array and battery sizing and controller selection
- Eclipse and load trades
- Automated FMEA with human review
- Baseline reconstruction
- Review view generation
- Telemetry replay with stale and missing data

Use existing evidence and engineering estimates to assess risks. Define later experiments, expected observations, and pass criteria. Do not build candidate feasibility slices during this three-sprint study. Mark untested integrations explicitly and reduce confidence accordingly.

Compile the cumulative Sprint 2 LaTeX report and pause for human review of the logical architecture and comparable candidates before scoring and selection.

## G. Evaluate and select

### 33. Establish analysis objectives and the decision model

Use OOSEM's sequence: identify analyses, define analysis context, specify analysis relationships, and perform engineering analysis.

Represent candidates as variants and define analysis cases binding candidate properties to criteria. Approve the criteria before scoring. Track evidence maturity alongside every consequential estimate.

### 34. Evaluate hard constraints first

Examples include required modeling semantics, local operation, affordable licensing, baseline recovery design, provenance preservation, explicit treatment of semantic loss, and FMEA traceability.

Distinguish demonstrated compliance, documented support, and unresolved feasibility. Unknown compliance cannot be silently counted as a pass. Define when an unresolved issue prevents selection and when a conditional recommendation is acceptable.

### 35. Compare feasible candidates quantitatively

Assess trace coverage, change impact support, requirement and model checking, reproducibility design, semantic loss risk, CSRM migration effort, FMEA coverage and review effort, analysis capability, lifecycle automation, review effort, configuration completeness, setup and administration, cost, vendor dependence, and telemetry handling.

Use measured model coverage where available. Use bounded estimates for implementation effort and operational performance. Do not report runtime, fidelity, or integration reliability as measured without supporting results.

### 36. Perform trade and sensitivity analysis

Use hard constraint filtering, Pareto analysis where useful, approved multi-attribute scoring, weight sensitivity, uncertainty analysis, evidence maturity, and residual risk comparison.

A weak or unstable ranking returns to candidate synthesis or requirements clarification. The study may conclude that evidence is insufficient to select a feasible candidate. Identify the later test most likely to resolve a consequential uncertainty.

### 37. Select the preferred physical architecture

Have the decision authority review the candidate evidence, select or conditionally recommend a candidate, record rationale and rejected alternatives, consider sensitivity and uncertainty, and accept or reject residual risks.

Link the decision to allocations and trade results. Preserve all candidates in the model. Do not force a definitive selection when the evidence supports only a conditional recommendation.

### 38. Conduct an independent technical and traceability review

Review SysML syntax and semantics, allocations, trace gaps, calculations, selection claims, native views, and OOSEM tailoring. Check that every substantive argument is readable in the report.

Complete the tailored SDR using the NASA criteria established in step 4. Record unmet criteria and resulting limitations. Human approval of the final report concludes Sprint 3. Proceeding to framework development requires a separate authorization.

### 39. Compile the self-contained LaTeX report and pause

Include:

1. Problem, intended users, scope, and working title
2. Review history and corpus methods
3. Cited narrative literature synthesis, cluster plots, and relevant statistics
4. OOSEM tailoring, SysML v1 to v2 mapping, and NASA review approach
5. Stakeholders, needs, and measures
6. Complete use cases and black-box requirements with rationale
7. Logical architecture
8. Three or more candidate physical architectures
9. Architecture walkthroughs, evidence maturity, and planned feasibility tests
10. Trade method, results, and sensitivity
11. Preferred architecture or conditional recommendation
12. Residual risks, limitations, and later OOSEM roadmap
13. Concise instructions for rerunning study analyses and rebuilding the report

Supply the PDF, LaTeX sources, bibliography, SysML sources, native views, and supporting scripts and inputs. Embed decision-relevant tables and traceability in the report or its appendices. Auxiliary artifacts support reuse and execution. They are not additional mandatory reading.

Require a successful report build with documented prerequisites. No clean network-free rebuild, lock files, CI pipeline, or checksum release manifest is required for any of the three design sprints.

Pause before framework construction, integration prototypes, procurement, deployment, training, and operational verification. Retain later development and verification activities in the roadmap for review after Sprint 3.

# Subagent organization

| Subagent or team | Responsibility |
|---|---|
| Corpus research sub-orchestrator | Coordinate retrieval, clustering, coverage analysis, and source verification |
| Narrative synthesis authors | Explain contributions, limitations, partial frameworks, and implications in cited LaTeX prose |
| OOSEM and NASA review auditor | Maintain tailoring, work product mapping, and source grounded review criteria |
| EPS domain specialist | Define mission-independent variation points and standard scenarios |
| CSRM sub-orchestrator and investigators | Investigate original distribution and thesis reconstruction in parallel, then recommend reuse |
| Needs and requirements team | Develop and independently review stakeholders, needs, requirements, use cases, and assurance scenarios |
| Logical architect | Derive behavior, logical structure, and contracts |
| Candidate A, B, and C architects | Develop independent candidates against the same approved requirements |
| Analysis and assurance specialist | Assess EPS analysis, requirement and model checking, FMEA, and future test plans |
| Trade analyst | Run filters, scoring, sensitivity, and uncertainty analysis |
| Independent model auditor | Validate SysML and check traceability and allocations |
| Report integrator | Integrate narrative, bibliography, views, plots, and tables into one reviewable report |

Resource the corpus and requirements teams at a scale comparable to the three candidate teams combined. Their output is a core research contribution.

Use these coordination rules:

1. Give concurrent writers separate files or Git worktrees where needed.
2. Give each model package one writer.
3. Give candidate architects the same approved requirements, scenarios, and criteria.
4. Independently review source interpretations, requirements, models, and trade results.
5. Require each team to contribute report-ready prose and figures. A collection of working notes is insufficient.

Subagent output remains draft until checked against sources and models. Keep coordination lightweight. The human reviews the integrated LaTeX report and its diagrams.

# Definitions of done

## Sprint 1: Measures, requirements, and use cases

- The report accurately explains the abandoned SLR and use of the 129-paper corpus.
- Cited narrative synthesis and justified corpus analyses support stakeholders, needs, standard scenarios, requirements, and use cases.
- Measures have definitions, targets or justified provisional targets, and scoring anchors.
- Framework mission requirements, black-box requirements, and complete use cases receive independent review and are fully readable in the report.
- Requirement and model quality checking are covered alongside EPS V&V support.
- The framework remains mission-independent and appropriate for university teams.
- Traceability through black-box requirements is complete or gaps are explicitly accepted. Architecture links are marked as future work.
- Applicable SysML checks pass and required views render.
- Tailored MCR and SRR findings and unresolved assumptions are explicit.
- The Sprint 1 LaTeX report builds and is ready for exhaustive human review.
- Work pauses before logical architecture definition.

## Sprint 2: Logical architecture and physical alternatives

- The approved Sprint 1 baseline guides the architecture work.
- Logical behavior, components, interactions, and contracts are defined.
- At least three complete physical candidates exist against common requirements.
- Each viable candidate allocates every required logical capability.
- Equivalent walkthroughs expose assumptions, automation, manual work, and integration risks.
- Future feasibility tests are specified without building integration prototypes.
- SysML checks pass, required views render, and architecture traceability is reviewed.
- The cumulative LaTeX report is ready for human review before candidate evaluation and selection.

## Sprint 3: Evaluation and selection

- Hard constraints, quantitative comparison, sensitivity, and evidence maturity are assessed consistently.
- Trade calculations can be rerun from supplied inputs.
- The decision or conditional recommendation is supported by evidence and explicit uncertainty.
- Traceability through the decision is complete or gaps are explicitly accepted.
- Tailored SDR findings and unmet criteria are explicit.
- The final self-contained LaTeX report builds and is ready for exhaustive human review.
- Later OOSEM development and verification activities remain visible in the roadmap.
- No framework implementation or candidate integration prototype has been built as part of these three sprints.

The three sprints produce a defensible architecture study for a reusable, lifecycle-spanning nanosatellite EPS framework. Human review controls progression between sprints and any later move to implementation.
