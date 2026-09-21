# Nanospace centered candidate: OOSEM steps 6 and 7

## Scope

This is a deliberately small candidate model. It performs:

- Step 6: define the candidate logical node distribution.
- Step 7: define the minimum physical nodes and components.

It does not yet assert logical to physical allocations, requirement satisfaction, or measured performance. Those belong to the following synthesis and evaluation steps.

The candidate preserves the system boundary in `final_report/final_report.tex`. The Versioned System Model, Analysis Tools, and Evidence Repository remain external to the framework. Nanospace provides the central concurrent engineering data and collaboration environment. A Python integration service connects the external system model, the Nanospace API, external analysis tools, and the evidence repository.

The candidate combines two related literature configurations. The Nanospace platform provides a browser client, application service, graph database, and interfaces to discipline tools. The later MBSE formalization makes an external CubeSat SysML model the central data reference and uses a Python model parser to exchange structured data with the Nanostar Software Suite tools. The proof of concept uses Gaphor and SysML v1. This candidate is described separately in textual SysML v2 under MC-01 so that it can be compared at the same abstraction as the other candidates. The SysML v2 comparison description does not require the candidate implementation or its native artifacts to use SysML v2.

## Evidence basis

The evidence was located with `embeddings/search.py` and checked in the source Markdown and referenced architecture figures.

| ID | Extracted evidence | Source |
|---|---|---|
| NS-E01 | Nanospace is an open source web application for academic CubeSat preliminary design. Its core consists of a GUI, database, and API. It supports concurrent remote access, transparent visualization, and exchange with third party expert software. | Salas Cordero, Gateau, and Vingerhoeds, *MBSE Challenges in the Concurrent Preliminary Design of CubeSats: Nanospace Study* (2022), PDF pp. 6 to 8, `review-0908`. Salas Cordero, Gateau, and Vingerhoeds, *Hierarchical Planning Applied to the Preliminary Design of CubeSats: Nanospace Study* (2025), PDF pp. 12 to 14, `review-0340`. |
| NS-E02 | The reproduced Nanospace architecture identifies an AngularJS client page, Nginx web server, Java Nanospace Service, Neo4j graph database connected through Bolt, a Python REST API, and REST or embedded interfaces for third party tools. | Luccisano, *Data Formalisation through MBSE for Concurrent Preliminary Design of CubeSats* (2024), PDF p. 31, Figure 18, `citation-2300`. |
| NS-E03 | The browser interface supports authentication, shared project responsibility, project and model editing, values, requirements, component modes, and access to modification history. It requires only a modern browser on the client. | Luccisano (2024), PDF pp. 32 to 33, `citation-2300`. |
| NS-E04 | Nanospace DB uses Neo4j graph storage with ACID properties and write protection for concurrent access. Its reported entities include Project, Component, Mode, Value, and User. | Luccisano (2024), PDF pp. 33 to 34, `citation-2300`. |
| NS-E05 | Nanospace supports manual GUI exchange, generic interfaces, and its dedicated API. The Nanostar constellation connects discipline tools for mission, structure, link, power, data, radiation, ADCS, and related preliminary design analyses at different integration levels. | Luccisano (2024), PDF pp. 31 and 34 to 35, Figures 18 and 20, `citation-2300`. |
| NS-E06 | In the CREME example, requirements and design parameters are stored in Nanospace, Python scripts update the database through the API, intermediate results are retained and shared, and dependency graphs or design structure matrices guide which analyses must run again. The process remains semi-automatic and requires human expertise. | Salas Cordero et al. (2022), PDF pp. 5 to 6, `review-0908`. Salas Cordero et al. (2025), PDF pp. 6 to 9, `review-0340`. |
| NS-E07 | A later open source formalization uses a CubeSat SysML model with UML stereotypes as the central data reference. A Gaphor specific Python parser extracts a software readable data structure, requirements lists, and dependency graphs. Reverse parsing can update the model after analysis or optimization. An end to end example generated power and data budgets with NSS tools. | Luccisano et al., *Open-Source Data Formalization through Model-Based Systems Engineering for Concurrent Preliminary Design of CubeSats* (2024), PDF pp. 3, 14 to 19, `review-0602`. |
| NS-E08 | The literature identifies unresolved continuity and interoperability concerns. The 2022 study reports possible information loss between MBSE tools and the need to reassess the Nanospace database to represent richer parameter relations. The 2024 parser works only with Gaphor without source changes, while real time versioning and cloud storage remain suggested improvements. | Salas Cordero et al. (2022), PDF pp. 6 to 8, `review-0908`. Luccisano et al. (2024), PDF pp. 19 to 21, `review-0602`. |
| NS-E09 | Hierarchical planning could encode expert knowledge and guide early design choices, but its integration into Nanospace is explicitly future work. The current minimum candidate therefore treats it as an optional later variant rather than an implemented component. | Salas Cordero et al. (2025), PDF pp. 12 to 14, `review-0340`. |

