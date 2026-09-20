# OOSEM Orchestration Plan for Nanosatellite EPS Digital Engineering

This project is an OOSEM architecture selection study for a socio-technical engineering environment.

Two framing decisions govern the work:

1. **The system of interest is the nanosatellite EPS digital engineering environment.** Its physical architecture contains modeling tools, analysis services, repositories, integration services, compute nodes, data stores, and operating procedures.
2. **The nanosatellite EPS is the reference subject.** Its requirements, design, analyses, FMEA, test data, and telemetry exercise the environment.

Buruso et al. present Requirements Management (RM), Model Development (MD), Simulation and Analysis (SA), Configuration Management (CM), and Collaboration and Communication (CC) as overlapping lifecycle processes. Figure 16 shows CM and CC spanning the lifecycle. They are modeled first as capabilities and activities. OOSEM then derives logical components and allocates them to physical components.

The final research claim is an evidence backed architecture selection. Operational proof across the full lifecycle remains future implementation and verification work.

## Original brain dump that inspired this plan

```
There's one paper
(SLR/SLR1/pdfs/psr-reports/psr-report
-0039.md,
SLR/SLR1/pdfs/psr-reports/psr-report-
0039_images) that makes this
statement: "Despite the progress
reflected in the literature, unifying
MBSE tools and methods to consistenly
support all lifecycle stages remains
an unresolved challenge".

I want to take on this challenge,
however, limiting it to the
electrical power system of
nanosatellites (instead of all
subsystems of all space systems that
the Buruso et al. review covers) for
feasability.

I thus want to apply OOSEM to this
problem. I want to stop, for now,
after selecting a candidate physical
architecture. The Buruso et al.
review provides several alternative
components that all fit their
proposed RM -> MD -> SA -> CM -> CC
logical architecture, that I want to
adopt.
SLR/SLR1/pdfs/psr-reports/psr-report-
0024.md is another review that covers
digital twins more specifically. If I
had propose a candidate, I would
leverage SysML v2 for RM/MD, Python
for MD/SA, Git for CM, and NVIDIA
Omniverse for CM/CC. Of course, this
is not a fully fledged candidate, but
merely a list of tools that I'd like
to see fully fledged out in a
candidate PA. To continue enumerating
assorted contributors to the
candidate, I'd say the CSRM CubeSat
model, automated FMEA. However, I
don't yet understand all else that
would be required to form a full
candidate, let alone multiple.

So, if you were in charge of applying
OOSEM up to selecting a PA for this
problem, and you had subagents
(~/agent-tools/subagents/skills/subag
ent/SKILL.md) to help you execute the
speciic OOSEM tasks and model in
SysML v2, and compile it into a
self-contained LaTeX report,

what are the numbered steps you would
take to get there?
```

## Initial candidate ingredients

The initial proposal mixes several architectural levels:

| Ingredient | Architectural role | Decisions still needed |
|---|---|---|
| SysML v2 | Modeling language | Authoring tool, semantic validator, repository, API, model ownership, interchange mechanism |
| Python | Programming and analysis language | Runtime, packages, orchestration, schemas, environment locking, result publication |
| Git | Configuration mechanism | Hosting, workflow, CI, large artifact storage, release manifests, access control |
| NVIDIA Omniverse | Platform family | Nucleus, Kit, USD, connectors, hosting, GPU needs, source authority, collaboration role |
| CSRM | Reusable model content | Exact version, availability, licence, SysML v1 to v2 transformation, tailoring and validation |
| Automated FMEA | Required capability | Failure library, extraction rules, propagation model, criticality method, validation, human approval |

A complete candidate must add deployment nodes, data ownership, interface contracts, orchestration, artifact storage, security, recovery, operating procedures, and configuration baseline semantics.

# Numbered execution plan

## A. Frame and prepare the study

### 1. State the architecture decision question

Use a question such as:

> Which physical architecture best enables a traceable, reproducible, and affordable digital thread for nanosatellite EPS engineering across concept, design, assembly and test, and operations?

Define the intended lifecycle stages and the nanosatellite class. Define whether the result targets university teams, commercial teams, or both.

### 2. Define the system boundary

Create separate namespaces for:

