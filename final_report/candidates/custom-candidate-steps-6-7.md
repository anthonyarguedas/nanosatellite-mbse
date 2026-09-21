# CSRM digital thread candidate: OOSEM steps 6 and 7

## Scope

This is a deliberately small candidate model. It performs:

- Step 6: define the candidate logical node distribution.
- Step 7: define the minimum physical nodes and components.

It deliberately defers logical to physical allocations, requirement satisfaction, and measured performance to the following synthesis and evaluation steps.

The candidate preserves the system boundary in `final_report/final_report.tex`. Requirements management (RM) and model development (MD) capabilities populate the external Versioned System Model through IF-04. External simulation and analysis (SA) capabilities execute through IF-05. The external Evidence Repository retains controlled packages through IF-06. The framework directly realizes configuration management (CM) and collaboration and communication (CC).

The candidate uses four complementary ideas:

1. A CubeSat System Reference Model (CSRM) semantic foundation supports reusable requirements and architecture content for RM and MD.
2. A native textual SysML v2 gateway provides the candidate's authoritative semantic exchange and tailoring mechanism.
3. A controlled Python runner mediates external SA tools and packages reproducible results.
4. An NVIDIA Omniverse and Isaac integration surface provides controlled OpenUSD views, collaborative review, robotics scenarios, and battery-aware simulation evidence.

The cited CSRM is a SysML v1 graphical model distributed through a foundational model, web publication, and XMI. The selected evidence provides no textual SysML v2 CSRM library. Its translation is a proposed development item. The complete CSRM, SysML v2, Python, Omniverse, Isaac, and battery co-simulation stack is a new end to end synthesis across sources.

The candidate initially treats its pre-physical environment as an offline predictive simulation model. It may evolve into a digital shadow or bidirectional twin after HIL or flight telemetry becomes available. This coupling choice follows the space robotics review's recommendation to state digital twin coupling and synchronization semantics explicitly.

## Evidence basis

The evidence was located with `embeddings/search.py` and checked in the source Markdown and relevant architecture figures.

