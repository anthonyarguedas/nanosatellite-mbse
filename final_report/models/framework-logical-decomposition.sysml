// Initial OOSEM logical decomposition of the framework.
package FrameworkLogicalDecomposition {
    private import ScalarValues::Boolean;
    private import ScalarValues::String;
    private import FrameworkBlackBoxSpecification
            ::'Specified Nanosatellite EPS Engineering Framework';
    private import FrameworkBoundaryInterfaces::*;
    private import FrameworkExchangeDefinitions::*;

    doc
    /* This package defines the implementation-independent decomposition used to begin the OOSEM
     * Define Logical Architecture activity. The logical framework inherits the complete black-box
     * specification and adds only abstract responsibilities. Products, file formats, protocols,
     * deployment nodes, and physical components remain open for physical architecture synthesis.
     *
     * Evidence basis: the mandatory black-box requirements and their literature traces are the
     * primary architecture inputs. Buruso et al. (2026), Secs. 4.4 and 5.1 and Table 5, support
     * lifecycle continuity, interoperability, modularity, and resource fit. Rostamnia et al. (2026),
     * Secs. 8.4-8.6 and Table 13, support explicit interfaces, shared semantics, configuration
     * governance, provenance, and assurance. Rojas Ramirez et al. (2022), Sec. 4.2.3, supports
     * transfer verification. Vizitiu et al. (2025), Sec. 4.7 and Table 3, supports efficiency,
     * collaboration, traceability, error reduction, and flexibility as evaluation concerns.
     */

    part def 'Logical Component' {
        doc
        /* Abstract responsibility within the framework logical design. A logical component may be
         * allocated to hardware, software, data, or procedure components in multiple ways.
         */
    }

    part def 'External Interface Component' :> 'Logical Component' {
        doc
        /* Mediates one black-box boundary while preserving its defined item types, directions,
         * transfer status, and semantics without selecting a transport or file format.
         */
    }

    part def 'Application Component' :> 'Logical Component' {
        doc
        /* Performs the application logic that transforms black-box requests and controlled records
         * into the assessments, packages, verdicts, and statuses required by the service functions.
         */
    }

    part def 'Infrastructure Component' :> 'Logical Component' {
        doc
        /* Manages internally generated control, configuration, evidence, provenance, transfer
         * assurance, and measurement responsibilities shared by the application components.
         */
    }

    metadata def logicalStore;

    item def 'Logical Outcome Control' {
        attribute accepted : Boolean;
        item discrepancies : 'Discrepancy Set';
        doc
        /* Internal authorization or discrepancy outcome applied by workflow control. It preserves
         * the terminal meaning of a typed service outcome without adding a black-box exchange.
         */
    }

    item def 'Logical Measurement Record' {
        attribute measureIdentifier : String;
        item evidenceBaseline : 'Baseline Reference';
        attribute observedValue : String;
        attribute uncertainty : String;
        item discrepancies : 'Discrepancy Set';
        doc
        /* Internal raw observation and status used to calculate an inherited MOP under the fixed
         * evaluation protocol. The representation does not choose a data format or tool.
         */
    }

    item def 'Logical Workflow State Store' {
        item selectedContextBaseline : 'Baseline Reference' [0..1];
        item configurationStatuses : 'Configuration Status' [0..*];
        item evidenceAssessments : 'Evidence Chain Assessment' [0..*];
        item reproductionVerdicts : 'Reproduction Verdict' [0..*];
        item changePackages : 'Change Evidence Package' [0..*];
        item candidateComparisonPackages : 'Candidate Comparison Package' [0..*];
        item reviewStatuses : 'Review Status' [0..*];
        item discrepancies : 'Discrepancy Set' [0..*];
    }

    item def 'Logical Baseline and Configuration Store' {
        item baselines : 'Baseline Reference' [0..*];
        item commonCorePackages : 'Common Core Package' [0..*];
        item caseConfigurationDrafts : 'Case Configuration Draft' [0..*];
        item controlledCaseConfigurations : 'Controlled Case Configuration' [0..*];
        item changeRevisionPackages : 'Change Revision Package' [0..*];
    }

    item def 'Logical Evidence and Provenance Store' {
        item modelRecords : 'Controlled Model Records' [0..*];
        item evidenceRecords : 'Retained Evidence Records' [0..*];
        item artifactRegistrations : 'Artifact Registration Set' [0..*];
        item evidenceAssessments : 'Evidence Chain Assessment' [0..*];
        item analysisResults : 'Analysis Result Package' [0..*];
        item reproductionVerdicts : 'Reproduction Verdict' [0..*];
        item changePackages : 'Change Evidence Package' [0..*];
        item candidateComparisonPackages : 'Candidate Comparison Package' [0..*];
        item reviewPackages : 'Review Package' [0..*];
        item reviewStatuses : 'Review Status' [0..*];
        item traces : 'Trace and Provenance Records' [0..*];
    }

    item def 'Logical Measurement Store' {
        item records : 'Logical Measurement Record' [0..*];
    }

    port def 'Logical Baseline Control Port' {
        inout item baselineReference : 'Baseline Reference';
        inout item commonCorePackage : 'Common Core Package';
        inout item caseConfigurationDraft : 'Case Configuration Draft';
        inout item controlledCaseConfiguration : 'Controlled Case Configuration';
        inout item changeRevisionPackage : 'Change Revision Package';
    }

    port def 'Logical Evidence Management Port' {
        inout item modelRecords : 'Controlled Model Records';
        inout item evidenceRecords : 'Retained Evidence Records';
        inout item artifactRegistrations : 'Artifact Registration Set';
        inout item evidenceChainAssessment : 'Evidence Chain Assessment';
        inout item controlledCaseConfiguration : 'Controlled Case Configuration';
        inout item configurationStatus : 'Configuration Status';
        inout item analysisResult : 'Analysis Result Package';
        inout item reproductionVerdict : 'Reproduction Verdict';
        inout item changeEvidencePackage : 'Change Evidence Package';
        inout item candidateComparisonPackage : 'Candidate Comparison Package';
        inout item reviewPackage : 'Review Package';
        inout item reviewStatus : 'Review Status';
    }

    port def 'Logical Workflow Control Port' {
        inout item evidenceChainAssessment : 'Evidence Chain Assessment';
        inout item configurationStatus : 'Configuration Status';
        inout item reproductionVerdict : 'Reproduction Verdict';
        inout item changeEvidencePackage : 'Change Evidence Package';
        inout item candidateComparisonPackage : 'Candidate Comparison Package';
        inout item reviewStatus : 'Review Status';
        inout item outcomeControl : 'Logical Outcome Control';
    }

    port def 'Logical Transfer Assurance Port' {
        inout item transferVerification : 'Transfer Verification Record';
    }

    port def 'Logical Measurement Port' {
        inout item measurementRecord : 'Logical Measurement Record';
    }

    // External interface components correspond one-to-one with the six black-box interfaces.
    part def <'LIF-01'> 'Mission Application Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-01 traffic with the Academic Mission Team. */

        port boundary : 'Mission Application Port';
        port services : 'Mission Application Port';
        port assurance : 'Logical Transfer Assurance Port';
    }

    part def <'LIF-02'> 'Research Governance Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-02 traffic with the Academic Researcher. */

        port boundary : 'Research Governance Port';
        port services : 'Research Governance Port';
        port assurance : 'Logical Transfer Assurance Port';
    }

    part def <'LIF-03'> 'Independent Review Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-03 traffic with the Reviewer. */

        port boundary : 'Independent Review Port';
        port services : 'Independent Review Port';
        port assurance : 'Logical Transfer Assurance Port';
    }

    part def <'LIF-04'> 'Model Control Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-04 traffic with the Versioned System Model. */

        port boundary : 'Model Control Port';
        port services : 'Model Control Port';
        port assurance : 'Logical Transfer Assurance Port';
    }

    part def <'LIF-05'> 'Analysis Execution Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-05 traffic with Analysis Tools. */

        port boundary : 'Analysis Execution Port';
        port services : 'Analysis Execution Port';
        port assurance : 'Logical Transfer Assurance Port';
    }

    part def <'LIF-06'> 'Evidence Custody Interface Manager' :> 'External Interface Component' {
        doc
        /* Mediates IF-06 traffic with the Evidence Repository. */

        port boundary : 'Evidence Custody Port';
        port services : 'Evidence Custody Port';
        port assurance : 'Logical Transfer Assurance Port';
    }

    // Service managers realize the six black-box services. The reusable F-03.2 analysis-control
    // action is assigned separately because it is also invoked by F-04 and F-05.
    part def <'LAP-01'> 'Evidence Chain Manager' :> 'Application Component' {
        doc
        /* Registers externally produced requirement, model, and result revisions, scopes and
         * validates designated evidence chains, and issues their assessments.
         */

        port missionApplication : 'Mission Application Port';
        port modelControl : 'Model Control Port';
        port baselineControl : 'Logical Baseline Control Port';
        port evidenceManagement : 'Logical Evidence Management Port';
        port workflowControl : 'Logical Workflow Control Port';
        port measurement : 'Logical Measurement Port';
    }

    part def <'LAP-02'> 'Case Configuration Manager' :> 'Application Component' {
        doc
        /* Captures, validates, and issues controlled EPS case configurations and status. */

        port missionApplication : 'Mission Application Port';
        port researchGovernance : 'Research Governance Port';
        port modelControl : 'Model Control Port';
        port baselineControl : 'Logical Baseline Control Port';
        port evidenceManagement : 'Logical Evidence Management Port';
        port workflowControl : 'Logical Workflow Control Port';
        port measurement : 'Logical Measurement Port';
    }

    part def <'LAP-03'> 'Analysis Reproduction Manager' :> 'Application Component' {
        doc
        /* Prepares controlled reproduction packages, evaluates results, and issues verdicts. */

        port independentReview : 'Independent Review Port';
        port controlledAnalysis : 'Analysis Execution Port';
        port selectedReviewReproduction : 'Independent Review Port';
        port baselineControl : 'Logical Baseline Control Port';
        port evidenceManagement : 'Logical Evidence Management Port';
        port workflowControl : 'Logical Workflow Control Port';
        port measurement : 'Logical Measurement Port';
    }

    part def <'LAP-07'> 'Controlled Analysis Coordinator' :> 'Application Component' {
        doc
        /* Coordinates the shared controlled-analysis action used by reproduction, change assessment,
         * and candidate evaluation without selecting an analysis tool or execution technology.
         */

        port analysisExecution : 'Analysis Execution Port';
        port reproduction : 'Analysis Execution Port';
        port designChange : 'Analysis Execution Port';
        port candidateEvaluation : 'Analysis Execution Port';
    }

    part def <'LAP-04'> 'Design Change Assessment Manager' :> 'Application Component' {
        doc
        /* Validates change requests, determines impact, and assembles change evidence. */

        port missionApplication : 'Mission Application Port';
        port modelControl : 'Model Control Port';
        port controlledAnalysis : 'Analysis Execution Port';
        port baselineControl : 'Logical Baseline Control Port';
        port evidenceManagement : 'Logical Evidence Management Port';
        port workflowControl : 'Logical Workflow Control Port';
        port measurement : 'Logical Measurement Port';
    }

    part def <'LAP-05'> 'Candidate Evaluation Manager' :> 'Application Component' {
        doc
        /* Establishes a common comparison basis, gates feasibility, and compares EPS candidates. */

        port missionApplication : 'Mission Application Port';
        port researchGovernance : 'Research Governance Port';
        port modelControl : 'Model Control Port';
        port controlledAnalysis : 'Analysis Execution Port';
        port baselineControl : 'Logical Baseline Control Port';
        port evidenceManagement : 'Logical Evidence Management Port';
        port workflowControl : 'Logical Workflow Control Port';
        port measurement : 'Logical Measurement Port';
    }

    part def <'LAP-06'> 'Design Review Manager' :> 'Application Component' {
        doc
        /* Assembles review packages, coordinates selected reproduction, and manages findings. */

        port missionApplication : 'Mission Application Port';
        port independentReview : 'Independent Review Port';
        port selectedReproduction : 'Independent Review Port';
        port baselineControl : 'Logical Baseline Control Port';
        port evidenceManagement : 'Logical Evidence Management Port';
        port workflowControl : 'Logical Workflow Control Port';
        port measurement : 'Logical Measurement Port';
    }

    // Infrastructure components provide shared logical resources and controls.
    part def <'LIN-01'> 'Workflow Control Manager' :> 'Infrastructure Component' {
        doc
        /* Dispatches service work, applies terminal outcome guards, exposes discrepancies, and
         * controls recovery according to the inherited operational state behavior.
         */

        port services : 'Logical Workflow Control Port';
        ref #logicalStore item workflowStateStore : 'Logical Workflow State Store';
    }

    part def <'LIN-02'> 'Transfer Assurance Manager' :> 'Infrastructure Component' {
        doc
        /* Checks producer, source revision, configuration and evidence-baseline identity,
         * structural completeness, semantic compatibility, provenance, and applicable traces before
         * any boundary transfer is accepted.
         */

        port interfaceManagers : 'Logical Transfer Assurance Port';
    }

    part def <'LIN-03'> 'Baseline and Configuration Manager' :> 'Infrastructure Component' {
        doc
        /* Controls the common core and generic-model identity, case configurations, immutable
         * evidence-baseline and external source-revision identities, approved adaptations, and
         * distinct successor revisions.
         */

        port services : 'Logical Baseline Control Port';
        ref #logicalStore item configurationStore : 'Logical Baseline and Configuration Store';
    }

    part def <'LIN-04'> 'Evidence and Provenance Manager' :> 'Infrastructure Component' {
        doc
        /* Retains and retrieves required artifact registrations, model and evidence revisions,
         * assessments, verdicts, packages, discrepancies, traces, and provenance by artifact,
         * source-revision, and evidence-baseline identity.
         */

        port services : 'Logical Evidence Management Port';
        port custody : 'Evidence Custody Port';
        ref #logicalStore item evidenceStore : 'Logical Evidence and Provenance Store';
    }

    part def <'LIN-05'> 'Evaluation Measurement Manager' :> 'Infrastructure Component' {
        doc
        /* Applies the fixed evaluation manifest and measurement protocols while preserving raw
         * observations, correctness gates, uncertainty, and derived MOP results.
         */

        port services : 'Logical Measurement Port';
        ref #logicalStore item measurementStore : 'Logical Measurement Store';
    }

    part def <'LA-00'> 'Logical Nanosatellite EPS Engineering Framework'
        :> 'Specified Nanosatellite EPS Engineering Framework' {
        doc
        /* Logical specialization of the complete framework black box. The parts below define the
         * initial responsibility decomposition. Their abstract ports and logical store references
         * support LA-01. Interactions, properties, and state behavior remain subject to later
         * logical architecture refinement.
         */

        part missionApplicationInterface : 'Mission Application Interface Manager';
        part researchGovernanceInterface : 'Research Governance Interface Manager';
        part independentReviewInterface : 'Independent Review Interface Manager';
        part modelControlInterface : 'Model Control Interface Manager';
        part analysisExecutionInterface : 'Analysis Execution Interface Manager';
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager';

        part evidenceChainManager : 'Evidence Chain Manager';
        part caseConfigurationManager : 'Case Configuration Manager';
        part analysisReproductionManager : 'Analysis Reproduction Manager';
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator';
        part designChangeAssessmentManager : 'Design Change Assessment Manager';
        part candidateEvaluationManager : 'Candidate Evaluation Manager';
        part designReviewManager : 'Design Review Manager';

        part workflowControlManager : 'Workflow Control Manager';
        part transferAssuranceManager : 'Transfer Assurance Manager';
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager';
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager';
        part evaluationMeasurementManager : 'Evaluation Measurement Manager';
    }

    part frameworkLogical : 'Logical Nanosatellite EPS Engineering Framework';
} // package FrameworkLogicalDecomposition
