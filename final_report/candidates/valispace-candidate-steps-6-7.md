# Valispace centered candidate: OOSEM steps 6 and 7

## Scope

This is a deliberately small candidate model. It performs:

- Step 6: define the candidate logical node distribution.
- Step 7: define the minimum physical nodes and components.

It does not yet assert logical to physical allocations, requirement satisfaction, or measured performance. Those belong to the following synthesis and evaluation steps.

The candidate preserves the system boundary in `final_report/final_report.tex`. The Versioned System Model, Analysis Tools, and Evidence Repository remain external to the framework. Valispace acts as the central collaborative engineering data and workflow environment. A Python integration service connects it to the external architecture model and the other resources.

The implementation follows the main literature example, which uses Capella as the architecture master and Valispace as the requirements, engineering data, budget, and trade study environment. This candidate is described separately in textual SysML v2 under MC-01 so that it can be compared at the same abstraction as the other candidates. The SysML v2 comparison description does not require the candidate implementation or its native artifacts to use SysML v2.

## Evidence basis

The evidence was located with `embeddings/search.py` and checked in the source Markdown.

| ID | Extracted evidence | Source |
|---|---|---|
| VS-E01 | Valispace is a browser based platform built around a consistent engineering database. It supports remote access, notifications, formulas, dependencies, and an API for import, export, and automation. | Deiana, *Integrating Data-Driven and Model-Based Systems Engineering for End-to-End Small-Satellite Design* (2025), PDF pp. 33 to 35, `citation-4690`. |
| VS-E02 | The reported platform exposes Project, Components, Requirements, Analyses, Scripting, and Tests modules. The Components module manages a product tree, properties, modes, and trade studies. The Scripting module runs Python or Octave calculations. | Deiana (2025), PDF pp. 36 to 37, `citation-4690`. |
| VS-E03 | The literature configuration makes Capella the architecture master and Valispace the supporting requirements, engineering data, budget, and trade study environment. Python scripts use Python for Capella and the Valispace REST API to synchronize them. | Campioli, Deiana, and Corpino, *Integrating Concurrent Engineering with Data-Driven and Model-Based Systems Engineering for End-to-End Small-Satellite Design* (2025), PDF p. 3, `review-0356`. Deiana (2025), PDF pp. 47 to 55, `citation-4690`. |
| VS-E04 | The Python bridge compares component hierarchies, reports discrepancies, and can restore missing Valispace components from the architecture master while preserving parent and child relationships. | Deiana (2025), PDF pp. 50, 55, and 79 to 80, `citation-4690`. Campioli et al. (2025), PDF pp. 6 to 7, `review-0356`. |
| VS-E05 | A CubeSat project used Valispace as a requirements hub connected to mission tools. The authors selected it for integration, requirements tracking, spacecraft budgets, and requirement linked test procedures. | Ivanov, *Spacecraft digital engineering: the tale of “digital twins” and lessons learned* (2023), PDF pp. 5 and 9, `review-0793`. |
| VS-E06 | A source comparison rates Valispace strongly for requirements and engineering data, while reporting weak support for functional analysis, architecture, ConOps, and modes and states. Another comparison reports no SysML diagram support and identifies licensed access as a concern for external procedure performers. | Deiana (2025), PDF pp. 46 to 47, `citation-4690`. Latserus et al., *Model-based approach for requirements management connection with verification procedures applied to space systems* (2020), PDF pp. 5 to 6, `citation-0569`. |
| VS-E07 | The reported integration consists of several scripts. The thesis identifies their fragmented operation and proposes a future user interface to reduce training and execution effort. | Deiana (2025), PDF pp. 90 to 91, `citation-4690`. |

Evidence classifications used below:

- **Reported:** stated directly in a cited source.
- **Inferred:** necessary architectural interpretation of reported behavior.
- **Proposed:** added to make the literature configuration address this project's baseline.
- **Unspecified:** required detail that the selected sources do not establish.

## Step 6: candidate logical node distribution

The node distribution separates participant access, centralized engineering services, and integration assurance. It remains independent of detailed deployment technology.

### VS-LN-01 Participant Access Node

