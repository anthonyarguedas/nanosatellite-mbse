// Minimal OOSEM steps 6 and 7 model for the lightweight Git and YAML candidate.
package FrameworkCandidateGitYaml {
    private import FrameworkBlackBoxSpecification
            ::'Specified Nanosatellite EPS Engineering Framework';
    private import FrameworkLogicalDecomposition::*;

    doc
    /* This package defines a literature grounded lightweight Git and YAML candidate.
     * It contains only the logical node distribution and minimum physical component inventory.
     * It does not yet assert logical-to-physical allocations, requirement satisfaction, or measured
     * performance.
     *
     * Evidence basis:
     * - Kanavouras, Bühler, and Hein (2024), Building a Lightweight Data Management Tool for Small
     *   Satellite Missions, PDF pages 1 and 3-10, review-0522.
     * - Chiu (2023), SeaLion CubeSat Mission Architecture Using Model Based Systems Engineering
     *   with a Docs as Code Approach, PDF pages 26-27, 31-32, and 52-78, review-0787.
     *
     * The candidate synthesizes the reported lightweight web engineering-data design with the
     * demonstrated SeaLion Git and YAML docs-as-code pattern. Its native records are Git and YAML
     * artifacts. This file is the separate common SysML v2 comparison representation required by
     * MC-01. Versioned System Model, Analysis Tools, and Evidence Repository remain outside the
     * framework boundary defined by the black-box context.
     */

    // Step 6: logical node distribution.

    part def 'Git and YAML Candidate Logical Node' {
        doc
        /* Responsibility and distribution partition for this candidate. The nodes remain
         * independent of detailed hosting and deployment products.
         */
    }

    part def <'GY-LN-01'> 'Participant Access and Review Logical Node'
        :> 'Git and YAML Candidate Logical Node' {
        doc
        /* Groups participant-facing interfaces and design review around browser views, generated
         * documents, raw versioned records, and issue-based findings. Browser access is a reported
         * design in Kanavouras et al. (2024), pages 4-7. Git-hosted generated views are demonstrated
         * by Chiu (2023), pages 52-75. Reviewer outcome authority remains a project addition.
         */

        part missionApplicationInterface : 'Mission Application Interface Manager';
        part researchGovernanceInterface : 'Research Governance Interface Manager';
        part independentReviewInterface : 'Independent Review Interface Manager';
        part designReviewManager : 'Design Review Manager';
    }

    part def <'GY-LN-02'> 'Versioned Engineering Records and Workflow Logical Node'
        :> 'Git and YAML Candidate Logical Node' {
        doc
        /* Groups evidence, case configuration, change assessment, workflow, baseline control, and
         * provenance around Git revisions, YAML records, explicit trace links, generated views, and
         * issue records. The complete framework baseline and evidence semantics remain additions.
         */

        part evidenceChainManager : 'Evidence Chain Manager';
        part caseConfigurationManager : 'Case Configuration Manager';
        part designChangeAssessmentManager : 'Design Change Assessment Manager';

        part workflowControlManager : 'Workflow Control Manager';
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager';
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager';
    }

    part def <'GY-LN-03'> 'Model Analysis and Assurance Integration Logical Node'
        :> 'Git and YAML Candidate Logical Node' {
        doc
        /* Groups external model, analysis, and evidence interfaces with reproduction, candidate
         * evaluation, controlled analysis, transfer assurance, and measurement. Kanavouras et al.
         * (2024), pages 4 and 8-10, provides the REST integration and parameter basis. Formal model
         * exchange, evidence custody, and complete assurance behavior are project additions.
         */

        part modelControlInterface : 'Model Control Interface Manager';
        part analysisExecutionInterface : 'Analysis Execution Interface Manager';
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager';

        part analysisReproductionManager : 'Analysis Reproduction Manager';
        part candidateEvaluationManager : 'Candidate Evaluation Manager';
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator';

        part transferAssuranceManager : 'Transfer Assurance Manager';
        part evaluationMeasurementManager : 'Evaluation Measurement Manager';
    }

    part def <'GY-NL-00'> 'Git and YAML Candidate Node Logical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Separate node-logical decomposition of the complete framework black box. All eighteen
         * logical components from LA-00 occur once across the three nodes.
         */

        part participantAccessAndReview : 'Participant Access and Review Logical Node';
        part versionedRecordsAndWorkflow
            : 'Versioned Engineering Records and Workflow Logical Node';
        part modelAnalysisAndAssurance
            : 'Model Analysis and Assurance Integration Logical Node';
    }

    // Step 7: minimum physical component inventory.

    part def 'Git and YAML Candidate Physical Component' {
        doc
        /* High-level implementation component retained only when it distinguishes the candidate or
         * identifies a required candidate addition.
         */
    }

    part def 'Git and YAML Candidate Software Component'
        :> 'Git and YAML Candidate Physical Component';

    part def 'Git and YAML Candidate Data Component'
        :> 'Git and YAML Candidate Physical Component';

    part def 'Git and YAML Candidate Hardware or Service Component'
        :> 'Git and YAML Candidate Physical Component';

    part def 'Git and YAML Candidate Procedure Component'
        :> 'Git and YAML Candidate Physical Component';

    part def 'Participant Browser Host'
        :> 'Git and YAML Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract participant device. The sources establish browser access but do not
         * constrain the device, operating system, or resource sizing.
         */
    }

    part def 'Modern Web Browser' :> 'Git and YAML Candidate Software Component' {
        doc
        /* Reported design. Provides participant access without a specialized client application. */
    }

    part def 'Nuxt and Tailwind Engineering Interface'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Reported early implementation in Kanavouras et al. (2024), pages 5 and 9. The complete
         * framework request, review, and discrepancy views remain candidate-specific additions.
         */
    }

    part def <'GY-PN-01'> 'Browser Client Physical Node' {
        doc
        /* Participant-side node. It contains the only client resources established by the
         * lightweight web design.
         */

        part host : 'Participant Browser Host';
        part browser : 'Modern Web Browser';
        part engineeringInterface : 'Nuxt and Tailwind Engineering Interface';
    }

    part def 'Engineering Data Service Host'
        :> 'Git and YAML Candidate Hardware or Service Component' {
        doc
        /* Reported local-server or cloud deployment choice with unspecified product, operating
         * system, packaging, resource sizing, redundancy, and physical location.
         */
    }

    part def 'Python Engineering Data Backend'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Reported early proof-of-concept component. Serves engineering records and coordinates
         * repository operations. Production behavior remains unvalidated.
         */
    }

    part def 'Engineering Data REST API'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Reported design. Provides documented programmatic access to engineering records for the
         * browser, adapters, analyses, and automations.
         */
    }

    part def 'Git Version Control Service'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Reported design and demonstrated docs-as-code workflow. Records authors, revisions,
         * differences, branches, merges, tags, and release history for native records.
         */
    }

    part def 'YAML Engineering Record Set'
        :> 'Git and YAML Candidate Data Component' {
        doc
        /* Reported design and implementation pattern. Stores human and machine readable entities,
         * parameters, references, needs, user stories, data structures, components, trace links,
         * and analysis references.
         */
    }

    part def 'Record Schema and Workflow Definitions'
        :> 'Git and YAML Candidate Data Component' {
        doc
        /* Synthesized from typed parameters, parameter states, M30ML records, derivedFrom links,
         * component metadata, and version information. Complete project schemas remain proposed.
         */
    }

    part def 'Docs as Code Generator'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Reported implementation pattern in Chiu (2023), pages 52-75. Generates diagrams, tables,
         * reports, review material, and procedure documents from YAML source records.
         */
    }

    part def 'Generated Engineering View Set'
        :> 'Git and YAML Candidate Data Component' {
        doc
        /* Reported implementation pattern. Contains human readable derived views tied to the exact
         * source revision and generator environment that produced them.
         */
    }

    part def 'Issue and Notification Integration'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Reported design and demonstrated workflow pattern. Connects changes and generated
         * architecture content to development issues and team notifications.
         */
    }

    part def <'GY-PN-02'> 'Git and YAML Engineering Data Service Physical Node' {
        doc
        /* Combines the lightweight web service design with the demonstrated Git and YAML docs-as-
         * code record and generation workflow. Exact local or cloud deployment remains open.
         */

        part host : 'Engineering Data Service Host';
        part backend : 'Python Engineering Data Backend';
        part restAPI : 'Engineering Data REST API';
        part versionControl : 'Git Version Control Service';
        part engineeringRecords : 'YAML Engineering Record Set';
        part recordSchemas : 'Record Schema and Workflow Definitions';
        part documentGenerator : 'Docs as Code Generator';
        part generatedViews : 'Generated Engineering View Set';
        part issueAndNotificationIntegration : 'Issue and Notification Integration';
    }

    part def 'Integration Runner Host'
        :> 'Git and YAML Candidate Hardware or Service Component' {
        doc
        /* Inferred abstract compute resource for adapters, validation, impact analysis, controlled
         * execution, and evidence packaging. Its deployment and resource sizing remain unspecified.
         */
    }

    part def 'External Model Record Adapter'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Proposed. Reads designated records from the external Versioned System Model, preserves
         * source identity, maps them to YAML records, and returns only approved updates through
         * IF-04. The selected sources demonstrate no bidirectional formal-model adapter.
         */
    }

    part def 'External Analysis Tool Adapter'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Reported REST integration pattern with candidate-specific implementation. Builds
         * controlled requests and correlates raw results returned through IF-05.
         */
    }

    part def 'Evidence Repository Adapter'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Proposed. Exports accepted evidence packages and retrieves retained records through IF-06.
         * The selected sources do not establish this repository contract.
         */
    }

    part def 'YAML Schema and Stable Identity Validator'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Proposed from reported structures. Checks schemas, stable identifiers, types, units,
         * references, trace targets, and component dependency declarations.
         */
    }

    part def 'Transfer and Consistency Checker'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Proposed. Checks source revision, evidence baseline, completeness, semantic compatibility,
         * provenance, and applicable traces before accepting a transfer.
         */
    }

    part def 'Dependency and Change Impact Analyzer'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Synthesized. Combines Git differences, trace links, parameter dependencies, component
         * dependencies, and document-generation dependencies to identify affected evidence.
         */
    }

    part def 'Reproducible Analysis Package'
        :> 'Git and YAML Candidate Data Component' {
        doc
        /* Proposed. Retains accepted inputs, scripts, dependency versions, environment declarations,
         * raw outputs, tolerances, uncertainty, and execution status.
         */
    }

    part def 'Reproducible Analysis Packager'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Proposed. Creates and checks the controlled package used for independent reconstruction
         * and analysis reproduction.
         */

        part output : 'Reproducible Analysis Package';
    }

    part def 'Evaluation Manifest Runner'
        :> 'Git and YAML Candidate Software Component' {
        doc
        /* Proposed. Applies the fixed framework evaluation manifest and preserves raw observations
         * and correctness gates for the common candidate comparison protocol.
         */
    }

    part def <'GY-PN-03'> 'Model and Analysis Integration Runner Physical Node' {
        doc
        /* Separates tool-specific adapters and assurance behavior from the lightweight engineering
         * data service. This limits the effect of model, analysis, repository, and schema changes.
         */

        part host : 'Integration Runner Host';
        part modelAdapter : 'External Model Record Adapter';
        part analysisAdapter : 'External Analysis Tool Adapter';
        part evidenceAdapter : 'Evidence Repository Adapter';
        part schemaValidator : 'YAML Schema and Stable Identity Validator';
        part transferChecker : 'Transfer and Consistency Checker';
        part impactAnalyzer : 'Dependency and Change Impact Analyzer';
        part reproductionPackager : 'Reproducible Analysis Packager';
        part evaluationRunner : 'Evaluation Manifest Runner';
    }

    part def 'Branch Review Merge and Release Procedure'
        :> 'Git and YAML Candidate Procedure Component' {
        doc
        /* Synthesized from reported Git workflows. Creates a controlled change, reviews source and
         * generated differences, approves or rejects it, and identifies an accepted release.
         */
    }

    part def 'External Artifact Import and Acceptance Procedure'
        :> 'Git and YAML Candidate Procedure Component' {
        doc
        /* Proposed. Registers source identity, maps designated records, runs transfer checks,
         * retains discrepancies, and accepts only a verified native projection.
         */
    }

    part def 'Controlled Analysis and Reproduction Procedure'
        :> 'Git and YAML Candidate Procedure Component' {
        doc
        /* Proposed from the reported API and version-control patterns. Builds a locked execution
         * package, invokes a designated external analysis, verifies results, and repeats execution
         * from a clean declared environment.
         */
    }

    part def 'Generated View and Finding Review Procedure'
        :> 'Git and YAML Candidate Procedure Component' {
        doc
        /* Synthesized. Generates review views from one source revision, records findings through the
         * issue workflow, and retains dispositions against the released baseline.
         */
    }

    part def 'Evidence Release Export and Restore Procedure'
        :> 'Git and YAML Candidate Procedure Component' {
        doc
        /* Proposed. Packages source records, mappings, generated views, analyses, discrepancies,
         * findings, and environment declarations for external custody and later reconstruction.
         */
    }

    part def <'GY-PC-01'> 'Git and YAML Candidate Operating Procedures' {
        part releaseChange : 'Branch Review Merge and Release Procedure';
        part acceptExternalArtifact : 'External Artifact Import and Acceptance Procedure';
        part reproduceAnalysis : 'Controlled Analysis and Reproduction Procedure';
        part reviewGeneratedViews : 'Generated View and Finding Review Procedure';
        part exportAndRestoreEvidence : 'Evidence Release Export and Restore Procedure';
    }

    part def <'GY-PA-00'> 'Lightweight Git and YAML Candidate Physical Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Minimum physical decomposition for comparison. Explicit logical-to-physical allocations,
         * ports, connectors, physical service activities, satisfy relationships, and measured MOPs
         * are intentionally deferred to the next OOSEM steps.
         */

        part browserClient : 'Browser Client Physical Node';
        part engineeringDataService : 'Git and YAML Engineering Data Service Physical Node';
        part integrationRunner : 'Model and Analysis Integration Runner Physical Node';
        part operatingProcedures : 'Git and YAML Candidate Operating Procedures';
    }

    part gitYamlCandidateNodeLogical : 'Git and YAML Candidate Node Logical Framework';
    part gitYamlCandidatePhysical : 'Lightweight Git and YAML Candidate Physical Framework';
} // package FrameworkCandidateGitYaml
