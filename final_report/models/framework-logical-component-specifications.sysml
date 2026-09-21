// Logical component specifications and system-requirement allocations for the framework.
package FrameworkLogicalComponentSpecifications {
    private import Base::Anything;
    private import ScalarValues::String;
    private import ModelingMetadata::refinement;
    private import FrameworkBlackBoxFunctions::*;
    private import FrameworkLogicalDecomposition::*;
    private import FrameworkSystemRequirements::*;

    doc
    /* This package specifies the logical components after the initial decomposition, logical
     * activities, and internal block architecture. Each specified component specializes its LA-00
     * component type, inherits its ports and logical store references, and adds the actions assigned
     * in the logical activities. The direct allocate relationships map every mandatory system
     * requirement leaf to one or more responsible logical features.
     *
     * The component requirements express allocated contributions to the black-box requirements.
     * They introduce no new stakeholder requirement, threshold, implementation technology, format,
     * repository, deployment, or physical property allocation. System MOP values remain system-level
     * until analysis supplies a justified component budget.
     */

    metadata def LogicalComponentRequirementTrace {
        ref sourceSystemRequirement : Anything [1..*];
        attribute allocatedFeatureIdentifier : String;
        attribute rationale : String;
    }

    // External interface component specifications.

    part def <'LCS-LIF-01'> 'Specified Mission Application Interface Manager'
        :> 'Mission Application Interface Manager' {
        doc
        /* Inherits boundary and services Mission Application Ports plus the transfer-assurance port.
         * It mediates the typed request, assessment, configuration, change, comparison, and review
         * exchanges defined by IF-01.
         */

        action receiveMissionApplicationRequests;
        action publishMissionApplicationOutcomes;
    }

    part def <'LCS-LIF-02'> 'Specified Research Governance Interface Manager'
        :> 'Research Governance Interface Manager' {
        doc
        /* Inherits boundary and services Research Governance Ports plus the transfer-assurance port.
         * It mediates case-adaptation and candidate-evaluation exchanges defined by IF-02.
         */

        action receiveResearchGovernanceInputs;
        action publishResearchGovernanceOutputs;
    }

    part def <'LCS-LIF-03'> 'Specified Independent Review Interface Manager'
        :> 'Independent Review Interface Manager' {
        doc
        /* Inherits boundary and services Independent Review Ports plus the transfer-assurance port.
         * It mediates reproduction and review exchanges defined by IF-03.
         */

        action receiveIndependentReviewInputs;
        action publishIndependentReviewOutputs;
    }

    part def <'LCS-LIF-04'> 'Specified Model Control Interface Manager'
        :> 'Model Control Interface Manager' {
        doc
        /* Inherits boundary and services Model Control Ports plus the transfer-assurance port.
         * It mediates controlled model, common-core, candidate, configuration, registration, and
         * authorized-revision exchanges defined by IF-04.
         */

        action receiveControlledModelRecords;
        action publishControlledModelUpdates;
    }

    part def <'LCS-LIF-05'> 'Specified Analysis Execution Interface Manager'
        :> 'Analysis Execution Interface Manager' {
        doc
        /* Inherits boundary and services Analysis Execution Ports plus the transfer-assurance port.
         * It submits controlled execution requests and receives correlated raw results through IF-05.
         */

        action submitAnalysisExecutionRequest;
        action receiveAnalysisExecutionResult;
    }

    part def <'LCS-LIF-06'> 'Specified Evidence Custody Interface Manager'
        :> 'Evidence Custody Interface Manager' {
        doc
        /* Inherits boundary and services Evidence Custody Ports plus the transfer-assurance port.
         * It mediates retained evidence, assessment, configuration, package, verdict, and status
         * exchanges defined by IF-06.
         */

        action retrieveRetainedEvidenceRecords;
        action submitControlledEvidenceRecords;
    }

    // Application component specifications. Typed actions retain their black-box definitions.

    part def <'LCS-LAP-01'> 'Specified Evidence Chain Manager' :> 'Evidence Chain Manager' {
        doc
        /* Inherits mission-application, model-control, baseline-control, evidence-management,
         * workflow-control, and measurement ports. It realizes F-01.0 through F-01.3.
         */

        action registerExternalArtifacts : 'Register External Engineering Artifacts';
        action scopeEvidenceChain : 'Scope Evidence Chain';
        action validateEvidenceChain : 'Validate Evidence Chain';
        action issueEvidenceChainAssessment : 'Issue Evidence Chain Assessment';
    }

    part def <'LCS-LAP-02'> 'Specified Case Configuration Manager' :> 'Case Configuration Manager' {
        doc
        /* Inherits mission-application, research-governance, model-control, baseline-control,
         * evidence-management, workflow-control, and measurement ports. It realizes F-02.1 through
         * F-02.3.
         */

        action captureCaseConfiguration : 'Capture Case Configuration';
        action validateCaseConfiguration : 'Validate Case Configuration';
        action issueConfigurationStatus : 'Issue Configuration Status';
    }

    part def <'LCS-LAP-03'> 'Specified Analysis Reproduction Manager'
        :> 'Analysis Reproduction Manager' {
        doc
        /* Inherits independent-review, controlled-analysis, selected-review-reproduction,
         * baseline-control, evidence-management, workflow-control, and measurement ports. It
         * realizes F-03.1, F-03.3, and F-03.4.
         */

        action prepareReproductionPackage : 'Prepare Reproduction Package';
        action evaluateReproducedResult : 'Evaluate Reproduced Result';
        action issueReproductionVerdict : 'Issue Reproduction Verdict';
    }

    part def <'LCS-LAP-07'> 'Specified Controlled Analysis Coordinator'
        :> 'Controlled Analysis Coordinator' {
        doc
        /* Inherits analysis-execution, reproduction, design-change, and candidate-evaluation ports.
         * It realizes the shared F-03.2 action for F-03, F-04, and F-05.
         */

        action coordinateControlledAnalysis : 'Coordinate Controlled Analysis';
    }

    part def <'LCS-LAP-04'> 'Specified Design Change Assessment Manager'
        :> 'Design Change Assessment Manager' {
        doc
        /* Inherits mission-application, model-control, controlled-analysis, baseline-control,
         * evidence-management, workflow-control, and measurement ports. It realizes F-04.1 through
         * F-04.4.
         */

        action validateChangeRequest : 'Validate Change Request';
        action analyzeChangeImpact : 'Analyze Change Impact';
        action validateRegeneratedEvidence : 'Validate Regenerated Evidence';
        action assembleChangeEvidencePackage : 'Assemble Change Evidence Package';
    }

    part def <'LCS-LAP-05'> 'Specified Candidate Evaluation Manager'
        :> 'Candidate Evaluation Manager' {
        doc
        /* Inherits mission-application, research-governance, model-control, controlled-analysis,
         * baseline-control, evidence-management, workflow-control, and measurement ports. It
         * realizes F-05.1 through F-05.4.
         */

        action validateComparisonBasis : 'Validate Comparison Basis';
        action determineCandidateFeasibility : 'Determine Candidate Feasibility';
        action compareCandidateArchitectures : 'Compare Candidate Architectures';
        action issueCandidateComparison : 'Issue Candidate Comparison';
    }

    part def <'LCS-LAP-06'> 'Specified Design Review Manager' :> 'Design Review Manager' {
        doc
        /* Inherits mission-application, independent-review, selected-reproduction, baseline-control,
         * evidence-management, workflow-control, and measurement ports. It realizes F-06.1 through
         * F-06.4.
         */

        action assembleReviewPackage : 'Assemble Review Package';
        action coordinateSelectedReproduction : 'Coordinate Selected Reproduction';
        action manageReviewFindings : 'Manage Review Findings';
        action issueReviewStatus : 'Issue Review Status';
    }

    // Infrastructure component specifications. Untyped actions are logical operations allocated
    // from the existing black-box control, interface, store, performance, quality, and resource
    // requirements. They do not add behavior beyond the logical activities and inherited SM-01.

    part def <'LCS-LIN-01'> 'Specified Workflow Control Manager' :> 'Workflow Control Manager' {
        doc
        /* Inherits the workflow-control port and the Workflow State Store reference. It applies the
         * control responsibilities expressed by SM-01 without defining its own component state
         * machine in this step.
         */

        action establishControlledContext;
        action dispatchVerifiedRequest;
        action applyTerminalOutcomeGuard;
        action recordExceptionalOutcome;
        action controlRecovery;
        action preserveContextAndBaseline;
    }

    part def <'LCS-LIN-02'> 'Specified Transfer Assurance Manager' :> 'Transfer Assurance Manager' {
        doc
        /* Inherits the transfer-assurance port. It performs common pre-acceptance checks and keeps
         * rejected-transfer status explicit for the interface managers.
         */

        action verifyBoundaryTransfer;
        action preserveRejectedTransferRecord;
    }

    part def <'LCS-LIN-03'> 'Specified Baseline and Configuration Manager'
        :> 'Baseline and Configuration Manager' {
        doc
        /* Inherits the baseline-control port and the Baseline and Configuration Store reference. It
         * controls identities, configuration declarations, approved adaptations, and reconstruction
         * declarations without selecting a configuration-management product.
         */

        action controlCaseConfiguration;
        action preserveBaselineIdentity;
        action declareExecutionEnvironment;
        action assembleReconstructionDeclaration;
    }

    part def <'LCS-LIN-04'> 'Specified Evidence and Provenance Manager'
        :> 'Evidence and Provenance Manager' {
        doc
        /* Inherits evidence-management and custody ports plus the Evidence and Provenance Store
         * reference. It retains controlled records and keeps their provenance and decision context
         * available for review and reconstruction.
         */

        action retainControlledRecords;
        action preserveOutputProvenance;
        action retainDecisionTransparency;
        action supplyReconstructionEvidence;
    }

    part def <'LCS-LIN-05'> 'Specified Evaluation Measurement Manager'
        :> 'Evaluation Measurement Manager' {
        doc
        /* Inherits the measurement port and Measurement Store reference. It records observations,
         * uncertainty, correctness gates, and the inherited system MOP results. It does not allocate
         * a component-specific target or threshold.
         */

        action recordTraceCoverage;
        action recordReproductionSuccess;
        action recordCriticalDiscrepancyStatus;
        action recordCompletedCaseCount;
        action recordAdaptationStatus;
        action recordChangeTurnaround;
        action recordCaseAdaptationEffort;
        action recordIndependentReproductionEffort;
        action recordAdoptionEffort;
        action recordDirectFrameworkCost;
        action evaluateConsistencyAssurance;
        action gateComparativeCredit;
    }

    // Derived logical component requirements.

    requirement <'LCR-LIF-01'> 'Mission Application Interface Manager Requirement' {
        subject manager : 'Specified Mission Application Interface Manager';
        doc
        /* The manager shall mediate every IF-01 item in its declared direction through the inherited
         * Mission Application Ports.
         */
        require constraint statement {
            doc
            /* The allocated IF-01 contract is preserved at the logical boundary. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement =
            FrameworkSystemRequirements::'Mission Application Interface Contract';
        allocatedFeatureIdentifier = "boundary, services";
        rationale = "LIF-01 is the sole logical mediator of IF-01.";
    }

    requirement <'LCR-LIF-02'> 'Research Governance Interface Manager Requirement' {
        subject manager : 'Specified Research Governance Interface Manager';
        doc
        /* The manager shall mediate every IF-02 item in its declared direction through the inherited
         * Research Governance Ports.
         */
        require constraint statement {
            doc
            /* The allocated IF-02 contract is preserved at the logical boundary. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement =
            FrameworkSystemRequirements::'Research Governance Interface Contract';
        allocatedFeatureIdentifier = "boundary, services";
        rationale = "LIF-02 is the sole logical mediator of IF-02.";
    }

    requirement <'LCR-LIF-03'> 'Independent Review Interface Manager Requirement' {
        subject manager : 'Specified Independent Review Interface Manager';
        doc
        /* The manager shall mediate every IF-03 item in its declared direction through the inherited
         * Independent Review Ports.
         */
        require constraint statement {
            doc
            /* The allocated IF-03 contract is preserved at the logical boundary. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement =
            FrameworkSystemRequirements::'Independent Review Interface Contract';
        allocatedFeatureIdentifier = "boundary, services";
        rationale = "LIF-03 is the sole logical mediator of IF-03.";
    }

    requirement <'LCR-LIF-04'> 'Model Control Interface Manager Requirement' {
        subject manager : 'Specified Model Control Interface Manager';
        doc
        /* The manager shall mediate every IF-04 item in its declared direction through the inherited
         * Model Control Ports.
         */
        require constraint statement {
            doc
            /* The allocated IF-04 contract is preserved at the logical boundary. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = FrameworkSystemRequirements::'Model Control Interface Contract';
        allocatedFeatureIdentifier = "boundary, services";
        rationale = "LIF-04 is the sole logical mediator of IF-04.";
    }

    requirement <'LCR-LIF-05'> 'Analysis Execution Interface Manager Requirement' {
        subject manager : 'Specified Analysis Execution Interface Manager';
        doc
        /* The manager shall mediate every IF-05 item in its declared direction through the inherited
         * Analysis Execution Ports.
         */
        require constraint statement {
            doc
            /* The allocated IF-05 contract is preserved at the logical boundary. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement =
            FrameworkSystemRequirements::'Analysis Execution Interface Contract';
        allocatedFeatureIdentifier = "boundary, services";
        rationale = "LIF-05 is the sole logical mediator of IF-05.";
    }

    requirement <'LCR-LIF-06'> 'Evidence Custody Interface Manager Requirement' {
        subject manager : 'Specified Evidence Custody Interface Manager';
        doc
        /* The manager shall mediate every IF-06 item in its declared direction through the inherited
         * Evidence Custody Ports.
         */
        require constraint statement {
            doc
            /* The allocated IF-06 contract is preserved at the logical boundary. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement =
            FrameworkSystemRequirements::'Evidence Custody Interface Contract';
        allocatedFeatureIdentifier = "boundary, services";
        rationale = "LIF-06 is the sole logical mediator of IF-06.";
    }

    requirement <'LCR-LAP-01'> 'Evidence Chain Manager Requirement' {
        subject manager : 'Specified Evidence Chain Manager';
        doc
        /* The manager shall register external artifacts, scope and validate each designated evidence
         * chain, and issue its assessment.
         */
        require constraint statement {
            doc
            /* F-01.0 through F-01.3 are allocated to the manager. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Register External Engineering Artifacts',
            FrameworkSystemRequirements::'Scope Designated Evidence Chain',
            FrameworkSystemRequirements::'Validate Evidence Chain',
            FrameworkSystemRequirements::'Issue Evidence Chain Assessment',
        );
        allocatedFeatureIdentifier =
            "registerExternalArtifacts, scopeEvidenceChain, validateEvidenceChain, issueEvidenceChainAssessment";
        rationale = "The LA-SC-01 logical activity assigns all F-01 subfunctions to LAP-01.";
    }

    requirement <'LCR-LAP-02'> 'Case Configuration Manager Requirement' {
        subject manager : 'Specified Case Configuration Manager';
        doc
        /* The manager shall capture, validate, and issue each controlled case configuration and its
         * status.
         */
        require constraint statement {
            doc
            /* F-02.1 through F-02.3 are allocated to the manager. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Capture Case Configuration',
            FrameworkSystemRequirements::'Validate Case Configuration',
            FrameworkSystemRequirements::'Issue Controlled Case Configuration',
        );
        allocatedFeatureIdentifier =
            "captureCaseConfiguration, validateCaseConfiguration, issueConfigurationStatus";
        rationale = "The LA-SC-02 logical activity assigns all F-02 subfunctions to LAP-02.";
    }

    requirement <'LCR-LAP-03'> 'Analysis Reproduction Manager Requirement' {
        subject manager : 'Specified Analysis Reproduction Manager';
        doc
        /* The manager shall prepare each reproduction package, evaluate its result, and issue the
         * reproduction verdict.
         */
        require constraint statement {
            doc
            /* F-03.1, F-03.3, and F-03.4 are allocated to the manager. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Prepare Reproduction Package',
            FrameworkSystemRequirements::'Evaluate Reproduced Result',
            FrameworkSystemRequirements::'Issue Reproduction Verdict',
        );
        allocatedFeatureIdentifier =
            "prepareReproductionPackage, evaluateReproducedResult, issueReproductionVerdict";
        rationale =
            "The LA-SC-03 logical activity assigns the nonshared F-03 subfunctions to LAP-03.";
    }

    requirement <'LCR-LAP-07'> 'Controlled Analysis Coordinator Requirement' {
        subject coordinator : 'Specified Controlled Analysis Coordinator';
        doc
        /* The coordinator shall submit each accepted analysis request and return its correlated raw
         * result without altering its controlled content.
         */
        require constraint statement {
            doc
            /* The shared F-03.2 action is allocated to the coordinator. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = FrameworkSystemRequirements::'Coordinate Controlled Analysis';
        allocatedFeatureIdentifier = "coordinateControlledAnalysis";
        rationale = "LA-SC-03 through LA-SC-05 share one controlled-analysis responsibility.";
    }

    requirement <'LCR-LAP-04'> 'Design Change Assessment Manager Requirement' {
        subject manager : 'Specified Design Change Assessment Manager';
        doc
        /* The manager shall validate change requests, determine their impact, validate regenerated
         * evidence, and assemble the change evidence package.
         */
        require constraint statement {
            doc
            /* F-04.1 through F-04.4 are allocated to the manager. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Validate Design Change Request',
            FrameworkSystemRequirements::'Analyze Design Change Impact',
            FrameworkSystemRequirements::'Validate Regenerated Evidence',
            FrameworkSystemRequirements::'Assemble Change Evidence Package',
        );
        allocatedFeatureIdentifier =
            "validateChangeRequest, analyzeChangeImpact, validateRegeneratedEvidence, assembleChangeEvidencePackage";
        rationale = "The LA-SC-04 logical activity assigns all F-04 subfunctions to LAP-04.";
    }

    requirement <'LCR-LAP-05'> 'Candidate Evaluation Manager Requirement' {
        subject manager : 'Specified Candidate Evaluation Manager';
        doc
        /* The manager shall validate the common comparison basis, determine feasibility, compare
         * feasible candidates, and issue the candidate comparison package.
         */
        require constraint statement {
            doc
            /* F-05.1 through F-05.4 are allocated to the manager. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Validate Candidate Comparison Basis',
            FrameworkSystemRequirements::'Determine Candidate EPS Feasibility',
            FrameworkSystemRequirements::'Compare Feasible EPS Candidates',
            FrameworkSystemRequirements::'Issue Candidate Comparison Package',
        );
        allocatedFeatureIdentifier =
            "validateComparisonBasis, determineCandidateFeasibility, compareCandidateArchitectures, issueCandidateComparison";
        rationale = "The LA-SC-05 logical activity assigns all F-05 subfunctions to LAP-05.";
    }

    requirement <'LCR-LAP-06'> 'Design Review Manager Requirement' {
        subject manager : 'Specified Design Review Manager';
        doc
        /* The manager shall assemble the review package, coordinate selected reproduction, manage
         * findings, and issue review status.
         */
        require constraint statement {
            doc
            /* F-06.1 through F-06.4 are allocated to the manager. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Assemble Early Design Review Package',
            FrameworkSystemRequirements::'Coordinate Selected Review Reproduction',
            FrameworkSystemRequirements::'Manage Review Findings',
            FrameworkSystemRequirements::'Issue Early Design Review Status',
        );
        allocatedFeatureIdentifier =
            "assembleReviewPackage, coordinateSelectedReproduction, manageReviewFindings, issueReviewStatus";
        rationale = "The LA-SC-06 logical activity assigns all F-06 subfunctions to LAP-06.";
    }

    requirement <'LCR-LIN-01'> 'Workflow Control Manager Requirement' {
        subject manager : 'Specified Workflow Control Manager';
        doc
        /* The manager shall establish and preserve the controlled context, dispatch verified work,
         * apply outcome guards, expose exceptional outcomes, and control recovery.
         */
        require constraint statement {
            doc
            /* The manager contributes the inherited SM-01 control behavior. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Establish Controlled Context Before Operational Work',
            FrameworkSystemRequirements::'Dispatch Verified Requests to Their Service States',
            FrameworkSystemRequirements::'Return to Ready Only After an Accepted Outcome',
            FrameworkSystemRequirements::'Enter Discrepancy State on Exceptional Outcome',
            FrameworkSystemRequirements::'Recover Through Controlled Retry and Revalidation',
            FrameworkSystemRequirements::'Preserve Baseline Identity Across Control Transitions',
            FrameworkSystemRequirements::'Expose Exceptional Outcomes',
        );
        allocatedFeatureIdentifier =
            "establishControlledContext, dispatchVerifiedRequest, applyTerminalOutcomeGuard, recordExceptionalOutcome, controlRecovery, preserveContextAndBaseline";
        rationale =
            "The logical activities assign every terminal success and discrepancy decision to LIN-01.";
    }

    requirement <'LCR-LIN-02'> 'Transfer Assurance Manager Requirement' {
        subject manager : 'Specified Transfer Assurance Manager';
        doc
        /* The manager shall verify each boundary transfer before acceptance and retain rejected
         * transfer status without replacing controlled content.
         */
        require constraint statement {
            doc
            /* Common transfer assurance is applied to all six boundary interfaces. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Verify Boundary Transfer Before Acceptance',
            FrameworkSystemRequirements::'Preserve Controlled Content After Rejected Transfer',
        );
        allocatedFeatureIdentifier = "verifyBoundaryTransfer, preserveRejectedTransferRecord";
        rationale = "The logical activities allocate transfer checks to LIN-02 before acceptance.";
    }

    requirement <'LCR-LIN-03'> 'Baseline and Configuration Manager Requirement' {
        subject manager : 'Specified Baseline and Configuration Manager';
        doc
        /* The manager shall retain and retrieve controlled baseline and configuration identities,
         * distinguish common-core and case adaptations, and provide the execution declarations
         * needed for reconstruction.
         */
        require constraint statement {
            doc
            /* Configuration control is separated from candidate-specific configuration technology. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Preserve Baseline Identity Across Control Transitions',
            FrameworkSystemRequirements::'Retain Controlled Model and Case Records',
            FrameworkSystemRequirements::'Retrieve Immutable Baseline Records',
            FrameworkSystemRequirements::'Distinguish Common Core and Case Adaptations',
            FrameworkSystemRequirements::'Declare Minimum Execution Environment',
            FrameworkSystemRequirements::'Reconstruct Controlled Execution Environment',
        );
        allocatedFeatureIdentifier =
            "configurationStore, controlCaseConfiguration, preserveBaselineIdentity, declareExecutionEnvironment, assembleReconstructionDeclaration";
        rationale =
            "Baseline, configuration, and reconstruction declarations are shared logical responsibilities.";
    }

    requirement <'LCR-LIN-04'> 'Evidence and Provenance Manager Requirement' {
        subject manager : 'Specified Evidence and Provenance Manager';
        doc
        /* The manager shall retain controlled evidence records, preserve output provenance and
         * decision context, and supply the evidence needed for controlled reconstruction.
         */
        require constraint statement {
            doc
            /* Evidence custody remains a logical responsibility independent of repository technology. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Retain Controlled Model and Case Records',
            FrameworkSystemRequirements::'Retain Raw Analysis Evidence',
            FrameworkSystemRequirements::'Retain Assessments, Verdicts, and Review Records',
            FrameworkSystemRequirements::'Identify Controlled Output Provenance',
            FrameworkSystemRequirements::'Preserve Decision Transparency',
            FrameworkSystemRequirements::'Reconstruct Controlled Execution Environment',
        );
        allocatedFeatureIdentifier =
            "evidenceStore, retainControlledRecords, preserveOutputProvenance, retainDecisionTransparency, supplyReconstructionEvidence";
        rationale =
            "The logical custody and provenance responsibilities are centralized in LIN-04.";
    }

    requirement <'LCR-LIN-05'> 'Evaluation Measurement Manager Requirement' {
        subject manager : 'Specified Evaluation Measurement Manager';
        doc
        /* The manager shall retain raw observations and uncertainty, calculate the inherited MOPs
         * under the fixed protocol, and prevent comparison credit before correctness passes.
         */
        require constraint statement {
            doc
            /* The component records measurements without assigning new component performance values. */
        }
    }
    @LogicalComponentRequirementTrace {
        sourceSystemRequirement = (
            FrameworkSystemRequirements::'Achieve Complete Valid Trace Coverage',
            FrameworkSystemRequirements::'Reproduce Every Designated Reference Analysis',
            FrameworkSystemRequirements::'Close Every Critical Discrepancy',
            FrameworkSystemRequirements::'Complete Two Contrasting EPS Cases',
            FrameworkSystemRequirements::'Eliminate Undeclared Case Adaptations',
            FrameworkSystemRequirements::'Measure Correct Change Turnaround Time',
            FrameworkSystemRequirements::'Measure Case Adaptation Effort',
            FrameworkSystemRequirements::'Measure Independent Reproduction Effort',
            FrameworkSystemRequirements::'Measure Framework Adoption Effort',
            FrameworkSystemRequirements::'Measure Direct Framework Cost',
            FrameworkSystemRequirements::'Measure Consistency Assurance Effectiveness',
            FrameworkSystemRequirements::'Gate Comparative Credit on Correctness',
        );
        allocatedFeatureIdentifier =
            "measurementStore and recordTraceCoverage through gateComparativeCredit";
        rationale =
            "LIN-05 owns the common measurement protocol and raw measurement record retention.";
    }

    // Component requirements refine their corresponding black-box requirement categories.

    #refinement dependency
        'Mission Application Interface Manager Requirement'
        to FrameworkSystemRequirements::'Interface Requirements';
    #refinement dependency
        'Research Governance Interface Manager Requirement'
        to FrameworkSystemRequirements::'Interface Requirements';
    #refinement dependency
        'Independent Review Interface Manager Requirement'
        to FrameworkSystemRequirements::'Interface Requirements';
    #refinement dependency
        'Model Control Interface Manager Requirement'
        to FrameworkSystemRequirements::'Interface Requirements';
    #refinement dependency
        'Analysis Execution Interface Manager Requirement'
        to FrameworkSystemRequirements::'Interface Requirements';
    #refinement dependency
        'Evidence Custody Interface Manager Requirement'
        to FrameworkSystemRequirements::'Interface Requirements';

    #refinement dependency
        'Evidence Chain Manager Requirement'
        to FrameworkSystemRequirements::'Functional Requirements';
    #refinement dependency
        'Case Configuration Manager Requirement'
        to FrameworkSystemRequirements::'Functional Requirements';
    #refinement dependency
        'Analysis Reproduction Manager Requirement'
        to FrameworkSystemRequirements::'Functional Requirements';
    #refinement dependency
        'Controlled Analysis Coordinator Requirement'
        to FrameworkSystemRequirements::'Functional Requirements';
    #refinement dependency
        'Design Change Assessment Manager Requirement'
        to FrameworkSystemRequirements::'Functional Requirements';
    #refinement dependency
        'Candidate Evaluation Manager Requirement'
        to FrameworkSystemRequirements::'Functional Requirements';
    #refinement dependency
        'Design Review Manager Requirement'
        to FrameworkSystemRequirements::'Functional Requirements';

    #refinement dependency
        'Workflow Control Manager Requirement'
        to FrameworkSystemRequirements::'Operational Control Requirements';
    #refinement dependency
        'Workflow Control Manager Requirement'
        to FrameworkSystemRequirements::'Quality Requirements';
    #refinement dependency
        'Transfer Assurance Manager Requirement'
        to FrameworkSystemRequirements::'Interface Requirements';
    #refinement dependency
        'Baseline and Configuration Manager Requirement'
        to FrameworkSystemRequirements::'Operational Control Requirements';
    #refinement dependency
        'Baseline and Configuration Manager Requirement'
        to FrameworkSystemRequirements::'Store Requirements';
    #refinement dependency
        'Baseline and Configuration Manager Requirement'
        to FrameworkSystemRequirements::'Quality Requirements';
    #refinement dependency
        'Baseline and Configuration Manager Requirement'
        to FrameworkSystemRequirements::'Execution Resource Requirements';
    #refinement dependency
        'Evidence and Provenance Manager Requirement'
        to FrameworkSystemRequirements::'Store Requirements';
    #refinement dependency
        'Evidence and Provenance Manager Requirement'
        to FrameworkSystemRequirements::'Quality Requirements';
    #refinement dependency
        'Evidence and Provenance Manager Requirement'
        to FrameworkSystemRequirements::'Execution Resource Requirements';
    #refinement dependency
        'Evaluation Measurement Manager Requirement'
        to FrameworkSystemRequirements::'Performance and Measurement Requirements';
    #refinement dependency
        'Evaluation Measurement Manager Requirement'
        to FrameworkSystemRequirements::'Quality Requirements';

    // Direct allocation of every system requirement leaf to the responsible logical feature.

    allocate FrameworkSystemRequirements::'Mission Application Interface Contract'
        to 'Specified Mission Application Interface Manager'::boundary;
    allocate FrameworkSystemRequirements::'Research Governance Interface Contract'
        to 'Specified Research Governance Interface Manager'::boundary;
    allocate FrameworkSystemRequirements::'Independent Review Interface Contract'
        to 'Specified Independent Review Interface Manager'::boundary;
    allocate FrameworkSystemRequirements::'Model Control Interface Contract'
        to 'Specified Model Control Interface Manager'::boundary;
    allocate FrameworkSystemRequirements::'Analysis Execution Interface Contract'
        to 'Specified Analysis Execution Interface Manager'::boundary;
    allocate FrameworkSystemRequirements::'Evidence Custody Interface Contract'
        to 'Specified Evidence Custody Interface Manager'::boundary;

    allocate FrameworkSystemRequirements::'Register External Engineering Artifacts'
        to 'Specified Evidence Chain Manager'::registerExternalArtifacts;
    allocate FrameworkSystemRequirements::'Scope Designated Evidence Chain'
        to 'Specified Evidence Chain Manager'::scopeEvidenceChain;
    allocate FrameworkSystemRequirements::'Validate Evidence Chain'
        to 'Specified Evidence Chain Manager'::validateEvidenceChain;
    allocate FrameworkSystemRequirements::'Issue Evidence Chain Assessment'
        to 'Specified Evidence Chain Manager'::issueEvidenceChainAssessment;

    allocate FrameworkSystemRequirements::'Capture Case Configuration'
        to 'Specified Case Configuration Manager'::captureCaseConfiguration;
    allocate FrameworkSystemRequirements::'Validate Case Configuration'
        to 'Specified Case Configuration Manager'::validateCaseConfiguration;
    allocate FrameworkSystemRequirements::'Issue Controlled Case Configuration'
        to 'Specified Case Configuration Manager'::issueConfigurationStatus;

    allocate FrameworkSystemRequirements::'Prepare Reproduction Package'
        to 'Specified Analysis Reproduction Manager'::prepareReproductionPackage;
    allocate FrameworkSystemRequirements::'Coordinate Controlled Analysis'
        to 'Specified Controlled Analysis Coordinator'::coordinateControlledAnalysis;
    allocate FrameworkSystemRequirements::'Evaluate Reproduced Result'
        to 'Specified Analysis Reproduction Manager'::evaluateReproducedResult;
    allocate FrameworkSystemRequirements::'Issue Reproduction Verdict'
        to 'Specified Analysis Reproduction Manager'::issueReproductionVerdict;

    allocate FrameworkSystemRequirements::'Validate Design Change Request'
        to 'Specified Design Change Assessment Manager'::validateChangeRequest;
    allocate FrameworkSystemRequirements::'Analyze Design Change Impact'
        to 'Specified Design Change Assessment Manager'::analyzeChangeImpact;
    allocate FrameworkSystemRequirements::'Validate Regenerated Evidence'
        to 'Specified Design Change Assessment Manager'::validateRegeneratedEvidence;
    allocate FrameworkSystemRequirements::'Assemble Change Evidence Package'
        to 'Specified Design Change Assessment Manager'::assembleChangeEvidencePackage;

    allocate FrameworkSystemRequirements::'Validate Candidate Comparison Basis'
        to 'Specified Candidate Evaluation Manager'::validateComparisonBasis;
    allocate FrameworkSystemRequirements::'Determine Candidate EPS Feasibility'
        to 'Specified Candidate Evaluation Manager'::determineCandidateFeasibility;
    allocate FrameworkSystemRequirements::'Compare Feasible EPS Candidates'
        to 'Specified Candidate Evaluation Manager'::compareCandidateArchitectures;
    allocate FrameworkSystemRequirements::'Issue Candidate Comparison Package'
        to 'Specified Candidate Evaluation Manager'::issueCandidateComparison;

    allocate FrameworkSystemRequirements::'Assemble Early Design Review Package'
        to 'Specified Design Review Manager'::assembleReviewPackage;
    allocate FrameworkSystemRequirements::'Coordinate Selected Review Reproduction'
        to 'Specified Design Review Manager'::coordinateSelectedReproduction;
    allocate FrameworkSystemRequirements::'Manage Review Findings'
        to 'Specified Design Review Manager'::manageReviewFindings;
    allocate FrameworkSystemRequirements::'Issue Early Design Review Status'
        to 'Specified Design Review Manager'::issueReviewStatus;

    allocate FrameworkSystemRequirements::'Establish Controlled Context Before Operational Work'
        to 'Specified Workflow Control Manager'::establishControlledContext;
    allocate FrameworkSystemRequirements::'Dispatch Verified Requests to Their Service States'
        to 'Specified Workflow Control Manager'::dispatchVerifiedRequest;
    allocate FrameworkSystemRequirements::'Return to Ready Only After an Accepted Outcome'
        to 'Specified Workflow Control Manager'::applyTerminalOutcomeGuard;
    allocate FrameworkSystemRequirements::'Enter Discrepancy State on Exceptional Outcome'
        to 'Specified Workflow Control Manager'::recordExceptionalOutcome;
    allocate FrameworkSystemRequirements::'Recover Through Controlled Retry and Revalidation'
        to 'Specified Workflow Control Manager'::controlRecovery;
    allocate FrameworkSystemRequirements::'Preserve Baseline Identity Across Control Transitions'
        to 'Specified Workflow Control Manager'::preserveContextAndBaseline;

    allocate FrameworkSystemRequirements::'Verify Boundary Transfer Before Acceptance'
        to 'Specified Transfer Assurance Manager'::verifyBoundaryTransfer;
    allocate FrameworkSystemRequirements::'Preserve Controlled Content After Rejected Transfer'
        to 'Specified Transfer Assurance Manager'::preserveRejectedTransferRecord;

    allocate FrameworkSystemRequirements::'Retain Controlled Model and Case Records'
        to 'Specified Baseline and Configuration Manager'::configurationStore;
    allocate FrameworkSystemRequirements::'Retrieve Immutable Baseline Records'
        to 'Specified Baseline and Configuration Manager'::configurationStore;
    allocate FrameworkSystemRequirements::'Preserve Baseline Identity Across Control Transitions'
        to 'Specified Baseline and Configuration Manager'::preserveBaselineIdentity;
    allocate FrameworkSystemRequirements::'Distinguish Common Core and Case Adaptations'
        to 'Specified Baseline and Configuration Manager'::controlCaseConfiguration;
    allocate FrameworkSystemRequirements::'Declare Minimum Execution Environment'
        to 'Specified Baseline and Configuration Manager'::declareExecutionEnvironment;
    allocate FrameworkSystemRequirements::'Reconstruct Controlled Execution Environment'
        to 'Specified Baseline and Configuration Manager'::assembleReconstructionDeclaration;

    allocate FrameworkSystemRequirements::'Retain Controlled Model and Case Records'
        to 'Specified Evidence and Provenance Manager'::evidenceStore;
    allocate FrameworkSystemRequirements::'Retain Raw Analysis Evidence'
        to 'Specified Evidence and Provenance Manager'::evidenceStore;
    allocate FrameworkSystemRequirements::'Retain Assessments, Verdicts, and Review Records'
        to 'Specified Evidence and Provenance Manager'::evidenceStore;
    allocate FrameworkSystemRequirements::'Identify Controlled Output Provenance'
        to 'Specified Evidence and Provenance Manager'::preserveOutputProvenance;
    allocate FrameworkSystemRequirements::'Preserve Decision Transparency'
        to 'Specified Evidence and Provenance Manager'::retainDecisionTransparency;
    allocate FrameworkSystemRequirements::'Reconstruct Controlled Execution Environment'
        to 'Specified Evidence and Provenance Manager'::supplyReconstructionEvidence;

    allocate FrameworkSystemRequirements::'Achieve Complete Valid Trace Coverage'
        to 'Specified Evaluation Measurement Manager'::recordTraceCoverage;
    allocate FrameworkSystemRequirements::'Reproduce Every Designated Reference Analysis'
        to 'Specified Evaluation Measurement Manager'::recordReproductionSuccess;
    allocate FrameworkSystemRequirements::'Close Every Critical Discrepancy'
        to 'Specified Evaluation Measurement Manager'::recordCriticalDiscrepancyStatus;
    allocate FrameworkSystemRequirements::'Complete Two Contrasting EPS Cases'
        to 'Specified Evaluation Measurement Manager'::recordCompletedCaseCount;
    allocate FrameworkSystemRequirements::'Eliminate Undeclared Case Adaptations'
        to 'Specified Evaluation Measurement Manager'::recordAdaptationStatus;
    allocate FrameworkSystemRequirements::'Measure Correct Change Turnaround Time'
        to 'Specified Evaluation Measurement Manager'::recordChangeTurnaround;
    allocate FrameworkSystemRequirements::'Measure Case Adaptation Effort'
        to 'Specified Evaluation Measurement Manager'::recordCaseAdaptationEffort;
    allocate FrameworkSystemRequirements::'Measure Independent Reproduction Effort'
        to 'Specified Evaluation Measurement Manager'::recordIndependentReproductionEffort;
    allocate FrameworkSystemRequirements::'Measure Framework Adoption Effort'
        to 'Specified Evaluation Measurement Manager'::recordAdoptionEffort;
    allocate FrameworkSystemRequirements::'Measure Direct Framework Cost'
        to 'Specified Evaluation Measurement Manager'::recordDirectFrameworkCost;
    allocate FrameworkSystemRequirements::'Measure Consistency Assurance Effectiveness'
        to 'Specified Evaluation Measurement Manager'::evaluateConsistencyAssurance;
    allocate FrameworkSystemRequirements::'Gate Comparative Credit on Correctness'
        to 'Specified Evaluation Measurement Manager'::gateComparativeCredit;

    allocate FrameworkSystemRequirements::'Expose Exceptional Outcomes'
        to 'Specified Workflow Control Manager'::recordExceptionalOutcome;

    // This is a catalogue of specifications. It does not duplicate LA-01 composition.
    part def <'LCS-00'> 'Logical Component Specification Set' {
        doc
        /* One representative occurrence of every specified logical component for navigation and
         * rendering. LA-01 remains the authoritative composition and connector architecture.
         */

        part missionApplicationInterface : 'Specified Mission Application Interface Manager';
        part researchGovernanceInterface : 'Specified Research Governance Interface Manager';
        part independentReviewInterface : 'Specified Independent Review Interface Manager';
        part modelControlInterface : 'Specified Model Control Interface Manager';
        part analysisExecutionInterface : 'Specified Analysis Execution Interface Manager';
        part evidenceCustodyInterface : 'Specified Evidence Custody Interface Manager';

        part evidenceChainManager : 'Specified Evidence Chain Manager';
        part caseConfigurationManager : 'Specified Case Configuration Manager';
        part analysisReproductionManager : 'Specified Analysis Reproduction Manager';
        part controlledAnalysisCoordinator : 'Specified Controlled Analysis Coordinator';
        part designChangeAssessmentManager : 'Specified Design Change Assessment Manager';
        part candidateEvaluationManager : 'Specified Candidate Evaluation Manager';
        part designReviewManager : 'Specified Design Review Manager';

        part workflowControlManager : 'Specified Workflow Control Manager';
        part transferAssuranceManager : 'Specified Transfer Assurance Manager';
        part baselineAndConfigurationManager : 'Specified Baseline and Configuration Manager';
        part evidenceAndProvenanceManager : 'Specified Evidence and Provenance Manager';
        part evaluationMeasurementManager : 'Specified Evaluation Measurement Manager';
    }

    part logicalComponentSpecificationSet : 'Logical Component Specification Set';
} // package FrameworkLogicalComponentSpecifications
