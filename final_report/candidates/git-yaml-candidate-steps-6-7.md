# Lightweight Git and YAML candidate: OOSEM steps 6 and 7

## Scope

This is a deliberately small candidate model. It performs:

- Step 6: define the candidate logical node distribution.
- Step 7: define the minimum physical nodes and components.

It defers logical to physical allocations, requirement satisfaction, and measured performance to the following synthesis and evaluation steps.

The candidate preserves the system boundary in `final_report/final_report.tex`. The Versioned System Model, Analysis Tools, and Evidence Repository remain external to the framework. The candidate maintains an internal Git and YAML working record set, generated participant views, and controlled integration services. It exchanges authoritative model revisions through IF-04, invokes external analyses through IF-05, and exports accepted evidence packages through IF-06.

The candidate synthesizes two related literature approaches:

1. A lightweight engineering data management concept for small satellites uses a hierarchical entity and parameter model, a browser interface, a Python backend, Git version control, YAML records, a REST API, and optional notifications.
2. The SeaLion docs as code approach demonstrates a Git hosted YAML mission architecture with explicit source links, stakeholder needs, user stories, data structures, components, generated diagrams, generated documents, and development issue links.

The lightweight tool paper presents a design and early proof of concept rather than a production ready system. The SeaLion source demonstrates the docs as code information pattern while reporting incomplete component coverage and limited team participation. The complete candidate is therefore a new synthesis with explicit project additions for artifact acceptance, independent reproduction, transfer assurance, evidence export, and evaluation measurement.

This file and its companion SysML v2 model provide the common comparison description required by MC-01. The candidate's native records remain Git and YAML artifacts.

## Evidence basis

The evidence was located with `embeddings/search.py` and checked in the source Markdown.

| ID | Extracted evidence | Source |
|---|---|---|
| GY-E01 | The proposed lightweight engineering data management tool targets small satellite teams that need lower modeling overhead. The authors present interface mockups, a Nuxt.js proof of concept front end, an early Python backend, and a POQUITO mission example. The implementation is released as free software. | Kanavouras, Bühler, and Hein, *Building a Lightweight Data Management Tool for Small Satellite Missions* (2024), PDF pp. 1 and 5 to 10, `review-0522`. |
| GY-E02 | The tool represents a spacecraft as a hierarchy of entities with typed parameters. The proposed web interface can run on a local server or in the cloud and is intended to expose all functions through a browser. The design objective is access to an engineering parameter within 20 seconds. | Kanavouras et al. (2024), PDF pp. 3 to 7, `review-0522`. |
| GY-E03 | The proposed storage design represents each entity as a human and machine readable YAML file under Git. The rationale is low overhead, raw inspection, diff support, history, merge support, auditing, transfer, and the option to author records without the web tool. | Kanavouras et al. (2024), PDF pp. 4 to 6, `review-0522`. |
| GY-E04 | The tool is designed around a REST API for front end access and external engineering integrations. Proposed extension mechanisms include a Python backend and plugins. Git or webhook integrations can announce changes through existing team communication systems. | Kanavouras et al. (2024), PDF pp. 4, 8, and 9, `review-0522`. |
| GY-E05 | Parameters may be entered manually, imported from an external tool, or calculated from other parameters. Proposed parameter states include rejected, pending, approved, expired, and new data. The data types include quantities with units, text, enumerations, entity references, tables, functions, and time varying values. | Kanavouras et al. (2024), PDF pp. 9 to 10, `review-0522`. |
| GY-E06 | The SeaLion mission architecture uses M30ML YAML files and Git based docs as code workflows. Its repository links references, stakeholder needs, user stories, data structures, and components. `derivedFrom` relationships provide explicit source and refinement links. | Chiu, *SeaLion CubeSat Mission Architecture Using Model Based Systems Engineering with a Docs as Code Approach* (2023), PDF pp. 26 to 27, 31 to 32, and 42 to 56, `review-0787`. |
| GY-E07 | SeaLion generates UML diagrams, tables, text, references, and assembly instructions from the YAML source. A changed architecture can regenerate dependent documents. Generated architecture content also supplies tasks in the flight software issue workflow. | Chiu (2023), PDF pp. 52 to 75, `review-0787`. |
| GY-E08 | The distributed component records include version, license, author, dependencies, nested components, parts, functions, tools, precautions, and assembly steps. The proposed interface and junction records can support generated interface views such as an N2 diagram. | Chiu (2023), PDF pp. 69 to 75, `review-0787`. |
| GY-E09 | The lightweight data tool remains a preliminary design with production implementation and case comparison left to future work. Requirements, test, and risk management are outside its initial scope. The SeaLion architecture remained incomplete because subject matter experts had limited availability, and many team members only viewed generated documents. | Kanavouras et al. (2024), PDF pp. 5 and 10, `review-0522`. Chiu (2023), PDF pp. 77 to 78, `review-0787`. |

