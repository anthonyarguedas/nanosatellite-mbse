// Proposed physical realization of the published six-component working API.
// Native consistency and planned allocation are separate from empirical qualification.
package PhysicalVocabulary {
    private import ScalarValues::*;
    private import FrameworkDomain::*;
    private import BoundaryViews::*;
    private import FrameworkLogical::*;
    metadata def PhysicalAllocation {
        attribute rationale : String;
        attribute plannedCheck : String;
        ref operation : SysML::ActionUsage;
    }
    metadata def physicalPrimary;
    metadata def physicalSupport;
    metadata def logicalRealization;
    metadata def executionHost;
    metadata def persistentStorage;
    metadata def procedurePerformer;
    metadata def physicalDetail;
    metadata def ComponentSpecification {
        attribute tools : String;
        attribute logical : String;
        attribute sourceMethods : String [0..*];
        attribute authority : String;
        attribute verificationNeed : String;
        attribute status : String;
    }
    metadata def ComparisonMechanism {
        attribute mop : String;
        attribute mechanism : String;
        attribute achieved : String = "unknown";
        ref operation : SysML::ActionUsage;
    }
    part def SoftwareResource;
    // Common required platform and Jev method contracts. Logical adapters are defined after export synchronization.
    package IntegrationScaffold {
        private import ScalarValues::*;
        private import FrameworkDomain::*;
        private import BoundaryViews::*;
        doc /* Proposed common platform and custom recommendation contracts. These definitions specify unexecuted work. They contain no candidate selection, engineering approval or empirical outcome. */

        part def RequiredFPrimeProfile {
            port hostSoftware : HostSoftwarePort;
            ref item interfaceMeaning : EPSInterfaceSpecification;
            attribute fPrimeRepresentationToolchainVersions : String;
            attribute componentsInstancesPortsTopology : String;
            attribute commandsTelemetryEventsParameters : String;
            attribute entityUnitPolarityEncodingTimeModeMappings : String;
            attribute unsupportedLossyCompatibilityFindings : String;
            attribute status : String = "proposed/unexecuted";
            doc /* Required F Prime host software profile for every candidate. Declare exact representation, tool and dependency versions. Architecture translation alone supplies neither mission behavior nor complete ground definitions. Coding/build admission requires a current engineer-authorized exact design/interface/software release. A successful host build supplies no SIL verdict or target qualification. */
        }
        part def RequiredWholeCUBICSProfile {
            port numericalExchange : AnalysisPort;
            ref item coupling : SimulationCouplingProfile;
            attribute epsSolverModelAndWholeSpacecraftRevisions : String;
            attribute incomingSpacecraftSubsystemHistories : String;
            attribute outgoingEPSStatesResultsSameScenario : String;
            attribute unitEntityTimeAdmissionAndUnsupportedEffects : String;
            attribute status : String = "proposed/unexecuted";
            doc /* Required NVIDIA Omniverse whole-CUBICS numerical connection for every candidate. AnalysisPort receives spacecraft/subsystem inputs and returns EPS responses for the same identified scenario. Scene display alone is insufficient. Entity/channel/quantity/unit, sample/receipt/scenario time, synchronization limits, delays, model revisions and supported effects are declared by coupling. Specialized external tools may compute EPS physics. Preserve raw invalid/missing/inactive samples, masks, failed/partial/cancelled statuses and transfer limitations. */
        }
        part def RequiredPlatformConnections {
            part fPrime : RequiredFPrimeProfile;
            part wholeCUBICS : RequiredWholeCUBICSProfile;
            doc /* Both connections are mandatory. This template is independent of logical component names. The simulation/software component binds both through managed IF-03/04. */
        }
        @SourceRecord about RequiredPlatformConnections {
            identifier = "PA-common-platform-contract";
            sourceText = "Required F Prime host software and numerical whole-CUBICS NVIDIA Omniverse connections. Source methods supply bounded architecture/battery mapping patterns. Whole-spacecraft and combined software adapters are proposed additions.";
            sourceLocator = "Halvorson/Thomas sections 3-4. Zhu PDF pages 4-5. Final FR-18/24/33/34/36.";
            citationRecord = "review-0853, handpicked-0001";
            status = "proposed/unexecuted";
        }

        item def MethodContext :> EngineeringArtifact {
            ref item contextRevision : ContextRevision;
            ref item nativeSubjectsAndInputs : EngineeringArtifact [0..*];
            attribute lifecyclePurposeQuestion : String;
            attribute requiredEffectsAvailableInputsValidityResources : String;
            attribute nativeSourceClassifierRubricRevisions : String;
        }
        item def EngineeringMethod :> EngineeringArtifact {
            attribute analysisOrVerificationOrValidation : String;
            attribute purposeApplicableSubjectsAndLifecycle : String;
            attribute requiredInputsQuantitiesUnitsAndValidity : String;
            attribute supportedEffectsOmissionsUncertainty : String;
            attribute independentReferenceAndAssessmentNeeds : String;
            attribute executionResourcesAndOutputMeaning : String;
            attribute sourceExcerptsLocatorsAuthorityRevisions : String;
        }
        item def MethodSuggestion :> EngineeringArtifact {
            ref item method : EngineeringMethod;
            attribute classifierScore : Real [0..1];
            attribute eligibilityInputsValidityResourcesFindings : String;
            attribute explanationCitationsRejectedAlternatives : String;
            doc /* A Jev score ranks a possible analysis or V&V method. Applicability is assessed separately against actual inputs, supported effects, maturity, resources and independent reference needs. Neither a score nor a suggestion authorizes execution, changes a design or establishes conformity. */
        }
        item def MethodRecommendations :> EngineeringArtifact {
            ref item context : MethodContext;
            ref item suggestions : MethodSuggestion [0..*];
            attribute requestedReturnedClassifierRubricIdentities : String;
            attribute rawResponseDigestTruncationAndServiceStatus : String;
            attribute eligibleNoneAbstainedStaleUnavailable : String;
        }
        item def EngineerMethodDisposition :> EngineeringArtifact {
            ref item context : MethodContext;
            ref item suggestion : MethodSuggestion;
            attribute responsibleEngineerAndAuthority : String;
            attribute acceptedModifiedRejectedDeferred : String;
            attribute applicabilityRationaleAndExecutionRequest : String;
            doc /* Preserve an engineer's decision as a separate record. An accepted suggestion still needs the applicable current-context, data admission and execution gates. */
        }
        action def AdmitJevMethodRequest {
            in profile : RequiredJevClassifier;
            in context : MethodContext;
            in methods : EngineeringMethod [0..*];
            out attribute authorizedPinnedQualifiedCurrent : Boolean;
            doc /* Require authorized minimized payload, source/data rights, declared service access, pinned requested identity and qualified analysis/V&V rubrics, current context, input limits and bounded timeout/retry. Outage returns unavailable. It never silently substitutes a local classifier. */
        }
        action def RequestJevMethodScores {
            in profile : RequiredJevClassifier;
            in context : MethodContext;
            in methods : EngineeringMethod [0..*];
            out response : MethodRecommendations;
            doc /* The required Jev classifiers suggest analyses and verification/validation methods. Preserve actual returned identity, raw scores, input truncation and service failures. Jev supplies no independent engineering explanation or execution authority. */
        }
        action def CheckJevMethodResponse {
            in profile : RequiredJevClassifier;
            in context : MethodContext;
            in response : MethodRecommendations;
            out attribute pinnedFiniteCompleteCurrent : Boolean;
        }
        action def ExplainApplicableMethods {
            in context : MethodContext;
            in response : MethodRecommendations;
            out recommendations : MethodRecommendations;
            doc /* Python checks method prerequisites and explains retained source/context comparisons separately from Jev ranking. Missing inputs, unsupported effects, unqualified identity, stale context or unavailable evidence cause rejection or abstention. The engineer makes the applicability and acceptance decision. */
        }
        action def UnavailableMethodRecommendations {
            in context : MethodContext;
            in response : MethodRecommendations [0..1];
            out recommendations : MethodRecommendations;
            bind recommendations.context = context;
            attribute scoringStatus : String = "unavailable/abstained";
            doc /* Preserve request and any raw response. Return unavailable or abstained status, distinct from an assessed no-eligible-method result. */
        }
        action def JevMethodRecommendations {
            ref part classifier : RequiredJevClassifier;
            in context : MethodContext;
            in methods : EngineeringMethod [0..*];
            out recommendations : MethodRecommendations;
            perform action admission : AdmitJevMethodRequest;
            perform action classify : RequestJevMethodScores;
            perform action checkResponse : CheckJevMethodResponse;
            perform action explain : ExplainApplicableMethods;
            perform action unavailable : UnavailableMethodRecommendations;
            first start then admission;
            first admission if admission.authorizedPinnedQualifiedCurrent then classify;
            first admission if not admission.authorizedPinnedQualifiedCurrent then unavailable;
            first classify then checkResponse;
            first checkResponse if checkResponse.pinnedFiniteCompleteCurrent then explain;
            first checkResponse if not checkResponse.pinnedFiniteCompleteCurrent then unavailable;
            first explain then done;
            first unavailable then done;
            bind admission.profile = classifier;
            bind classify.profile = classifier;
            bind checkResponse.profile = classifier;
            bind admission.context = context;
            bind admission.methods = methods;
            bind classify.context = context;
            bind classify.methods = methods;
            bind checkResponse.context = context;
            bind checkResponse.response = classify.response;
            bind explain.context = context;
            bind explain.response = classify.response;
            bind unavailable.context = context;
            flow rawUnavailableResponse of MethodRecommendations from classify.response to unavailable.response;
            flow explained of MethodRecommendations from explain.recommendations to recommendations;
            flow unavailableReport of MethodRecommendations from unavailable.recommendations to recommendations;
            doc /* Proposed guarded method service. Logical presentation/application currency and human authority guards remain additional requirements at integration. This action neither applies guidance nor implements an engineering analysis. */
        }
        part def RequiredJevClassifier {
            attribute requestedPinnedClassifierAndRubricVersions : String;
            attribute authorizedDataPolicyAccessTimeoutRetry : String;
            attribute qualificationEvidenceAndLimits : String;
            doc /* Mandatory PA-CDT analysis/V&V classifier role. Concrete identities and qualification evidence are supplied by a controlled project profile. An inaccessible or unqualified Jev service produces explicit unavailable guidance. */
        }
        part def RequiredJevRecommendations {
            part classifier : RequiredJevClassifier;
            perform action recommendMethods : JevMethodRecommendations {
                bind classifier = RequiredJevRecommendations::classifier;
            }
        }
    }
    part def HostResource {
        attribute runtimeToolAndDependencyVersions : String;
        attribute declaredCapacityAccessRecovery : String;
        doc /* Generic computation and storage roles. Capacity, access and recovery require verification. These are framework infrastructure, not executing EPS hardware or a preferred deployment. */
    }
    part def ResponsibilityNode { attribute responsibilityAndLocation : String; }
    item def ControlledData :> EngineeringArtifact {
        ref item context : ContextRevision;
        attribute digestSchemaProducerAndSourceRevisions : String;
        attribute proposedReleasedStaleFailedStatus : String;
    }
    item def ModelData :> ControlledData {
        ref item requirements : RequirementAllocation [0..*];
        ref item designs : DesignWork [0..*];
        ref item interfaces : EPSInterfaceSpecification [0..*];
    }
    item def AdviceData :> ControlledData {
        ref item reports : AssistanceReport [0..*];
        ref item dispositions : SuggestionDisposition [0..*];
    }
    item def ReleaseData :> ControlledData {
        ref item baselines : PhaseBaseline [0..*];
        ref item models : ModelData [0..*];
        ref item advice : AdviceData [0..*];
        ref item runs : RunWork [0..*];
        ref item assessments : EvidenceAssessment [0..*];
        ref item rejectedTransfers : CheckedTransfer [0..*];
        doc /* Exact native/vendor/source/software revisions, raw outputs, masks, logs, statuses, decisions and replay dependencies remain retrievable. A digest proves identity only. */
    }
    item def AuthoringRecords :> ControlledData {
        ref item requirements : RequirementRecord [0..*];
        ref item quantities : Quantity [0..*];
        ref item interfaces : EPSInterfaceSpecification [0..*];
        attribute relationsModesOwnershipAndSchema : String;
    }
    item def COMETRecords :> AuthoringRecords {
        attribute serverStudyCatalogueAndCategoryRevisions : String;
        attribute workbookCellsAddInAndParameterOwners : String;
    }
    item def CapellaValispaceRecords :> AuthoringRecords {
        attribute architectureTreeRequirementAndModeExportRevisions : String;
        attribute valispaceParameterAndSynchronizationScriptRevisions : String;
        attribute asynchronousTransferAndAuthorityFindings : String;
    }
    item def NanospaceRecords :> AuthoringRecords {
        attribute databaseSnapshotAPISchemaAndRequirementRelations : String;
        attribute dependencyGraphHDDLDomainProblemAndPlannerRevisions : String;
    }
    item def YAMLCSRMRecords :> AuthoringRecords {
        attribute gitRevisionYAMLSchemaAndCSRMTraceRevisions : String;
        attribute schemaAndSemanticServiceFindings : String;
    }
    item def NativeRecords :> AuthoringRecords {
        attribute nativeSubjectRequirementQuantityCalculationBindingRevisions : String;
        attribute ruleSourceClassifierRubricRevisions : String;
    }
    part def AuthoringProfile {
        ref item currentRecords : AuthoringRecords;
        ref item sourcedMethods : IntegrationScaffold::EngineeringMethod [0..*];
        attribute qualityRulesSemanticChecksAndLimitations : String;
        attribute recommendationContextAndApplicability : String;
    }
    part def COMETAuthoringProfile :> AuthoringProfile {
        ref item records : COMETRecords;
        bind currentRecords = records;
    }
    part def CapellaValispaceAuthoringProfile :> AuthoringProfile {
        ref item records : CapellaValispaceRecords;
        bind currentRecords = records;
    }
    part def NanospaceAuthoringProfile :> AuthoringProfile {
        ref item records : NanospaceRecords;
        bind currentRecords = records;
        part planner : FirstValidHTNProfile;
    }
    part def YAMLCSRMProfile :> AuthoringProfile {
        ref item records : YAMLCSRMRecords;
        bind currentRecords = records;
    }
    part def NativeAuthoringProfile :> AuthoringProfile {
        ref item records : NativeRecords;
        bind currentRecords = records;
    }
    item def HTNPlanProposal :> EngineeringArtifact {
        ref item request : GuidanceRequest;
        attribute domainProblemPlannerFirstValidPlanRevisions : String;
        attribute requiredInputsActionsPrerequisitesAndLimits : String;
        attribute applicabilityRejectionsAndUnknowns : String;
        doc /* Separate proposed integration of the reported first-valid HTN planner. A valid plan is not optimality, execution admission or engineer approval. */
    }
    action def ProposeFirstValidHTNPlan {
        in work : AssistanceWork;
        out proposal : HTNPlanProposal;
        bind proposal.request = work.request;
    }
    part def FirstValidHTNProfile {
        perform action propose : ProposeFirstValidHTNPlan;
        attribute domainProblemPlannerActionLibraryRevisions : String;
    }
    action def CheckDraftRules {
        in work : AssistanceWork;
        in profile : AuthoringProfile;
        out checked : AssistanceWork;
        doc /* Check identified requirement fields, subject, condition, quantity/unit, parent/source revisions and project-approved drafting rules using this exact native/vendor schema. Preserve drafts and dispositions. Findings remain proposed corrections or clarification questions. */
    }
    action def CompanionSemanticChecks {
        in work : AssistanceWork;
        in profile : AuthoringProfile;
        out checked : AssistanceWork;
        doc /* Proposed semantic checks compare subject, level, mode, conditions, quantities, trace and declared coverage. Explain findings, unsupported checks and uncertainty separately from deterministic rules. This service is separate from Jev method suggestions and grants no technical validation or application authority. */
    }
    action def PhysicalCheckDraft :> CheckDraft {
        ref part authoring : AuthoringProfile;
        perform action rules : CheckDraftRules;
        perform action semantics : CompanionSemanticChecks;
        first start then rules;
        first rules then semantics;
        first semantics then done;
        bind rules.work = work;
        bind rules.profile = authoring;
        bind semantics.work = rules.checked;
        bind semantics.profile = authoring;
        bind updatedWork = semantics.checked;
    }
    action def SelectSourcedMethods {
        in work : AssistanceWork;
        in profile : AuthoringProfile;
        in htn : HTNPlanProposal [0..1];
        out report : AssistanceReport;
        bind report.context = work.request.context;
        doc /* Select sourced analysis/V&V and lifecycle methods from the exact catalogue/architecture/database/YAML context. Check purpose, maturity, available inputs, supported effects, validity, resources, prerequisites and independent reference needs. Explain citations and rejected alternatives. If a separate HTN proposal is supplied, check every planned action and prerequisite before recommendation. No-eligible, unavailable and stale outcomes remain distinct. Scores or first-valid plans grant no execution or design-change authority. */
    }
    action def PhysicalRecommendMethods :> RecommendMethods {
        ref part authoring : AuthoringProfile;
        perform action select : SelectSourcedMethods;
        first start then select;
        first select then done;
        bind select.work = work;
        bind select.profile = authoring;
        bind report = select.report;
    }
    action def PhysicalHTNRecommendMethods :> RecommendMethods {
        ref part authoring : NanospaceAuthoringProfile;
        perform action planner : ProposeFirstValidHTNPlan;
        perform action select : SelectSourcedMethods;
        first start then planner;
        first planner then select;
        first select then done;
        bind planner.work = work;
        bind select.work = work;
        bind select.profile = authoring;
        bind select.htn = planner.proposal;
        bind report = select.report;
    }
    action def ReturnAdviceWork {
        in original : AssistanceWork;
        in report : AssistanceReport;
        out updated : AssistanceWork;
        bind updated.submission = original.submission;
        bind updated.request = original.request;
        bind updated.drafts = original.drafts;
        bind updated.dispositions = original.dispositions;
        bind updated.triggerAcknowledgementCompletion = original.triggerAcknowledgementCompletion;
        bind updated.findings = report.findings;
        bind updated.report = report;
    }
    action def PhysicalReassessAssistance :> ReassessAssistance {
        perform action prepare : ReassessAssistance;
        perform action checkDraft : CheckDraft;
        perform action recommend : RecommendMethods;
        perform action returnWork : ReturnAdviceWork;
        first start then prepare;
        first prepare then checkDraft;
        first checkDraft then recommend;
        first recommend then returnWork;
        first returnWork then done;
        bind prepare.impact = impact;
        bind checkDraft.work = prepare.work;
        bind recommend.work = checkDraft.updatedWork;
        bind returnWork.original = checkDraft.updatedWork;
        bind returnWork.report = recommend.report;
        bind work = returnWork.updated;
    }
    item def PhysicalDependencyContext :> ControlledData {
        attribute authoringParameterWorkbookOrToolTransferRevisions : String;
        attribute databaseDependencyPlannerRevisions : String;
        attribute nativeSourceClassifierRuleRevisions : String;
        attribute currentRequestReplyAndInvalidationIdentities : String;
    }
    part def CurrencyProfile {
        ref item latest : PhysicalDependencyContext;
        attribute affectedRevisionKeysAndInvalidationPolicy : String;
    }
    action def CheckPhysicalCurrency {
        in report : AssistanceReport;
        in context : ContextRevision;
        in profile : CurrencyProfile;
        out attribute currentPhysicalDependencies : Boolean;
        doc /* Recheck latest physical source/tool/schema/rule/classifier revisions, not just the saved request. A superseded or unqualified reply is stale/unavailable and cannot replace newer guidance. Preserve raw delayed replies. */
    }
    action def PhysicalCheckCurrency :> CheckCurrency {
        ref part profile : CurrencyProfile;
        out attribute sameContext : Boolean :>> CheckCurrency::sameContext = logicalCheck.sameContext and physicalCheck.currentPhysicalDependencies and report.currentStalePendingUnavailable != "stale";
        perform action logicalCheck : CheckCurrency;
        perform action physicalCheck : CheckPhysicalCurrency;
        first start then logicalCheck;
        first logicalCheck then physicalCheck;
        first physicalCheck then done;
        bind logicalCheck.report = report;
        bind logicalCheck.context = context;
        bind physicalCheck.report = report;
        bind physicalCheck.context = context;
        bind physicalCheck.profile = profile;
    }
    action def InvalidatePhysicalDependencies {
        in submission : EngineeringSubmission;
        in logicalImpact : ImpactNotice;
        in profile : CurrencyProfile;
        out impact : ImpactNotice;
        out updatedSubmission : EngineeringSubmission;
        out attribute physicalChange : Boolean;
        doc /* Immediately mark affected current and pending guidance stale on the profile's revision changes. Preserve predecessor/report/request identities, record extra source/tool/classifier/rule impacts and trigger reassessment. This operation grants no successor or application authority. */
    }
    action def PhysicalInvalidateAndReassess :> InvalidateAndReassess {
        ref part profile : CurrencyProfile;
        out attribute hasChange : Boolean :>> InvalidateAndReassess::hasChange = logicalChange.hasChange or physicalChange.physicalChange;
        perform action logicalChange : InvalidateAndReassess;
        perform action physicalChange : InvalidatePhysicalDependencies;
        first start then logicalChange;
        first logicalChange then physicalChange;
        first physicalChange then done;
        bind logicalChange.submission = submission;
        bind physicalChange.submission = logicalChange.updatedSubmission;
        bind physicalChange.logicalImpact = logicalChange.impact;
        bind physicalChange.profile = profile;
        bind impact = physicalChange.impact;
        bind updatedSubmission = physicalChange.updatedSubmission;
    }
    item def ExactDependencyManifest :> ControlledData {
        ref item nativeSourceModelSoftwareAndRawProducts : EngineeringArtifact [0..*];
        attribute sourceExportsCataloguesWorkbooksAddIns : String;
        attribute scriptsPlannerFMUsSolversConnectors : String;
        attribute pythonHostToolchainEnvironmentCOTS : String;
        attribute exactAvailabilityDigestsAndFixedComparisonRules : String;
    }
    part def ReplayProfile {
        ref item dependencies : ExactDependencyManifest;
        attribute requiredDependencyClasses : String;
    }
    action def CheckReplayDependencies {
        in request : ReplayRequest;
        in profile : ReplayProfile;
        out attribute exactDependenciesAvailable : Boolean;
        doc /* Resolve every declared native/vendor/tool/environment/data dependency independently. Missing revision, unavailable export or unresolved reconstruction instructions blocks replay admission. This check neither executes replay nor establishes prediction validity. */
    }
    action def PhysicalPrepareReplay :> PrepareReplay {
        ref part profile : ReplayProfile;
        out attribute dependenciesComplete : Boolean :>> PrepareReplay::dependenciesComplete = logicalPreparation.dependenciesComplete and dependencies.exactDependenciesAvailable;
        perform action logicalPreparation : PrepareReplay;
        perform action dependencies : CheckReplayDependencies;
        first start then logicalPreparation;
        first logicalPreparation then dependencies;
        first dependencies then done;
        bind logicalPreparation.request = request;
        bind dependencies.request = request;
        bind dependencies.profile = profile;
        bind preparation = logicalPreparation.preparation;
        bind rulesFixed = logicalPreparation.rulesFixed;
    }
    part def IntegrationMethodProfile {
        ref item sourceRecords : AuthoringRecords;
        ref item wholeSpacecraftInputHistories : ReferenceData [0..*];
        ref item coupling : SimulationCouplingProfile;
        attribute authoringDesignToPythonPlantUSDOrFMIMappings : String;
        attribute fPrimeInterfaceTranslationPathAndVersions : String;
        attribute disciplineSolverEffectsAndUnsupportedTransfers : String;
        attribute numericalEntityUnitSampleReceiptScenarioTimeChecks : String;
    }
    action def MapNumericalPlan {
        in work : DesignWork;
        in proposed : AnalysisPlan;
        in profile : IntegrationMethodProfile;
        out mapped : AnalysisPlan;
        doc /* Proposed source-specific adapter maps workbook/architecture/database/YAML/native quantities to declared numerical plant inputs and EPS responses for the same whole-CUBICS scenario. Declare entity/channel/unit/sign mappings, time bases, synchronization limits/delays, model/tool revisions, omissions and raw validity masks. Required whole-CUBICS and EPS SIL plans carry the numerical coupling profile. Unrelated RAM runs may omit it. No scene-only update or unsupported mandatory mapping is admitted as numerical coupling. */
    }
    action def PhysicalPlanAnalysis :> PlanAnalysis {
        ref part profile : IntegrationMethodProfile;
        perform action logicalPlan : PlanAnalysis;
        perform action map : MapNumericalPlan;
        first start then logicalPlan;
        first logicalPlan then map;
        first map then done;
        bind logicalPlan.work = work;
        bind map.work = work;
        bind map.proposed = logicalPlan.plan;
        bind map.profile = profile;
        bind plan = map.mapped;
    }
    action def MapSourceInterfaces {
        in specification : EPSInterfaceSpecification;
        in profile : IntegrationMethodProfile;
        out mapped : EPSInterfaceSpecification;
        out attribute compatibleCompleteCurrent : Boolean;
        doc /* Translate identified source fields into the required versioned F Prime component/instance/port/topology and command/telemetry/event/parameter profile. Preserve endpoint ownership, direction, types, units, polarity, ranges, encoding and time/mode meaning. New adapters and mission behavior need verification. Retain unsupported/lossy findings and incompatible versions. */
    }
    action def PhysicalMapFPrime :> MapFPrime {
        ref part profile : IntegrationMethodProfile;
        out attribute profileCompatible : Boolean :>> MapFPrime::profileCompatible = adapter.compatibleCompleteCurrent and logicalMapping.profileCompatible;
        perform action adapter : MapSourceInterfaces;
        perform action logicalMapping : MapFPrime;
        first start then adapter;
        first adapter then logicalMapping;
        first logicalMapping then done;
        bind adapter.specification = specification;
        bind adapter.profile = profile;
        bind logicalMapping.specification = adapter.mapped;
        bind work = logicalMapping.work;
    }
    part def CredibilityMethodProfile {
        ref item independentReferences : ReferenceData [0..*];
        attribute waveformHistorySeparateModelAndCSRMMethods : String;
        attribute applicabilityTimingRawMasksAndIndependentDataRules : String;
    }
    action def AdmitAssessmentHistories {
        in work : RunWork;
        in profile : CredibilityMethodProfile;
        out checked : RunWork;
        out attribute numericallySuitable : Boolean;
        out attribute intendedUseIndependentEvidenceAdequate : Boolean;
        doc /* Check entity/channel identity, units, scenario/sample/receipt time, synchronization limits/delays, completeness and validity before numerical assessment. Retain raw values and processing masks. Missing/inactive readings never become zero. Calibration data and independent assessment data remain distinct or have explicit gaps. */
    }
    action def PhysicalAssessModel :> AssessModel {
        ref part profile : CredibilityMethodProfile;
        out attribute numericallyValid : Boolean :>> AssessModel::numericallyValid = histories.numericallySuitable and logicalAssessment.numericallyValid;
        out attribute applicable : Boolean :>> AssessModel::applicable = histories.intendedUseIndependentEvidenceAdequate and logicalAssessment.applicable;
        perform action histories : AdmitAssessmentHistories;
        perform action logicalAssessment : AssessModel;
        first start then histories;
        first histories then logicalAssessment;
        first logicalAssessment then done;
        bind histories.work = work;
        bind histories.profile = profile;
        bind logicalAssessment.work = histories.checked;
        bind evidence = logicalAssessment.evidence;
    }
    part def EvidenceMethodProfile {
        attribute requirementProcedureVerdictAndPublishedReviewTraces : String;
        attribute exactBaselineAuthorityAndCoverageAssembly : String;
    }
    action def PhysicalAssistanceRealization :> LogicalRealization::AssistanceRealization {
        perform action :>> checkDraft : PhysicalCheckDraft;
        perform action :>> reassess : PhysicalReassessAssistance;
        perform action :>> checkReply : PhysicalCheckCurrency;
        perform action :>> checkApplication : PhysicalCheckCurrency;
    }
    part def RequirementsGuidanceSoftware :> FrameworkLogical::RequirementsAssistance, SoftwareResource;
    part def MissionDesignSoftware :> FrameworkLogical::MissionDesign, SoftwareResource;
    part def SimulationIntegrationSoftware :> FrameworkLogical::SimulationIntegration, SoftwareResource {
        part platforms : IntegrationScaffold::RequiredPlatformConnections;
        part mapping : IntegrationMethodProfile;
        part replayDependencies : ReplayProfile;
        bind platforms.wholeCUBICS.numericalExchange = p03;
        bind platforms.fPrime.hostSoftware = p04;
        bind platforms.wholeCUBICS.coupling = mapping.coupling;
        bind mapping.wholeSpacecraftInputHistories = p03.spacecraftInputs;
        perform action verifyProfiles : AdmitProfiles {
            bind mapping = SimulationIntegrationSoftware::mapping;
            bind platforms = SimulationIntegrationSoftware::platforms;
        }
        perform action verifyHostProfiles : AdmitHostProfiles {
            bind mapping = SimulationIntegrationSoftware::mapping;
            bind platforms = SimulationIntegrationSoftware::platforms;
        }
        doc /* Every candidate includes both mandatory external platform connections and declares applicable electrical, thermal, EMC/geometry and RAM profiles. Authored failure-data-to-fault-tree adaptation is proposed. Missing failure/repair data remain unresolved. The cited source supplies no generic rates or complete RAM validity. */
    }
    part def ModelCredibilitySoftware :> FrameworkLogical::ModelCredibility, SoftwareResource;
    part def EvidenceReviewSoftware :> FrameworkLogical::EvidenceReview, SoftwareResource;
    part def ConfigurationExchangeSoftware :> FrameworkLogical::ConfigurationExchange, SoftwareResource;
    port def BaselinePort { inout item record : ControlledData; }
    port def AdviceExchangePort { inout item report : AdviceData; }
    part def EngineeringHost :> HostResource {
        ref part requirements : RequirementsGuidanceSoftware;
        ref part design : MissionDesignSoftware;
        ref part analyses : SimulationIntegrationSoftware;
        ref part credibility : ModelCredibilitySoftware;
        ref part review : EvidenceReviewSoftware;
        port revisions : BaselinePort;
        port assistance : AdviceExchangePort;
        port models : AnalysisPort;
        port hostCode : HostSoftwarePort;
    }
    part def AssistanceHost :> HostResource {
        ref part advice : RequirementsGuidanceSoftware;
        port assistance : AdviceExchangePort;
        port revisions : BaselinePort;
    }
    part def ArchiveHost :> HostResource {
        ref part configuration : ConfigurationExchangeSoftware;
        port engineering : BaselinePort;
        port assistance : BaselinePort;
    }
    part def ModelEnvironment :> HostResource {
        port requests : ~AnalysisPort;
        attribute wholeCUBICSOmniverseAndExternalNumericalToolRevisions : String;
        doc /* Required whole-CUBICS Omniverse numerical environment with declared external EPS/discipline solvers. Return identified EPS effects and same-scenario histories, raw masks and all execution statuses. Display alone supplies no coupling verdict. */
    }
    part def HostToolchain :> HostResource {
        port requests : ~HostSoftwarePort;
        attribute requiredFPrimeHostRepresentationCompilerDependencies : String;
        doc /* Required F Prime host build/SIL toolchain. Exact current engineer-authorized release, profile versions and dependencies precede coding/build. Released host SIL uses simulated products coupled through managed IF-03/04 to the same whole-CUBICS scenario. No target qualification is asserted. */
    }
    action def EngineeringProcedure { in submission : EngineeringSubmission; out response : EngineeringResponse; }
    action def ReviewProcedure { in reviewPackage : ReviewPackage; out decision : TechnicalReviewDecision; }
    part def DesignMethodProfile {
        ref item sourceRecords : AuthoringRecords;
        ref item sourcedComponentAndMissionData : EngineeringArtifact [0..*];
        attribute publishedSizingPlantEnergyOrCSRMMethods : String;
        attribute missingEffectsUnknownsAndProposedCompletion : String;
    }
    action def MapSourcedDesignStudy {
        in work : DesignWork;
        in profile : DesignMethodProfile;
        out mapped : DesignWork;
        doc /* Apply the declared catalogue/workbook, characterized EPS plant, Boan energy workflow or CSRM/concept sizing input mapping. Retain source revisions, quantities/units, mode/scenario assumptions and missing effects. Technical mass/volume estimates and power/energy sizing remain proposed study outputs. No component choice or design change is applied. */
    }
    action def PhysicalBudgetSize :> BudgetSize {
        ref part profile : DesignMethodProfile;
        perform action map : MapSourcedDesignStudy;
        perform action logicalBudget : BudgetSize;
        first start then map;
        first map then logicalBudget;
        first logicalBudget then done;
        bind map.work = work;
        bind map.profile = profile;
        bind logicalBudget.work = map.mapped;
        bind updatedWork = logicalBudget.updatedWork;
    }
    action def AssembleSourcedReviewInputs {
        in baseline : PhaseBaseline;
        in views : ReviewPackage;
        in evidence : EvidenceAssessment;
        in profile : EvidenceMethodProfile;
        out mappedViews : ReviewPackage;
        out mappedEvidence : EvidenceAssessment;
        doc /* Map the declared numerical compliance, Capella review/AIV, Nanospace intermediate result or generated YAML/native evidence paths to exact baseline-linked requirement/procedure/result records. Preserve missing coverage, critical gaps, uncertainty, raw statuses and independent references. Assembly grants prepared status only. */
    }
    action def PhysicalPrepareReviewPackage :> PrepareReviewPackage {
        ref part profile : EvidenceMethodProfile;
        perform action assemble : AssembleSourcedReviewInputs;
        perform action logicalPackage : PrepareReviewPackage;
        first start then assemble;
        first assemble then logicalPackage;
        first logicalPackage then done;
        bind assemble.baseline = baseline;
        bind assemble.views = views;
        bind assemble.evidence = evidence;
        bind assemble.profile = profile;
        bind logicalPackage.baseline = baseline;
        bind logicalPackage.views = assemble.mappedViews;
        bind logicalPackage.evidence = assemble.mappedEvidence;
        bind reviewPackage = logicalPackage.reviewPackage;
        bind entranceComplete = logicalPackage.entranceComplete;
    }
    action def ReturnAdmittedCoupledEPSResponse {
        in result : AnalysisResult;
        in mapping : IntegrationMethodProfile;
        in currency : CurrencyProfile;
        out response : AnalysisResult [0..1];
        doc /* For an applicable whole-CUBICS numerical or EPS SIL result, recheck current scenario/profile/model identities, entity/channel/quantity/unit mappings, sample/receipt times, timing limits/delays and raw masks before returning EPS states/results to the same scene. Unsupported, stale, invalid, missing or failed results retain explicit status/limitations and supply no admitted numerical payload. Unrelated RAM work produces no artificial scene response. A returned simulation result supplies no independent predictive-validity or product-conformity verdict. */
    }
    action def PhysicalPreserveRun :> PreserveRun {
        ref part mapping : IntegrationMethodProfile;
        ref part currency : CurrencyProfile;
        ref port numericalEndpoint : AnalysisPort;
        perform action preserve : PreserveRun;
        perform action mapResponse : ReturnAdmittedCoupledEPSResponse;
        first start then preserve;
        first preserve then mapResponse;
        first mapResponse then done;
        bind preserve.result = result;
        bind preserve.software = software;
        bind work = preserve.work;
        bind mapResponse.result = result;
        bind mapResponse.mapping = mapping;
        bind mapResponse.currency = currency;
        bind numericalEndpoint.epsResponses = mapResponse.response;
        doc /* The original scenario reaches this operation only after receiving compatibility. Preserve all raw/status records, then map current suitable coupled EPS responses. This adapter changes no baseline, release, review state or engineering conclusion. */
    }
    action def AdmitProfiles {
        ref part mapping : IntegrationMethodProfile;
        ref part platforms : IntegrationScaffold::RequiredPlatformConnections;
        in plan : AnalysisPlan; out admittedPlan : AnalysisPlan;
        out attribute mandatoryProfilesVerified : Boolean;
        bind admittedPlan = plan;
        doc /* Recheck the exact current plan/configuration, criteria, source/model/software/scope and selected profile revisions before execution. Check required electrical, thermal, applicable EMC/geometry and numerical whole-CUBICS Omniverse profiles, RAM transformation and software profile/version against required effects, available resources/access, supported mappings and verification records. Independent reference/numerical/calibration evidence bounds intended use. An unverified mandatory profile or unresolved loss blocks admission. All empirical profile evidence remains unexecuted. */
    }
    item def BlockedAnalysisResult :> AnalysisResult {
        attribute :>> executionSuccessFailedCancelledPartial = "blocked: mandatory profile admission failed";
        attribute externalExecutionOccurred : Boolean = false;
        ref item :>> samples [0];
        doc /* A defined failed result for the exact attempted plan. Retain missing/unverified profiles and reasons with no external raw output. Numerical validity and supported feasibility remain false. */
    }
    action def BlockExecution {
        in plan : AnalysisPlan; out result : BlockedAnalysisResult;
        bind result.plan = plan;
    }
    item def ExistingSILRequest :> CodingRequest {
        ref item plan : AnalysisPlan;
        attribute codingOrBuildAllowed : Boolean = false;
        doc /* Request only the identified existing released host product and simulated plant. Resolve exact source/build/host dependencies from the admitted repeated/replay plan. A required code revision returns through the existing detailed-design release path. */
    }
    action def MapExistingSILRequest {
        in plan : AnalysisPlan; out request : ExistingSILRequest;
        bind request.plan = plan;
        bind request.couplingProfile = plan.couplingProfile;
        doc /* Resolve the released design/interface mapping, existing product, matched stimuli, criteria and dependencies identified by the plan. Preserve their exact revisions. Admission verifies their availability and compatibility before this adapter is reached. No coding or build is requested. */
    }
    action def ExecuteExistingSoftware {
        in request : ExistingSILRequest; out result : SoftwareRunResult;
        ref port endpoint : ~HostSoftwarePort;
        bind request = endpoint.codingRequest;
        bind result = endpoint.softwareResult;
        doc /* The declared external host toolchain runs the existing released code with the admitted simulated products. Return raw histories, logs, host identity and failed/partial status. Perform no new coding or build. */
    }
    item def HostAnalysisResult :> AnalysisResult { ref item software : SoftwareRunResult; }
    action def MapSoftwareResult {
        in plan : AnalysisPlan; in software : SoftwareRunResult;
        out result : HostAnalysisResult;
        bind result.plan = plan;
        bind result.software = software;
        doc /* Map the exact SIL histories, units, time bases, raw values, masks, execution statuses and fixed comparison outcomes into the analysis result. Retain the original software result. Missing or invalid channels remain gaps. */
    }
    action def ExistingHostSIL {
        ref port hostEndpoint : ~HostSoftwarePort;
        bind execute.endpoint = hostEndpoint;
        in plan : AnalysisPlan; out result : AnalysisResult;
        perform action map : MapExistingSILRequest;
        perform action execute : ExecuteExistingSoftware;
        perform action returnResult : MapSoftwareResult;
        first start then map;
        first map then execute;
        first execute then returnResult;
        first returnResult then done;
        flow planInput of AnalysisPlan from plan to map.plan;
        flow softwareRequest of ExistingSILRequest from map.request to execute.request;
        flow resultPlan of AnalysisPlan from plan to returnResult.plan;
        flow softwareResult of SoftwareRunResult from execute.result to returnResult.software;
        flow returnedResult of AnalysisResult from returnResult.result to result;
    }
    action def SelectExecutionKind {
        in plan : AnalysisPlan; out attribute existingSIL : Boolean;
        doc /* Select existing host SIL for an admitted change/calibration/replay plan that identifies released code. Numerical and MIL plans select model execution. Mixed repeated work consists of separately admitted requests for every selected profile. A plan requiring new coding is rejected by admission and returns to detailed-design authorization. */
    }
    action def DeclaredModelExecution :> ScenarioViews::SC03External3 {
        ref port endpoint : ~AnalysisPort;
        bind plan = endpoint.analysisPlan;
        bind result = endpoint.analysisResult;
    }
    action def DeclaredHostExecution :> ScenarioViews::SC04External5 {
        ref port endpoint : ~HostSoftwarePort;
        bind request = endpoint.codingRequest;
        bind result = endpoint.softwareResult;
    }
    action def ExecuteSelectedProfiles {
        ref port modelEndpoint : ~AnalysisPort;
        ref port hostEndpoint : ~HostSoftwarePort;
        bind models.endpoint = modelEndpoint;
        bind sil.hostEndpoint = hostEndpoint;
        in plan : AnalysisPlan; out result : AnalysisResult;
        perform action kind : SelectExecutionKind;
        perform action models : DeclaredModelExecution;
        perform action sil : ExistingHostSIL;
        decide selected;
        merge complete;
        first start then kind;
        first kind then selected;
        succession modelExecution first selected if not kind.existingSIL then models;
        succession softwareExecution first selected if kind.existingSIL then sil;
        first models then complete;
        first sil then complete;
        first complete then done;
        flow kindInput of AnalysisPlan from plan to kind.plan;
        flow modelInput of AnalysisPlan from plan to models.plan;
        flow silInput of AnalysisPlan from plan to sil.plan;
        flow modelResult of AnalysisResult from models.result to result;
        flow silResult of AnalysisResult from sil.result to result;
        doc /* Execute exactly the declared numerical/MIL or existing SIL profile after mandatory admission. The model operation applies the selected coupled discipline or controller/plant plan. SIL uses the separate external host operation and typed adapters. */
    }
    action def SupportedExecution :> ScenarioViews::SC01External3, ScenarioViews::SC03External3, ScenarioViews::SC04External3, ScenarioViews::SC05External3 {
        in plan : AnalysisPlan :>> ScenarioViews::SC01External3::plan, ScenarioViews::SC03External3::plan, ScenarioViews::SC04External3::plan, ScenarioViews::SC05External3::plan;
        out result : AnalysisResult :>> ScenarioViews::SC01External3::result, ScenarioViews::SC03External3::result, ScenarioViews::SC04External3::result, ScenarioViews::SC05External3::result;
        out attribute admitted : Boolean = profiles.mandatoryProfilesVerified;
        ref port modelEndpoint : ~AnalysisPort;
        ref port hostEndpoint : ~HostSoftwarePort;
        bind execute.modelEndpoint = modelEndpoint;
        bind execute.hostEndpoint = hostEndpoint;
        perform action profiles : AdmitProfiles;
        perform action execute : ExecuteSelectedProfiles;
        perform action blocked : BlockExecution;
        decide ready;
        merge complete;
        first start then profiles;
        first profiles then ready;
        succession admitProfiles first ready if profiles.mandatoryProfilesVerified then execute;
        succession rejectProfiles first ready if not profiles.mandatoryProfilesVerified then blocked;
        first execute then complete;
        first blocked then complete;
        first complete then done;
        flow planFlow of AnalysisPlan from plan to profiles.plan;
        flow executeFlow of AnalysisPlan from profiles.admittedPlan to execute.plan;
        flow blockedPlan of AnalysisPlan from plan to blocked.plan;
        flow executionResult of AnalysisResult from execute.result to result;
        flow blockedResult of AnalysisResult from blocked.result to result;
        doc /* This wrapper replaces the logical external operation. Admission controls the actual call, including selected MIL/SIL/change/replay profiles. The blocked result follows the existing preservation and evidence-gap paths. No execution occurs on rejected admission. */
    }
    action def AdmitHostProfiles {
        ref part mapping : IntegrationMethodProfile;
        ref part platforms : IntegrationScaffold::RequiredPlatformConnections;
        in request : CodingRequest; in plan : AnalysisPlan;
        out admittedRequest : CodingRequest;
        out attribute mandatoryProfilesVerified : Boolean;
        bind admittedRequest = request;
        doc /* Check the exact authorized request, required F Prime host build/SIL toolchain and whole-CUBICS numerical coupling, simulated plant, mappings, dependencies, numerical/resource limits and every mandatory discipline/software verification record. Recheck current design/context. Missing capability blocks the request with no coding/build/SIL call. */
    }
    item def BlockedSoftwareResult :> SoftwareRunResult {
        ref item request : CodingRequest;
        ref item :>> product [0];
        attribute :>> milSilDifferencesFailuresStatus = "blocked: profile admission failed, no coding/build/SIL execution";
        attribute externalExecutionOccurred : Boolean = false;
    }
    action def BlockHostExecution {
        in request : CodingRequest; out result : BlockedSoftwareResult;
        bind result.request = request;
    }
    action def SupportedHostExecution :> ScenarioViews::SC04External5 {
        ref port hostEndpoint : ~HostSoftwarePort;
        bind execute.endpoint = hostEndpoint;
        in :>> request;
        out :>> result;
        in plan : AnalysisPlan;
        in attribute priorProfilesAdmitted : Boolean;
        perform action profiles : AdmitHostProfiles;
        perform action execute : DeclaredHostExecution;
        perform action blocked : BlockHostExecution;
        decide ready;
        merge complete;
        first start then profiles;
        first profiles then ready;
        succession admitProfiles first ready if priorProfilesAdmitted and profiles.mandatoryProfilesVerified then execute;
        succession rejectProfiles first ready if not (priorProfilesAdmitted and profiles.mandatoryProfilesVerified) then blocked;
        first execute then complete;
        first blocked then complete;
        first complete then done;
        flow requestInput of CodingRequest from request to profiles.request;
        flow planInput of AnalysisPlan from plan to profiles.plan;
        flow admittedRequest of CodingRequest from profiles.admittedRequest to execute.request;
        flow blockedRequest of CodingRequest from request to blocked.request;
        flow executionResult of SoftwareRunResult from execute.result to result;
        flow blockedResult of SoftwareRunResult from blocked.result to result;
    }
    action def PhysicalConceptRealization :> LogicalRealization::ConceptRealization {
        perform action :>> execute : SupportedExecution {
            in plan : AnalysisPlan :>> SupportedExecution::plan, ScenarioViews::SC01External3::plan;
            out result : AnalysisResult :>> SupportedExecution::result, ScenarioViews::SC01External3::result;
        }
    }
    action def PhysicalDesignRealization :> LogicalRealization::DesignRealization {
        perform action :>> execute : SupportedExecution {
            in plan : AnalysisPlan :>> SupportedExecution::plan, ScenarioViews::SC03External3::plan;
            out result : AnalysisResult :>> SupportedExecution::result, ScenarioViews::SC03External3::result;
        }
    }
    action def PhysicalSoftwareRealization :> LogicalRealization::SoftwareRealization {
        perform action :>> executeMIL : SupportedExecution {
            in plan : AnalysisPlan :>> SupportedExecution::plan, ScenarioViews::SC04External3::plan;
            out result : AnalysisResult :>> SupportedExecution::result, ScenarioViews::SC04External3::result;
        }
        perform action :>> codeBuildSil : SupportedHostExecution {
            in request : CodingRequest :>> SupportedHostExecution::request, ScenarioViews::SC04External5::request;
            out result : SoftwareRunResult :>> SupportedHostExecution::result, ScenarioViews::SC04External5::result;
        }
        flow hostPlan of AnalysisPlan from planMIL.plan to codeBuildSil.plan;
        flow milAdmission of Boolean from executeMIL.admitted to codeBuildSil.priorProfilesAdmitted;
    }
    action def PhysicalChangeReviewRealization :> LogicalRealization::ChangeReviewRealization {
        perform action :>> reassessAdvice : PhysicalReassessAssistance;
        perform action :>> repeat : SupportedExecution {
            in plan : AnalysisPlan :>> SupportedExecution::plan, ScenarioViews::SC05External3::plan;
            out result : AnalysisResult :>> SupportedExecution::result, ScenarioViews::SC05External3::result;
        }
    }
    action def PhysicalReplayRealization :> LogicalRealization::ReplayRealization {
        perform action :>> execute : SupportedExecution {
            in plan : AnalysisPlan :>> SupportedExecution::plan, ScenarioViews::SC05External3::plan;
            out result : AnalysisResult :>> SupportedExecution::result, ScenarioViews::SC05External3::result;
        }
    }
    action def PhysicalCalibrationRealization :> LogicalRealization::CalibrationRealization {
        perform action :>> reassess : PhysicalReassessAssistance;
        perform action :>> repeat : SupportedExecution {
            in plan : AnalysisPlan :>> SupportedExecution::plan, ScenarioViews::SC05External3::plan;
            out result : AnalysisResult :>> SupportedExecution::result, ScenarioViews::SC05External3::result;
        }
    }
}