Purpose: mediate interactions with the Academic Mission Team, Academic Researcher, and Reviewer through a shared browser based environment.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-01 Mission Application Interface Manager | Valispace provides browser based, stakeholder oriented access to common project data. | Reported and synthesized from VS-E01. |
| LIF-02 Research Governance Interface Manager | The shared data, analysis, and trade study environment provides a plausible research interaction surface. | Inferred from VS-E01, VS-E02, and VS-E05. |
| LIF-03 Independent Review Interface Manager | Reviews and test records can be exposed through the shared environment, subject to licensing and access controls. | Partial evidence from VS-E02, VS-E05, and VS-E06. |

### VS-LN-02 Engineering Data and Workflow Node

Purpose: coordinate the six framework services using the centralized product tree, requirements, engineering properties, analyses, test records, and workflow information.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LAP-01 Evidence Chain Manager | Central requirements, components, values, links, test records, and reports provide inputs for evidence chain management. | Partial evidence from VS-E01, VS-E02, and VS-E05. Complete chain semantics remain unverified. |
| LAP-02 Case Configuration Manager | Product trees, component properties, modes, matrices, and reusable information support case configuration. | Reported and inferred from VS-E02. Baseline semantics remain unverified. |
| LAP-03 Analysis Reproduction Manager | Stored analyses, scripts, parameters, and test procedures can package a reproduction attempt. | Partial evidence from VS-E02 and VS-E05. Independent reconstruction remains unverified. |
| LAP-04 Design Change Assessment Manager | Connected properties, formulas, notifications, and synchronized hierarchies support change propagation and discrepancy reporting. | Reported and inferred from VS-E01 and VS-E04. |
| LAP-05 Candidate Evaluation Manager | The Components and Analyses modules support budgets and trade studies over alternatives. | Reported in VS-E02 and VS-E05. |
| LAP-06 Design Review Manager | Project information, analyses, reports, tests, and requirement status can support a review package and findings workflow. | Partial evidence from VS-E02 and VS-E05. |
| LIN-01 Workflow Control Manager | The Project module and the platform workflow provide the natural shared control responsibility. | Reported and inferred from VS-E02. |
| LIN-03 Baseline and Configuration Manager | The central database and hierarchy synchronization provide configuration inputs. Immutable baseline and source revision semantics remain unreported. | Partial evidence from VS-E01 and VS-E04. |
| LIN-04 Evidence and Provenance Manager | The database, reports, tests, and requirement links provide retained records. Complete provenance and immutable evidence custody remain unreported. | Partial evidence from VS-E01, VS-E02, and VS-E05. |
| LIN-05 Evaluation Measurement Manager | Properties, formulas, matrices, analyses, and trade studies provide the measurement mechanism. | Reported in VS-E01 and VS-E02. |

### VS-LN-03 Integration and Assurance Node

Purpose: mediate controlled exchanges with the external architecture model, analysis tools, and evidence repository. It also checks consistency before accepting transferred information.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-04 Model Control Interface Manager | The literature uses Capella as an architecture master connected through Python scripts. | Reported in VS-E03 and VS-E04. |
| LIF-05 Analysis Execution Interface Manager | Valispace exposes an API and has been connected to external mission tools. | Reported in VS-E01, VS-E03, and VS-E05. |
| LIF-06 Evidence Custody Interface Manager | An adapter is required to exchange controlled packages with the external Evidence Repository. | Proposed. The selected sources do not establish this interface. |
| LAP-07 Controlled Analysis Coordinator | The API bridge and scripting environment provide a natural location for controlled execution requests and returned results. | Inferred from VS-E02, VS-E03, and VS-E05. |
| LIN-02 Transfer Assurance Manager | The reported bridge compares hierarchies and exposes discrepancies before restoring conformity. This candidate extends the same pattern to source identity, units, traces, provenance, and baseline checks. | Reported core pattern from VS-E04. Extended checks are proposed. |

All 18 logical components from `FrameworkLogicalDecomposition` occur once across these three nodes.

## Step 7: minimum physical nodes and components

### VS-PN-01 Valispace Hosted Service Node