| ID | Extracted evidence | Source |
|---|---|---|
| CDT-E01 | CSRM provides a reusable logical architecture for CubeSat space and ground systems. A mission team tailors it into a mission-specific logical and physical architecture. Its principal elements cover requirements, architecture, stakeholders, technical measures, and use cases. The mission-specific model is maintained as the central design baseline and includes verification and validation relationships. | Kaslow, Cahill, and Frank, *Developing a CubeSat System MBSE Reference Model: Interim Status #5*, PDF pp. 1 to 6, `citation-2362`. |
| CDT-E02 | A RAX CubeSat model connected SysML architecture and behavior to external STK, MATLAB, and script analyses. The integrated workflow returned time histories to the model, supported battery and solar-array trades, and checked energy and data requirements across a simulated mission. | Kaslow et al., *Integrated Model-Based Systems Engineering Applied to the Simulation of a CubeSat Mission*, PDF pp. 4 to 13, `review-1563`. |
| CDT-E03 | A reusable CubeSat SysML model can be parsed into a software-readable data structure, requirements list, and dependency graph. Python can connect the model to external analysis tools and reverse approved analysis or optimization updates into the model. The demonstrated parser is Gaphor and SysML v1 specific, which confirms both the integration pattern and the risk of tool-specific mappings. | Luccisano et al., *Open-Source Data Formalization through Model-Based Systems Engineering for Concurrent Preliminary Design of CubeSats*, PDF pp. 3 and 14 to 21, `review-0602`. |
| CDT-E04 | A CubeSat EPS development framework proceeds from mission definition and power budgeting through EPS topology and component design to functional and environmental testing. It validates solar and battery sizing with orbital simulation, applies preliminary thermal and EMC analyses, records telemetry, and compares simulated protection behavior with experiments. | El Hachimi et al., *A Framework for Sizing, Designing, and Testing of Electrical Power System for Nanosatellites*, PDF pp. 1 to 18, `handpicked-0003`. |
| CDT-E05 | The five-tier battery digital twin uses Omniverse as a spatial and data plane, a USD scene with semantic identifiers and units, telemetry and simulation bindings, read and write APIs, multi-physics battery models, and physics-informed prediction. Its implementation uses PyBaMM for coupled electrochemical and thermal models and reports calibrated voltage, temperature, and SOH prediction results with uncertainty. The evaluation covers calibration and health prediction. A complete autonomous closed loop remains unvalidated. | Zhu et al., *Towards Intelligent Systems for Battery Management: A Five-Tier Digital Twin Architecture*, PDF pp. 2 to 9, `handpicked-0001`. |
| CDT-E06 | OpenUSD supports packaging, assembly, simulation, standardized APIs, and collaborative 3D workflows. The presented Omniverse co-simulation patterns use Python, OpenModelica, Omniverse Kit extensions, FMI and FMU, external physics solvers, and Isaac Sim. The UUV example estimates battery consumption, while the lunar robot example tracks energy consumption and validates a robotics solution in simulation. The USD and FMI integration is described as an MVP, proof of concept, and in-progress standardization effort. | Janiak and Cristiano, *Physics-Based Digital Twins for Co-Simulation*, PDF pp. 8 to 24, `handpicked-0002`. |
| CDT-E07 | A validated 6U CubeSat EPS digital twin models solar arrays, solar-array regulators, a battery, a power distribution unit, and loads. Python scripts update model inputs through a SCADA interface. Real-time outputs were compared with physical hardware, followed by CHIL and PHIL tests. A full-orbit simulation used irradiance and temperature profiles to evaluate EPS behavior. The study identifies computational cost and omitted degradation and balancing behavior as limitations. | Casado et al., *Implementation of a 6U CubeSat Electrical Power System Digital Twin* (2024), PDF pp. 2 to 14, `review-0573`. |
| CDT-E08 | Space robotic systems are becoming more complex, intelligent, and autonomous, which increases the value of virtual evaluation and verification before mission execution. The review finds that lifecycle continuity, configuration governance, model fidelity, data quality, interoperability, and representative validation remain major gaps. It recommends modular services, explicit contracts, shared semantics, versioned models and data, uncertainty, change impact, and integration-level V&V. It also identifies Omniverse and robotic simulators within the modeling and simulation layer used by space robotics digital twins. | Rostamnia, Pettinari, and Pelliccione, *Digital Twin Models for Space Robotics: Objectives, Applications, and Challenges*, PDF pp. 7 to 8 and 14 to 18, `psr-0024`. |

Evidence classifications used below:

- **Reported:** stated directly in a cited source or identified in its architecture figure.
- **Synthesized:** combines compatible patterns reported across sources.
- **Inferred:** necessary architectural interpretation of reported behavior.
- **Proposed:** added to realize this candidate and the project's black-box baseline.
- **Unspecified:** required implementation detail that the selected sources do not establish.

## Step 6: candidate logical node distribution

The logical distribution separates participant decision and review, reference-model configuration and evidence, and controlled analysis and digital twin assurance. Detailed products and deployment choices remain in Step 7.

### CDT-LN-01 Collaborative Decision and Review Logical Node

Purpose: mediate mission-team, research, and independent-review interactions through controlled textual views, evidence packages, and optional OpenUSD scene views.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-01 Mission Application Interface Manager | A lightweight framework interface and controlled Omniverse view can present case, change, comparison, and review information to the mission team. | Proposed from the collaboration patterns in CDT-E05, CDT-E06, and CDT-E08. |
| LIF-02 Research Governance Interface Manager | CSRM tailoring records, model queries, raw analyses, uncertainty, and reusable scenario definitions provide the researcher interaction surface. | Synthesized from CDT-E01 through CDT-E03 and CDT-E08. |
| LIF-03 Independent Review Interface Manager | Immutable textual baselines, reproducible Python packages, and scene-linked evidence can provide review material without granting authority to modify the model. | Proposed from CDT-E01, CDT-E03, and CDT-E08. |
| LAP-06 Design Review Manager | The node assembles model, analysis, requirement, discrepancy, and visual evidence into a review package. Omniverse supports the shared view. Finding disposition remains controlled by framework records. | Partial evidence from CDT-E05, CDT-E06, and CDT-E08. The findings workflow is proposed. |