Evidence classifications used below:

- **Reported implementation:** demonstrated in a cited source.
- **Reported design:** proposed explicitly by a cited source but not demonstrated as production ready.
- **Synthesized:** combines compatible elements reported across the two sources.
- **Inferred:** necessary architectural interpretation of reported behavior.
- **Proposed:** added to realize this candidate and the project's black box baseline.
- **Unspecified:** required implementation detail that the selected sources do not establish.

## Step 6: candidate logical node distribution

The logical distribution separates participant access and review, versioned engineering records and workflow, and controlled model and analysis integration. Detailed hosting products remain open until Step 7.

### GY-LN-01 Participant Access and Review Logical Node

Purpose: mediate mission team, research, and independent review interactions through browser views, generated documents, controlled requests, and findings.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-01 Mission Application Interface Manager | The lightweight web interface exposes the system hierarchy, parameters, context, actions, and change state to mission participants. | Reported design from GY-E01, GY-E02, and GY-E05. |
| LIF-02 Research Governance Interface Manager | Human readable YAML, raw Git history, generated views, and API access provide a low overhead surface for inspecting and extending case data. | Synthesized from GY-E03, GY-E04, GY-E06, and GY-E07. |
| LIF-03 Independent Review Interface Manager | Raw versioned records and generated documents can be published for independent inspection. Reviewer roles, blinded tests, and outcome authority remain project additions. | Partial evidence from GY-E03, GY-E06, and GY-E07. |
| LAP-06 Design Review Manager | Generated architecture documents, Git changes, issue records, and linked source information can form a review package. Findings and disposition control remain proposed. | Partial evidence from GY-E06 and GY-E07. |

### GY-LN-02 Versioned Engineering Records and Workflow Logical Node

Purpose: control the candidate's normalized Git and YAML working records, case configuration, change history, evidence relationships, generated views, and service workflow.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LAP-01 Evidence Chain Manager | YAML source and refinement links can connect references, needs, user stories, data structures, components, and generated artifacts. The report's complete chain validity rules remain proposed. | Reported trace pattern from GY-E06 and GY-E07. |
| LAP-02 Case Configuration Manager | Hierarchical entities, parameters, component versions, dependencies, and Git revisions provide a compact case configuration structure. Generic model and approved adaptation semantics remain proposed. | Synthesized from GY-E02, GY-E03, GY-E05, and GY-E08. |
| LAP-04 Design Change Assessment Manager | Git diffs, `derivedFrom` links, component dependencies, generated views, and stale parameter states provide change impact inputs. Complete cross tool impact analysis remains proposed. | Synthesized from GY-E03, GY-E05, GY-E06, and GY-E08. |
| LIN-01 Workflow Control Manager | Git branches, review actions, issue records, parameter approval states, regeneration, and release steps provide the candidate workflow skeleton. | Synthesized from GY-E03, GY-E05, and GY-E07. |
| LIN-03 Baseline and Configuration Manager | Git revisions and versioned YAML records provide history and merge control. Protected release, immutable baseline, environment, and source revision semantics remain proposed. | Reported basis from GY-E03, GY-E06, and GY-E08. |
| LIN-04 Evidence and Provenance Manager | Source links, authorship, versions, dependencies, history, generated documents, and issue records provide provenance inputs. Complete external artifact registration and evidence custody remain proposed. | Partial evidence from GY-E03, GY-E06, GY-E07, and GY-E08. |

### GY-LN-03 Model, Analysis, and Assurance Integration Logical Node