- `EnvironmentSOI`
- `EPSReferenceCase`
- `PhysicalCandidates`
- `Analyses`
- `Traceability`
- `Evidence`
- `Views`

Environment components satisfy environment requirements. EPS components satisfy EPS requirements. Tool components do not satisfy spacecraft power requirements.

### 3. Tailor OOSEM and record the tailoring

Include:

- Setup model
- Analyze stakeholder needs
- Analyze system requirements
- Define logical architecture
- Synthesize candidate physical architecture
- Optimize and evaluate alternatives
- Manage requirements traceability
- Conduct technical reviews

Exclude after selection:

- Develop database
- Develop hardware
- Develop software
- Develop operator procedures
- Integrate and verify system

Treat the OOSEM geometric model task as conditional. A traditional CAD model of the engineering environment adds little value. A SysML to USD geometry correspondence may still be needed to evaluate Omniverse.

### 4. Define review gates and exit criteria

Use:

- **G0:** Scope and tailoring approved
- **G1:** Stakeholder needs and measures approved
- **G2:** Black-box requirements approved
- **G3:** Logical architecture approved
- **G4:** Candidate architectures complete and comparable
- **G5:** Preferred architecture selected

A failed gate returns work to the relevant OOSEM activity.

### 5. Create an evidence ledger

For every literature or vendor claim, record:

- Claim identifier
- Source and page
- Direct quotation or extracted evidence
- Applicability to nanosatellite EPS
- Limitations
- Linked requirement or criterion
- Review status

Use Buruso et al. to form the design space. Verify tool capabilities through primary papers, current documentation, and feasibility tests.

The digital twin review concerns space robotics. Its coupling, synchronization, assurance, and lifecycle principles transfer well. Its tool findings require EPS specific confirmation.

### 6. Establish modeling and reporting conventions

Define:

- Naming and identifier rules
- Units and quantity conventions
- Requirement patterns
- Evidence and rationale metadata
- Candidate naming
- Viewpoints and required views
- Generated artifact policy
- Configuration item policy

Create a mapping from OOSEM's SysML v1 work products to SysML v2 concepts. Use requirement definitions and usages, actions, states, parts, ports, connections, variations, analysis cases, verification cases, viewpoints, and views.

### 7. Create the reproducible project skeleton

Establish:

- SysML v2 source tree
- Python package and tests
- Evidence ledger
- Candidate and criteria data
- LaTeX report
- Generated figures and tables
- CI workflow
- Tool and dependency locks
- Release manifest

Run the Syside `doctor` check at this point. Every model merge should later pass `check`, `inspect`, and native `render`.

## B. Establish the EPS reference case

### 8. Select a bounded EPS reference mission

Choose one explicit mission class, such as a 3U or 6U low Earth orbit nanosatellite. Document:

- Orbit and eclipse profile
- Attitude assumptions
- Solar array configuration
- Battery configuration
- PCDU and bus architecture
- Nominal and peak loads
- Operating modes
- Degradation assumptions
- Telemetry availability

Add at least one variation case so the environment is not optimized for a single fixed design.

### 9. Define standard EPS benchmark scenarios

Include:

- Nominal sunlit operation
- Worst case eclipse
- Peak payload load
- Safe mode
- Solar array degradation
- Battery aging
- Converter or switch failure
- AIT measurement import
- Delayed or incomplete telemetry replay

### 10. Assess and adapt CSRM

Determine:

- Whether the actual model is available
- Its licence and provenance
- Its modeling language and tool dependencies
- Which EPS elements can be reused
- Which semantics would be lost during SysML v2 transformation
- How local extensions remain separate from the source library

Preserve the source CSRM package. Create a versioned EPS specialization or adaptation package. Validate every transformed relationship.

## C. Analyze stakeholder needs

### 11. Characterize the current engineering environment

Model the current workflow only to the level needed to expose problems. Capture:

- Documents and spreadsheets
- Existing models and analysis scripts
- Manual transformations
- Review and approval flow
- Configuration practices
- Test and telemetry handling
- Repeated data entry
- Broken or missing trace links

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

### 13. Identify stakeholders and define the future domain

Include at least:

- Systems engineer
- EPS engineer
- Requirements engineer
- Analysis engineer
- Reliability and safety engineer
- AIT engineer
- Operations engineer
- Configuration manager
- Reviewer
- Project manager
- Supplier
- Independent reproducer

Capture their concerns and required views.

### 14. Specify mission requirements for the environment

Examples include:

- Preserve traceability across lifecycle stages.
- Reproduce an EPS analysis from an approved baseline.
- Propagate requirement and configuration changes.
- Generate reviewable FMEA candidates from the system model.
- Maintain distinct as-designed, as-analyzed, as-built, as-tested, and as-operated configurations.
- Support controlled multidisciplinary review.
- Produce a self-contained technical baseline.

### 15. Define enterprise use cases

Core use cases should include:

- Reuse and specialize the EPS reference model
- Capture and change a requirement
- Create an EPS design
- Execute power and energy analyses
- Generate and review an FMEA
- Compare EPS design variants
- Process a controlled change
- Create and restore a baseline
- Review a model collaboratively
- Import test or telemetry data
- Recalibrate an analysis model
- Generate a technical report

### 16. Define measures of effectiveness

Organize them under:

- **Continuity:** lifecycle and trace coverage
- **Trustworthiness:** semantic correctness, provenance, uncertainty, reproducibility
- **Efficiency:** elapsed time, manual steps, analysis runtime
- **Adoptability:** cost, training, administration, portability
- **Interoperability:** data loss, API coverage, adapter effort
- **Collaboration:** review time, conflict handling, decision closure

Set targets before seeing candidate scores.

## D. Analyze black-box requirements

### 17. Define lifecycle scenarios and the system context

Use several end-to-end scenarios:

1. Requirement change to model update to analysis to decision
2. Failure identification to FMEA to mitigation to verification case
3. Change request to impact analysis to approved baseline
4. Test or telemetry data to calibration to updated analysis
5. Architecture review to visualization to signed decision report

Include nominal, stressing, alternative, and failure paths.

### 18. Specify black-box behavior and interfaces

Define what the environment must do without naming products. Specify:

- Inputs and outputs
- External actors
- Model and data exchanges
- Required services
- Timing and quality constraints
- Security boundaries
- Recovery behavior

### 19. Define environment states

Useful states include:

- Initialized
- In work
- Under analysis
- Under review
- Baselined
- Released
- Superseded
- Degraded
- Recovering

Define permitted transitions and approval conditions.

### 20. Analyze variation and design constraints

Consider variation in:

- Mission and satellite size
- Team size
- Local or distributed development
- Connectivity
- Tool versions
- Supplier participation
- Model fidelity
- Digital twin coupling
- Data sensitivity

Treat SysML v2, Python, Git, and Omniverse as candidate choices unless the research question explicitly fixes them. A fixed choice becomes a validated design constraint and narrows the study claim.

### 21. Analyze potential failures at two levels

**Environment failures:**

- Stale trace
- Unit mismatch
- Schema drift
- Nonreproducible analysis
- Concurrent edit conflict
- Lost provenance
- Failed synchronization
- Corrupted baseline
- Unauthorized change
- Telemetry delay or loss

**EPS failures used as benchmark inputs:**

- Solar string open circuit
- Battery degradation
- Converter failure
- Sensor bias
- Switch stuck open or closed
- Unexpected load growth

Keep the two analyses distinct.

### 22. Baseline requirements and close traceability gaps

Maintain this environment trace:

> Need -> mission requirement -> use case -> scenario -> black-box requirement -> logical behavior -> logical component -> candidate physical component -> analysis evidence -> decision

Conduct the G2 technical review before defining tool allocations.

## E. Define the logical architecture

### 23. Derive logical behavior from the scenarios

Allocate actions such as:

- Manage requirements
- Author and query models
- Execute analyses
- Generate safety analyses
- Transform and exchange data
- Validate artifacts
- Manage variants and baselines
- Review and publish results
- Ingest lifecycle data
- Generate evidence and reports

### 24. Derive the logical decomposition

RM, MD, SA, CM, and CC provide a useful starting taxonomy. The decomposition will probably require an explicit integration capability:

- Requirements and Traceability Service
- Model and Knowledge Service
- Analysis and Assurance Service
- Configuration and Provenance Service
- Collaboration and Presentation Service
- Integration and Orchestration Service