### CDT-LN-02 Reference Model Configuration and Evidence Logical Node

Purpose: apply and tailor CSRM semantics, mediate the external versioned model, control case and baseline identity, assess changes, and preserve evidence and provenance.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-04 Model Control Interface Manager | CSRM provides the reusable architecture and requirements basis. A proposed SysML v2 gateway exchanges generic, tailored, and candidate model records with external RM and MD capabilities. | Reported basis from CDT-E01 and CDT-E03 with proposed SysML v2 realization. |
| LIF-06 Evidence Custody Interface Manager | A repository adapter submits and retrieves model, mapping, environment, analysis, review, and verification packages through IF-06. | Proposed. The selected implementation papers do not establish the report's evidence repository contract. |
| LAP-01 Evidence Chain Manager | CSRM relationships, stable identifiers, verification links, parser outputs, and analysis mappings provide the structure needed to build an evidence chain. The report's complete validity rules remain proposed. | Partial evidence from CDT-E01 through CDT-E03. |
| LAP-02 Case Configuration Manager | CSRM explicitly requires mission-specific selection, pruning, expansion, and replacement of logical elements. The candidate records every tailoring decision against the CSRM and case baselines. | Reported tailoring basis from CDT-E01 with proposed SysML v2 configuration records. |
| LAP-04 Design Change Assessment Manager | Dependency graphs, stable mappings, textual revisions, and regenerated analyses identify affected model, scene, simulation, and evidence elements. | Reported dependency pattern from CDT-E03 with proposed cross-tool extension. |
| LIN-01 Workflow Control Manager | The controlled model-to-analysis-to-evidence sequence provides the shared service workflow and outcome gates. | Synthesized from CDT-E02, CDT-E03, and CDT-E08. |
| LIN-03 Baseline and Configuration Manager | The model, mapping registry, OpenUSD package, scenario, execution environment, and results are treated as versioned configuration items. | Proposed in direct response to CDT-E08. |
| LIN-04 Evidence and Provenance Manager | The node retains source identity, mappings, assumptions, raw results, uncertainty, findings, and decision context while the external repository provides custody. | Proposed from the assurance guidance in CDT-E08 and the evidence structures in CDT-E01 through CDT-E03. |

### CDT-LN-03 Analysis Twin and Assurance Logical Node

Purpose: coordinate reproducible external analyses, evaluate EPS candidates, control Omniverse and Isaac exchanges, and measure transfer and decision quality.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-05 Analysis Execution Interface Manager | Python adapters submit typed requests to external orbit, power-budget, circuit, thermal, battery, robotics, optimization, and HIL tools and correlate their returned results. | Reported integration pattern in CDT-E02, CDT-E03, CDT-E04, and CDT-E07. |
| LAP-03 Analysis Reproduction Manager | Locked Python environments, accepted model inputs, solver identity, raw outputs, and tolerances form the reproduction package and verdict basis. | Proposed from the executable and open-source patterns in CDT-E02 and CDT-E03. |
| LAP-05 Candidate Evaluation Manager | Mission, EPS, and battery simulations provide raw measures for feasibility and architecture comparison. The report's Pareto and score protocol remains a framework addition. | Reported analysis uses from CDT-E02, CDT-E04, CDT-E05, and CDT-E07. |
| LAP-07 Controlled Analysis Coordinator | Python provides the common control point for model extraction, solver execution, Omniverse and Isaac scenario setup, EPS co-simulation, and evidence return. | Synthesized from CDT-E02, CDT-E03, and CDT-E05 through CDT-E07. |
| LIN-02 Transfer Assurance Manager | Cross-tool exchanges require checks for identifiers, units, semantics, mappings, source revision, baseline, timestamps, uncertainty, and synchronization state before acceptance. | Proposed from the reported parser limitation in CDT-E03 and assurance findings in CDT-E08. |
| LIN-05 Evaluation Measurement Manager | The Python runner retains raw observations and applies the common framework measurement manifest after correctness gates pass. | Proposed. The sources provide analysis values, while the report defines the comparison protocol. |

