# COMET centered candidate: OOSEM steps 6 and 7

## Scope

This is a deliberately small candidate model. It performs:

- Step 6: define the candidate logical node distribution.
- Step 7: define the minimum physical nodes and components.

It defers logical to physical allocations, requirement satisfaction, and measured performance to the following synthesis and evaluation steps.

The candidate preserves the system boundary in `final_report/final_report.tex`. The Versioned System Model, Analysis Tools, and Evidence Repository remain external to the framework. COMET provides the central concurrent engineering workspace for shared parameters, reference data, requirements, study configuration, and near real time collaboration. A separate integration and assurance runner connects the external authoritative model, COMET, external analysis tools, and the evidence repository.

The main literature configuration combines COMET, ECSS-E-TM-10-25A data semantics, and a CubeSat model architecture derived from the CubeSat System Reference Model (CSRM). It uses a reusable Template Model, a parts Model Catalogue, and a mission-specific Study Model. This candidate treats the external Versioned System Model as the architecture and requirement authority. COMET holds a synchronized concurrent engineering representation and the candidate study data. That authority split is a proposed adaptation required by the current framework boundary.

The candidate is described separately in textual SysML v2 under MC-01. Its native implementation and native COMET artifacts do not need to use SysML v2 or the OOSEM study repository.

## Evidence basis

The evidence was located with `embeddings/search.py` and checked in the source Markdown and architecture figures.

| ID | Extracted evidence | Source |
|---|---|---|
| COM-E01 | COMET is reported as open source concurrent engineering software implementing ECSS-E-TM-10-25A. Its three integral parts are a server that stores models, users, and reference data, a Microsoft Excel add-in for calculations and analysis, and a stand-alone Integrated Modeling Environment (IME) for administration and preparation. Regular client-server synchronization supports near real time collaboration. | Deutsch, Hoffmann, and Bertrand, *Development of a Concurrent Engineering Tutorial as part of the ESA_Lab@ initiative* (2022), PDF p. 3, `review-0876`. |
| COM-E02 | ECSS-E-TM-10-25A supplies common data definitions and an equipment-level decomposition for conceptual design. The source also states that this decomposition is intentionally limited to phases 0 and A. | Deutsch et al. (2022), PDF p. 3, `review-0876`. |
| COM-E03 | The reported CubeSat COMET architecture contains a reusable Template Model, a Model Catalogue of parts and equipment, and a Study Model created from the template as its source model. | Deutsch et al. (2022), PDF pp. 4 to 5, `review-0876`. |
| COM-E04 | The study maps CSRM subsystem components into COMET Categories and the ECSS Equipment super-category. These categories are stored in the server Site Directory and can be assigned to model elements. The authors present this as a bridge between CSRM and ECSS semantics. | Deutsch et al. (2022), PDF pp. 4 and 6, `review-0876`. |
| COM-E05 | The Template Model defines Domains of Expertise and owners, a product tree for space, ground, and launch segments, grouped system and subsystem parameters, and owner responsibility for values and equipment. These data support subsystem mass and power budgets. | Deutsch et al. (2022), PDF pp. 4 to 5, `review-0876`. |
| COM-E06 | COMET finite state lists support state-dependent parameters. The Template Model also integrates requirements, links them to model elements and parameters, and supports automated compliance checks for numerical requirements. | Deutsch et al. (2022), PDF p. 5, `review-0876`. |
| COM-E07 | The Model Catalogue contains specific COTS parts and assemblies with linked data sheets and generic equipment definitions with unvalued parameters. Users can copy catalogue elements into a Study Model. | Deutsch et al. (2022), PDF p. 5, `review-0876`. |
| COM-E08 | A student pilot applied the architecture to an active CubeSat project and evaluated the applicability of the Template Model and usefulness of the Model Catalogue. The paper reports a positive conclusion, while providing no measurements comparable to this project's MOP protocol. | Deutsch et al. (2022), PDF pp. 5 to 6, `review-0876`. |
| COM-E09 | CSRM provides a reusable CubeSat space and ground logical architecture that mission teams tailor into mission-specific logical and physical architectures. It includes requirements, architecture, stakeholders, technical measures, use cases, and verification and validation relationships. | Kaslow, Cahill, and Frank, *Developing a CubeSat System MBSE Reference Model: Interim Status #5*, PDF pp. 1 to 6, `citation-2362`. |
| COM-E10 | A related ECSS concurrent engineering tool, OCDT, exposes a generic REST API for exchange with external calculations. This supports the general integration pattern, but it does not establish that the selected COMET configuration exposes the same API. The COMET exchange adapter therefore remains proposed. | Fischer et al., *Spacecraft Interface Management in Concurrent Engineering Sessions* (2019), PDF p. 3, `review-1277`. |
| COM-E11 | A later small satellite study classifies COMET among informal engineering data platforms and warns that MBSE setup and maintenance effort can outweigh benefits for small teams. It motivates explicit measurement of adoption effort and direct cost. | Kanavouras, Bühler, and Hein, *Building a Lightweight Data Management Tool for Small Satellite Missions* (2024), PDF pp. 1 to 4, `review-0522`. |