CM and CC remain cross-cutting. The integration service may be a component or an explicitly allocated responsibility with owned interfaces.

### 25. Define logical interactions and contracts

Model flows for:

- Requirements and rationale
- Model elements and stable identifiers
- Parameter sets and units
- Analysis requests and results
- FMEA records
- Configuration manifests
- Review comments and decisions
- Test and telemetry data
- Visualization data
- Report evidence

Specify invariants such as immutable analysis inputs and traceable transformations.

### 26. Specify logical components and review the baseline

Define inputs, outputs, operations, persistent data, quality properties, and failure behavior for every component. Complete G3 before naming tools.

## F. Synthesize physical alternatives

### 27. Define partitioning criteria and the design space

Include these decision dimensions:

- Model authority topology
- SysML v2 implementation
- File, API, or event based integration
- Analysis execution model
- Data and artifact storage
- Configuration strategy
- Collaboration platform
- Hosting topology
- Security and identity
- CSRM reuse mechanism
- FMEA implementation
- Digital twin coupling
- Synchronization policy
- Report and evidence generation

### 28. Feasibility-screen candidate components

Verify actual capabilities through documentation and small tests. Check:

- SysML v2 conformance
- API maturity
- Stable identifiers
- Query capability
- Merge behavior
- Supported formats
- Automation
- Licensing
- Operating systems
- GPU and storage needs
- Backup and recovery
- Current maintenance status

Omniverse appearing in a review does not establish its suitability for EPS configuration management. Verify Nucleus, Kit, USD, and connector behavior directly.

### 29. Create at least three coherent candidate families

| Candidate | Architecture concept |
|---|---|
| **A. Text and Git centered workbench** | Textual SysML v2, Python packages, Git and CI, controlled artifact storage, generated USD views, Omniverse for release review |
| **B. Model repository centered environment** | SysML v2 repository and API as model authority, Python workers, metadata or graph store, Git for code, controlled collaboration views |
| **C. Federated lifecycle environment** | Separate model, analysis, FMEA, telemetry, configuration, and visualization services connected through contracts, identifiers, and an event or workflow service |

The proposed stack is the seed for Candidate A. A COTS or managed suite can serve as a fourth control candidate if licences and current SysML v2 support permit it.

### 30. Complete every candidate physical architecture

Each candidate must specify:

- Named products and versions
- Licences
- Logical-to-physical allocations
- Authoring, server, CI, storage, analysis, GPU, and test nodes
- Software components and layers
- Data stores and schemas
- Interfaces, direction, protocol, and failure handling
- Source authority for every artifact class
- Security zones and roles
- Backup, recovery, and migration
- Operating procedures
- Cost and resource properties
- Residual assumptions and risks

Define a release manifest that binds model revision, code revision, data version, analysis environment, CSRM version, FMEA library, results, and Omniverse scene.

### 31. Make digital twin choices explicit

For each candidate define:

- Twin subject
- Intended decision
- Offline model, shadow, bidirectional twin, or predictive twin
- Physics, data, or hybrid model
- Fidelity and uncertainty
- Ground or hybrid deployment
- Batch, event, or continuous synchronization
- Telemetry quality and provenance
- Advisory or command authority
- Degraded behavior

An offline model and replay shadow provide sensible initial comparison points. A bidirectional command path adds a much larger assurance burden.

### 32. Build equivalent feasibility slices

Build only enough of each candidate to measure architecture risk:

- CSRM to SysML v2 EPS specialization
- Requirement change propagated to analysis and report
- Eclipse and load trade executed in Python
- Automated FMEA compared with expert review
- Baseline reconstructed from a clean checkout
- Omniverse or alternative review view generated
- Telemetry replay with stale and missing data

These are engineering analysis prototypes. They are not implementation of the selected environment.

## G. Evaluate and select

### 33. Freeze the analysis objectives and decision model

Use OOSEM's sequence:

1. Identify analyses
2. Define analysis context
3. Specify analysis relationships
4. Perform engineering analysis

In SysML v2, represent candidates as variants and define analysis cases that bind candidate properties to criteria.

### 34. Evaluate hard constraints first

Examples include:

- Required SysML v2 semantics work
- Mandatory artifacts are version controlled
- A baseline can be reconstructed
- Analysis inputs and results retain provenance
- No silent semantic loss occurs
- FMEA output traces to source elements
- Required access controls exist

### 35. Compare feasible candidates quantitatively

Measure:

- Trace coverage
- Seeded change impact detection
- Reproducibility
- Semantic loss
- CSRM migration effort
- FMEA completeness and review effort
- EPS analysis fidelity and uncertainty
- Collaboration performance
- Configuration audit completeness
- Setup and administration effort
- Cost and vendor dependence
- Telemetry freshness and dropout tolerance

### 36. Perform trade and sensitivity analysis

Use:

- Hard constraint filtering
- Pareto analysis
- Approved multi-attribute utility or scoring
- Weight sensitivity
- Uncertainty analysis
- Evidence maturity assessment
- Residual risk comparison

A weak or unstable ranking returns to candidate synthesis. The study may conclude that no current candidate is feasible.

### 37. Select the preferred physical architecture

Freeze the candidate evidence before the decision. Have the decision authority:

- Select the candidate
- Record the rationale
- Record rejected alternatives
- Record sensitivity and uncertainty
- Accept or reject residual risks
- Link the decision to the applicable allocations and trade results

Preserve every rejected candidate in the model.

### 38. Conduct an independent technical and traceability review

Require:

- Valid SysML v2 syntax and semantics
- Complete logical-to-physical allocations
- No unexplained trace gaps
- Reproducible analysis
- Evidence for every selection claim
- Native architecture views
- Explicit waivers for tailored OOSEM products

### 39. Compile the self-contained LaTeX report and stop

Generate the report from controlled artifacts. Include:

1. Problem and scope
2. Literature evidence
3. OOSEM tailoring
4. Stakeholders and measures
5. Black-box requirements
6. Logical architecture
7. Candidate physical architectures
8. Feasibility experiments
9. Trade method and sensitivity
10. Preferred architecture
11. Residual risks and limitations
12. Reproduction instructions

Package:

- PDF and LaTeX sources
- Bibliography
- SysML v2 sources
- Native Syside views and manifests
- Python code, locks, tests, and inputs
- Evidence ledger
- Traceability matrices
- Trade results
- Tool versions
- SHA-256 manifest

Require a clean, network-free rebuild. Stop before procurement, implementation, deployment, training, integration, or operational verification.

# Subagent organization

| Subagent | Responsibility |
|---|---|
| Evidence curator | Verify claims, pages, primary sources, and tool documentation |
| OOSEM auditor | Maintain tailoring matrix, work products, and gate criteria |
| EPS and CSRM specialist | Define benchmark mission and validate CSRM reuse |
| Needs and requirements modeler | Build stakeholder, scenario, and black-box packages |
| Logical architect | Build behavior, logical structure, and contracts |
| Candidate A, B, and C architects | Model independent candidates against the same locked requirements |
| Analysis and FMEA engineer | Build EPS analyses, FMEA automation, and benchmark tests |
| Trade analyst | Run hard filters, scoring, Pareto, and sensitivity analyses |
| Independent model auditor | Run Syside validation and traceability checks |
| Report integrator | Generate tables, views, bibliography, and final LaTeX package |

Enforce four rules:

1. Each mutating agent works in an isolated Git worktree.
2. Each model package has one writer.
3. Candidate architects receive the same frozen requirements and criteria.
4. No agent approves its own work. The orchestrator merges only reviewed commits.

Subagent output remains draft material until a human or independent agent verifies it against the source and model.

# Definition of done

The project reaches its stopping point when:

- At least three complete physical candidates exist.
- Every viable candidate allocates every required logical capability.
- The SysML v2 model passes syntax and semantic validation.
- Required native views render successfully.
- Traceability gaps are closed or explicitly waived.
- Trade results rebuild from controlled inputs.
- Sensitivity analysis supports a stable decision.
- The selection authority signs the rationale and residual risks.
- The self-contained report rebuilds from the released source bundle.

This scope produces a defensible selected architecture for lifecycle-spanning nanosatellite EPS engineering. It also leaves a clean starting baseline for later implementation and verification.