The selected papers establish a web platform and consistent central database. They do not expose the vendor's detailed server or database deployment. The node therefore remains an opaque hosted environment.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Valispace Web Interface | Software | Reported | Present stakeholder views and browser based access. |
| Valispace Project Module | Software | Reported | Project overview, coordination, and workflow information. |
| Valispace Components Module | Software | Reported | Product tree, components, properties, modes, and alternatives. |
| Valispace Requirements Module | Software | Reported | Requirement hierarchy, links, and verification status. |
| Valispace Analyses Module | Software | Reported | Reports, budgets, graphs, tables, and trade study results. |
| Valispace Scripting Module | Software | Reported | Python or Octave calculations and simulations. |
| Valispace Tests Module | Software | Reported | Verification procedures, attachments, tags, and status. |
| Valispace Engineering Database | Persistent data | Reported at platform level | Store connected engineering values, requirements, component structures, and associated records. |
| Valispace REST API Endpoint | Software interface | Reported | Provide authenticated CRUD access for integrations. |
| Valispace Hosted Compute Infrastructure | Hardware or service | Inferred and unspecified | Host the web application and engineering database. Vendor deployment details remain open. |

### VS-PN-02 Python Integration Runner Node

The literature directly supports a Python bridge, a Capella-side model adapter, and REST API integration. The remaining adapters are explicit additions required by the current framework boundary and system requirements.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Python Integration Bridge | Software | Reported | Coordinate synchronization, transformation, comparison, discrepancy reporting, and controlled updates. |
| Capella Architecture Model Adapter | Software | Reported | Use the Capella-side Python API and export scripts to supply architecture-model elements through IF-04. The separate SysML v2 comparison model describes this component without changing it. |
| Analysis Tool Adapter | Software | Reported pattern, candidate specific implementation proposed | Issue controlled analysis requests and correlate returned results through IF-05. |
| Evidence Repository Adapter | Software | Proposed | Register and retrieve controlled evidence packages through IF-06. |
| Transfer and Consistency Checker | Software | Reported core, extended behavior proposed | Generalize product tree comparison to the complete transfer contract. |
| Evaluation Manifest Runner | Software | Proposed | Apply the fixed framework evaluation manifest and retain raw observations. |
| Integration Compute Host | Hardware or service | Inferred and unspecified | Execute the Python bridge and adapters in a declared reproducible environment. |

### VS-PC-01 Candidate operating procedures

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Role and Access Administration Procedure | Procedure | Inferred | Establish users, licenses, permissions, and reviewer access. |
| Model and Data Synchronization Procedure | Procedure | Reported pattern | Execute synchronization, inspect discrepancies, and authorize controlled updates. |
| Baseline Release and Evidence Export Procedure | Procedure | Proposed | Bind Valispace records to the framework evidence baseline and export the package required for independent reconstruction. It does not use the OOSEM study repository unless the candidate independently selects that mechanism. |
| Analysis Reproduction Procedure | Procedure | Proposed from reported scripting and test capabilities | Reconstruct the declared environment, execute the designated analysis, and issue its evidence package. |

## Boundary and feasibility observations

1. Valispace remains the central data and workflow platform. Capella remains the native architecture source in this literature-based implementation.
2. The Python bridge is essential. The literature reports hierarchy comparison and repair between Capella and Valispace.
3. The candidate's SysML v2 file is a common comparison description under MC-01. It is not a runtime component or native-artifact requirement.
4. The selected sources do not establish immutable evidence baselines, complete provenance, clean environment reconstruction, or the report's complete transfer contract.
5. Weak native SysML and architecture support does not make the candidate infeasible because SysML v2 applies to the comparison description. Architecture completeness still depends on Capella and the bridge.
6. Licensed reviewer access is a known concern. The later feasibility step must test whether controlled review packages can be exported without giving every reviewer a Valispace authoring license.
7. No detailed geometric model is needed for this software centered candidate at this stage. Hardware and hosted deployment remain abstract until they affect cost, reconstruction, security, or performance.

## SysML artifact

The corresponding simple model is:

`final_report/models/framework-candidate-valispace.sysml`

Generated views are available in SVG, PNG, and PDF:

- `final_report/figures/sysml/valispace-candidate-node-logical-general.*`
- `final_report/figures/sysml/valispace-candidate-physical-general.*`