Evidence classifications used below:

- **Reported:** stated directly in a cited source or visible in its architecture figures.
- **Synthesized:** combines compatible elements reported across sources.
- **Inferred:** necessary architectural interpretation of reported behavior.
- **Proposed:** added to make the literature configuration address this project's black-box baseline.
- **Unspecified:** required implementation detail that the selected sources do not establish.

## Step 6: candidate logical node distribution

The logical distribution separates participant collaboration, engineering model and configuration control, and analysis and assurance. Detailed products and deployment choices appear in Step 7.

### COM-LN-01 Concurrent Participant Access Logical Node

Purpose: mediate mission team, researcher, and reviewer interactions through synchronized COMET client views and controlled review products.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-01 Mission Application Interface Manager | COMET clients provide synchronized access for domain participants working on one shared study model. | Reported and synthesized from COM-E01 and COM-E05. |
| LIF-02 Research Governance Interface Manager | The reusable Template Model, Model Catalogue, reference data, and Study Model provide a plausible surface for researchers to inspect and extend the method. | Inferred from COM-E03, COM-E04, COM-E07, and COM-E08. |
| LIF-03 Independent Review Interface Manager | Remotely accessible models, requirement checks, and exported evidence can support review. Reviewer-specific permissions, findings, and disposition behavior remain unreported. | Partial evidence from COM-E01, COM-E06, and COM-E08. The review workflow is proposed. |
| LAP-06 Design Review Manager | Product trees, parameter ownership, budgets, requirement links, and compliance results can be assembled into a review package. | Partial evidence from COM-E05 and COM-E06. Findings control is proposed. |

### COM-LN-02 Engineering Model and Configuration Logical Node

Purpose: manage the reusable template, mission-specific study configuration, shared semantic definitions, requirements, changes, and retained engineering records around the COMET server.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-04 Model Control Interface Manager | A model adapter synchronizes accepted architecture and requirement records between the external Versioned System Model and the COMET Study Model. | CSRM and ECSS mapping patterns are reported in COM-E04 and COM-E09. The external-model adapter is proposed. |
| LAP-01 Evidence Chain Manager | Requirement links, parameter ownership, reference data, catalogue sources, and compliance records provide evidence-chain inputs. Complete provenance and chain-validity semantics remain unreported. | Partial evidence from COM-E04 through COM-E07. |
| LAP-02 Case Configuration Manager | A Study Model is instantiated from a reusable Template Model and populated from a categorized Model Catalogue. | Reported in COM-E03 and COM-E07. Approved adaptation and baseline semantics are proposed. |
| LAP-04 Design Change Assessment Manager | Client-server synchronization exposes changed shared values and model records. The candidate adds dependency and impact checks before accepting a successor configuration. | Synchronization is reported in COM-E01. Complete impact analysis is proposed. |
| LIN-01 Workflow Control Manager | Domains of Expertise, ownership, a system engineer moderator, and iterative concurrent sessions provide the reported workflow-control pattern. | Reported in COM-E01, COM-E05, and COM-E08. |
| LIN-03 Baseline and Configuration Manager | The server stores models, users, reference data, categories, templates, catalogues, and study models. Immutable release and source-revision semantics remain unreported. | Reported storage and model structure from COM-E01, COM-E03, and COM-E04. |
| LIN-04 Evidence and Provenance Manager | The model retains requirements, parameters, owners, catalogue definitions, linked data sheets, and compliance records. Complete external artifact provenance and evidence custody remain proposed. | Partial evidence from COM-E05 through COM-E07. |

### COM-LN-03 Analysis, Compliance, and Assurance Logical Node

Purpose: coordinate calculations and external analyses, verify exchanges, evaluate EPS candidates, and package controlled results for external evidence custody.