Evidence classifications used below:

- **Reported:** stated directly in a cited source or identified in its architecture figure.
- **Synthesized:** combines compatible elements reported across the Nanospace literature lineage.
- **Inferred:** necessary architectural interpretation of reported behavior.
- **Proposed:** added to make the literature configuration address this project's baseline.
- **Unspecified:** required detail that the selected sources do not establish.

## Step 6: candidate logical node distribution

The node distribution separates browser access, collaborative engineering data and workflow, and model and analysis integration. It remains independent of detailed deployment technology.

### NS-LN-01 Participant Web Access Node

Purpose: mediate interactions with the Academic Mission Team, Academic Researcher, and Reviewer through the Nanospace browser environment.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-01 Mission Application Interface Manager | Nanospace provides browser access to shared projects, models, requirements, values, and analysis information. | Reported and synthesized from NS-E01 and NS-E03. |
| LIF-02 Research Governance Interface Manager | Shared project responsibility, transparent data views, model editing, and analysis outputs provide a plausible research interaction surface. | Inferred from NS-E01, NS-E03, and NS-E07. |
| LIF-03 Independent Review Interface Manager | Modification history and browser access can expose controlled information to a reviewer. Reviewer specific permissions, findings, and disposition workflows remain unreported. | Partial evidence from NS-E03. |

### NS-LN-02 Collaborative Engineering Data and Workflow Node

Purpose: coordinate evidence, case configuration, review, shared workflow, configuration information, and retained engineering records around Nanospace and its graph database.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LAP-01 Evidence Chain Manager | Requirements, project elements, values, users, history, and intermediate results provide inputs for an evidence chain. Complete chain semantics and endpoint provenance remain unverified. | Partial evidence from NS-E03, NS-E04, and NS-E06. |
| LAP-02 Case Configuration Manager | Projects, models, components, modes, and values can represent a case configuration. Generic model and approved adaptation baseline semantics remain unreported. | Reported structure and inferred use from NS-E03 and NS-E04. |
| LAP-06 Design Review Manager | Shared browser views, modification history, requirements, reports, and analysis outputs can support review package assembly. Findings and disposition control remain proposed. | Partial evidence from NS-E03, NS-E06, and NS-E07. |
| LIN-01 Workflow Control Manager | The reported process uses dependency graphs or design structure matrices to sequence semi-automatic analysis iterations while retaining human decisions. | Reported in NS-E06. Complete framework service control remains proposed. |
| LIN-03 Baseline and Configuration Manager | The graph database, user identity, write protection, and modification history provide configuration inputs. Immutable baseline and source revision semantics remain unreported. | Partial evidence from NS-E03 and NS-E04. |
| LIN-04 Evidence and Provenance Manager | Nanospace retains shared project data and intermediate results and attributes changes to users. Complete artifact provenance and immutable evidence custody remain unreported. | Partial evidence from NS-E03, NS-E04, and NS-E06. |

### NS-LN-03 Model, Analysis, and Assurance Integration Node

