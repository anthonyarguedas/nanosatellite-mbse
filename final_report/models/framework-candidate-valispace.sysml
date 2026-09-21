// Minimal OOSEM steps 6 and 7 model for the Valispace centered candidate.
package FrameworkCandidateValispace {
    private import FrameworkBlackBoxSpecification
            ::'Specified Nanosatellite EPS Engineering Framework';
    private import FrameworkLogicalDecomposition::*;

    doc
    /* This package defines a literature grounded example of a Valispace centered candidate.
     * It contains only the logical node distribution and minimum physical component inventory.
     * It does not yet assert logical-to-physical allocations, requirement satisfaction, or measured
     * performance.
     *
     * Evidence basis:
     * - Deiana (2025), Integrating Data-Driven and Model-Based Systems Engineering for End-to-End
     *   Small-Satellite Design, PDF pages 33-37 and 47-55, citation-4690.
     * - Campioli, Deiana, and Corpino (2025), Integrating Concurrent Engineering with Data-Driven
     *   and Model-Based Systems Engineering for End-to-End Small-Satellite Design, PDF pages 3-7,
     *   review-0356.
     * - Ivanov (2023), Spacecraft digital engineering: the tale of digital twins and lessons
     *   learned, PDF pages 5 and 9, review-0793.
     * - Latserus et al. (2020), Model-based approach for requirements management connection with
     *   verification procedures applied to space systems, PDF pages 5-6, citation-0569.
     *
     * The literature configuration uses Capella as the architecture master and Valispace as the
     * requirements, engineering-data, budget, and trade-study environment. This candidate preserves
     * that implementation choice. Its description in this file is the separate common SysML v2
     * comparison representation required by MC-01. Versioned System Model, Analysis Tools, and
     * Evidence Repository remain outside the framework boundary defined by the black-box context.
     */

    // Step 6: logical node distribution.

    part def 'Valispace Candidate Logical Node' {
        doc
        /* Responsibility and distribution partition for this candidate. Node definitions remain
         * independent of the detailed hosting technology.
         */
    }

    part def <'VS-LN-01'> 'Participant Access Logical Node' :> 'Valispace Candidate Logical Node' {
        doc
        /* Groups the three participant-facing interfaces. Placement in a shared browser-accessible
         * environment is supported by Deiana (2025), pages 34-35. Independent reviewer access is
         * provisional because Latserus et al. (2020), pages 5-6, identifies license access as a
         * concern for external verification performers.
         */

        part missionApplicationInterface : 'Mission Application Interface Manager';
        part researchGovernanceInterface : 'Research Governance Interface Manager';
        part independentReviewInterface : 'Independent Review Interface Manager';
    }

    part def <'VS-LN-02'> 'Engineering Data and Workflow Logical Node'
        :> 'Valispace Candidate Logical Node' {
        doc
        /* Groups service coordination, workflow, configuration, evidence, and measurement around
         * the centralized product tree, requirements, engineering data, analysis, and test records.
         * This is a synthesis from the Valispace modules reported by Deiana (2025), pages 36-37.
         * Complete immutable-baseline and provenance semantics remain evidence gaps.
         */

        part evidenceChainManager : 'Evidence Chain Manager';
        part caseConfigurationManager : 'Case Configuration Manager';
        part analysisReproductionManager : 'Analysis Reproduction Manager';
        part designChangeAssessmentManager : 'Design Change Assessment Manager';
        part candidateEvaluationManager : 'Candidate Evaluation Manager';
        part designReviewManager : 'Design Review Manager';

        part workflowControlManager : 'Workflow Control Manager';
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager';
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager';
        part evaluationMeasurementManager : 'Evaluation Measurement Manager';
    }

    part def <'VS-LN-03'> 'Integration and Assurance Logical Node'
        :> 'Valispace Candidate Logical Node' {
        doc
        /* Groups the interfaces to the authoritative model, analysis tools, and evidence repository
         * with controlled analysis and transfer assurance. The core bridge pattern is reported by
         * Deiana (2025), pages 47-55 and 79-80. Evidence-custody integration is a candidate-specific
         * addition. SysML v2 is used only to describe this candidate for comparison.
         */

        part modelControlInterface : 'Model Control Interface Manager';
        part analysisExecutionInterface : 'Analysis Execution Interface Manager';
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager';
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator';
        part transferAssuranceManager : 'Transfer Assurance Manager';
    }

    part def <'VS-NL-00'> 'Valispace Candidate Node Logical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Separate node-logical decomposition of the complete framework black box. All eighteen
         * logical components from LA-00 occur once across the three nodes.
         */

        part participantAccess : 'Participant Access Logical Node';
        part engineeringDataAndWorkflow : 'Engineering Data and Workflow Logical Node';
        part integrationAndAssurance : 'Integration and Assurance Logical Node';
    }

    // Step 7: minimum physical component inventory.

    part def 'Valispace Candidate Physical Component' {
        doc
        /* High-level implementation component retained only when it distinguishes the candidate or
         * identifies a required candidate addition.
         */
    }

    part def 'Valispace Candidate Software Component' :> 'Valispace Candidate Physical Component';

    part def 'Valispace Candidate Data Component' :> 'Valispace Candidate Physical Component';

    part def 'Valispace Candidate Hardware or Service Component'
        :> 'Valispace Candidate Physical Component';

    part def 'Valispace Candidate Procedure Component' :> 'Valispace Candidate Physical Component';

    part def 'Valispace Web Interface' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Browser-based access and stakeholder-oriented views are described by Deiana
         * (2025), pages 34-35.
         */
    }

    part def 'Valispace Project Module' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Provides project overview, timeline, and team coordination. */
    }

    part def 'Valispace Components Module' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Holds the product tree, properties, modes, matrices, and trade alternatives. */
    }

    part def 'Valispace Requirements Module' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Holds requirement hierarchy, links, and verification status. */
    }

    part def 'Valispace Analyses Module' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Holds graphs, tables, budgets, reports, and trade-study results. */
    }

    part def 'Valispace Scripting Module' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Executes Python or Octave calculations and simulations. */
    }

    part def 'Valispace Tests Module' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Creates, organizes, and tracks requirement verification procedures. */
    }

    part def 'Valispace Engineering Database' :> 'Valispace Candidate Data Component' {
        doc
        /* Reported at platform level as the consistent database for connected requirements,
         * components, values, formulas, and associated engineering records. Detailed database
         * technology and deployment are not reported by the selected sources.
         */
    }

    part def 'Valispace REST API Endpoint' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Provides authenticated HTTP CRUD operations for external integrations. */
    }

    part def 'Valispace Hosted Compute Infrastructure'
        :> 'Valispace Candidate Hardware or Service Component' {
        doc
        /* Inferred opaque hosting resource. The sources establish a browser-based platform but do
         * not establish its server topology, database product, redundancy, or physical location.
         */
    }

    part def <'VS-PN-01'> 'Valispace Hosted Service Physical Node' {
        doc
        /* Opaque hosted node containing only platform elements directly reported in the literature
         * plus an abstract hosting resource.
         */

        part hosting : 'Valispace Hosted Compute Infrastructure';
        part webInterface : 'Valispace Web Interface';
        part projectModule : 'Valispace Project Module';
        part componentsModule : 'Valispace Components Module';
        part requirementsModule : 'Valispace Requirements Module';
        part analysesModule : 'Valispace Analyses Module';
        part scriptingModule : 'Valispace Scripting Module';
        part testsModule : 'Valispace Tests Module';
        part engineeringDatabase : 'Valispace Engineering Database';
        part restAPI : 'Valispace REST API Endpoint';
    }

    part def 'Python Integration Bridge' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported core. The source bridge transforms and synchronizes architecture information,
         * compares component hierarchies, reports discrepancies, and can restore conformity.
         */
    }

    part def 'Capella Architecture Model Adapter' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported. Uses the Capella-side Python API and export scripts to read architecture-model
         * elements and produce exchanges consumed by the bridge. The SysML v2 comparison model
         * describes this component without changing its implementation technology.
         */
    }

    part def 'Analysis Tool Adapter' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported integration pattern with candidate-specific implementation. Issues controlled
         * requests to external analysis tools and correlates their returned results through IF-05.
         */
    }

    part def 'Evidence Repository Adapter' :> 'Valispace Candidate Software Component' {
        doc
        /* Proposed. Registers and retrieves controlled evidence packages through IF-06. The
         * selected Valispace sources do not establish this repository interface.
         */
    }

    part def 'Transfer and Consistency Checker' :> 'Valispace Candidate Software Component' {
        doc
        /* Reported product-tree comparison core with proposed extension to source revision,
         * baseline, completeness, identifiers, units, meaning, provenance, and trace checks.
         */
    }

    part def 'Evaluation Manifest Runner' :> 'Valispace Candidate Software Component' {
        doc
        /* Proposed. Applies the fixed framework evaluation manifest and preserves raw observations
         * needed by the common candidate comparison protocol.
         */
    }

    part def 'Integration Compute Host' :> 'Valispace Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract compute resource for the Python bridge and adapters. Its operating
         * system, packaging, deployment location, and resource sizing remain unspecified.
         */
    }

    part def <'VS-PN-02'> 'Python Integration Runner Physical Node' {
        doc
        /* Separates adapter and assurance changes from the hosted COTS platform. This limits the
         * impact of API, model-language, analysis-tool, and evidence-repository changes.
         */

        part host : 'Integration Compute Host';
        part bridge : 'Python Integration Bridge';
        part architectureAdapter : 'Capella Architecture Model Adapter';
        part analysisAdapter : 'Analysis Tool Adapter';
        part evidenceAdapter : 'Evidence Repository Adapter';
        part transferChecker : 'Transfer and Consistency Checker';
        part evaluationRunner : 'Evaluation Manifest Runner';
    }

    part def 'Role and Access Administration Procedure'
        :> 'Valispace Candidate Procedure Component' {
        doc
        /* Inferred. Establishes users, licenses, permissions, and reviewer access. */
    }

    part def 'Model and Data Synchronization Procedure'
        :> 'Valispace Candidate Procedure Component' {
        doc
        /* Reported pattern. Executes synchronization, inspects discrepancies, and authorizes
         * controlled updates rather than silently replacing authoritative content.
         */
    }

    part def 'Baseline Release and Evidence Export Procedure'
        :> 'Valispace Candidate Procedure Component' {
        doc
        /* Proposed to satisfy the framework's evidence-baseline and reconstruction requirements.
         * It exports a controlled candidate evidence package without requiring the candidate to use
         * the OOSEM study repository governed by MC-02.
         */
    }

    part def 'Analysis Reproduction Procedure' :> 'Valispace Candidate Procedure Component' {
        doc
        /* Proposed from reported scripting and test capabilities. Reconstructs the declared
         * environment, executes a designated analysis, and issues its evidence package.
         */
    }

    part def <'VS-PC-01'> 'Valispace Candidate Operating Procedures' {
        part administerAccess : 'Role and Access Administration Procedure';
        part synchronizeModelAndData : 'Model and Data Synchronization Procedure';
        part releaseBaseline : 'Baseline Release and Evidence Export Procedure';
        part reproduceAnalysis : 'Analysis Reproduction Procedure';
    }

    part def <'VS-PA-00'> 'Valispace Centered Candidate Physical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Minimum physical decomposition for comparison. Explicit logical-to-physical allocations,
         * ports, connectors, physical service activities, satisfy relationships, and measured MOPs
         * are intentionally deferred to the next OOSEM steps.
         */

        part hostedService : 'Valispace Hosted Service Physical Node';
        part integrationRunner : 'Python Integration Runner Physical Node';
        part operatingProcedures : 'Valispace Candidate Operating Procedures';
    }

    part valispaceCandidateNodeLogical : 'Valispace Candidate Node Logical Framework';
    part valispaceCandidatePhysical : 'Valispace Centered Candidate Physical Framework';
} // package FrameworkCandidateValispace