All 18 logical components from `FrameworkLogicalDecomposition` occur once across these three nodes.

## Step 7: minimum physical nodes and components

### CDT-PN-01 CSRM and SysML v2 Model Gateway Physical Node

This node contains candidate-owned interoperability components. The mission-specific authoritative model remains the external Versioned System Model.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Model Gateway Compute Host | Hardware or service | Inferred and unspecified | Host model validation, querying, transformations, and participant views in a declared environment. |
| Framework Command and Review Interface | Software | Proposed | Present controlled requests, status, reports, findings, and approval actions without making a 3D scene authoritative. |
| CSRM Semantic Reference Library | Persistent model data | Reported semantic basis, proposed SysML v2 realization | Preserve the selected CSRM requirements, architecture, stakeholder, measure, use-case, verification, and validation semantics with source provenance and tailoring rules. |
| SysML v2 Model API and Text Adapter | Software | Proposed | Parse, validate, query, and write approved textual SysML v2 elements while preserving stable identifiers and baseline context. |
| Requirements Management Interoperability Adapter | Software | Proposed from reported patterns | Exchange requirement sets, identifiers, verification relations, status, and provenance with external RM capabilities through IF-04. |
| Model Development Interoperability Adapter | Software | Proposed from reported patterns | Exchange generic, tailored, and candidate structure, behavior, interface, property, and trace records with external MD capabilities through IF-04. |
| Stable Identity, Trace, and Mapping Registry | Persistent data | Synthesized | Map CSRM and SysML v2 elements to external requirements and models, analysis variables, OpenUSD prims, verification criteria, and returned evidence. |
| Version Control and Baseline Client | Software | Proposed | Resolve immutable model and evidence revisions and accepted configuration manifests. The version-control product remains open. |

### CDT-PN-02 Python Digital Thread and Analysis Runner Physical Node

Python acts as the integration spine. Domain calculations remain external SA capabilities.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Python Runner Compute Host | Hardware or service | Inferred and unspecified | Execute orchestration, checking, impact analysis, and evidence services in a declared environment. |
| Locked Python Runtime and Environment | Software | Proposed | Pin dependencies and runtime declarations so a designated execution can be reconstructed. |
| Controlled Workflow Orchestrator | Software | Synthesized from reported bridges | Dispatch accepted work, preserve execution identity, apply outcome guards, and prevent unverified results from replacing controlled content. |
| Simulation and Analysis Adapter Registry | Software | Proposed | Register adapters for orbit, power budget, circuit, thermal, battery, robotics, optimization, and later HIL tools with declared schemas and versions. |
| Analysis Request and Result Bridge | Software | Reported pattern, SysML v2 implementation proposed | Build controlled requests from accepted model properties and correlate returned raw results with their request, solver, environment, source revision, and tolerances. |
| Dependency and Change Impact Analyzer | Software | Reported pattern, cross-tool extension proposed | Use model dependencies and mappings to identify affected requirements, analyses, OpenUSD elements, scenarios, and evidence. |
| Transfer and Semantic Checker | Software | Proposed | Check source and baseline identity, schema, stable identifiers, quantities, units, meanings, mappings, provenance, traces, and synchronization status. |
| Evidence and Provenance Packager | Software | Proposed | Package accepted models, mappings, inputs, raw results, uncertainty, discrepancies, verification evidence, and decision context for IF-06. |
| Evaluation Manifest Runner | Software | Proposed | Apply the fixed candidate-evaluation manifest and preserve observations and correctness gates. |
| Typed Analysis Exchange Package | Persistent data | Synthesized from software-readable data patterns | Carry typed analysis inputs and outputs, units, assumptions, execution status, uncertainty, and raw results without becoming the authoritative source. |

### CDT-PN-03 Omniverse and Isaac Interoperability Physical Node

