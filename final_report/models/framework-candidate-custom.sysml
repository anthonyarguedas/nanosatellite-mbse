// Minimal OOSEM steps 6 and 7 model for the custom CSRM digital thread candidate.
package FrameworkCandidateCustom {
    private import FrameworkBlackBoxSpecification
            ::'Specified Nanosatellite EPS Engineering Framework';
    private import FrameworkLogicalDecomposition::*;

    doc
    /* This package defines a literature grounded custom candidate built around a CSRM semantic
     * foundation, native textual SysML v2 interoperability, Python analysis orchestration, and an
     * NVIDIA Omniverse and Isaac integration surface. It contains only the logical node distribution
     * and minimum physical component inventory. It deliberately defers logical-to-physical
     * allocations, requirement satisfaction, and measured performance.
     *
     * Evidence basis:
     * - Kaslow, Cahill, and Frank, Developing a CubeSat System MBSE Reference Model - Interim
     *   Status #5, PDF pages 1-6, citation-2362.
     * - Kaslow et al., Integrated MBSE Applied to the Simulation of a CubeSat Mission, PDF pages
     *   4-13, review-1563.
     * - Luccisano et al., Open-Source Data Formalization through MBSE for Concurrent Preliminary
     *   Design of CubeSats, PDF pages 3 and 14-21, review-0602.
     * - El Hachimi et al., A Framework for Sizing, Designing, and Testing of Electrical Power System
     *   for Nanosatellites, PDF pages 1-18, handpicked-0003.
     * - Zhu et al., Towards Intelligent Systems for Battery Management: A Five-Tier Digital Twin
     *   Architecture, PDF pages 2-9, handpicked-0001.
     * - Janiak and Cristiano, Physics-Based Digital Twins for Co-Simulation, PDF pages 8-24,
     *   handpicked-0002.
     * - Casado et al., Implementation of a 6U CubeSat Electrical Power System Digital Twin, PDF
     *   pages 2-14, review-0573.
     * - Rostamnia, Pettinari, and Pelliccione, Digital Twin Models for Space Robotics: Objectives,
     *   Applications, and Challenges, PDF pages 7-8 and 14-18, psr-0024.
     *
     * The candidate preserves the black-box boundary. Requirements-management and model-development
     * tools populate the external Versioned System Model through IF-04. External simulation and
     * analysis tools execute through IF-05. The external Evidence Repository retains packages
     * through IF-06. Candidate-owned adapters and extensions may execute inside those tool hosts,
     * while the authoritative source identity and acceptance decision remain with the framework.
     *
     * The cited CSRM is a SysML v1 graphical model distributed through a foundational model, web
     * publication, and XMI. Translation of its reusable semantics into a native textual SysML v2
     * library is a proposed development item in this candidate. The complete combination of CSRM,
     * SysML v2, Python, Omniverse, Isaac, and battery co-simulation has not been demonstrated by one
     * source and is explicitly a synthesized architecture hypothesis.
     */

    // Step 6: logical node distribution.

    part def 'Custom Candidate Logical Node' {
        doc
        /* Responsibility and distribution partition for the custom candidate. These definitions
         * remain independent of detailed hosting, repository, solver, and transport products.
         */
    }

    part def <'CDT-LN-01'> 'Collaborative Decision and Review Logical Node'
        :> 'Custom Candidate Logical Node' {
        doc
        /* Groups participant exchanges and review authority around controlled textual views,
         * evidence packages, and optional OpenUSD scene views. OpenUSD and Omniverse support shared
         * 3D workflows. The framework retains authority for reviewer findings and disposition
         * control through candidate-specific records.
         */

        part missionApplicationInterface : 'Mission Application Interface Manager';
        part researchGovernanceInterface : 'Research Governance Interface Manager';
        part independentReviewInterface : 'Independent Review Interface Manager';
        part designReviewManager : 'Design Review Manager';
    }

    part def <'CDT-LN-02'> 'Reference Model Configuration and Evidence Logical Node'
        :> 'Custom Candidate Logical Node' {
        doc
        /* Groups CSRM tailoring, model exchange, evidence-chain continuity, controlled case and
         * baseline identity, change impact, workflow state, provenance, and repository custody.
         * CSRM supplies the reusable logical foundation. The SysML v2 gateway and configuration
         * records are proposed candidate realizations.
         */

        part modelControlInterface : 'Model Control Interface Manager';
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager';

        part evidenceChainManager : 'Evidence Chain Manager';
        part caseConfigurationManager : 'Case Configuration Manager';
        part designChangeAssessmentManager : 'Design Change Assessment Manager';

        part workflowControlManager : 'Workflow Control Manager';
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager';
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager';
    }

    part def <'CDT-LN-03'> 'Analysis Twin and Assurance Logical Node'
        :> 'Custom Candidate Logical Node' {
        doc
        /* Groups controlled Python analysis exchanges, reproduction, EPS candidate evaluation,
         * transfer assurance, measurement, and the optional Omniverse and Isaac simulation view.
         * Detailed domain solvers remain external SA capabilities. This node controls their inputs,
         * outputs, mappings, execution identity, and evidence.
         */

        part analysisExecutionInterface : 'Analysis Execution Interface Manager';

        part analysisReproductionManager : 'Analysis Reproduction Manager';
        part candidateEvaluationManager : 'Candidate Evaluation Manager';
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator';

        part transferAssuranceManager : 'Transfer Assurance Manager';
        part evaluationMeasurementManager : 'Evaluation Measurement Manager';
    }

    part def <'CDT-NL-00'> 'CSRM Digital Thread Candidate Node Logical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Separate node-logical decomposition of the complete framework black box. All eighteen
         * logical components from LA-00 occur once across the three logical nodes.
         */

        part collaborativeDecisionAndReview
            : 'Collaborative Decision and Review Logical Node';
        part referenceModelConfigurationAndEvidence
            : 'Reference Model Configuration and Evidence Logical Node';
        part analysisTwinAndAssurance : 'Analysis Twin and Assurance Logical Node';
    }

    // Step 7: minimum physical component inventory.

    part def 'Custom Candidate Physical Component' {
        doc
        /* High-level implementation component retained only when it distinguishes the candidate or
         * identifies a required candidate development item.
         */
    }

    part def 'Custom Candidate Software Component' :> 'Custom Candidate Physical Component';

    part def 'Custom Candidate Data Component' :> 'Custom Candidate Physical Component';

    part def 'Custom Candidate Hardware or Service Component'
        :> 'Custom Candidate Physical Component';

    part def 'Custom Candidate Procedure Component' :> 'Custom Candidate Physical Component';

    // CSRM and SysML v2 model gateway.

    part def 'Model Gateway Compute Host'
        :> 'Custom Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract compute or continuous-integration resource. The operating system,
         * hosting product, and resource size remain open.
         */
    }

    part def 'Framework Command and Review Interface'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed participant interface for controlled requests, statuses, reports, findings, and
         * approvals. It may be implemented with generated web views, repository review views, or a
         * lightweight client without changing the logical allocation.
         */
    }

    part def 'CSRM Semantic Reference Library' :> 'Custom Candidate Data Component' {
        doc
        /* Reported semantic basis with proposed realization. The cited CSRM supplies reusable
         * requirements, architecture, stakeholder, technical-measure, use-case, verification, and
         * validation concepts. This candidate translates and profiles the required subset as a
         * textual SysML v2 library while retaining source provenance and explicit tailoring.
         */
    }

    part def 'SysML v2 Model API and Text Adapter'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed. Reads, validates, queries, and writes approved textual SysML v2 elements through
         * a conformant parser or model API. It preserves stable identifiers and refuses direct
         * updates that lack an accepted case and baseline context.
         */
    }

    part def 'Requirements Management Interoperability Adapter'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed from the CSRM requirement hierarchy and the reported parser pattern. Exchanges
         * requirement sets, identifiers, text, verification relations, status, and provenance with
         * external RM capabilities through IF-04.
         */
    }

    part def 'Model Development Interoperability Adapter'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed from CSRM mission-specific tailoring and model-parser evidence. Exchanges generic,
         * tailored, and candidate structures, behavior, interfaces, properties, and traces with
         * external MD capabilities through IF-04.
         */
    }

    part def 'Stable Identity Trace and Mapping Registry'
        :> 'Custom Candidate Data Component' {
        doc
        /* Synthesized assurance component. Records stable semantic identifiers and explicit mappings
         * among CSRM and SysML v2 elements, external requirements and models, analysis variables,
         * OpenUSD prims, verification criteria, and returned evidence.
         */
    }

    part def 'Version Control and Baseline Client'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed. Resolves immutable source revisions and approved configuration manifests in the
         * external Versioned System Model and Evidence Repository. The specific version-control
         * product remains open.
         */
    }

    part def <'CDT-PN-01'> 'CSRM and SysML v2 Model Gateway Physical Node' {
        doc
        /* Candidate-owned gateway for CSRM semantics, textual SysML v2 exchanges, stable identity,
         * and participant review. The authoritative mission model remains the external Versioned
         * System Model defined by the black-box context.
         */

        part host : 'Model Gateway Compute Host';
        part commandAndReview : 'Framework Command and Review Interface';
        part csrmLibrary : 'CSRM Semantic Reference Library';
        part sysmlAdapter : 'SysML v2 Model API and Text Adapter';
        part requirementsAdapter : 'Requirements Management Interoperability Adapter';
        part modelDevelopmentAdapter : 'Model Development Interoperability Adapter';
        part identityRegistry : 'Stable Identity Trace and Mapping Registry';
        part baselineClient : 'Version Control and Baseline Client';
    }

    // Python digital thread and controlled analysis runner.

    part def 'Python Runner Compute Host'
        :> 'Custom Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract compute resource for orchestration and evidence services. Packaging,
         * operating system, execution isolation, and resource sizing remain unspecified.
         */
    }

    part def 'Locked Python Runtime and Environment'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed. Executes candidate services from a declared dependency and environment lock so
         * that a designated baseline can be reconstructed and rerun.
         */
    }

    part def 'Controlled Workflow Orchestrator'
        :> 'Custom Candidate Software Component' {
        doc
        /* Synthesized from reported SysML-to-analysis bridges and Python parser workflows. Dispatches
         * accepted work, records execution identity, applies terminal guards, and prevents unverified
         * results from replacing controlled content.
         */
    }

    part def 'Simulation and Analysis Adapter Registry'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed extensibility point for external orbit, power-budget, circuit, thermal, battery,
         * robotics, optimization, and HIL tools. Each adapter declares its input and output schema,
         * version, units, assumptions, and execution requirements.
         */
    }

    part def 'Analysis Request and Result Bridge'
        :> 'Custom Candidate Software Component' {
        doc
        /* Reported integration pattern with proposed SysML v2 implementation. Builds controlled SA
         * requests from accepted model properties and correlates raw returned results to the request,
         * solver, environment, source revision, and declared tolerances through IF-05.
         */
    }

    part def 'Dependency and Change Impact Analyzer'
        :> 'Custom Candidate Software Component' {
        doc
        /* Reported Python-parser pattern with proposed CSRM and SysML v2 implementation. Uses model
         * dependencies and trace mappings to identify affected artifacts, analyses, requirements,
         * scenes, and evidence after a controlled change.
         */
    }

    part def 'Transfer and Semantic Checker' :> 'Custom Candidate Software Component' {
        doc
        /* Proposed from reported interoperability risks and space-DT assurance principles. Checks
         * source and baseline identity, schema, identifiers, quantities, units, meanings, mappings,
         * provenance, traces, and synchronization status before accepting a transfer.
         */
    }

    part def 'Evidence and Provenance Packager'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed. Packages accepted models, mappings, environment declarations, inputs, raw
         * results, uncertainty, discrepancies, verification evidence, and decision context for IF-06.
         */
    }

    part def 'Evaluation Manifest Runner' :> 'Custom Candidate Software Component' {
        doc
        /* Proposed. Applies the fixed framework evaluation manifest and preserves observations,
         * correctness gates, uncertainty, and MOP inputs under the common comparison protocol.
         */
    }

    part def 'Typed Analysis Exchange Package' :> 'Custom Candidate Data Component' {
        doc
        /* Proposed normalization of the software-readable data structures demonstrated in the
         * literature. Carries typed inputs, outputs, units, assumptions, mappings, execution status,
         * and raw results. The external source and accepted baseline retain authority.
         */
    }

    part def <'CDT-PN-02'> 'Python Digital Thread and Analysis Runner Physical Node' {
        doc
        /* Candidate-owned orchestration spine. Detailed engineering calculations remain in external
         * SA tools, while this node controls their exchange, execution identity, impact analysis,
         * acceptance checks, and evidence packaging.
         */

        part host : 'Python Runner Compute Host';
        part runtime : 'Locked Python Runtime and Environment';
        part workflow : 'Controlled Workflow Orchestrator';
        part adapterRegistry : 'Simulation and Analysis Adapter Registry';
        part analysisBridge : 'Analysis Request and Result Bridge';
        part impactAnalyzer : 'Dependency and Change Impact Analyzer';
        part transferChecker : 'Transfer and Semantic Checker';
        part evidencePackager : 'Evidence and Provenance Packager';
        part evaluationRunner : 'Evaluation Manifest Runner';
        part exchangePackage : 'Typed Analysis Exchange Package';
    }

    // Omniverse, OpenUSD, Isaac, and battery-aware V&V integration.

    part def 'Omniverse Integration Compute Host'
        :> 'Custom Candidate Hardware or Service Component' {
        doc
        /* Inferred GPU-capable host or service for the candidate extensions and controlled scene
         * sessions. Exact GPU, memory, operating system, license, and service requirements remain
         * unspecified and must enter later cost and adoption evaluation.
         */
    }

    part def 'Omniverse Kit Collaboration Extension'
        :> 'Custom Candidate Software Component' {
        doc
        /* Reported extension mechanism with proposed candidate implementation. Presents controlled
         * model identity, simulation results, review overlays, findings, and approval status in an
         * OpenUSD-based collaborative view. The textual SysML v2 model retains semantic authority.
         */
    }

    part def 'Controlled OpenUSD Twin Package' :> 'Custom Candidate Data Component' {
        doc
        /* Synthesized from OpenUSD and battery-DT evidence. Contains versioned scene layers,
         * geometry references, units, coordinate frames, semantic identifiers, data bindings,
         * scenario references, and accepted review state tied to one evidence baseline.
         */
    }

    part def 'SysML v2 to OpenUSD Semantic Bridge'
        :> 'Custom Candidate Software Component' {
        doc
        /* Proposed. Maps approved CSRM and SysML v2 structure, properties, interfaces, and stable
         * identifiers to OpenUSD prims and metadata. It records lossy or unsupported transformations
         * as discrepancies and never treats geometry as a replacement for system semantics.
         */
    }

    part def 'Isaac Sim Controlled Scenario Adapter'
        :> 'Custom Candidate Software Component' {
        doc
        /* Synthesized from reported Isaac visualization, robot simulation, and simulation-first
         * use cases. Configures reproducible robotic scenarios and returns time-stamped states,
         * actions, contacts, modes, and power-demand traces through the controlled analysis bridge.
         */
    }

    part def 'FMI and FMU Co-Simulation Bridge'
        :> 'Custom Candidate Software Component' {
        doc
        /* Reported proof-of-concept pattern with proposed CubeSat application. Couples tool-neutral
         * dynamic models to an OpenUSD or Isaac scenario. The cited USD-FMI integration remains an
         * MVP and in-progress standardization effort, so conformance and performance are unverified.
         */
    }

    part def 'EPS and Battery Model Connector'
        :> 'Custom Candidate Software Component' {
        doc
        /* Synthesized from CubeSat EPS, battery-DT, Python, and HIL evidence. Exchanges load and
         * environment histories with external power-budget, circuit, electrothermal, degradation,
         * or real-time EPS models and returns generated power, bus state, SOC or DoD, temperature,
         * health, uncertainty, and available-power limits.
         */
    }

    part def 'Telemetry and Simulation Data Binder'
        :> 'Custom Candidate Software Component' {
        doc
        /* Reported battery-DT pattern with proposed CubeSat semantics. Binds measured, simulated,
         * estimated, and predicted values to model and scene identities with explicit topics, update
         * rates, data types, units, timestamps, and source baselines.
         */
    }

    part def 'Battery-Aware Verification Scenario Library'
        :> 'Custom Candidate Data Component' {
        doc
        /* Proposed. Defines controlled pre-physical scenarios for eclipse, peak payload demand,
         * communication, deployment, safe mode, thermal extremes, degraded generation, protection,
         * robotic duty cycles, and energy-limited task planning with declared requirements and
         * verdict criteria.
         */
    }

    part def 'Simulation Evidence Collector' :> 'Custom Candidate Software Component' {
        doc
        /* Proposed. Collects scenario configuration, solver and seed identity, time histories, raw
         * outputs, uncertainty, requirement verdicts, scene snapshots, discrepancies, and execution
         * logs without replacing the external evidence repository.
         */
    }

    part def <'CDT-PN-03'> 'Omniverse and Isaac Interoperability Physical Node' {
        doc
        /* Candidate extensions and controlled data deployed with the external Omniverse and Isaac
         * environment. Omniverse supplies spatial collaboration and visualization. Isaac supplies a
         * robotics scenario environment. Specialized EPS, orbit, circuit, thermal, and battery
         * solvers remain external SA capabilities connected through Python or FMI adapters.
         */

        part host : 'Omniverse Integration Compute Host';
        part collaborationExtension : 'Omniverse Kit Collaboration Extension';
        part twinPackage : 'Controlled OpenUSD Twin Package';
        part semanticBridge : 'SysML v2 to OpenUSD Semantic Bridge';
        part isaacAdapter : 'Isaac Sim Controlled Scenario Adapter';
        part fmiBridge : 'FMI and FMU Co-Simulation Bridge';
        part epsBatteryConnector : 'EPS and Battery Model Connector';
        part dataBinder : 'Telemetry and Simulation Data Binder';
        part scenarioLibrary : 'Battery-Aware Verification Scenario Library';
        part evidenceCollector : 'Simulation Evidence Collector';
    }

    // Candidate operating procedures.

    part def 'CSRM Tailoring and Model Acceptance Procedure'
        :> 'Custom Candidate Procedure Component' {
        doc
        /* Synthesized from CSRM mission-specific application and model-parser evidence. Selects the
         * CSRM subset, records adaptations, validates identifiers and traces, and accepts RM and MD
         * artifacts into a controlled case baseline.
         */
    }

    part def 'Controlled Analysis Execution and Reproduction Procedure'
        :> 'Custom Candidate Procedure Component' {
        doc
        /* Synthesized from integrated CubeSat analysis and open-source parser patterns. Creates a
         * locked execution package, invokes designated external SA tools, verifies transfers, and
         * repeats the run from a clean declared environment.
         */
    }

    part def 'SysML and OpenUSD Synchronization Procedure'
        :> 'Custom Candidate Procedure Component' {
        doc
        /* Proposed. Generates an OpenUSD view from an accepted model baseline, checks every semantic
         * mapping, records discrepancies, and permits reverse changes only through an approved model
         * change request.
         */
    }

    part def 'Battery-Aware Pre-Physical Verification Procedure'
        :> 'Custom Candidate Procedure Component' {
        doc
        /* Proposed synthesis. Runs controlled mission and robotic scenarios, couples action-derived
         * loads to an external EPS or battery model, returns available-power and health constraints,
         * checks requirement tolerances, and retains raw evidence before physical integration.
         */
    }

    part def 'Baseline Release and Collaborative Review Procedure'
        :> 'Custom Candidate Procedure Component' {
        doc
        /* Proposed. Binds model, mapping, scene, scenario, environment, result, uncertainty,
         * discrepancy, finding, and verdict records to one baseline and releases a review package to
         * the external evidence repository.
         */
    }

    part def <'CDT-PC-01'> 'Custom Candidate Operating Procedures' {
        part tailorAndAcceptModel : 'CSRM Tailoring and Model Acceptance Procedure';
        part executeAndReproduceAnalysis
            : 'Controlled Analysis Execution and Reproduction Procedure';
        part synchronizeSysMLAndOpenUSD : 'SysML and OpenUSD Synchronization Procedure';
        part verifyBatteryAwareScenarios : 'Battery-Aware Pre-Physical Verification Procedure';
        part releaseAndReviewBaseline : 'Baseline Release and Collaborative Review Procedure';
    }

    part def <'CDT-PA-00'> 'CSRM Digital Thread Candidate Physical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Minimum physical decomposition for comparison. Explicit logical-to-physical allocations,
         * ports, connectors, physical service activities, satisfy relationships, and measured MOPs
         * are intentionally deferred to the next OOSEM steps.
         */

        part modelGateway : 'CSRM and SysML v2 Model Gateway Physical Node';
        part pythonRunner : 'Python Digital Thread and Analysis Runner Physical Node';
        part omniverseGateway : 'Omniverse and Isaac Interoperability Physical Node';
        part operatingProcedures : 'Custom Candidate Operating Procedures';
    }

    part customCandidateNodeLogical : 'CSRM Digital Thread Candidate Node Logical Framework';
    part customCandidatePhysical : 'CSRM Digital Thread Candidate Physical Framework';
} // package FrameworkCandidateCustom