Purpose: synchronize the external system model with Nanospace, coordinate external analyses, generate dependency information, and check controlled exchanges.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-04 Model Control Interface Manager | The model centered formalization uses a dedicated parser to read and reverse update an external Gaphor SysML model. | Reported in NS-E07. |
| LIF-05 Analysis Execution Interface Manager | Nanospace and NSS exchange data with discipline tools through manual, generic, embedded, and REST interfaces. | Reported in NS-E01, NS-E05, NS-E06, and NS-E07. |
| LIF-06 Evidence Custody Interface Manager | An adapter is required to exchange controlled packages with the external Evidence Repository. | Proposed. The selected sources do not establish this interface. |
| LAP-03 Analysis Reproduction Manager | Open source scripts, structured inputs, generated data sets, and retained outputs can form a reproduction package. Clean environment reconstruction and verdict semantics remain unverified. | Partial evidence from NS-E06 and NS-E07. |
| LAP-04 Design Change Assessment Manager | Dependency graphs and design structure matrices identify affected parameters, while reverse parsing can return analysis changes to the model. | Reported in NS-E06 and NS-E07. |
| LAP-05 Candidate Evaluation Manager | The tool constellation executes budgets and analyses that support design iteration and trade assessment. The report's feasibility and Pareto protocol remains proposed. | Partial evidence from NS-E05 through NS-E07. |
| LAP-07 Controlled Analysis Coordinator | The Python parser, Nanospace API, software readable data, and discipline scripts provide the natural coordination point for controlled execution. | Reported components with a synthesized coordination role from NS-E06 and NS-E07. |
| LIN-02 Transfer Assurance Manager | The literature explicitly identifies coherence and information loss risks across tools. This candidate adds checks for source identity, completeness, units, meaning, provenance, traces, and baseline identity. | Problem reported in NS-E08. Assurance implementation proposed. |
| LIN-05 Evaluation Measurement Manager | Python scripts and NSS tools generate raw budgets, reports, and dependency information. Applying the common evaluation manifest and MOP protocol is proposed. | Reported analysis mechanism from NS-E06 and NS-E07 with proposed framework measurements. |

All 18 logical components from `FrameworkLogicalDecomposition` occur once across these three nodes.

## Step 7: minimum physical nodes and components

### NS-PN-01 Browser Client Node

The literature directly distinguishes a browser client from the Nanospace server. The participant device and its operating environment remain abstract.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Participant Browser Host | Hardware or service | Inferred and unspecified | Provide the participant device and execution environment for browser access. |
| Modern Web Browser | Software | Reported | Access Nanospace without a candidate specific client installation. |
| Nanospace AngularJS Web Interface | Software | Reported | Present projects, models, requirements, modes, values, history, users, and shared analysis information. |

### NS-PN-02 Nanospace Application and Data Server Node

The reproduced platform architecture places the web server, Java service, and graph database on the server side. It does not establish whether these elements run on one machine, several containers, or separate hosts. This physical node therefore represents one deployment responsibility rather than a detailed server topology.

| Physical component | Kind | Evidence classification | Minimal responsibility |
| Nanospace Application Compute Host | Hardware or service | Inferred and unspecified | Host the web server, application service, API, and graph database in a declared environment. |
| Nginx Web Server | Software | Reported | Serve the Nanospace web application over HTTP. |
| Nanospace Java Service | Software | Reported | Provide application logic and HTTP access to engineering data. |
| Nanospace REST API Endpoint | Software interface | Reported | Expose project data to the browser, Python integrations, and third party applications. |
| Nanospace Neo4j Engineering Database | Persistent data and database software | Reported | Store graph structured Project, Component, Mode, Value, User, history, and related engineering records with concurrent transaction control. |

### NS-PN-03 Python Model and Analysis Integration Runner Node

The literature reports each core integration mechanism. Their combination into one controlled runner is the candidate synthesis. Evidence repository integration and the complete transfer contract are project additions.

