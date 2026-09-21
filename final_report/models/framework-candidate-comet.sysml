// Minimal OOSEM steps 6 and 7 model for the COMET centered candidate.
package FrameworkCandidateComet {
    private import FrameworkBlackBoxSpecification
            ::'Specified Nanosatellite EPS Engineering Framework';
    private import FrameworkLogicalDecomposition::*;

    doc
    /* This package defines a literature grounded COMET centered candidate.
     * It contains only the logical node distribution and minimum physical component inventory.
     * It does not yet assert logical-to-physical allocations, requirement satisfaction, or measured
     * performance.
     *
     * Evidence basis:
     * - Deutsch, Hoffmann, and Bertrand (2022), Development of a Concurrent Engineering Tutorial
     *   as part of the ESA_Lab@ initiative, PDF pages 3-6, review-0876.
     * - Kaslow, Cahill, and Frank, Developing a CubeSat System MBSE Reference Model: Interim
     *   Status #5, PDF pages 1-6, citation-2362.
     * - Fischer et al. (2019), Spacecraft Interface Management in Concurrent Engineering Sessions,
     *   PDF page 3, review-1277.
     * - Kanavouras, Bühler, and Hein (2024), Building a Lightweight Data Management Tool for Small
     *   Satellite Missions, PDF pages 1-4, review-0522.
     *
     * The reported architecture combines an ECSS-E-TM-10-25A COMET server, synchronized IME and
     * Excel clients, a CSRM-derived Template Model, a Model Catalogue, and a mission Study Model.
     * This candidate preserves the black-box boundary by treating the external Versioned System
     * Model as the architecture and requirements authority. COMET is the synchronized concurrent
     * engineering workspace. The model, analysis, and evidence runner is an explicit candidate
     * addition. This file is the common SysML v2 comparison representation required by MC-01.
     */

    // Step 6: logical node distribution.

    part def 'COMET Candidate Logical Node' {
        doc
        /* Responsibility and distribution partition for this candidate. The node definitions remain
         * independent of detailed client, server, and integration deployment technology.
         */
    }

    part def <'COM-LN-01'> 'Concurrent Participant Access Logical Node'
        :> 'COMET Candidate Logical Node' {
        doc
        /* Groups participant interaction and design review around synchronized COMET clients.
         * Client-server synchronization, Domains of Expertise, ownership, and remote training-model
         * access are reported by Deutsch et al. (2022), pages 2-5. Reviewer-specific findings and
         * disposition control remain proposed.
         */

        part missionApplicationInterface : 'Mission Application Interface Manager';
        part researchGovernanceInterface : 'Research Governance Interface Manager';
        part independentReviewInterface : 'Independent Review Interface Manager';
        part designReviewManager : 'Design Review Manager';
    }

    part def <'COM-LN-02'> 'Engineering Model and Configuration Logical Node'
        :> 'COMET Candidate Logical Node' {
        doc
        /* Groups the reusable template, case Study Model, catalogue, requirements, shared reference
         * definitions, workflow, configuration, and retained records around the COMET server. The
         * external-model adapter and complete evidence-chain semantics are candidate additions.
         */

        part modelControlInterface : 'Model Control Interface Manager';

        part evidenceChainManager : 'Evidence Chain Manager';
        part caseConfigurationManager : 'Case Configuration Manager';
        part designChangeAssessmentManager : 'Design Change Assessment Manager';

        part workflowControlManager : 'Workflow Control Manager';
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager';
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager';
    }

    part def <'COM-LN-03'> 'Analysis Compliance and Assurance Logical Node'
        :> 'COMET Candidate Logical Node' {
        doc
        /* Groups calculations, external analysis, evidence custody, candidate assessment, transfer
         * assurance, and measurement. The Excel calculation surface is reported by Deutsch et al.
         * (2022), page 3. External tool orchestration, evidence-repository integration, and the
         * complete framework transfer contract are proposed.
         */

        part analysisExecutionInterface : 'Analysis Execution Interface Manager';
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager';

        part analysisReproductionManager : 'Analysis Reproduction Manager';
        part candidateEvaluationManager : 'Candidate Evaluation Manager';
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator';

        part transferAssuranceManager : 'Transfer Assurance Manager';
        part evaluationMeasurementManager : 'Evaluation Measurement Manager';
    }

    part def <'COM-NL-00'> 'COMET Candidate Node Logical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Separate node-logical decomposition of the complete framework black box. All eighteen
         * logical components from LA-00 occur once across the three logical nodes.
         */

        part participantAccess : 'Concurrent Participant Access Logical Node';
        part engineeringModelAndConfiguration : 'Engineering Model and Configuration Logical Node';
        part analysisComplianceAndAssurance : 'Analysis Compliance and Assurance Logical Node';
    }

    // Step 7: minimum physical component inventory.

    part def 'COMET Candidate Physical Component' {
        doc
        /* High-level implementation component retained only when it distinguishes the candidate or
         * identifies a required candidate addition.
         */
    }

    part def 'COMET Candidate Software Component' :> 'COMET Candidate Physical Component';

    part def 'COMET Candidate Data Component' :> 'COMET Candidate Physical Component';

    part def 'COMET Candidate Hardware or Service Component'
        :> 'COMET Candidate Physical Component';

    part def 'COMET Candidate Procedure Component' :> 'COMET Candidate Physical Component';

    part def 'Participant Workstation Host'
        :> 'COMET Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract host for the COMET client applications. The selected sources do not
         * constrain workstation hardware, operating system, or network topology.
         */
    }

    part def 'COMET Integrated Modeling Environment Client'
        :> 'COMET Candidate Software Component' {
        doc
        /* Reported. Supports administrative, preparatory, organizational, and model-access work. */
    }

    part def 'COMET Excel Add-in' :> 'COMET Candidate Software Component' {
        doc
        /* Reported. Synchronizes shared parameters and supports spreadsheet calculations and
         * analysis against the COMET engineering model.
         */
    }

    part def 'Microsoft Excel Host Application' :> 'COMET Candidate Software Component' {
        doc
        /* Reported COTS dependency hosting the COMET add-in and calculation surface. Product
         * version, license, operating-system, and automation constraints remain open.
         */
    }

    part def <'COM-PN-01'> 'COMET Participant Client Physical Node' {
        doc
        /* Client-side node containing the two integral COMET clients reported by Deutsch et al.
         * (2022), page 3, plus their abstract execution host.
         */

        part host : 'Participant Workstation Host';
        part ime : 'COMET Integrated Modeling Environment Client';
        part excel : 'Microsoft Excel Host Application';
        part excelAddIn : 'COMET Excel Add-in';
    }

    part def 'COMET Server Compute Host'
        :> 'COMET Candidate Hardware or Service Component' {
        doc
        /* Inferred opaque hosting resource. Database product, server process topology, backup,
         * redundancy, physical location, and resource sizing remain unspecified.
         */
    }

    part def 'COMET Server Application' :> 'COMET Candidate Software Component' {
        doc
        /* Reported. Stores and synchronizes models, users, reference data, and shared study
         * information for the COMET clients.
         */
    }

    part def 'COMET Engineering Model Repository' :> 'COMET Candidate Data Component' {
        doc
        /* Reported at platform level. Retains reusable and study-specific engineering models and
         * their parameters. Detailed persistence and revision semantics remain unspecified.
         */
    }

    part def 'Site Directory and Reference Data Set' :> 'COMET Candidate Data Component' {
        doc
        /* Reported. Holds users, Domains of Expertise, categories, measurement definitions, and
         * shared reference information at server Site Directory level.
         */
    }

    part def 'CSRM to ECSS Category Mapping Library' :> 'COMET Candidate Data Component' {
        doc
        /* Reported. Maps selected CSRM subsystem-component semantics to COMET Categories and the
         * ECSS Equipment super-category. A complete authoritative-model mapping remains unverified.
         */
    }

    part def 'CubeSat Template Model' :> 'COMET Candidate Data Component' {
        doc
        /* Reported. Provides the reusable mission, segment, subsystem, parameter, finite-state,
         * and requirement blueprint from which a case Study Model is initialized.
         */
    }

    part def 'CubeSat Model Catalogue' :> 'COMET Candidate Data Component' {
        doc
        /* Reported. Holds generic equipment definitions and specific COTS parts and assemblies with
         * parameters and linked data sheets.
         */
    }

    part def 'Candidate Study Model' :> 'COMET Candidate Data Component' {
        doc
        /* Reported. Holds the case-specific concurrent design created with the Template Model as its
         * source. Approved-adaptation and immutable-baseline semantics remain proposed.
         */
    }

    part def 'Requirements and Compliance Record Set' :> 'COMET Candidate Data Component' {
        doc
        /* Reported. Retains imported and case-derived requirements, links to model elements and
         * parameters, and automated numerical compliance results.
         */
    }

    part def 'COMET Client Synchronization Service' :> 'COMET Candidate Software Component' {
        doc
        /* Inferred from the reported regular client-server synchronization that enables near
         * real-time collaboration. Detailed service decomposition remains unspecified.
         */
    }

    part def <'COM-PN-02'> 'COMET Server and Engineering Model Physical Node' {
        doc
        /* Central model and data node combining only reported COMET server responsibilities,
         * reported CubeSat model assets, and an abstract hosting resource.
         */

        part host : 'COMET Server Compute Host';
        part server : 'COMET Server Application';
        part modelRepository : 'COMET Engineering Model Repository';
        part siteAndReferenceData : 'Site Directory and Reference Data Set';
        part semanticMapping : 'CSRM to ECSS Category Mapping Library';
        part templateModel : 'CubeSat Template Model';
        part modelCatalogue : 'CubeSat Model Catalogue';
        part studyModel : 'Candidate Study Model';
        part complianceRecords : 'Requirements and Compliance Record Set';
        part synchronization : 'COMET Client Synchronization Service';
    }

    part def 'Integration Runner Compute Host'
        :> 'COMET Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract compute resource for adapters, checks, impact analysis, measurement, and
         * evidence packaging. Packaging, operating system, deployment location, and sizing remain
         * unspecified.
         */
    }

    part def 'External System Model Adapter' :> 'COMET Candidate Software Component' {
        doc
        /* Proposed. Reads accepted requirements, architecture, interfaces, properties, and traces
         * from the external Versioned System Model through IF-04 and returns only approved updates.
         */
    }

    part def 'COMET Exchange Adapter' :> 'COMET Candidate Software Component' {
        doc
        /* Proposed. Maps controlled exchanges to COMET server records. The related OCDT evidence in
         * Fischer et al. (2019), page 3, supports an ECSS-tool integration pattern but does not prove
         * that this COMET configuration exposes the same REST API.
         */
    }

    part def 'External Analysis Tool Adapter' :> 'COMET Candidate Software Component' {
        doc
        /* Proposed from the reported Excel calculation pattern. Issues typed requests to external
         * EPS analysis tools through IF-05 and correlates returned raw results.
         */
    }

    part def 'Evidence Repository Adapter' :> 'COMET Candidate Software Component' {
        doc
        /* Proposed. Registers and retrieves controlled evidence packages through IF-06. The
         * selected COMET sources do not establish this repository interface.
         */
    }

    part def 'Transfer and Semantic Checker' :> 'COMET Candidate Software Component' {
        doc
        /* Proposed. Checks source and baseline identity, schema completeness, stable identifiers,
         * quantities, units, semantic mappings, provenance, and applicable traces before accepting
         * any transferred record.
         */
    }

    part def 'Change Impact and Compliance Coordinator'
        :> 'COMET Candidate Software Component' {
        doc
        /* Synthesized. Combines changed model records, parameter dependencies, requirement links,
         * and reported numerical compliance checks to identify affected analyses and evidence.
         */
    }

    part def 'Evidence and Provenance Packager' :> 'COMET Candidate Software Component' {
        doc
        /* Proposed. Packages accepted model records, COMET configuration, calculations, raw
         * results, uncertainty, discrepancies, review records, and verification evidence.
         */
    }

    part def 'Evaluation Manifest Runner' :> 'COMET Candidate Software Component' {
        doc
        /* Proposed. Applies the fixed framework evaluation manifest and preserves raw observations
         * and correctness gates needed by the common comparison protocol.
         */
    }

    part def 'Typed Candidate Exchange Package' :> 'COMET Candidate Data Component' {
        doc
        /* Proposed. Carries controlled model, analysis, status, uncertainty, and evidence records
         * without replacing their authoritative sources.
         */
    }

    part def <'COM-PN-03'> 'Model Analysis and Evidence Integration Runner Physical Node' {
        doc
        /* Explicitly separates candidate additions from the reported COMET product. This isolates
         * model-language, COMET-access, analysis-tool, repository, and assurance changes.
         */

        part host : 'Integration Runner Compute Host';
        part systemModelAdapter : 'External System Model Adapter';
        part cometAdapter : 'COMET Exchange Adapter';
        part analysisAdapter : 'External Analysis Tool Adapter';
        part evidenceAdapter : 'Evidence Repository Adapter';
        part transferChecker : 'Transfer and Semantic Checker';
        part impactCoordinator : 'Change Impact and Compliance Coordinator';
        part evidencePackager : 'Evidence and Provenance Packager';
        part evaluationRunner : 'Evaluation Manifest Runner';
        part exchangePackage : 'Typed Candidate Exchange Package';
    }

    part def 'Site and Reference Data Administration Procedure'
        :> 'COMET Candidate Procedure Component' {
        doc
        /* Reported pattern. Establishes users, Domains of Expertise, ownership, units, categories,
         * and shared reference definitions.
         */
    }

    part def 'Template and Study Model Setup Procedure'
        :> 'COMET Candidate Procedure Component' {
        doc
        /* Reported. Selects the Template Model as the Study Model source and records case-specific
         * setup decisions.
         */
    }

    part def 'Concurrent Engineering Session Procedure'
        :> 'COMET Candidate Procedure Component' {
        doc
        /* Reported. Synchronizes domain work, moderates iterative sessions, reviews shared values,
         * and resolves cross-domain issues.
         */
    }

    part def 'Catalogue Selection and Budget Procedure'
        :> 'COMET Candidate Procedure Component' {
        doc
        /* Reported. Selects generic or COTS equipment, assigns owners and parameters, and calculates
         * state-dependent mass and power budgets.
         */
    }

    part def 'Requirements Linking and Compliance Procedure'
        :> 'COMET Candidate Procedure Component' {
        doc
        /* Reported. Links requirements to model elements and parameters and executes applicable
         * numerical compliance checks.
         */
    }

    part def 'Model Synchronization and Transfer Review Procedure'
        :> 'COMET Candidate Procedure Component' {
        doc
        /* Synthesized. Compares authoritative-model and COMET records, inspects transfer findings,
         * and authorizes controlled updates rather than silently replacing content.
         */
    }

    part def 'Baseline Release and Evidence Export Procedure'
        :> 'COMET Candidate Procedure Component' {
        doc
        /* Proposed. Binds the model, reference data, study configuration, calculations,
         * discrepancies, and review records to a controlled candidate evidence package without
         * requiring the candidate to use the OOSEM study repository governed by MC-02.
         */
    }

    part def 'Analysis Reproduction Procedure' :> 'COMET Candidate Procedure Component' {
        doc
        /* Proposed. Reconstructs the declared client, server, spreadsheet, adapter, and analysis
         * environment and issues a reproduction package and verdict inputs.
         */
    }

    part def <'COM-PC-01'> 'COMET Candidate Operating Procedures' {
        part administerSiteAndReferenceData : 'Site and Reference Data Administration Procedure';
        part setupStudyModel : 'Template and Study Model Setup Procedure';
        part conductConcurrentSession : 'Concurrent Engineering Session Procedure';
        part selectCatalogueAndCalculateBudgets : 'Catalogue Selection and Budget Procedure';
        part checkRequirementCompliance : 'Requirements Linking and Compliance Procedure';
        part reviewModelTransfers : 'Model Synchronization and Transfer Review Procedure';
        part releaseBaseline : 'Baseline Release and Evidence Export Procedure';
        part reproduceAnalysis : 'Analysis Reproduction Procedure';
    }

    part def <'COM-PA-00'> 'COMET Centered Candidate Physical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Minimum physical decomposition for comparison. Explicit logical-to-physical allocations,
         * ports, connectors, physical service activities, satisfy relationships, and measured MOPs
         * are intentionally deferred to the next OOSEM steps.
         */

        part participantClient : 'COMET Participant Client Physical Node';
        part serverAndEngineeringModel : 'COMET Server and Engineering Model Physical Node';
        part integrationRunner : 'Model Analysis and Evidence Integration Runner Physical Node';
        part operatingProcedures : 'COMET Candidate Operating Procedures';
    }

    part cometCandidateNodeLogical : 'COMET Candidate Node Logical Framework';
    part cometCandidatePhysical : 'COMET Centered Candidate Physical Framework';
} // package FrameworkCandidateComet