| Logical component | Placement rationale | Evidence status |
|---|---|---|
| LIF-05 Analysis Execution Interface Manager | The COMET Excel add-in supports parameter calculations and analysis. Candidate adapters extend this interface to other external analysis tools. | Reported core from COM-E01. Other tool adapters are proposed. |
| LIF-06 Evidence Custody Interface Manager | An adapter submits and retrieves controlled packages through the external Evidence Repository. | Proposed. The selected COMET sources do not establish this interface. |
| LAP-03 Analysis Reproduction Manager | Shared parameters, formulas, states, catalogue selections, and requirements can define a repeatable calculation case. Clean environment reconstruction and reproduction verdicts remain unreported. | Partial evidence from COM-E01 and COM-E05 through COM-E07. |
| LAP-05 Candidate Evaluation Manager | Model Catalogue alternatives, state-dependent parameters, mass and power budgets, and compliance checks support early candidate assessment. | Reported analysis inputs from COM-E05 through COM-E07. The common feasibility, Pareto, and score protocol is proposed. |
| LAP-07 Controlled Analysis Coordinator | Client synchronization and the Excel add-in provide the reported coordination core for shared calculations. The candidate extends this pattern to typed external requests and returned results. | Reported core from COM-E01 with proposed extension. |
| LIN-02 Transfer Assurance Manager | ECSS reference definitions and the CSRM-to-COMET category mapping provide shared semantics. The candidate adds source, baseline, completeness, identifier, unit, provenance, and trace checks. | Reported semantic basis from COM-E02, COM-E04, and COM-E09. Complete assurance behavior is proposed. |
| LIN-05 Evaluation Measurement Manager | Parameters, state-dependent values, budgets, and requirement compliance provide measurement inputs. Applying the fixed evaluation manifest and retaining raw MOP observations are proposed. | Reported inputs from COM-E05 and COM-E06 with proposed framework measurement behavior. |

All 18 logical components from `FrameworkLogicalDecomposition` occur once across these three nodes.

## Step 7: minimum physical nodes and components

### COM-PN-01 COMET Participant Client Physical Node

The paper distinguishes two COMET clients. The workstation and network deployment remain abstract.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Participant Workstation Host | Hardware or service | Inferred and unspecified | Host the candidate client applications and secure network access. |
| COMET Integrated Modeling Environment Client | Software | Reported | Perform model administration, preparation, organization, and participant model access. |
| COMET Excel Add-in | Software | Reported | Synchronize engineering parameters and support calculations and analysis from the spreadsheet client. |
| Microsoft Excel Host Application | COTS software dependency | Reported | Host the COMET add-in and the reported parameter calculations. Product version and license requirements remain open. |

### COM-PN-02 COMET Server and Engineering Model Physical Node

The source establishes a server responsibility but does not provide its database product, process topology, backup strategy, or physical deployment.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| COMET Server Compute Host | Hardware or service | Inferred and unspecified | Host the COMET server in a declared environment. |
| COMET Server Application | Software | Reported | Store and synchronize models, users, reference data, and shared study information. |
| COMET Engineering Model Repository | Persistent data | Reported at platform level | Retain the reusable and study-specific engineering models and their shared parameters. |
| Site Directory and Reference Data Set | Persistent data | Reported | Hold users, Domains of Expertise, measurement definitions, categories, and other shared reference data. |
| CSRM-to-ECSS Category Mapping Library | Persistent model data | Reported | Map selected CSRM component semantics to COMET Categories and the ECSS Equipment super-category. |
| CubeSat Template Model | Persistent model data | Reported | Provide the reusable mission, segment, subsystem, parameter, state, and requirement blueprint. |
| CubeSat Model Catalogue | Persistent model data | Reported | Hold generic equipment definitions and specific COTS parts with parameters and linked data sheets. |
| Candidate Study Model | Persistent model data | Reported | Hold the case-specific concurrent design initialized from the Template Model. |
| Requirements and Compliance Record Set | Persistent data | Reported | Retain imported and derived requirements, links to model elements, and automated numerical compliance results. |
| COMET Client Synchronization Service | Software | Inferred from reported behavior | Synchronize IME and Excel clients with the shared server model. Detailed service decomposition remains unspecified. |

### COM-PN-03 Model, Analysis, and Evidence Integration Runner Physical Node

The selected sources do not establish a COMET API or the report's complete transfer and evidence contracts. These candidate components are therefore explicit development items.

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Integration Runner Compute Host | Hardware or service | Inferred and unspecified | Execute adapters, checks, impact analysis, and evidence packaging in a declared environment. |
| External System Model Adapter | Software | Proposed | Read accepted requirements, structure, interfaces, properties, and traces from the external Versioned System Model through IF-04 and return only approved updates. |
| COMET Exchange Adapter | Software | Proposed | Map controlled exchanges to COMET server records. COM-E10 supports the standard-ecosystem pattern but does not prove a COMET REST interface. |
| External Analysis Tool Adapter | Software | Proposed from reported Excel integration | Issue typed requests to external EPS analysis tools through IF-05 and correlate returned raw results. |
| Evidence Repository Adapter | Software | Proposed | Register and retrieve controlled evidence packages through IF-06. |
| Transfer and Semantic Checker | Software | Proposed | Check source and baseline identity, schema completeness, identifiers, quantities, units, mappings, provenance, and applicable traces before accepting a transfer. |
| Change Impact and Compliance Coordinator | Software | Synthesized | Combine changed model records, parameter dependencies, requirement links, and compliance checks to identify affected evidence and analyses. |
| Evidence and Provenance Packager | Software | Proposed | Package accepted model records, COMET configuration, calculations, raw results, discrepancies, review records, and verification evidence. |
| Evaluation Manifest Runner | Software | Proposed | Apply the fixed framework evaluation manifest and preserve raw observations and correctness gates. |
| Typed Candidate Exchange Package | Persistent data | Proposed | Carry controlled model, analysis, status, uncertainty, and evidence records without replacing their authoritative sources. |