Purpose: accept external model records, coordinate external analyses through the API, check transfers, package reproducible evidence, and apply the common evaluation manifest.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-04 Model Control Interface Manager | A model adapter imports designated records from the external Versioned System Model into normalized YAML and returns only approved changes. | Proposed. The sources establish Git and YAML records but no bidirectional formal model adapter. |
| LIF-05 Analysis Execution Interface Manager | The REST API is intended to connect external engineering tools and import their parameter values. | Reported design in GY-E04 and GY-E05. |
| LIF-06 Evidence Custody Interface Manager | An adapter exports accepted release packages to and retrieves retained records from the external Evidence Repository. | Proposed. Neither source establishes the report's evidence repository contract. |
| LAP-03 Analysis Reproduction Manager | Versioned inputs, scripts, environment declarations, raw outputs, and generated reports can form a reproduction package. Clean environment reconstruction and verdict semantics remain proposed. | Inferred from GY-E03, GY-E04, and GY-E07. |
| LAP-05 Candidate Evaluation Manager | Imported and calculated parameters, functions, time series, and generated tables can carry raw candidate measures. Feasibility, Pareto, and score logic remain project additions. | Partial evidence from GY-E05 and GY-E07. |
| LAP-07 Controlled Analysis Coordinator | The Python service and REST API provide the control point for extracting accepted inputs, invoking external tools, checking returned values, and committing accepted outputs. | Synthesized from GY-E01, GY-E04, and GY-E05. |
| LIN-02 Transfer Assurance Manager | Human readable records and explicit units provide useful checks. The candidate adds source revision, schema, identifier, meaning, trace, provenance, and baseline verification before acceptance. | Proposed from the data structures in GY-E03, GY-E05, and GY-E08. |
| LIN-05 Evaluation Measurement Manager | Versioned raw observations and generated values can support the common measurement protocol. The fixed manifest and correctness gates remain project additions. | Proposed from GY-E03, GY-E05, and GY-E07. |

All 18 logical components from `FrameworkLogicalDecomposition` occur once across these three nodes.

## Step 7: minimum physical nodes and components

### GY-PN-01 Browser Client Physical Node

The participant device and operating system remain abstract. The sources establish browser access and an early Nuxt.js interface.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Participant Browser Host | Hardware or service | Inferred and unspecified | Provide a desktop or handheld environment for participant access. |
| Modern Web Browser | Software | Reported design | Access the candidate without a specialized participant application. |
| Nuxt and Tailwind Engineering Interface | Software | Reported implementation | Present hierarchy, entities, parameters, search, context, change state, generated views, requests, and review information. The proof of concept covers only part of this responsibility. |

### GY-PN-02 Git and YAML Engineering Data Service Physical Node

This node combines the reported lightweight web service design with the demonstrated docs as code records and generation workflow. Exact local or cloud deployment remains open.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Engineering Data Service Host | Hardware or service | Reported deployment choice, sizing unspecified | Host the web service, Git working repository, render jobs, and notification integration locally or in the cloud. |
| Python Engineering Data Backend | Software | Reported early implementation | Serve engineering records, apply approved updates, expose workflow state, and coordinate repository operations. |
| Engineering Data REST API | Software interface | Reported design | Provide documented access for the browser, model adapter, analysis adapter, and automation. |
| Git Version Control Service | Software | Reported design and demonstrated workflow | Record author, time, differences, branches, merges, tags, and release history for native candidate records. |
| YAML Engineering Record Set | Persistent model data | Reported design and demonstrated implementation | Store normalized entities, typed parameters, source links, needs, cases, component records, traces, assumptions, and analysis references in human and machine readable form. |
| Record Schema and Workflow Definitions | Persistent data | Synthesized | Define required identifiers, value types, units, parameter states, trace types, review states, and release rules. |
| Docs as Code Generator | Software | Reported implementation pattern | Generate diagrams, tables, reports, review packages, and procedure documents from accepted YAML records. |
| Generated Engineering View Set | Persistent data | Reported implementation pattern | Retain generated human readable views tied to the source revision that produced them. |
| Issue and Notification Integration | Software | Reported design and demonstrated workflow pattern | Connect changes and generated architecture content to issue tracking and team notifications. |

### GY-PN-03 Model and Analysis Integration Runner Physical Node