This node contains candidate extensions and controlled data deployed with the external Omniverse and Isaac environment. Omniverse supplies the spatial collaboration plane. Isaac supplies a robotics scenario environment. Specialized EPS and battery calculations remain in external SA tools.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Omniverse Integration Compute Host | Hardware or service | Inferred and unspecified | Provide the GPU-capable environment required by the selected Omniverse and Isaac deployment. Exact resource, license, and service requirements remain open. |
| Omniverse Kit Collaboration Extension | Software | Reported extension mechanism, custom implementation proposed | Present controlled model identity, simulation results, review overlays, findings, and approval status in an OpenUSD view. |
| Controlled OpenUSD Twin Package | Persistent model data | Synthesized | Store versioned scene layers, geometry references, coordinate frames, units, semantic identifiers, bindings, and scenario references for one evidence baseline. |
| SysML v2 to OpenUSD Semantic Bridge | Software | Proposed | Map approved model elements and stable identities to USD prims and metadata. Record every lossy or unsupported transformation as a discrepancy. |
| Isaac Sim Controlled Scenario Adapter | Software | Synthesized from reported robotics uses | Configure reproducible robotics scenarios and return time-stamped states, actions, contacts, modes, and action-derived power demands. |
| FMI and FMU Co-simulation Bridge | Software | Reported proof-of-concept pattern, CubeSat use proposed | Couple tool-neutral dynamic models to the scene and simulation clock. FMI and OpenUSD integration maturity must be verified before selection. |
| EPS and Battery Model Connector | Software | Synthesized | Send mission, environment, and robot load histories to external EPS or battery models and return generated power, bus state, SOC or DoD, temperature, health, uncertainty, and available-power limits. |
| Telemetry and Simulation Data Binder | Software | Reported battery-DT pattern, CubeSat semantics proposed | Bind measured, simulated, estimated, and predicted values to model and scene identities with topics, rates, types, units, timestamps, and source baselines. |
| Battery-Aware Verification Scenario Library | Persistent data | Proposed | Define eclipse, peak load, communication, deployment, safe-mode, thermal, degraded-generation, protection, and energy-limited robotic scenarios with requirement verdict criteria. |
| Simulation Evidence Collector | Software | Proposed | Retain scenario configuration, solver and seed identity, time histories, uncertainty, verdicts, scene snapshots, discrepancies, and logs. |

### CDT-PC-01 Candidate operating procedures

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| CSRM Tailoring and Model Acceptance Procedure | Procedure | Synthesized | Select and tailor the CSRM subset, declare every adaptation, validate identifiers and traces, and accept RM and MD artifacts into a controlled case baseline. |
| Controlled Analysis Execution and Reproduction Procedure | Procedure | Synthesized | Create a locked execution package, invoke designated SA tools, verify transfers, and repeat the execution from a clean declared environment. |
| SysML and OpenUSD Synchronization Procedure | Procedure | Proposed | Generate an OpenUSD view from an accepted model baseline, check semantic mappings, retain discrepancies, and route reverse changes through an approved model change request. |
| Battery-Aware Pre-Physical Verification Procedure | Procedure | Proposed synthesis | Couple robotic action loads and mission environments to an EPS model, return power and health constraints, test requirement tolerances, and retain raw evidence before physical integration. |
| Baseline Release and Collaborative Review Procedure | Procedure | Proposed | Bind model, mapping, scene, scenario, environment, result, uncertainty, discrepancy, finding, and verdict records to one released evidence baseline. |

## Proposed battery-aware pre-physical V&V thread

The minimum candidate supports the following controlled thread:

1. Accept a CSRM-derived SysML v2 model, EPS requirements, mission modes, interfaces, and a named case baseline.
2. Extract only designated parameters and traces into a typed Python analysis package.
3. Generate or update an OpenUSD scene while preserving model identifiers, units, coordinate frames, and mapping status.
4. Run an Isaac scenario that produces time-stamped mode, actuator, payload, contact, thermal-environment, and subsystem-load histories.
5. Pass those histories to an external power-budget, circuit, electrothermal, or battery solver through Python or FMI.
6. Return generated power, bus voltage and current, SOC or DoD, temperature, power margin, health indicators, and uncertainty to the scenario.
7. Exercise power-aware behavior such as task deferral, load shedding, safe-mode entry, charging opportunities, or mission replanning without controlling physical flight hardware.
8. Compare the results with declared requirement criteria and tolerances.
9. Package model, mapping, scene, scenario, solver, environment, inputs, raw time histories, findings, and verdicts under one immutable evidence baseline.