### COM-PC-01 Candidate operating procedures

| Physical component | Kind | Evidence classification | Minimal responsibility |
|---|---|---|---|
| Site and Reference Data Administration Procedure | Procedure | Reported pattern | Establish users, Domains of Expertise, ownership, units, categories, and shared reference definitions. |
| Template and Study Model Setup Procedure | Procedure | Reported | Select the Template Model as the Study Model source and record case-specific setup decisions. |
| Concurrent Engineering Session Procedure | Procedure | Reported | Synchronize domain work, moderate iterations, review shared values, and resolve cross-domain issues. |
| Catalogue Selection and Budget Procedure | Procedure | Reported | Select generic or COTS equipment, assign owners and parameters, and calculate state-dependent mass and power budgets. |
| Requirements Linking and Compliance Procedure | Procedure | Reported | Link requirements to model elements and parameters and execute applicable numerical compliance checks. |
| Model Synchronization and Transfer Review Procedure | Procedure | Synthesized | Compare external model and COMET records, inspect transfer findings, and authorize controlled updates. |
| Baseline Release and Evidence Export Procedure | Procedure | Proposed | Bind model, reference data, study configuration, calculations, discrepancies, and review records to a controlled evidence package. |
| Analysis Reproduction Procedure | Procedure | Proposed | Reconstruct the declared client, server, spreadsheet, adapter, and analysis environment and issue a reproduction package and verdict inputs. |

## Associated external environment

These resources remain outside the framework boundary.

| External resource | Candidate use |
|---|---|
| Versioned System Model | Hold the authoritative generic, tailored, and candidate architecture and requirement records and their source revisions. |
| RM and MD capabilities | Author and refine requirements, structure, behavior, interfaces, traces, and approved adaptations. |
| Analysis Tools | Execute detailed EPS, orbit, thermal, battery, optimization, and uncertainty analyses beyond the COMET and Excel calculation surface. |
| Evidence Repository | Retain accepted baselines, raw results, mappings, discrepancies, review records, and verification evidence. |

## Boundary and feasibility observations

1. COMET provides the collaborative concurrent engineering representation. The external Versioned System Model remains the architecture and requirement authority under the current black-box boundary.
2. The Template Model, Model Catalogue, and Study Model offer a strong case-configuration pattern for CubeSat preliminary design.
3. COMET and ECSS-E-TM-10-25A represent a restricted conceptual-design decomposition. They do not replace the richer behavior, interface, trace, and provenance semantics required by the external system model.
4. The CSRM-to-COMET category mapping is reported. A complete and lossless mapping from the authoritative model remains unverified.
5. The selected source establishes regular synchronization. It does not establish immutable evidence baselines, external source revision identity, complete provenance, accepted artifact registration, or clean environment reconstruction.
6. Automated requirement checks are reported for numerical properties. Semantic validity and the full set of mandatory framework requirements still require separate verification.
7. The selected COMET source does not establish a public integration API. OCDT evidence cannot be transferred to COMET without verification. The COMET Exchange Adapter is therefore a selection risk and development item.
8. The Microsoft Excel dependency may affect licenses, reproducibility, automation, and operating-system support. These properties belong in the later adoption-effort, direct-cost, and reproduction measurements.
9. Reviewer access, findings disposition, evidence export, transfer assurance, and the complete comparison protocol remain project additions.
10. The pilot supports educational usability and CubeSat applicability. It does not provide values that can replace this project's common MOP measurements.
11. No detailed geometric model is needed for this software centered candidate at this stage. Client, server, and network sizing remain abstract until they affect cost, reconstruction, security, or performance.

## SysML artifact

The corresponding simple model is:

`final_report/models/framework-candidate-comet.sysml`

Generated views are available in SVG, PNG, and PDF:

- `final_report/figures/sysml/comet-candidate-node-logical-general.*`
- `final_report/figures/sysml/comet-candidate-physical-general.*`
