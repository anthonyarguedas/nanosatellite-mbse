// Current native interface specification and black-box function signatures.
package BoundaryViews {
    private import FrameworkDomain::*;
    private import ScalarValues::*;
    doc /* Versioned interface specifications define information meaning and receiving checks. Algorithm, transport, tool implementation and storage selections belong to later architecture. IF-05 is retired with no current participant or exchange. */

    // Typed black-box signatures. Mission-level definitions are unchanged.
    // The shared legacy signatures in FrameworkDomain are compatibility bases only.
    item def Quantity :> EngineeringArtifact {
        attribute value : Real [0..1];
        attribute unit : String;
        attribute quantityKind : String;
        attribute uncertainty : String;
        attribute unknownReason : String [0..1];
    }
    item def ContextRevision :> EngineeringArtifact {
        attribute missionRevision : String;
        attribute requirementsRevision : String;
        attribute designRevision : String;
        attribute sourcesRevision : String;
        attribute criteriaRevision : String;
        attribute scopeRevision : String;
    }
    item def EngineeringDecision :> NeedRequirementDecision {
        attribute authorizedRole : String;
        attribute disposition : String;
        attribute rationale : String;
        attribute subjectRevision : String;
        attribute acceptedModifiedRejectedDeferred : String;
        doc /* An identified human decision. Technical review progression additionally requires TechnicalReviewDecision and agreed success criteria. */
    }
    item def RequirementRecord :> NeedRequirementDecision {
        attribute statement : String;
        attribute level : String;
        attribute parentAndSourceRevisions : String [0..*];
        attribute conditionQuantityUnitCriterion : String;
        attribute ownerAndMethod : String;
        attribute unresolvedOrInapplicableRationale : String;
    }
    item def MissionDefinition :> EPSModelArtifact {
        attribute expectationsConstraints : String [0..*];
        attribute orbitAttitudeDurationEnvironment : String;
        attribute nominalDegradedConOps : String;
        attribute modesLoadsSchedulesTransitions : String;
        attribute scenarioRevision : String;
    }
    item def DesignConfiguration :> EPSModelArtifact {
        ref item mission : MissionDefinition;
        ref item requirements : RequirementRecord [0..*];
        attribute functionsElementsAllocationsInterfaces : String;
        attribute candidateComponentVariants : String;
        attribute parametersExtensionsAssumptions : String;
        attribute physicalDesignModelReferences : String [0..*];
    }
    item def DesignStudy :> BOMCostRAM {
        ref item configuration : DesignConfiguration;
        ref item quantities : Quantity [0..*];
        attribute powerEnergySizingEquationsMargins : String;
        attribute bomMassVolumeCostAvailability : String;
        attribute commonCriteriaAlternativesSensitivity : String;
        attribute feasibilityRiskUnknowns : String;
    }
    item def GuidanceRequest :> EngineeringArtifact {
        ref item context : ContextRevision;
        attribute phaseMaturityQuestion : String;
        attribute availableInputsValidityResourcesScope : String;
        attribute trigger : String;
    }
    item def AssistanceFinding :> EngineeringArtifact {
        attribute affectedTextRecords : String;
        attribute ruleOrSourcePassage : String;
        attribute correctionOrQuestion : String;
        attribute deterministicOrProbable : String;
        attribute uncertaintyAssessmentLimit : String;
        attribute assessedNotAssessedNoFinding : String;
    }
    item def MethodRecommendation :> EngineeringArtifact {
        attribute methodOrModelPurpose : String;
        attribute applicabilityInputsValidityResourcesScope : String;
        attribute rationaleSourcePassage : String;
        attribute alternativesRejectionsUnresolvedGaps : String;
        attribute assessedScopeUncertainty : String;
    }
    item def AssistanceReport :> KnowledgeCaseReview {
        ref item context : ContextRevision;
        ref item findings : AssistanceFinding [0..*];
        ref item recommendations : MethodRecommendation [0..*];
        attribute prerequisiteActivitiesReassessments : String;
        attribute ruleReferenceAssessmentRevision : String;
        attribute currentStalePendingUnavailable : String;
        attribute triggerTimeFirstResponseTimeCompletionTimeSeconds : String;
        doc /* Suggestions establish no technical verification or human approval. A later edit invalidates currency before a late response can be applied. */
    }
    item def ReferenceData :> ObservationPackage {
        attribute independentCalibrationAssessmentUse : String;
        attribute channelsUnitsSampleReceiptTimes : String;
        attribute completenessInvalidValuesMasks : String;
        attribute suppliedSourceDomainUncertainty : String;
    }
    item def ModelAssessment :> ModelCredibility {
        attribute intendedUseFidelityMechanismsOmissions : String;
        attribute validityDomainNumericalChecks : String;
        attribute calibrationDataRevision : String [0..1];
        attribute independentAssessmentDataRevision : String [0..1];
        attribute residualsUncertaintyAcceptanceRules : String;
        attribute reviewerDispositionEvidenceGaps : String;
    }
    item def AnalysisPlan :> ScenarioAnalysisPlan {
        ref item configuration : DesignConfiguration;
        ref item assessment : ModelAssessment;
        attribute methodInputsOutputsCriterion : String;
        attribute scenarioTimeStepCouplingConvergence : String;
        attribute environmentVersionsResourcesRuntimeLimit : String;
        attribute selectedFaultsProtectionRecovery : String;
    }
    item def AnalysisResult :> RunPackage {
        ref item plan : AnalysisPlan;
        ref item samples : ReferenceData [0..*];
        attribute exactVersionsInputsEnvironmentRawOutputs : String;
        attribute executionSuccessFailedCancelledPartial : String;
        attribute quantitiesLimitsUncertaintyCriterionVerdicts : String;
        attribute replayDependenciesSeedsComparisonRules : String;
    }
    item def EPSInterfaceSpecification :> ArchitectureServiceContract {
        attribute endpointsIdentifiersTypesUnitsRangesEncoding : String;
        attribute polarityTimeModeOwnership : String;
        attribute commandsTelemetryEventsParameters : String;
        attribute guardsOrderEffectsRejectionRecovery : String;
        attribute selectedSoftwareMappingRevision : String;
        attribute unsupportedOrLossyMeanings : String;
    }
    item def EPSAssessmentPlan :> VerificationSpecification {
        ref item configuration : DesignConfiguration;
        attribute verificationRequirements : String [0..*];
        attribute validationExpectationsConOps : String [0..*];
        attribute subjectMethodConditionsInputsExpectedCriterion : String;
        attribute observationsApplicabilityLimitsStatus : String;
        doc /* EPS phase-product assessment plan only. Framework V&V and research evaluation have different subjects. Analysis, MIL and SIL use no target hardware. */
    }
    item def SoftwareAssessment :> EngineeringArtifact {
        ref item specification : EPSInterfaceSpecification;
        attribute scopedBehaviorMappingCompatibilityGaps : String;
        attribute milSilComparisonDisposition : String;
    }
    item def HostSoftwareProduct :> SoftwareArtifact {
        attribute sourceBuildDependencyRevision : String;
        attribute declaredHostEnvironment : String;
        attribute authorizedDesignRelease : String;
    }
    item def SoftwareRunResult :> RunPackage {
        ref item product : HostSoftwareProduct;
        attribute hostToolchainBuildLogs : String;
        attribute simulatedInputsExpectedOutputsActualOutputs : String;
        attribute milSilDifferencesFailuresStatus : String;
    }
    item def ChangeProposal :> NeedRequirementDecision {
        ref item previousBaseline : PhaseBaseline;
        attribute submittedReplacementsRationale : String;
        attribute reciprocalImpactsUnresolvedDependencies : String;
        attribute repeatedChecksStaleEvidence : String;
        ref item decision : EngineeringDecision [0..1];
    }
    item def ReviewRequest :> EngineeringArtifact {
        ref item baseline : PhaseBaseline;
        attribute phaseReviewEntranceSuccessCriteriaRevision : String;
        attribute requestedAssessmentScope : String;
    }
    item def ReviewFinding :> EngineeringArtifact {
        attribute baselineCriteriaSubject : String;
        attribute blockingConditionalAdvisory : String;
        attribute findingRationaleActionOwnerDueDate : String;
    }
    item def ReviewPackage :> TechnicalReviewPackage {
        ref item evidence : AnalysisResult [0..*];
        ref item findings : ReviewFinding [0..*];
        attribute requirementsExpectationsCoverage : String;
        attribute designDecisionsViewsLimitsGaps : String;
    }
    item def EngineeringSubmission :> Submission01 {
        ref item context : ContextRevision;
        ref item mission : MissionDefinition [0..1];
        ref item requirements : RequirementRecord [0..*];
        ref item design : DesignConfiguration [0..1];
        ref item guidance : GuidanceRequest [0..1];
        ref item changes : ChangeProposal [0..*];
        ref item decisions : EngineeringDecision [0..*];
        ref item review : ReviewRequest [0..1];
    }
    item def EngineeringResponse :> Response01 {
        ref item context : ContextRevision;
        ref item assistance : AssistanceReport [0..1];
        ref item study : DesignStudy [0..1];
        ref item assessment : ModelAssessment [0..1];
        ref item changes : ChangeProposal [0..*];
        ref item baseline : PhaseBaseline [0..1];
        ref item reviewPackage : ReviewPackage [0..1];
        attribute transferFindingsStatus : String;
    }
    item def SourceSubmission :> Submission02 {
        attribute sourceAuthorityRevisionLocator : String;
        attribute componentPropertiesPricesDatesEvidence : String;
        attribute methodsModelsApplicabilityLimits : String;
        ref item referenceData : ReferenceData [0..*];
    }
    item def SourceQuery :> Response02 {
        attribute questionRequiredPropertiesSourceRevision : String;
        attribute receiptFindingsUnknowns : String;
    }
    item def AnalysisRequest :> Submission03 { ref item plan : AnalysisPlan; }
    item def AnalysisResponse :> Response03 {
        attribute requestRevisionEnvironmentRuntimeStatus : String;
        attribute unsupportedMappingsDiagnostics : String;
    }
    item def CodingResponse :> Submission04 {
        attribute requestDesignRevisionHostEnvironmentStatus : String;
        attribute diagnosticsCompatibilityGaps : String;
    }
    item def CodingRequest :> Response04 {
        ref item design : EPSInterfaceSpecification;
        attribute approvedScopeBuildSilInputsCriteria : String;
        attribute requiredHostVersionsDependencies : String;
    }
    item def ReviewSubmission :> Submission06 {
        ref item findings : ReviewFinding [0..*];
        ref item decisions : TechnicalReviewDecision [0..*];
        attribute subjectBaselineAuthorizedRole : String;
    }
    item def ReviewResponse :> Response06 {
        ref item reviewPackage : ReviewPackage;
        attribute recordedDispositionProgressionConditions : String;
    }
    port def EngineeringUsePort :> P01 {
        in item engineeringSubmission : EngineeringSubmission :>> submission;
        out item engineeringResponse : EngineeringResponse :>> response;
    }
    port def KnowledgePort :> P02 {
        in item sourceSubmission : SourceSubmission :>> submission;
        out item sourceQuery : SourceQuery :>> response;
    }
    port def AnalysisPort :> P03 {
        out item analysisRequest : AnalysisRequest :>> submission;
        in item analysisResponse : AnalysisResponse :>> response;
        out item analysisPlan : AnalysisPlan :>> executionPlan;
        in item analysisResult : AnalysisResult :>> rawResult;
    }
    port def HostSoftwarePort :> P04 {
        in item codingResponse : CodingResponse :>> submission;
        out item codingRequest : CodingRequest :>> response;
        out item interfaceSpecification : EPSInterfaceSpecification :>> sharedContract;
        in item softwareProduct : HostSoftwareProduct :>> implementationArtifact;
        in item softwareResult : SoftwareRunResult :>> resourceEvidence;
    }
    port def TechnicalReviewPort :> P06 {
        in item reviewSubmission : ReviewSubmission :>> submission;
        out item reviewResponse : ReviewResponse :>> response;
    }
    interface def <'IF-01'> EngineeringUseInterface {
        end client : ~EngineeringUsePort;
        end framework : EngineeringUsePort;
    }
    interface def <'IF-02'> KnowledgeInterface {
        end client : ~KnowledgePort;
        end framework : KnowledgePort;
    }
    interface def <'IF-03'> AnalysisInterface {
        end client : ~AnalysisPort;
        end framework : AnalysisPort;
    }
    interface def <'IF-04'> HostSoftwareInterface {
        end client : ~HostSoftwarePort;
        end framework : HostSoftwarePort;
    }
    interface def <'IF-06'> TechnicalReviewInterface {
        end client : ~TechnicalReviewPort;
        end framework : TechnicalReviewPort;
    }
    action def F01 :> FrameworkDomain::F01 {
        in item request : GuidanceRequest;
        out item guidance : AssistanceReport;
        doc /* F01: Recommend lifecycle activities, derivation/analysis/V&V methods and models from the current question, maturity, dependencies and scoped resources. */
    }
    action def F02 :> FrameworkDomain::F02 {
        in item submission : EngineeringSubmission;
        out item response : EngineeringResponse;
        doc /* F02: Check drafts actively, explain findings and corrections, derive and allocate requirements with engineer dispositions and bidirectional traces. */
    }
    action def F03 :> FrameworkDomain::F03 {
        in item configuration : DesignConfiguration;
        out item study : DesignStudy;
        doc /* F03: Calculate preliminary power/energy budgets and sizing, characterize modeled components and compare EPS alternatives with resources and uncertainty. */
    }
    action def F04 :> FrameworkDomain::F04 {
        in item :>> observations : ReferenceData [0..*];
        in item plan : AnalysisPlan;
        out item result : AnalysisResult;
        doc /* F04: Coordinate coupled time-dependent and applicable RAM analyses, model assessment and reproducible execution through declared software tools. */
    }
    action def F05 :> FrameworkDomain::F05 {
        in item specification : EPSInterfaceSpecification;
        out item assessment : SoftwareAssessment;
        doc /* F05: Specify and check detailed EPS control/interfaces, coordinate approved host coding and MIL/SIL assessment against simulated products. */
    }
    action def F06 :> FrameworkDomain::F06 {
        in item :>> analyticalResults : AnalysisResult [0..*];
        in item plan : EPSAssessmentPlan;
        out item findings : ReviewFinding [0..*];
        doc /* F06: Plan EPS phase-product verification and validation and assess applicable results against requirements and expectations with explicit limitations. */
    }
    action def F07 :> FrameworkDomain::F07 {
        in item proposal : ChangeProposal;
        out item baseline : PhaseBaseline;
        doc /* F07: Check transfers, identify impacts, invalidate affected guidance/evidence and retain coherent successors only after authorized engineering decisions. */
    }
    action def F08 :> FrameworkDomain::F08 {
        in item request : ReviewRequest;
        out item reviewPackage : ReviewPackage;
        doc /* F08: Prepare baseline-linked views and review evidence, record findings and designated authority decisions against agreed scoped success criteria. */
    }
    @InterfaceControl about EngineeringUsePort {
        owner = "IF-01, F01/F02/F03/F07, engineering use";
        validation = "Current context revision, scoped request, record fields, decision identity and authorized role";
        failureBehavior = "Retain raw request and findings. Incomplete drafts remain unresolved. Unauthorized or stale decisions change no controlled record.";
    }
    @InterfaceControl about KnowledgePort {
        owner = "IF-02, F01/F03/F04, knowledge and supplied data";
        validation = "Source locator, authority, revision, applicability, quantity units and data-use separation";
        failureBehavior = "Keep missing properties unknown and conflicting sources separate. Source retrieval establishes no truth or mandatory applicability.";
    }
    @InterfaceControl about AnalysisPort {
        owner = "IF-03, F04/F06/F07, model execution";
        validation = "Plan and model revision, supported discipline mappings, validity, units, time base, convergence and environment";
        failureBehavior = "Retain failed/cancelled/partial logs and raw results. Unsupported effects, failed numerical checks or out-of-domain results support no unqualified conclusion.";
    }
    @InterfaceControl about HostSoftwarePort {
        owner = "IF-04, F05/F06/F07, host coding/build/SIL";
        validation = "Authorized design release, scope, interface revision, selected integration profile, host dependencies and build identity";
        failureBehavior = "Block unreleased coding. Retain build failures and mapping gaps. MIL/SIL establishes no target-hardware qualification.";
    }
    @InterfaceControl about TechnicalReviewPort {
        owner = "IF-06, F08/F07, technical review";
        validation = "Exact baseline, scoped criteria revision, findings and designated review authority";
        failureBehavior = "A prepared package confers no acceptance. Blocking findings prevent progression. Conditional decisions retain limits, actions, owners and dates. Reject unauthorized or stale-baseline dispositions.";
    }
}
