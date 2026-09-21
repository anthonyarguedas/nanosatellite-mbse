// Logical internal block architecture for the nanosatellite EPS engineering framework.
package FrameworkLogicalInterconnections {
    private import ModelingMetadata::refinement;
    private import FrameworkBoundaryInterfaces::*;
    private import FrameworkExchangeDefinitions::*;
    private import FrameworkLogicalDecomposition::*;

    doc
    /* This package completes the OOSEM logical-interaction step. LA-01 inherits the complete
     * black-box boundary from LA-00. Its outer ports retain IF-01 through IF-06 unchanged. The
     * logical connectors allocate their typed item flows to interface, application, and
     * infrastructure components without choosing a transport, format, tool, deployment, or
     * physical component.
     *
     * The logical stores partition access to the inherited controlled record set. They represent
     * persistent information responsibilities, not repository products or database schemas.
     */

    interface def <'LI-01'> 'Logical Evidence Chain Mission Interface' {
        end interfaceManager : 'Mission Application Port';
        end service : 'Mission Application Port';

        flow interfaceManager.evidenceChainRequest to service.evidenceChainRequest;
        flow service.evidenceChainScope to interfaceManager.evidenceChainScope;
        flow service.evidenceChainAssessment to interfaceManager.evidenceChainAssessment;
    }

    interface def <'LI-02'> 'Logical Case Configuration Mission Interface' {
        end interfaceManager : 'Mission Application Port';
        end service : 'Mission Application Port';

        flow interfaceManager.caseConfigurationRequest to service.caseConfigurationRequest;
        flow service.caseConfigurationDraft to interfaceManager.caseConfigurationDraft;
        flow service.controlledCaseConfiguration to interfaceManager.controlledCaseConfiguration;
        flow service.configurationStatus to interfaceManager.configurationStatus;
    }

    interface def <'LI-03'> 'Logical Design Change Mission Interface' {
        end interfaceManager : 'Mission Application Port';
        end service : 'Mission Application Port';

        flow interfaceManager.designChangeRequest to service.designChangeRequest;
        flow interfaceManager.changeRevisionPackage to service.changeRevisionPackage;
        flow service.changeImpactAssessment to interfaceManager.changeImpactAssessment;
        flow service.changeEvidencePackage to interfaceManager.changeEvidencePackage;
    }

    interface def <'LI-04'> 'Logical Candidate Evaluation Mission Interface' {
        end interfaceManager : 'Mission Application Port';
        end service : 'Mission Application Port';

        flow interfaceManager.candidateComparisonRequest to service.candidateComparisonRequest;
        flow service.candidateComparisonPackage to interfaceManager.candidateComparisonPackage;
    }

    interface def <'LI-05'> 'Logical Design Review Mission Interface' {
        end interfaceManager : 'Mission Application Port';
        end service : 'Mission Application Port';

        flow interfaceManager.designReviewRequest to service.designReviewRequest;
        flow interfaceManager.findingDisposition to service.findingDisposition;
        flow service.reviewFindings to interfaceManager.reviewFindings;
        flow service.reviewStatus to interfaceManager.reviewStatus;
    }

    interface def <'LI-06'> 'Logical Case Configuration Research Interface' {
        end interfaceManager : 'Research Governance Port';
        end service : 'Research Governance Port';

        flow service.caseConfigurationDraft to interfaceManager.caseConfigurationDraft;
        flow interfaceManager.adaptationDecision to service.adaptationDecision;
    }

    interface def <'LI-07'> 'Logical Candidate Evaluation Research Interface' {
        end interfaceManager : 'Research Governance Port';
        end service : 'Research Governance Port';

        flow interfaceManager.comparisonProtocol to service.comparisonProtocol;
        flow service.analysisResult to interfaceManager.analysisResult;
        flow interfaceManager.sensitivityAndUncertainty to service.sensitivityAndUncertainty;
        flow service.candidateComparisonPackage to interfaceManager.candidateComparisonPackage;
    }

    interface def <'LI-08'> 'Logical Reproduction Review Interface' {
        end interfaceManager : 'Independent Review Port';
        end service : 'Independent Review Port';

        flow interfaceManager.reproductionRequest to service.reproductionRequest;
        flow service.reproducedResult to interfaceManager.reproducedResult;
        flow service.reproductionVerdict to interfaceManager.reproductionVerdict;
    }

    interface def <'LI-09'> 'Logical Design Review Review Interface' {
        end interfaceManager : 'Independent Review Port';
        end service : 'Independent Review Port';

        flow service.reviewPackage to interfaceManager.reviewPackage;
        flow interfaceManager.reviewFindings to service.reviewFindings;
        flow interfaceManager.reviewOutcome to service.reviewOutcome;
        flow service.reviewStatus to interfaceManager.reviewStatus;
    }

    interface def <'LI-10'> 'Logical Evidence Chain Model Interface' {
        end interfaceManager : 'Model Control Port';
        end service : 'Model Control Port';

        flow interfaceManager.controlledModelRecords to service.controlledModelRecords;
        flow service.artifactRegistrations to interfaceManager.artifactRegistrations;
    }

    interface def <'LI-11'> 'Logical Case Configuration Model Interface' {
        end interfaceManager : 'Model Control Port';
        end service : 'Model Control Port';

        flow interfaceManager.commonCorePackage to service.commonCorePackage;
        flow service.controlledCaseConfiguration to interfaceManager.controlledCaseConfiguration;
    }

    interface def <'LI-12'> 'Logical Design Change Model Interface' {
        end interfaceManager : 'Model Control Port';
        end service : 'Model Control Port';

        flow service.acceptedChangeRevision to interfaceManager.acceptedChangeRevision;
    }

    interface def <'LI-13'> 'Logical Candidate Evaluation Model Interface' {
        end interfaceManager : 'Model Control Port';
        end service : 'Model Control Port';

        flow interfaceManager.candidateModelPackage to service.candidateModelPackage;
    }

    interface def <'LI-14'> 'Logical Analysis Execution Interface' {
        end interfaceManager : 'Analysis Execution Port';
        end coordinator : 'Analysis Execution Port';

        flow coordinator.executionRequest to interfaceManager.executionRequest;
        flow interfaceManager.analysisResult to coordinator.analysisResult;
    }

    interface def <'LI-15'> 'Logical Evidence Custody Interface' {
        end interfaceManager : 'Evidence Custody Port';
        end evidenceManager : 'Evidence Custody Port';

        flow interfaceManager.retainedEvidenceRecords to evidenceManager.retainedEvidenceRecords;
        flow evidenceManager.artifactRegistrations to interfaceManager.artifactRegistrations;
        flow evidenceManager.evidenceChainAssessment to interfaceManager.evidenceChainAssessment;
        flow evidenceManager.controlledCaseConfiguration
            to interfaceManager.controlledCaseConfiguration;
        flow evidenceManager.configurationStatus to interfaceManager.configurationStatus;
        flow evidenceManager.analysisResult to interfaceManager.analysisResult;
        flow evidenceManager.reproductionVerdict to interfaceManager.reproductionVerdict;
        flow evidenceManager.changeEvidencePackage to interfaceManager.changeEvidencePackage;
        flow evidenceManager.candidateComparisonPackage
            to interfaceManager.candidateComparisonPackage;
        flow evidenceManager.reviewPackage to interfaceManager.reviewPackage;
        flow evidenceManager.reviewStatus to interfaceManager.reviewStatus;
    }

    interface def <'LI-16'> 'Logical Controlled Analysis Interface' {
        end service : 'Analysis Execution Port';
        end coordinator : 'Analysis Execution Port';

        flow service.executionRequest to coordinator.executionRequest;
        flow coordinator.analysisResult to service.analysisResult;
    }

    interface def <'LI-17'> 'Logical Selected Reproduction Interface' {
        end designReviewManager : 'Independent Review Port';
        end reproductionManager : 'Independent Review Port';

        flow designReviewManager.reviewPackage to reproductionManager.reviewPackage;
        flow reproductionManager.reproductionVerdict to designReviewManager.reproductionVerdict;
    }

    interface def <'LI-18'> 'Logical Baseline Control Interface' {
        end baselineManager : 'Logical Baseline Control Port';
        end service : 'Logical Baseline Control Port';

        flow baselineManager.baselineReference to service.baselineReference;
        flow baselineManager.commonCorePackage to service.commonCorePackage;
        flow baselineManager.controlledCaseConfiguration to service.controlledCaseConfiguration;
        flow service.caseConfigurationDraft to baselineManager.caseConfigurationDraft;
        flow service.controlledCaseConfiguration to baselineManager.controlledCaseConfiguration;
        flow service.changeRevisionPackage to baselineManager.changeRevisionPackage;
    }

    interface def <'LI-19'> 'Logical Evidence Management Interface' {
        end evidenceManager : 'Logical Evidence Management Port';
        end service : 'Logical Evidence Management Port';

        flow evidenceManager.modelRecords to service.modelRecords;
        flow evidenceManager.evidenceRecords to service.evidenceRecords;
        flow service.artifactRegistrations to evidenceManager.artifactRegistrations;
        flow service.evidenceChainAssessment to evidenceManager.evidenceChainAssessment;
        flow service.controlledCaseConfiguration to evidenceManager.controlledCaseConfiguration;
        flow service.configurationStatus to evidenceManager.configurationStatus;
        flow service.analysisResult to evidenceManager.analysisResult;
        flow service.reproductionVerdict to evidenceManager.reproductionVerdict;
        flow service.changeEvidencePackage to evidenceManager.changeEvidencePackage;
        flow service.candidateComparisonPackage to evidenceManager.candidateComparisonPackage;
        flow service.reviewPackage to evidenceManager.reviewPackage;
        flow service.reviewStatus to evidenceManager.reviewStatus;
    }

    interface def <'LI-20'> 'Logical Workflow Control Interface' {
        end workflowManager : 'Logical Workflow Control Port';
        end service : 'Logical Workflow Control Port';

        flow service.evidenceChainAssessment to workflowManager.evidenceChainAssessment;
        flow service.configurationStatus to workflowManager.configurationStatus;
        flow service.reproductionVerdict to workflowManager.reproductionVerdict;
        flow service.changeEvidencePackage to workflowManager.changeEvidencePackage;
        flow service.candidateComparisonPackage to workflowManager.candidateComparisonPackage;
        flow service.reviewStatus to workflowManager.reviewStatus;
        flow workflowManager.outcomeControl to service.outcomeControl;
    }

    interface def <'LI-21'> 'Logical Transfer Assurance Interface' {
        end interfaceManager : 'Logical Transfer Assurance Port';
        end assuranceManager : 'Logical Transfer Assurance Port';

        flow interfaceManager.transferVerification to assuranceManager.transferVerification;
        flow assuranceManager.transferVerification to interfaceManager.transferVerification;
    }

    interface def <'LI-22'> 'Logical Measurement Interface' {
        end service : 'Logical Measurement Port';
        end measurementManager : 'Logical Measurement Port';

        flow service.measurementRecord to measurementManager.measurementRecord;
    }

    part def <'LA-01'> 'Logical Framework Internal Block Architecture'
        :> 'Logical Nanosatellite EPS Engineering Framework' {
        doc
        /* Complete logical interconnection architecture. The inherited boundary ports connect only
         * to their corresponding interface managers. Internal connectors then route the exact
         * service exchanges and shared controls defined below. Every logical part of LA-00 appears
         * in this specialization. The stores are logical partitions of the inherited controlled
         * record set and have no selected physical realization.
         */

        item workflowStateStore : 'Logical Workflow State Store';
        item baselineAndConfigurationStore : 'Logical Baseline and Configuration Store';
        item evidenceAndProvenanceStore : 'Logical Evidence and Provenance Store';
        item measurementStore : 'Logical Measurement Store';

        bind workflowControlManager.workflowStateStore = workflowStateStore;
        bind baselineAndConfigurationManager.configurationStore = baselineAndConfigurationStore;
        bind evidenceAndProvenanceManager.evidenceStore = evidenceAndProvenanceStore;
        bind evaluationMeasurementManager.measurementStore = measurementStore;

        // Retain the six inherited black-box ports and interface contracts at the system boundary.
        interface missionApplicationBoundary : 'Mission Application Interface'
            connect missionApplication to missionApplicationInterface.boundary;
        interface researchGovernanceBoundary : 'Research Governance Interface'
            connect researchGovernance to researchGovernanceInterface.boundary;
        interface independentReviewBoundary : 'Independent Review Interface'
            connect independentReview to independentReviewInterface.boundary;
        interface modelControlBoundary : 'Model Control Interface'
            connect modelControl to modelControlInterface.boundary;
        interface analysisExecutionBoundary : 'Analysis Execution Interface'
            connect analysisExecution to analysisExecutionInterface.boundary;
        interface evidenceCustodyBoundary : 'Evidence Custody Interface'
            connect evidenceCustody to evidenceCustodyInterface.boundary;

        // Route mission-application work to the five service managers that use IF-01.
        interface evidenceChainMission : 'Logical Evidence Chain Mission Interface'
            connect missionApplicationInterface.services to evidenceChainManager.missionApplication;
        interface caseConfigurationMission : 'Logical Case Configuration Mission Interface'
            connect missionApplicationInterface.services to caseConfigurationManager.missionApplication;
        interface designChangeMission : 'Logical Design Change Mission Interface'
            connect missionApplicationInterface.services
                to designChangeAssessmentManager.missionApplication;
        interface candidateEvaluationMission : 'Logical Candidate Evaluation Mission Interface'
            connect missionApplicationInterface.services
                to candidateEvaluationManager.missionApplication;
        interface designReviewMission : 'Logical Design Review Mission Interface'
            connect missionApplicationInterface.services to designReviewManager.missionApplication;

        // Route research governance to configuration and candidate-evaluation services.
        interface caseConfigurationResearch : 'Logical Case Configuration Research Interface'
            connect researchGovernanceInterface.services
                to caseConfigurationManager.researchGovernance;
        interface candidateEvaluationResearch : 'Logical Candidate Evaluation Research Interface'
            connect researchGovernanceInterface.services
                to candidateEvaluationManager.researchGovernance;

        // Route independent review to reproduction and review services.
        interface reproductionReview : 'Logical Reproduction Review Interface'
            connect independentReviewInterface.services
                to analysisReproductionManager.independentReview;
        interface designReviewReview : 'Logical Design Review Review Interface'
            connect independentReviewInterface.services to designReviewManager.independentReview;

        // Route model-control traffic only to the managers that consume or issue it directly.
        interface evidenceChainModel : 'Logical Evidence Chain Model Interface'
            connect modelControlInterface.services to evidenceChainManager.modelControl;
        interface caseConfigurationModel : 'Logical Case Configuration Model Interface'
            connect modelControlInterface.services to caseConfigurationManager.modelControl;
        interface designChangeModel : 'Logical Design Change Model Interface'
            connect modelControlInterface.services to designChangeAssessmentManager.modelControl;
        interface candidateEvaluationModel : 'Logical Candidate Evaluation Model Interface'
            connect modelControlInterface.services to candidateEvaluationManager.modelControl;

        // The shared coordinator is the sole logical route to the analysis-execution boundary.
        interface analysisExecutionInternal : 'Logical Analysis Execution Interface'
            connect analysisExecutionInterface.services to controlledAnalysisCoordinator.analysisExecution;
        interface reproductionAnalysis : 'Logical Controlled Analysis Interface'
            connect analysisReproductionManager.controlledAnalysis
                to controlledAnalysisCoordinator.reproduction;
        interface changeAnalysis : 'Logical Controlled Analysis Interface'
            connect designChangeAssessmentManager.controlledAnalysis
                to controlledAnalysisCoordinator.designChange;
        interface candidateEvaluationAnalysis : 'Logical Controlled Analysis Interface'
            connect candidateEvaluationManager.controlledAnalysis
                to controlledAnalysisCoordinator.candidateEvaluation;
        interface selectedReviewReproduction : 'Logical Selected Reproduction Interface'
            connect designReviewManager.selectedReproduction
                to analysisReproductionManager.selectedReviewReproduction;

        // Evidence custody is mediated by the evidence and provenance manager.
        interface evidenceCustodyInternal : 'Logical Evidence Custody Interface'
            connect evidenceCustodyInterface.services to evidenceAndProvenanceManager.custody;

        // Workflow control applies each terminal outcome guard and returns an explicit control result.
        interface evidenceChainWorkflow : 'Logical Workflow Control Interface'
            connect evidenceChainManager.workflowControl to workflowControlManager.services;
        interface caseConfigurationWorkflow : 'Logical Workflow Control Interface'
            connect caseConfigurationManager.workflowControl to workflowControlManager.services;
        interface reproductionWorkflow : 'Logical Workflow Control Interface'
            connect analysisReproductionManager.workflowControl to workflowControlManager.services;
        interface designChangeWorkflow : 'Logical Workflow Control Interface'
            connect designChangeAssessmentManager.workflowControl to workflowControlManager.services;
        interface candidateEvaluationWorkflow : 'Logical Workflow Control Interface'
            connect candidateEvaluationManager.workflowControl to workflowControlManager.services;
        interface designReviewWorkflow : 'Logical Workflow Control Interface'
            connect designReviewManager.workflowControl to workflowControlManager.services;

        // Transfer assurance checks each incoming and outgoing boundary exchange.
        interface missionApplicationAssurance : 'Logical Transfer Assurance Interface'
            connect missionApplicationInterface.assurance to transferAssuranceManager.interfaceManagers;
        interface researchGovernanceAssurance : 'Logical Transfer Assurance Interface'
            connect researchGovernanceInterface.assurance to transferAssuranceManager.interfaceManagers;
        interface independentReviewAssurance : 'Logical Transfer Assurance Interface'
            connect independentReviewInterface.assurance to transferAssuranceManager.interfaceManagers;
        interface modelControlAssurance : 'Logical Transfer Assurance Interface'
            connect modelControlInterface.assurance to transferAssuranceManager.interfaceManagers;
        interface analysisExecutionAssurance : 'Logical Transfer Assurance Interface'
            connect analysisExecutionInterface.assurance to transferAssuranceManager.interfaceManagers;
        interface evidenceCustodyAssurance : 'Logical Transfer Assurance Interface'
            connect evidenceCustodyInterface.assurance to transferAssuranceManager.interfaceManagers;

        // Baseline, configuration, evidence, and measurement services are shared logical resources.
        interface evidenceChainBaseline : 'Logical Baseline Control Interface'
            connect evidenceChainManager.baselineControl
                to baselineAndConfigurationManager.services;
        interface caseConfigurationBaseline : 'Logical Baseline Control Interface'
            connect caseConfigurationManager.baselineControl
                to baselineAndConfigurationManager.services;
        interface reproductionBaseline : 'Logical Baseline Control Interface'
            connect analysisReproductionManager.baselineControl
                to baselineAndConfigurationManager.services;
        interface designChangeBaseline : 'Logical Baseline Control Interface'
            connect designChangeAssessmentManager.baselineControl
                to baselineAndConfigurationManager.services;
        interface candidateEvaluationBaseline : 'Logical Baseline Control Interface'
            connect candidateEvaluationManager.baselineControl
                to baselineAndConfigurationManager.services;
        interface designReviewBaseline : 'Logical Baseline Control Interface'
            connect designReviewManager.baselineControl
                to baselineAndConfigurationManager.services;

        interface evidenceChainEvidence : 'Logical Evidence Management Interface'
            connect evidenceChainManager.evidenceManagement
                to evidenceAndProvenanceManager.services;
        interface caseConfigurationEvidence : 'Logical Evidence Management Interface'
            connect caseConfigurationManager.evidenceManagement
                to evidenceAndProvenanceManager.services;
        interface reproductionEvidence : 'Logical Evidence Management Interface'
            connect analysisReproductionManager.evidenceManagement
                to evidenceAndProvenanceManager.services;
        interface designChangeEvidence : 'Logical Evidence Management Interface'
            connect designChangeAssessmentManager.evidenceManagement
                to evidenceAndProvenanceManager.services;
        interface candidateEvaluationEvidence : 'Logical Evidence Management Interface'
            connect candidateEvaluationManager.evidenceManagement
                to evidenceAndProvenanceManager.services;
        interface designReviewEvidence : 'Logical Evidence Management Interface'
            connect designReviewManager.evidenceManagement
                to evidenceAndProvenanceManager.services;

        interface evidenceChainMeasurement : 'Logical Measurement Interface'
            connect evidenceChainManager.measurement to evaluationMeasurementManager.services;
        interface caseConfigurationMeasurement : 'Logical Measurement Interface'
            connect caseConfigurationManager.measurement to evaluationMeasurementManager.services;
        interface reproductionMeasurement : 'Logical Measurement Interface'
            connect analysisReproductionManager.measurement to evaluationMeasurementManager.services;
        interface designChangeMeasurement : 'Logical Measurement Interface'
            connect designChangeAssessmentManager.measurement to evaluationMeasurementManager.services;
        interface candidateEvaluationMeasurement : 'Logical Measurement Interface'
            connect candidateEvaluationManager.measurement to evaluationMeasurementManager.services;
        interface designReviewMeasurement : 'Logical Measurement Interface'
            connect designReviewManager.measurement to evaluationMeasurementManager.services;
    }

    #refinement dependency
        'Logical Framework Internal Block Architecture'
        to 'Logical Nanosatellite EPS Engineering Framework';

    part frameworkLogicalInternalBlock : 'Logical Framework Internal Block Architecture';
} // package FrameworkLogicalInterconnections
