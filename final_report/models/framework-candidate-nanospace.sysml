// Minimal OOSEM steps 6 and 7 model for the Nanospace centered candidate.
package FrameworkCandidateNanospace {
    private import FrameworkBlackBoxSpecification
            ::'Specified Nanosatellite EPS Engineering Framework';
    private import FrameworkLogicalDecomposition::*;

    doc
    /* This package defines a literature grounded Nanospace centered candidate.
     * It contains only the logical node distribution and minimum physical component inventory.
     * It does not yet assert logical-to-physical allocations, requirement satisfaction, or measured
     * performance.
     *
     * Evidence basis:
     * - Salas Cordero, Gateau, and Vingerhoeds (2022), MBSE Challenges in the Concurrent
     *   Preliminary Design of CubeSats: Nanospace Study, PDF pages 5-8, review-0908.
     * - Salas Cordero, Gateau, and Vingerhoeds (2025), Hierarchical Planning Applied to the
     *   Preliminary Design of CubeSats: Nanospace Study, PDF pages 6-14, review-0340.
     * - Luccisano (2024), Data Formalisation through MBSE for Concurrent Preliminary Design of
     *   CubeSats, PDF pages 31-35 and 66-79, citation-2300.
     * - Luccisano et al. (2024), Open-Source Data Formalization through Model-Based Systems
     *   Engineering for Concurrent Preliminary Design of CubeSats, PDF pages 3 and 14-21,
     *   review-0602.
     *
     * This candidate combines the reported Nanospace browser, service, graph-database, and API
     * architecture with the later model-centered MBSE formalization. The external Gaphor SysML model
     * is the engineering-data master in the reported proof of concept. Nanospace provides the
     * concurrent working database and collaboration surface. A Python runner parses and synchronizes
     * model data and coordinates external analyses. This file is the separate common SysML v2
     * comparison representation required by MC-01. Versioned System Model, Analysis Tools, and
     * Evidence Repository remain outside the framework boundary defined by the black-box context.
     */

    // Step 6: logical node distribution.

    part def 'Nanospace Candidate Logical Node' {
        doc
        /* Responsibility and distribution partition for this candidate. Node definitions remain
         * independent of detailed hosting and deployment technology.
         */
    }

    part def <'NS-LN-01'> 'Participant Web Access Logical Node'
        :> 'Nanospace Candidate Logical Node' {
        doc
        /* Groups the participant-facing interfaces around the reported browser environment.
         * Browser access, authentication, shared project responsibility, and transparent views are
         * reported by Luccisano (2024), pages 32-33. Reviewer-specific findings and disposition
         * control remain an evidence gap.
         */

        part missionApplicationInterface : 'Mission Application Interface Manager';
        part researchGovernanceInterface : 'Research Governance Interface Manager';
        part independentReviewInterface : 'Independent Review Interface Manager';
    }

    part def <'NS-LN-02'> 'Collaborative Engineering Data and Workflow Logical Node'
        :> 'Nanospace Candidate Logical Node' {
        doc
        /* Groups evidence, case configuration, review, workflow, configuration, and retained
         * engineering records around Nanospace and its graph database. Project, Component, Mode,
         * Value, User, history, requirements, and intermediate-result support are reported in the
         * selected sources. Immutable baseline and complete provenance semantics remain gaps.
         */

        part evidenceChainManager : 'Evidence Chain Manager';
        part caseConfigurationManager : 'Case Configuration Manager';
        part designReviewManager : 'Design Review Manager';

        part workflowControlManager : 'Workflow Control Manager';
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager';
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager';
    }

    part def <'NS-LN-03'> 'Model Analysis and Assurance Integration Logical Node'
        :> 'Nanospace Candidate Logical Node' {
        doc
        /* Groups model parsing, external analyses, impact assessment, candidate evaluation,
         * measurement, and controlled transfers. The model parser, API exchanges, discipline tools,
         * dependency graphs, and reverse model updates are reported by Salas Cordero et al. (2022)
         * and Luccisano et al. (2024). Evidence custody and the complete transfer contract are
         * candidate-specific additions.
         */

        part modelControlInterface : 'Model Control Interface Manager';
        part analysisExecutionInterface : 'Analysis Execution Interface Manager';
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager';

        part analysisReproductionManager : 'Analysis Reproduction Manager';
        part designChangeAssessmentManager : 'Design Change Assessment Manager';
        part candidateEvaluationManager : 'Candidate Evaluation Manager';
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator';

        part transferAssuranceManager : 'Transfer Assurance Manager';
        part evaluationMeasurementManager : 'Evaluation Measurement Manager';
    }

    part def <'NS-NL-00'> 'Nanospace Candidate Node Logical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Separate node-logical decomposition of the complete framework black box. All eighteen
         * logical components from LA-00 occur once across the three nodes.
         */

        part participantWebAccess : 'Participant Web Access Logical Node';
        part collaborativeDataAndWorkflow
            : 'Collaborative Engineering Data and Workflow Logical Node';
        part modelAnalysisAndAssurance
            : 'Model Analysis and Assurance Integration Logical Node';
    }

    // Step 7: minimum physical component inventory.

    part def 'Nanospace Candidate Physical Component' {
        doc
        /* High-level implementation component retained only when it distinguishes the candidate or
         * identifies a required candidate addition.
         */
    }

    part def 'Nanospace Candidate Software Component'
        :> 'Nanospace Candidate Physical Component';

    part def 'Nanospace Candidate Data Component'
        :> 'Nanospace Candidate Physical Component';

    part def 'Nanospace Candidate Hardware or Service Component'
        :> 'Nanospace Candidate Physical Component';

    part def 'Nanospace Candidate Procedure Component'
        :> 'Nanospace Candidate Physical Component';

    part def 'Participant Browser Host'
        :> 'Nanospace Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract participant device. The sources establish cross-platform browser access
         * but do not constrain device type, operating system, or resource sizing.
         */
    }

    part def 'Modern Web Browser' :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported. The Nanospace UI requires only a modern browser on the client side. */
    }

    part def 'Nanospace AngularJS Web Interface'
        :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported in the reproduced Nanospace architecture. Presents projects, models,
         * requirements, modes, values, users, history, and shared engineering information.
         */
    }

    part def <'NS-PN-01'> 'Browser Client Physical Node' {
        doc
        /* Client-side node directly distinguished from the server side in the reported Nanospace
         * architecture.
         */

        part host : 'Participant Browser Host';
        part browser : 'Modern Web Browser';
        part webInterface : 'Nanospace AngularJS Web Interface';
    }

    part def 'Nanospace Application Compute Host'
        :> 'Nanospace Candidate Hardware or Service Component' {
        doc
        /* Inferred opaque hosting resource. The sources do not establish whether the web server,
         * Java service, API, and Neo4j database share a machine, use containers, or use separate
         * hosts.
         */
    }

    part def 'Nginx Web Server' :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported in the reproduced architecture. Serves the web application over HTTP. */
    }

    part def 'Nanospace Java Service' :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported in the reproduced architecture. Provides application logic and HTTP access to
         * engineering data.
         */
    }

    part def 'Nanospace REST API Endpoint' :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported. Exposes project data to browser, Python, and third-party integrations. */
    }

    part def 'Nanospace Neo4j Engineering Database'
        :> 'Nanospace Candidate Data Component' {
        doc
        /* Reported. Graph-based Neo4j storage with ACID properties and concurrent write protection.
         * Reported entities include Project, Component, Mode, Value, and User. Complete framework
         * evidence and baseline schemas remain candidate additions.
         */
    }

    part def <'NS-PN-02'> 'Nanospace Application and Data Server Physical Node' {
        doc
        /* Server-side deployment responsibility containing the platform components reported in the
         * Nanospace architecture. Detailed server topology remains unspecified.
         */

        part host : 'Nanospace Application Compute Host';
        part webServer : 'Nginx Web Server';
        part applicationService : 'Nanospace Java Service';
        part restAPI : 'Nanospace REST API Endpoint';
        part engineeringDatabase : 'Nanospace Neo4j Engineering Database';
    }

    part def 'Python Model and Data Bridge' :> 'Nanospace Candidate Software Component' {
        doc
        /* Synthesized from reported mechanisms. Coordinates model extraction, Nanospace API
         * updates, analysis requests, returned results, and approved reverse model updates.
         */
    }

    part def 'Gaphor SysML Model Parser and Adapter'
        :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported. Reads the external Gaphor model file, extracts stereotyped model data and
         * requirements, and can reverse approved updates after analysis or optimization. Supporting
         * other native modeling tools requires parser changes or another adapter.
         */
    }

    part def 'Nanospace API Client' :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported integration pattern. Reads and updates Nanospace records through its API. */
    }

    part def 'Software Readable Exchange Data Set'
        :> 'Nanospace Candidate Data Component' {
        doc
        /* Reported. Carries selected model parameters and analysis inputs and outputs in a tool
         * readable structure. YAML is used in the cited proof of concept, while the formalization
         * allows other formats.
         */
    }

    part def 'Analysis Tool Adapter' :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported integration pattern with candidate-specific implementation. Invokes external NSS
         * or other analysis tools and correlates returned budgets, reports, and raw results through
         * IF-05.
         */
    }

    part def 'Dependency and DSM Generator' :> 'Nanospace Candidate Software Component' {
        doc
        /* Reported. Generates dependency graphs or design structure matrices for impact analysis
         * and iteration sequencing.
         */
    }

    part def 'Evidence Repository Adapter' :> 'Nanospace Candidate Software Component' {
        doc
        /* Proposed. Registers and retrieves controlled evidence packages through IF-06. The
         * selected Nanospace sources do not establish this repository interface.
         */
    }

    part def 'Transfer and Consistency Checker' :> 'Nanospace Candidate Software Component' {
        doc
        /* Proposed in response to the coherence and information-loss problem reported by the
         * literature. Checks source revision, baseline, completeness, identifiers, quantities,
         * units, meaning, provenance, and applicable traces before accepting a transfer.
         */
    }

    part def 'Evaluation Manifest Runner' :> 'Nanospace Candidate Software Component' {
        doc
        /* Proposed. Applies the fixed framework evaluation manifest and preserves raw observations
         * needed by the common candidate comparison protocol.
         */
    }

    part def 'Python Integration Compute Host'
        :> 'Nanospace Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract compute resource for the bridge, parser, API clients, dependency
         * generation, and assurance checks. Packaging, operating system, and deployment location
         * remain unspecified.
         */
    }

    part def <'NS-PN-03'> 'Python Model and Analysis Integration Runner Physical Node' {
        doc
        /* Combines the reported model parser and API integration mechanisms into a controlled
         * runner. This separates model-language, API, analysis-tool, and repository changes from the
         * Nanospace application server.
         */

        part host : 'Python Integration Compute Host';
        part bridge : 'Python Model and Data Bridge';
        part modelAdapter : 'Gaphor SysML Model Parser and Adapter';
        part nanospaceClient : 'Nanospace API Client';
        part exchangeData : 'Software Readable Exchange Data Set';
        part analysisAdapter : 'Analysis Tool Adapter';
        part dependencyGenerator : 'Dependency and DSM Generator';
        part evidenceAdapter : 'Evidence Repository Adapter';
        part transferChecker : 'Transfer and Consistency Checker';
        part evaluationRunner : 'Evaluation Manifest Runner';
    }

    part def 'User Role and Project Administration Procedure'
        :> 'Nanospace Candidate Procedure Component' {
        doc
        /* Reported pattern. Establishes users, shared project responsibility, permissions, and
         * reviewer access.
         */
    }

    part def 'Model and Nanospace Synchronization Procedure'
        :> 'Nanospace Candidate Procedure Component' {
        doc
        /* Synthesized from reported mechanisms. Extracts approved model data, inspects transfer
         * findings, updates Nanospace, and reverses only authorized changes to the model.
         */
    }

    part def 'Semi-Automatic Design Iteration Procedure'
        :> 'Nanospace Candidate Procedure Component' {
        doc
        /* Reported. Uses dependency information and expert judgment to select affected analyses,
         * execute them, and assess the next design iteration.
         */
    }

    part def 'Baseline Release and Evidence Export Procedure'
        :> 'Nanospace Candidate Procedure Component' {
        doc
        /* Proposed to satisfy evidence-baseline and reconstruction requirements. Binds model,
         * Nanospace, analysis, and discrepancy records to a controlled candidate evidence package
         * without requiring the candidate to use the OOSEM study repository governed by MC-02.
         */
    }

    part def 'Analysis Reproduction Procedure' :> 'Nanospace Candidate Procedure Component' {
        doc
        /* Proposed from reported open-source scripts and structured data. Reconstructs the declared
         * environment, executes a designated analysis, and issues its evidence package and verdict
         * inputs.
         */
    }

    part def <'NS-PC-01'> 'Nanospace Candidate Operating Procedures' {
        part administerUsersAndProjects : 'User Role and Project Administration Procedure';
        part synchronizeModelAndNanospace : 'Model and Nanospace Synchronization Procedure';
        part performDesignIteration : 'Semi-Automatic Design Iteration Procedure';
        part releaseBaseline : 'Baseline Release and Evidence Export Procedure';
        part reproduceAnalysis : 'Analysis Reproduction Procedure';
    }

    part def <'NS-PA-00'> 'Nanospace Centered Candidate Physical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Minimum physical decomposition for comparison. Explicit logical-to-physical allocations,
         * ports, connectors, physical service activities, satisfy relationships, and measured MOPs
         * are intentionally deferred to the next OOSEM steps.
         */

        part browserClient : 'Browser Client Physical Node';
        part applicationAndDataServer : 'Nanospace Application and Data Server Physical Node';
        part integrationRunner : 'Python Model and Analysis Integration Runner Physical Node';
        part operatingProcedures : 'Nanospace Candidate Operating Procedures';
    }

    part nanospaceCandidateNodeLogical : 'Nanospace Candidate Node Logical Framework';
    part nanospaceCandidatePhysical : 'Nanospace Centered Candidate Physical Framework';
} // package FrameworkCandidateNanospace