This thread integrates EPS constraints directly into robotic system behavior and extends the conventional power-budget artifact. The first implementation should use a low-cost fidelity level, such as power budget and dynamic battery state. Electrothermal, degradation, SIL, CHIL, and PHIL fidelity can be added only when the decision requires it and validation evidence is available.

## Associated external environment

These resources remain outside the framework boundary even when candidate-owned adapters execute within their hosts.

| External resource | Candidate use |
|---|---|
| Versioned System Model | Hold the authoritative CSRM-derived textual SysML v2 generic, tailored, and candidate EPS models and their source revisions. |
| RM and MD capabilities | Author and refine requirements, architecture, behavior, interfaces, and mission-specific adaptations. |
| SA capabilities | Execute orbit, power-budget, circuit, thermal, electrochemical, degradation, robotics, optimization, and later HIL analyses. Candidate examples include STK-like mission analysis, PyBaMM-like battery analysis, and validated real-time EPS models. |
| NVIDIA Omniverse and Isaac environment | Host the candidate Kit extension, controlled OpenUSD views, collaborative sessions, and robotics scenarios. |
| Evidence Repository | Retain accepted baselines, raw results, mappings, discrepancies, review records, and verification evidence. |

## Boundary and feasibility observations

1. CSRM supplies reusable CubeSat semantics and a starting logical architecture. The candidate must translate, validate, and maintain the required subset as a textual SysML v2 library.
2. SysML v2 remains the semantic authority in this candidate. OpenUSD provides a controlled geometric and collaboration view. Geometry and scene metadata do not replace requirements, behavior, interfaces, or traces.
3. Python provides orchestration and adapters. Specialized tools retain responsibility for domain analysis.
4. The selected sources demonstrate SysML-to-analysis integration, Python model parsing, Omniverse co-simulation, battery digital twins, and CubeSat EPS digital twins separately. No source validates the combined architecture.
5. The initial environment is an offline predictive simulation model for pre-physical V&V. Digital-shadow, HIL, and operational-twin variants require additional telemetry, synchronization, safety, and validation components.
6. Isaac provides robotic and physical scenario behavior. It needs an external electrical or battery model to make energy constraints physically meaningful.
7. The battery architecture in `handpicked-report-0001` targets electric vehicles and stationary storage. Its satellite-use data profile supports relevance, while CubeSat transfer requires new calibration and validation.
8. The USD and FMI work in `handpicked-report-0002` is presented as an MVP, proof of concept, and in-progress standardization effort. Interface maturity, timing, determinism, and tool support remain selection risks.
9. The direct 6U CubeSat EPS digital twin evidence uses Typhoon HIL. It supports the EPS model and validation pattern. The proposed scene integration requires separate validation.
10. Model fidelity must follow the decision. High fidelity increases computing cost, calibration work, and validation burden.
11. The candidate must expose uncertainty, data quality, synchronization state, assumptions, and validity limits in every reported result.
12. GPU resources, product licenses, OpenUSD asset preparation, cybersecurity, repository technology, backup, and operational support remain unspecified and must enter feasibility, cost, and adoption evaluation.
13. No detailed deployment sizing or geometric model of the framework itself is needed at this stage. The controlled CubeSat geometry is an engineering artifact handled by the candidate.

## SysML artifact

The corresponding simple model is:

`final_report/models/framework-candidate-custom.sysml`

Generated views are available in SVG, PNG, and PDF:

- `final_report/figures/sysml/custom-candidate-node-logical-general.*`
- `final_report/figures/sysml/custom-candidate-physical-general.*`