The literature supports the API integration pattern. The assurance and evidence components are explicit additions required by the framework specification.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Integration Runner Host | Hardware or service | Inferred and unspecified | Execute adapters, validation, impact analysis, controlled analyses, and evidence packaging in a declared environment. |
| External Model Record Adapter | Software | Proposed | Read designated records from the external Versioned System Model, preserve their source identity, map them to YAML records, and return only approved updates through IF-04. |
| External Analysis Tool Adapter | Software | Reported API pattern, implementation proposed | Build controlled requests from accepted records and correlate returned raw results through IF-05. |
| Evidence Repository Adapter | Software | Proposed | Export and retrieve controlled evidence packages through IF-06. |
| YAML Schema and Stable Identity Validator | Software | Proposed from reported structures | Check schema, stable identifiers, types, units, references, trace targets, and component dependency declarations. |
| Transfer and Consistency Checker | Software | Proposed | Check source revision, evidence baseline, completeness, semantic compatibility, provenance, and applicable traces before accepting a transfer. |
| Dependency and Change Impact Analyzer | Software | Synthesized | Combine Git differences, trace links, parameter dependencies, component dependencies, and generation dependencies to identify affected evidence. |
| Reproducible Analysis Packager | Software and persistent data | Proposed | Retain accepted inputs, scripts, dependency versions, environment declarations, raw outputs, tolerances, uncertainty, and execution status. |
| Evaluation Manifest Runner | Software | Proposed | Apply the fixed candidate evaluation manifest and preserve raw observations and correctness gates. |

### GY-PC-01 Candidate operating procedures

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Branch, Review, Merge, and Release Procedure | Procedure | Synthesized from reported Git workflows | Create a controlled change, review differences and generated effects, approve or reject it, and identify an accepted release revision. |
| External Artifact Import and Acceptance Procedure | Procedure | Proposed | Register the external source and revision, map it to native records, run transfer checks, retain discrepancies, and accept only a verified projection. |
| Controlled Analysis and Reproduction Procedure | Procedure | Proposed from reported API and version control patterns | Build a locked execution package, invoke a designated external analysis, verify returned records, and repeat it from a clean declared environment. |
| Generated View and Finding Review Procedure | Procedure | Synthesized | Generate review views from one source revision, record findings through the issue workflow, and retain dispositions against the released baseline. |
| Evidence Release, Export, and Restore Procedure | Procedure | Proposed | Package source records, mappings, generated views, analyses, discrepancies, findings, and environment declarations for external custody and later reconstruction. |

## Associated external environment

These resources remain outside the framework boundary.

| External resource | Candidate use |
|---|---|
| Versioned System Model | Hold authoritative external requirement sets and generic, tailored, and candidate EPS model revisions. |
| RM and MD capabilities | Author native requirements and models. The candidate imports designated records through the model adapter. |
| Analysis Tools | Execute domain analyses requested through the REST integration layer. |
| Evidence Repository | Retain accepted baseline and evidence packages exported by the candidate. |
| Team identity and communication services | Supply authentication, issue notifications, and discussion channels where selected. |

## Boundary and feasibility observations

1. The candidate's Git and YAML repository is an internal normalized working record set. It does not replace the authoritative external Versioned System Model or the external Evidence Repository.
2. The lightweight engineering data tool is a design and early proof of concept. Its REST API, Git storage, workflow, and production deployment require implementation and validation.
3. The SeaLion source demonstrates Git hosted YAML architecture records and generated documents. It does not demonstrate this report's complete evidence chain, reproduction, discrepancy, or evaluation semantics.
4. The lightweight source explicitly leaves requirements, test, and risk management outside its initial scope. This candidate must add the missing record schemas and workflows or fail the applicable mandatory requirements.
5. Git history supports change traceability. A controlled evidence baseline also requires protected release rules, complete environment declarations, accepted external artifact registrations, and reconstruction tests.
6. YAML provides readable and transferable records. Schema validation, stable identifiers, quantity types, units, controlled vocabularies, and reference integrity are required to prevent semantic drift.
7. The sources do not demonstrate a bidirectional adapter to SysML, Capella, or another formal architecture model. IF-04 interoperability is a major feasibility risk.
8. The sources propose API based analysis integration. They do not demonstrate independent reconstruction of a multidisciplinary analysis from a clean environment.
9. Reviewer permissions, finding disposition, blinded discrepancy testing, authentication, authorization, backup, concurrency, merge conflict resolution, and cybersecurity remain unspecified.
10. Generated documents are derived views. Candidate acceptance must use the controlled source records and their exact generator and environment versions.
11. The candidate's native artifacts remain Git and YAML records. The accompanying SysML v2 model is the common OOSEM comparison description required by MC-01.
12. No detailed geometric model is needed for this software centered candidate at this stage. Hardware and hosting stay abstract until they affect cost, reconstruction, security, or performance.

## SysML artifact

The corresponding simple model is:

`final_report/models/framework-candidate-git-yaml.sysml`

Generated views are available in SVG, PNG, and PDF:

- `final_report/figures/sysml/git-yaml-candidate-node-logical-general.*`
- `final_report/figures/sysml/git-yaml-candidate-physical-general.*`