| Physical component | Kind | Evidence classification | Minimal responsibility |
| Python Integration Compute Host | Hardware or service | Inferred and unspecified | Execute the model parser, API clients, dependency generation, analysis coordination, and assurance checks. |
| Python Model and Data Bridge | Software | Synthesized from reported mechanisms | Coordinate model extraction, Nanospace updates, analysis requests, returned results, and reverse model updates. |
| Gaphor SysML Model Parser and Adapter | Software | Reported | Read the external Gaphor model file, extract stereotyped data and requirements, and reverse approved updates through IF-04. |
| Nanospace API Client | Software | Reported pattern | Read and update Nanospace engineering records through the dedicated API. |
| Software Readable Exchange Data Set | Persistent data | Reported | Carry selected model parameters and analysis inputs and outputs in a tool readable structure. YAML is used in the cited proof of concept, while the format remains adaptable. |
| Analysis Tool Adapter | Software | Reported pattern, candidate specific implementation proposed | Invoke external NSS or other analysis tools through IF-05 and correlate returned budgets, reports, and raw results. |
| Dependency and DSM Generator | Software | Reported | Generate dependency graphs or design structure matrices used for impact analysis and iteration sequencing. |
| Evidence Repository Adapter | Software | Proposed | Register and retrieve controlled evidence packages through IF-06. |
| Transfer and Consistency Checker | Software | Proposed | Check source revision, baseline, structural completeness, identifiers, quantities, units, meaning, provenance, and applicable traces before accepting transfers. |
| Evaluation Manifest Runner | Software | Proposed | Apply the fixed framework evaluation manifest and preserve raw observations needed by the common comparison protocol. |

### NS-PC-01 Candidate operating procedures

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| User, Role, and Project Administration Procedure | Procedure | Reported pattern | Establish users, shared project responsibility, permissions, and reviewer access. |
| Model and Nanospace Synchronization Procedure | Procedure | Synthesized from reported mechanisms | Extract approved model data, inspect transfer findings, update Nanospace, and reverse only authorized changes to the model. |
| Semi-Automatic Design Iteration Procedure | Procedure | Reported | Use dependency information and expert judgment to select affected analyses, execute them, and assess the next design iteration. |
| Baseline Release and Evidence Export Procedure | Procedure | Proposed | Bind model, Nanospace, analysis, and discrepancy records to a controlled evidence baseline and export the package needed for independent reconstruction. |
| Analysis Reproduction Procedure | Procedure | Proposed from reported open source scripts and structured data | Reconstruct the declared environment, execute a designated analysis, and issue its evidence package and verdict inputs. |

## Boundary and feasibility observations

1. The selected variant makes the external SysML model the architecture and engineering data master. Nanospace provides the concurrent working database and collaboration surface.
2. The literature proof of concept uses Gaphor and SysML v1. The candidate's SysML v2 file is a separate common comparison description under MC-01.
3. Nanospace requires external tools and human experts. The literature explicitly states that it cannot complete a preliminary design autonomously.
4. The Python bridge is essential because the native platform, model files, and discipline tools use different structures and interfaces.
5. Modification history, Neo4j transactions, and user attribution provide useful configuration inputs. The selected sources do not establish immutable baselines, complete provenance, accepted external artifact registration, or clean environment reconstruction.
6. The Gaphor parser is tool specific. Supporting another native modeling tool requires parser changes or another adapter.
7. Reviewer access, findings disposition, controlled evidence export, and the complete transfer verification contract remain project additions.
8. Hierarchical planning is a possible Nanospace subvariant. It is excluded from this minimum candidate because the cited paper identifies its integration as future work.
9. The exact application hosting, database deployment, network security, backup, recovery, and operational support topology remain unspecified.
10. No detailed geometric model is needed for this software centered candidate at this stage. Hardware and deployment stay abstract until they affect cost, reconstruction, security, or performance.

## SysML artifact

The corresponding simple model is:

`final_report/models/framework-candidate-nanospace.sysml`

Generated views are available in SVG, PNG, and PDF:

- `final_report/figures/sysml/nanospace-candidate-node-logical-general.*`
- `final_report/figures/sysml/nanospace-candidate-physical-general.*`
