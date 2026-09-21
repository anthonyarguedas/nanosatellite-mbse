// Black-box system context and typed interfaces for the framework.
package FrameworkBoundaryInterfaces {
    private import ScalarValues::Boolean;
    private import FrameworkExchangeDefinitions::*;

    doc
    /* The port and interface definitions organize the typed exchanges derived from the mission
     * scenarios. Interface flows state direction relative to the framework boundary. They do not
     * select a transport protocol, file format, repository product, or analysis tool.
     * Evidence basis: buruso2026modelbased Sec. 5.1 and Table 5;
     * rostamnia2026digitaltwin Secs. 8.4-8.6 and Table 13;
     * rojasramirez2022comparative Sec. 4.2.3.
     */

    item def 'Transfer Verification Record' {
        attribute sourceIdentified : Boolean;
        attribute sourceRevisionIdentified : Boolean;
        attribute configurationIdentified : Boolean;
        attribute structurallyComplete : Boolean;
        attribute semanticallyCompatible : Boolean;
        attribute provenancePreserved : Boolean;
        attribute applicableTracesPreserved : Boolean;
        attribute accepted : Boolean;
        item discrepancies : 'Discrepancy Set';
        doc
        /* A receiving endpoint returns this record for a boundary transfer. For an engineering
         * artifact, acceptance also requires its producer, source revision, evidence baseline,
         * provenance, and applicable traces. A rejected transfer remains visible with its
         * discrepancies and does not silently replace controlled content.
         */
    }

    port def 'Mission Application Port' {
        inout item transferVerification : 'Transfer Verification Record';
        inout item evidenceChainRequest : 'Evidence Chain Request';
        inout item evidenceChainScope : 'Evidence Chain Scope';
        inout item evidenceChainAssessment : 'Evidence Chain Assessment';
        inout item caseConfigurationRequest : 'Case Configuration Request';
        inout item caseConfigurationDraft : 'Case Configuration Draft';
        inout item controlledCaseConfiguration : 'Controlled Case Configuration';
        inout item configurationStatus : 'Configuration Status';
        inout item designChangeRequest : 'Design Change Request';
        inout item changeRevisionPackage : 'Change Revision Package';
        inout item changeImpactAssessment : 'Change Impact Assessment';
        inout item changeEvidencePackage : 'Change Evidence Package';
        inout item candidateComparisonRequest : 'Candidate Comparison Request';
        inout item candidateComparisonPackage : 'Candidate Comparison Package';
        inout item designReviewRequest : 'Design Review Request';
        inout item reviewFindings : 'Review Findings';
        inout item findingDisposition : 'Finding Disposition';
        inout item reviewStatus : 'Review Status';
    }

    port def 'Research Governance Port' {
        inout item transferVerification : 'Transfer Verification Record';
        inout item caseConfigurationDraft : 'Case Configuration Draft';
        inout item adaptationDecision : 'Adaptation Decision';
        inout item comparisonProtocol : 'Comparison Protocol';
        inout item analysisResult : 'Analysis Result Package';
        inout item sensitivityAndUncertainty : 'Sensitivity and Uncertainty Assessment';
        inout item candidateComparisonPackage : 'Candidate Comparison Package';
    }

    port def 'Independent Review Port' {
        inout item transferVerification : 'Transfer Verification Record';
        inout item reproductionRequest : 'Reproduction Request';
        inout item reproducedResult : 'Analysis Result Package';
        inout item reproductionVerdict : 'Reproduction Verdict';
        inout item reviewPackage : 'Review Package';
        inout item reviewFindings : 'Review Findings';
        inout item reviewOutcome : 'Review Outcome';
        inout item reviewStatus : 'Review Status';
    }

    port def 'Model Control Port' {
        inout item transferVerification : 'Transfer Verification Record';
        inout item controlledModelRecords : 'Controlled Model Records';
        inout item commonCorePackage : 'Common Core Package';
        inout item candidateModelPackage : 'Candidate Model Package';
        inout item artifactRegistrations : 'Artifact Registration Set';
        inout item controlledCaseConfiguration : 'Controlled Case Configuration';
        inout item acceptedChangeRevision : 'Change Revision Package';
    }

    port def 'Analysis Execution Port' {
        inout item transferVerification : 'Transfer Verification Record';
        inout item executionRequest : 'Analysis Execution Request';
        inout item analysisResult : 'Analysis Result Package';
    }

    port def 'Evidence Custody Port' {
        inout item transferVerification : 'Transfer Verification Record';
        inout item retainedEvidenceRecords : 'Retained Evidence Records';
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

    interface def <'IF-01'> 'Mission Application Interface' {
        end missionTeam : 'Mission Application Port';
        end framework : 'Mission Application Port';

        flow missionTeam.transferVerification to framework.transferVerification;
        flow framework.transferVerification to missionTeam.transferVerification;
        flow missionTeam.evidenceChainRequest to framework.evidenceChainRequest;
        flow framework.evidenceChainScope to missionTeam.evidenceChainScope;
        flow framework.evidenceChainAssessment to missionTeam.evidenceChainAssessment;
        flow missionTeam.caseConfigurationRequest to framework.caseConfigurationRequest;
        flow framework.caseConfigurationDraft to missionTeam.caseConfigurationDraft;
        flow framework.controlledCaseConfiguration to missionTeam.controlledCaseConfiguration;
        flow framework.configurationStatus to missionTeam.configurationStatus;
        flow missionTeam.designChangeRequest to framework.designChangeRequest;
        flow missionTeam.changeRevisionPackage to framework.changeRevisionPackage;
        flow framework.changeImpactAssessment to missionTeam.changeImpactAssessment;
        flow framework.changeEvidencePackage to missionTeam.changeEvidencePackage;
        flow missionTeam.candidateComparisonRequest to framework.candidateComparisonRequest;
        flow framework.candidateComparisonPackage to missionTeam.candidateComparisonPackage;
        flow missionTeam.designReviewRequest to framework.designReviewRequest;
        flow framework.reviewFindings to missionTeam.reviewFindings;
        flow missionTeam.findingDisposition to framework.findingDisposition;
        flow framework.reviewStatus to missionTeam.reviewStatus;
    }

    interface def <'IF-02'> 'Research Governance Interface' {
        end researcher : 'Research Governance Port';
        end framework : 'Research Governance Port';

        flow researcher.transferVerification to framework.transferVerification;
        flow framework.transferVerification to researcher.transferVerification;
        flow framework.caseConfigurationDraft to researcher.caseConfigurationDraft;
        flow researcher.adaptationDecision to framework.adaptationDecision;
        flow researcher.comparisonProtocol to framework.comparisonProtocol;
        flow framework.analysisResult to researcher.analysisResult;
        flow researcher.sensitivityAndUncertainty to framework.sensitivityAndUncertainty;
        flow framework.candidateComparisonPackage to researcher.candidateComparisonPackage;
    }

    interface def <'IF-03'> 'Independent Review Interface' {
        end reviewer : 'Independent Review Port';
        end framework : 'Independent Review Port';

        flow reviewer.transferVerification to framework.transferVerification;
        flow framework.transferVerification to reviewer.transferVerification;
        flow reviewer.reproductionRequest to framework.reproductionRequest;
        flow framework.reproducedResult to reviewer.reproducedResult;
        flow framework.reproductionVerdict to reviewer.reproductionVerdict;
        flow framework.reviewPackage to reviewer.reviewPackage;
        flow reviewer.reviewFindings to framework.reviewFindings;
        flow reviewer.reviewOutcome to framework.reviewOutcome;
        flow framework.reviewStatus to reviewer.reviewStatus;
    }

    interface def <'IF-04'> 'Model Control Interface' {
        end systemModel : 'Model Control Port';
        end framework : 'Model Control Port';

        flow systemModel.transferVerification to framework.transferVerification;
        flow framework.transferVerification to systemModel.transferVerification;
        flow systemModel.controlledModelRecords to framework.controlledModelRecords;
        flow systemModel.commonCorePackage to framework.commonCorePackage;
        flow systemModel.candidateModelPackage to framework.candidateModelPackage;
        flow framework.artifactRegistrations to systemModel.artifactRegistrations;
        flow framework.controlledCaseConfiguration to systemModel.controlledCaseConfiguration;
        flow framework.acceptedChangeRevision to systemModel.acceptedChangeRevision;
    }

    interface def <'IF-05'> 'Analysis Execution Interface' {
        end framework : 'Analysis Execution Port';
        end analysisTool : 'Analysis Execution Port';

        flow framework.transferVerification to analysisTool.transferVerification;
        flow analysisTool.transferVerification to framework.transferVerification;
        flow framework.executionRequest to analysisTool.executionRequest;
        flow analysisTool.analysisResult to framework.analysisResult;
    }

    interface def <'IF-06'> 'Evidence Custody Interface' {
        end repository : 'Evidence Custody Port';
        end framework : 'Evidence Custody Port';

        flow repository.transferVerification to framework.transferVerification;
        flow framework.transferVerification to repository.transferVerification;
        flow repository.retainedEvidenceRecords to framework.retainedEvidenceRecords;
        flow framework.artifactRegistrations to repository.artifactRegistrations;
        flow framework.evidenceChainAssessment to repository.evidenceChainAssessment;
        flow framework.controlledCaseConfiguration to repository.controlledCaseConfiguration;
        flow framework.configurationStatus to repository.configurationStatus;
        flow framework.analysisResult to repository.analysisResult;
        flow framework.reproductionVerdict to repository.reproductionVerdict;
        flow framework.changeEvidencePackage to repository.changeEvidencePackage;
        flow framework.candidateComparisonPackage to repository.candidateComparisonPackage;
        flow framework.reviewPackage to repository.reviewPackage;
        flow framework.reviewStatus to repository.reviewStatus;
    }
} // package FrameworkBoundaryInterfaces

package FrameworkSystemContext {
    private import ToBeOperationalDomain::*;
    private import FrameworkBoundaryInterfaces::*;

    doc
    /* The context contains one opaque framework and every external participant or resource that
     * exchanges information with it in the mission scenarios. The mission team, researcher, system
     * model, analysis tools, and evidence repository are enterprise resources. The reviewer remains
     * external to the enterprise. All six remain external to the framework system boundary.
     */

    part 'Framework System Context' {
        part missionTeam : 'Academic Mission Team';
        part researcher : 'Academic Researcher';
        part reviewer : Reviewer;
        #systemOfInterest part framework : 'Nanosatellite EPS Engineering Framework';
        part systemModel : 'Versioned System Model';
        part analysisTools : 'Analysis Tools';
        part evidenceRepository : 'Evidence Repository';

        interface missionApplication : 'Mission Application Interface'
            connect missionTeam.frameworkApplication to framework.missionApplication;
        interface researchGovernance : 'Research Governance Interface'
            connect researcher.frameworkResearch to framework.researchGovernance;
        interface independentReview : 'Independent Review Interface'
            connect reviewer.frameworkReview to framework.independentReview;
        interface modelControl : 'Model Control Interface'
            connect systemModel.frameworkControl to framework.modelControl;
        interface analysisExecution : 'Analysis Execution Interface'
            connect framework.analysisExecution to analysisTools.frameworkExecution;
        interface evidenceCustody : 'Evidence Custody Interface'
            connect evidenceRepository.frameworkCustody to framework.evidenceCustody;
    }
} // package FrameworkSystemContext
