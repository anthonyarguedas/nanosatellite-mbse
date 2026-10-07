// Proposed physical component specifications. No implementation or satisfaction claim.
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
        attribute authority : String;
        attribute verificationNeed : String;
        attribute status : String;
    }
    part def SoftwareResource;
    part def HostResource {
        attribute operatingSystemRuntimeVersions : String;
        attribute cpuMemoryStorageNetworkLimits : String;
        attribute accessLicenceBackupRecovery : String;
        doc /* Generic computers, networks and storage are framework infrastructure. Capacity and legal access require declaration and verification. They are not executing EPS hardware. Co-location is allowed only while access, workload isolation and recovery rules remain satisfied. */
    }
    part def ResponsibilityNode { attribute responsibilityAndLocation : String; }
    item def ControlledData :> EngineeringArtifact {
        ref item context : ContextRevision;
        attribute contentDigestSchemaProducerSourceRevisions : String;
        attribute proposedReleasedStaleFailedStatus : String;
    }
    item def ModelData :> ControlledData {
        ref item requirements : RequirementAllocation [0..*];
        ref item designs : DesignWork [0..*];
        ref item interfaces : EPSInterfaceSpecification [0..*];
        doc /* Working native/YAML/vendor records retain the declared field owner. A release captures their exact native revisions in ReleaseData. */
    }
    item def AdviceData :> ControlledData {
        ref item batches : AdviceBatch [0..*];
        ref item referenceData : ReferenceData [0..*];
        ref item dispositions : SuggestionDisposition [0..*];
        doc /* Local source/advice indexes are rebuildable. Exact cited source packages and disposition records are preserved in ReleaseData. */
    }
    item def ReleaseData :> ControlledData {
        ref item baselines : PhaseBaseline [0..*];
        ref item models : ModelData [0..*];
        ref item advice : AdviceData [0..*];
        ref item runs : RunWork [0..*];
        ref item assessments : EvidenceAssessment [0..*];
        ref item rejectedTransfers : CheckedTransfer [0..*];
        doc /* Managed archive preserves exact native source/model/software revisions, cited data, raw outputs, logs, statuses, masks, review decisions and replay dependencies. Digests check file identity, not engineering correctness. */
    }
    item def AdviceInput :> EngineeringArtifact {
        ref item work : AssistanceWork;
        ref item context : ContextRevision;
        ref item request : GuidanceRequest;
        ref item drafts : RequirementRecord [0..*];
        attribute purpose : String;
        attribute questionStagePurposeAvailableInputsConstraints : String;
        attribute ruleRubricSourceModelRevisions : String;
    }
    item def AdviceBatch :> EngineeringArtifact {
        ref item input : AdviceInput;
        ref item report : AssistanceReport;
        attribute affectedTextSubjectLevelModeConditionQuantity : String;
        attribute sourceExcerptsLocatorsAndAuthority : String;
        attribute modelIdentityRevisionPromptRawScoresTruncation : String;
        attribute eligibilityRejectedAlternativesUncertainty : String;
        attribute citedCorrectionOrQuestionAndComparedContext : String;
        attribute assessedNoFindingAbstainedUnavailableScope : String;
    }
    part def DeterministicRules :> SoftwareResource {
        attribute ruleRevision : String;
        doc /* Python rules check identifiers, required fields, parent/end revisions, responsible product, one thought, shall/should/will wording, vague terms, dimensional units, inequality direction, declared quantity limits and arithmetic consistency. NASA Appendix C is a default reference, supplemented by an expert-approved project rubric. Rules expose exact affected text and a cited correction template or clarification question. Missing quantities stay unresolved. Technical validity remains a reviewer decision. */
    }
    part def LocalScoring :> SoftwareResource {
        attribute embeddingModel : String = "Qwen/Qwen3-Embedding-0.6B";
        attribute rerankerModel : String = "Qwen/Qwen3-Reranker-0.6B";
        attribute embeddingRevision : String = "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3";
        attribute rerankerRevision : String = "e61197ed45024b0ed8a2d74b80b4d909f1255473";
        attribute modelRevisionTokenizerPromptLibraryIdentity : String;
        doc /* BM25 and exact quantity/subject queries provide lexical candidates. Pinned local Qwen embedding retrieval and CrossEncoder pairwise reranking are a semantic alternative through sentence-transformers. Separate source-content selection, contextual question relevance and requirement-pair candidate assessment use qualified rubrics. Local content selection defaults to declared section types and retained source authority. A local probabilistic content classifier needs separate qualification. Scores only rank potential evidence or probable similarity. They cannot establish duplicate equivalence. Input truncation, unsupported language and incomplete conditions cause flags or abstention. Exact weights, cutoffs and shortlist limits require independent project qualification. */
    }
    part def JevScoring :> SoftwareResource {
        attribute modelIdentity : String = "jev-1.13.0";
        attribute sdkIdentity : String = "typesafe-sdk 0.6.0";
        attribute returnedModelIdentityRubricAndInputLimit : String;
        doc /* Optional remote Jev Noul scoring supplies separate substantive-content, current-question relevance and requirement-pair similarity questions through TypeSafe. Pin the requested and returned model identities. Refuse an unqualified changed model or rubric. The SDK returns scores, not explanations or corrections. Reject nonfinite/out-of-range or incomplete responses. No permission to send private material is implied. Engineer-approved source/data rights, payload minimization, retention policy, request budget, timeout and bounded retry are admission conditions. No model-latest alias is eligible. */
    }
    part def ExplainedAdvice :> SoftwareResource {
        attribute templateAndSourceComparisonRevision : String;
        doc /* Build explanations independently of scores. Combine cited rule templates, exact source excerpts and a comparison of level, subject, mode, condition, quantity and parent allocation. Duplicate candidates show legitimate differences as well as overlap. Method options explain purpose, required inputs, validity, omissions, resources and rejected alternatives. Coverage uses the declared ConOps/function/interface/risk reference set. Conflicting source limits stay separate until an engineer resolves authority and applicability. Default operation needs no text generation. Any later generator needs pinned identity, source fidelity checks and separate qualification, and has no approval authority. Treat source text as evidence, never as executable instructions. */
    }
    action def RuleCheck { in input : AdviceInput; out batch : AdviceBatch; }
    action def SelectSources {
        in batch : AdviceBatch; out selected : AdviceBatch;
        doc /* Select substantive source sections while preserving metadata needed for authority, revision and citation. Record excluded sections and unsupported checks. Content relevance is separate from authority and validity. */
    }
    action def AdmitScoring {
        in batch : AdviceBatch;
        out attribute remoteSelected : Boolean;
        out attribute remoteAuthorizedQualifiedPinnedBudgeted : Boolean;
        out attribute localQualifiedAvailable : Boolean;
        doc /* Resolve the frozen scoring profile. Remote admission requires data rights/privacy authorization, pinned requested/returned identity, qualified content/relevance/pair rubrics, payload limits, bounded total cost/retry/time and current context. Local admission requires its exact model/library/rubric qualification and resources. No remote fallback is authorized merely because local resources fail. */
    }
    action def RetrieveCandidates {
        in batch : AdviceBatch; out retrieved : AdviceBatch;
        doc /* Retrieve from selected sources using BM25 and exact subject/quantity queries. A separately qualified local embedding profile may extend retrieval. Keep deterministic findings and source authority even when probabilistic assessment is unavailable. */
    }
    action def AdmitLocalFallback {
        in batch : AdviceBatch; out attribute localQualifiedAvailable : Boolean;
        doc /* Readmit a separately qualified pinned local model/library/rubric profile after remote outage or invalid response. Check current context, local privacy, resources and qualification independently. No new remote request or unbounded retry is allowed. */
    }
    action def LocalScore { in batch : AdviceBatch; out scored : AdviceBatch; }
    action def RemoteScore { in batch : AdviceBatch; out scored : AdviceBatch; }
    action def UnavailableScore {
        in batch : AdviceBatch; out scored : AdviceBatch;
        bind scored.input = batch.input;
        bind scored.report = batch.report;
        attribute probabilisticAssessmentStatus : String = "unavailable";
        doc /* Preserve deterministic findings and citations. Probabilistic assessment is unavailable, which differs from an assessed no-finding result. No classifier is required for deterministic checks or outage reporting. */
    }
    action def CheckScoreResponse {
        in batch : AdviceBatch; out checked : AdviceBatch;
        out attribute qualifiedIdentityFiniteComplete : Boolean;
        doc /* After scoring, check actual returned model/revision and qualified rubric against the selected profile. Validate finite scores within that model's declared scale, completeness and decisive input truncation. Preserve raw responses. Invalid, changed, incomplete or unqualified outputs become unavailable/abstained and never eligible ranking evidence. Local raw logits are not forced into a probability scale. */
    }
    action def ReturnScores { in batch : AdviceBatch; out scored : AdviceBatch; }
    action def ScoreCandidates {
        in batch : AdviceBatch; out scored : AdviceBatch;
        perform action admit : AdmitScoring;
        perform action local : LocalScore;
        perform action remote : RemoteScore;
        perform action unavailable : UnavailableScore;
        perform action check : CheckScoreResponse;
        perform action checkRemote : CheckScoreResponse;
        perform action fallback : AdmitLocalFallback;
        perform action returnScores : ReturnScores;
        decide profile;
        decide validScores;
        decide validRemote;
        decide fallbackReady;
        merge complete;
        first start then admit;
        first admit then profile;
        succession remoteAdmitted first profile if admit.remoteSelected and admit.remoteAuthorizedQualifiedPinnedBudgeted then remote;
        succession localAdmitted first profile if not admit.remoteSelected and admit.localQualifiedAvailable then local;
        succession unavailableProfile first profile if (admit.remoteSelected and not admit.remoteAuthorizedQualifiedPinnedBudgeted) or (not admit.remoteSelected and not admit.localQualifiedAvailable) then unavailable;
        first local then check;
        first remote then checkRemote;
        first checkRemote then validRemote;
        succession admitRemoteScores first validRemote if checkRemote.qualifiedIdentityFiniteComplete then returnScores;
        succession invalidRemoteScores first validRemote if not checkRemote.qualifiedIdentityFiniteComplete then fallback;
        first fallback then fallbackReady;
        succession admitFallback first fallbackReady if fallback.localQualifiedAvailable then local;
        succession noFallback first fallbackReady if not fallback.localQualifiedAvailable then unavailable;
        first check then validScores;
        succession admitScores first validScores if check.qualifiedIdentityFiniteComplete then returnScores;
        succession invalidScores first validScores if not check.qualifiedIdentityFiniteComplete then unavailable;
        first returnScores then complete;
        first unavailable then complete;
        first complete then done;
        flow admissionInput of AdviceBatch from batch to admit.batch;
        flow localInput of AdviceBatch from batch to local.batch;
        flow remoteInput of AdviceBatch from batch to remote.batch;
        flow unavailableInput of AdviceBatch from batch to unavailable.batch;
        flow localOutput of AdviceBatch from local.scored to check.batch;
        flow remoteOutput of AdviceBatch from remote.scored to checkRemote.batch;
        flow fallbackInput of AdviceBatch from checkRemote.checked to fallback.batch;
        flow fallbackBatch of AdviceBatch from checkRemote.checked to local.batch;
        flow remoteFailureRecord of AdviceBatch from checkRemote.checked to unavailable.batch;
        flow remoteCheckedOutput of AdviceBatch from checkRemote.checked to returnScores.batch;
        flow checkedOutput of AdviceBatch from check.checked to returnScores.batch;
        flow invalidOutput of AdviceBatch from check.checked to unavailable.batch;
        flow admittedOutput of AdviceBatch from returnScores.scored to scored;
        flow unavailableOutput of AdviceBatch from unavailable.scored to scored;
        doc /* Retrieve and score source/method/requirement candidates under the frozen local or admitted remote profile. Retain both question relevance and pair comparison scores with model/rubric identity. Do not reuse corpus retrieval cutoffs or fusion weights as engineering acceptance limits. API outage falls back only through readmission of a separately qualified local profile. Otherwise return unavailable/abstained, with deterministic findings intact. */
    }
    action def FilterApplicability {
        in batch : AdviceBatch; out eligible : AdviceBatch;
        out attribute hasEligible : Boolean;
        doc /* Apply engineer-approved mandatory scope, phase/purpose, requirements, available inputs, model validity, required discipline/fidelity, resource and legal-access conditions before ranking eligible options. Unknown mandatory inputs are unresolved, never favorable defaults. Keep rejected alternatives with reasons. Rank by qualified contextual relevance only among eligible options. Raw probability is neither technical confidence nor acceptance. */
    }
    action def ExplainOptions {
        in batch : AdviceBatch; out explained : AdviceBatch;
        doc /* Produce cited rule corrections and context/source comparisons using ExplainedAdvice. Explain the eligible shortlist and close alternatives. No score is an explanation. Retain uncertain findings and unsupported scope for engineer disposition. */
    }
    action def NoEligible {
        in batch : AdviceBatch; out explained : AdviceBatch;
        doc /* Return no eligible recommendation and unmet prerequisites, abstention or service-unavailable status. Still explain supported deterministic drafting findings. No finding and not assessed are distinct. */
    }
    action def CheckAdviceCurrency {
        in batch : AdviceBatch; out attribute current : Boolean;
        doc /* Compare latest requirement, mission, design, source, criterion and scope revisions plus assistance model/rule revisions immediately before display. Cache identity includes all these revisions, question, content digests, applicability profile and qualification version. Superseded cached advice remains historical. A delayed response never replaces newer advice. Current engineer authority and context are checked again by the retained logical application gate. */
    }
    action def PublishAdvice {
        in batch : AdviceBatch; out report : AssistanceReport;
        bind report.context = batch.input.context;
        bind report.findings = batch.report.findings;
        bind report.recommendations = batch.report.recommendations;
        doc /* Return the current explained findings, method options, prerequisites, limitations and assessment scope. Scoring alone supplies no explanation or corrective suggestion. */
    }
    item def StaleAdviceReport :> AssistanceReport {
        attribute :>> currentStalePendingUnavailable = "stale";
    }
    action def PreserveStale {
        in batch : AdviceBatch; out report : StaleAdviceReport;
        bind report.context = batch.input.context;
        doc /* Preserve the stale report and its findings, invalidate its use and request the latest context. Return stale status without displaying it as current. The enclosing logical latest-context gate rejects this report for presentation or application. */
    }
    action def ActiveAssistance {
        in input : AdviceInput; out report : AssistanceReport;
        perform action rules : RuleCheck;
        perform action sources : SelectSources;
        perform action retrieve : RetrieveCandidates;
        perform action scores : ScoreCandidates;
        perform action applicability : FilterApplicability;
        perform action explain : ExplainOptions;
        perform action none : NoEligible;
        perform action currency : CheckAdviceCurrency;
        perform action publish : PublishAdvice;
        perform action stale : PreserveStale;
        decide eligible;
        merge explained;
        decide current;
        merge complete;
        first start then rules;
        first rules then sources;
        first sources then retrieve;
        first retrieve then scores;
        first scores then applicability;
        first applicability then eligible;
        succession admitOptions first eligible if applicability.hasEligible then explain;
        succession noOptions first eligible if not applicability.hasEligible then none;
        first explain then explained;
        first none then explained;
        first explained then currency;
        first currency then current;
        succession admitCurrent first current if currency.current then publish;
        succession rejectStale first current if not currency.current then stale;
        first publish then complete;
        first stale then complete;
        first complete then done;
        flow inputFlow of AdviceInput from input to rules.input;
        flow sourceFlow of AdviceBatch from rules.batch to sources.batch;
        flow retrievalFlow of AdviceBatch from sources.selected to retrieve.batch;
        flow scoreFlow of AdviceBatch from retrieve.retrieved to scores.batch;
        flow applicabilityFlow of AdviceBatch from scores.scored to applicability.batch;
        flow explanationFlow of AdviceBatch from applicability.eligible to explain.batch;
        flow noOptionFlow of AdviceBatch from applicability.eligible to none.batch;
        flow explanationCurrency of AdviceBatch from explain.explained to currency.batch;
        flow noneCurrency of AdviceBatch from none.explained to currency.batch;
        flow presentFlow of AdviceBatch from explain.explained to publish.batch;
        flow presentNoneFlow of AdviceBatch from none.explained to publish.batch;
        flow staleFlow of AdviceBatch from explain.explained to stale.batch;
        flow staleNoneFlow of AdviceBatch from none.explained to stale.batch;
        flow publishedReport of AssistanceReport from publish.report to report;
        flow staleReport of AssistanceReport from stale.report to report;
        doc /* Refines L02 checking/recommendation. The approved logical receive/capture/immediate edit invalidation/acknowledgement steps precede this action. Its presentation check supplements the retained latest-context and human application gates. It cannot apply a correction or authorize a review. */
    }
    action def MapAdviceWork {
        in work : AssistanceWork; in attribute purpose : String;
        out input : AdviceInput;
        bind input.work = work;
        bind input.request = work.request;
        bind input.context = work.request.context;
        bind input.drafts = work.drafts;
        bind input.purpose = purpose;
        doc /* Preserve the exact request, drafts, submission and prior dispositions. The request carries the current question, maturity, available inputs, validity, resources and scope. Resolve rule/source/model revisions for this purpose without changing context or granting application authority. */
    }
    action def ReturnAdviceWork {
        in work : AssistanceWork; in report : AssistanceReport;
        out updatedWork : AssistanceWork;
        bind updatedWork.submission = work.submission;
        bind updatedWork.request = work.request;
        bind updatedWork.drafts = work.drafts;
        bind updatedWork.dispositions = work.dispositions;
        bind updatedWork.findings = report.findings;
        bind updatedWork.report = report;
        bind updatedWork.triggerAcknowledgementCompletion = work.triggerAcknowledgementCompletion;
        doc /* Return the actual explained report and findings in the logical work record. Preserve acknowledgement/completion information and all human dispositions. This adapter applies no suggestion. */
    }
    action def PhysicalCheckDraft :> CheckDraft {
        perform action map : MapAdviceWork { in :>> purpose = "draft check"; }
        perform action pipeline : ActiveAssistance;
        perform action returnWork : ReturnAdviceWork;
        first start then map;
        first map then pipeline;
        first pipeline then returnWork;
        first returnWork then done;
        flow workInput of AssistanceWork from work to map.work;
        flow mappedInput of AdviceInput from map.input to pipeline.input;
        flow originalWork of AssistanceWork from work to returnWork.work;
        flow explainedReport of AssistanceReport from pipeline.report to returnWork.report;
        flow workOutput of AssistanceWork from returnWork.updatedWork to updatedWork;
    }
    action def PhysicalRecommendMethods :> RecommendMethods {
        perform action map : MapAdviceWork { in :>> purpose = "methods and lifecycle guidance"; }
        perform action pipeline : ActiveAssistance;
        first start then map;
        first map then pipeline;
        first pipeline then done;
        flow workInput of AssistanceWork from work to map.work;
        flow mappedInput of AdviceInput from map.input to pipeline.input;
        flow explainedReport of AssistanceReport from pipeline.report to report;
        doc /* Include the draft report in work with its deterministic findings and unsupported scope. Explain contextual method/model alternatives and lifecycle prerequisites. Return the pipeline report, never a score. */
    }
    action def PhysicalReassessAssistance :> ReassessAssistance {
        perform action prepare : ReassessAssistance;
        perform action checkDraft : PhysicalCheckDraft;
        perform action recommend : PhysicalRecommendMethods;
        perform action returnWork : ReturnAdviceWork;
        first start then prepare;
        first prepare then checkDraft;
        first checkDraft then recommend;
        first recommend then returnWork;
        first returnWork then done;
        flow impactInput of ImpactNotice from impact to prepare.impact;
        flow newWork of AssistanceWork from prepare.work to checkDraft.work;
        flow checkedWork of AssistanceWork from checkDraft.updatedWork to recommend.work;
        flow preservedWork of AssistanceWork from checkDraft.updatedWork to returnWork.work;
        flow explainedReport of AssistanceReport from recommend.report to returnWork.report;
        flow workOutput of AssistanceWork from returnWork.updatedWork to work;
    }
    action def CheckReturnedAdvice {
        in report : AssistanceReport;
        out attribute presentable : Boolean = report.currentStalePendingUnavailable != "stale";
    }
    action def PhysicalCheckCurrency :> CheckCurrency {
        out attribute sameContext : Boolean :>> CheckCurrency::sameContext = latest.sameContext and status.presentable;
        perform action latest : CheckCurrency;
        perform action status : CheckReturnedAdvice;
        first start then latest;
        first latest then status;
        first status then done;
        flow reportInput of AssistanceReport from report to latest.report;
        flow contextInput of ContextRevision from context to latest.context;
        flow statusInput of AssistanceReport from report to status.report;
        doc /* Preserve the logical latest-context check. A physical pipeline that rejected model/rule/source currency returns stale status and cannot pass the enclosing display or application gate, even if the six logical context revisions otherwise match. */
    }
    action def PhysicalAssistanceRealization :> LogicalRealization::AssistanceRealization {
        perform action :>> checkDraft : PhysicalCheckDraft;
        perform action :>> recommend : PhysicalRecommendMethods;
        perform action :>> reassess : PhysicalReassessAssistance;
        perform action :>> checkReply : PhysicalCheckCurrency;
        perform action :>> checkApplication : PhysicalCheckCurrency;
    }
    part def ExchangeSoftware :> Exchange, SoftwareResource;
    part def AssistanceSoftware :> Assistance, SoftwareResource {
        part rules : DeterministicRules;
        part localScoring : LocalScoring;
        part explanation : ExplainedAdvice;
        part remoteScoring : JevScoring [0..1];
        part planning : DependencyPlanningProfile [0..1];
        perform action :>> checkDraft : PhysicalCheckDraft;
        perform action :>> recommend : PhysicalRecommendMethods;
        perform action :>> reassess : PhysicalReassessAssistance;
    }
    part def RequirementsSoftware :> Requirements, SoftwareResource;
    part def ToolProfile :> SoftwareResource {
        port modelExchange : AnalysisPort;
        attribute toolModelSolverRevisionApplicabilityAccess : String;
        attribute sourceSupportedRoleAndProposedAdaptation : String;
        attribute numericalMappingCalibrationIndependentEvidence : String;
    }
    part def ConceptSeedProfile :> ToolProfile {
        doc /* Optional GREATCUBE+ empirical/analytical/COTS/numerical placement profile, Girardello sections 2--4. Import starting design quantities with correlation/database limits and engineer adaptation. Price/availability ranking is excluded by the source. Current tool access is unknown. */
    }
    part def DependencyPlanningProfile :> SoftwareResource {
        doc /* Optional curated dependency graph/DSM and HDDL/HyperTension profile for L02 activity recommendations, Gateau sections 3--6. Nanospace API sharing is reported. Full HTN integration is prospective. A valid task plan is not an optimum or engineering approval. */
    }
    part def BoanEnergyProfile :> ToolProfile {
        doc /* Alternative linked preliminary profile: IDM-CIC system/geometry/budgets, Simu-CIC orbital scenario ephemerides, IDM-Power mode-linked temporal demand, Flows Manager ephemeris-to-flux conversion and Opalis energy simulation. Boan sections 2--4 supports this chain, not a full lifecycle or independently validated fidelity. Current access is unknown. Verify exact records, quantities/time bases, raw export and reconstruction before admission. */
    }
    part def BatteryProfile :> ToolProfile {
        doc /* Conditional PyBaMM SPM/DFN and thermal model profile informed by Zhu pp.7--9. Declare cell/pack parameters and supported temperature/aging/current domain. Supplied-data calibration and SOH prediction demonstration does not validate arbitrary CubeSat packs. Independent data and prediction-error rules remain necessary. */
    }
    part def SurrogateProfile :> ToolProfile {
        doc /* Optional PhysicsNeMo surrogate, informed by Zhu. Requires sufficient identified training data, separate independent assessment, numerical/physics checks, uncertainty and host/GPU resources for the actual decision. No autonomous control is admitted. */
    }
    part def GeometryProfile :> ToolProfile {
        doc /* Optional Omniverse/OpenUSD view for a declared illumination, accommodation or thermal engineering decision, informed by Zhu. Exact model/geometry correspondence needs verification. Visualization alone supplies no electrical fidelity. Isaac and live feedback are outside this proposed profile. */
    }
    part def DisciplineProfile :> ToolProfile {
        doc /* Select electrical, thermal, applicable EMC/geometry and RAM tools or transparent analyses according to required effects. No complete EMC implementation is established. Averaged converters cannot predict switching spectra. Calibration fit, source workflow matching and successful execution cannot establish independent validity. Missing mandatory capability blocks admission. */
    }
    part def DesignSoftware :> Design, SoftwareResource {
        part conceptSeeds : ConceptSeedProfile [0..1];
    }
    part def AnalysisSoftware :> Analysis, SoftwareResource {
        part electrical : DisciplineProfile;
        part thermal : DisciplineProfile;
        part emc : DisciplineProfile [0..1];
        part ram : DisciplineProfile [0..1];
        part boanAlternative : BoanEnergyProfile [0..1];
        part battery : BatteryProfile [0..1];
        part surrogate : SurrogateProfile [0..1];
        part geometry : GeometryProfile [0..1];
        attribute declaredElectricalThermalEMCGeometryRAMProfiles : String;
        attribute selectedHostCodeProfile : String;
        perform action verifyProfiles : AdmitProfiles;
        perform action verifyHostProfiles : AdmitHostProfiles;
        doc /* Python analysis adapters coordinate declared external numerical tools. A proposed CPU minimum uses transparent sizing/budget equations, time-dependent EPS component/control models informed by Casado, PyBaMM battery models when applicable, declared thermal and applicable EMC analyses, RAM transformations and host MIL/SIL profiles. Every mandatory profile requires mapping, numerical/fidelity and independent-reference verification. Unavailable mandatory profiles block the affected complete-use claim. FMI/FMU exchange is optional pending quantity/time/solver compatibility. Source tool chains are alternatives, not silently combined executables. */
    }
    part def CredibilitySoftware :> Credibility, SoftwareResource;
    part def ReviewSoftware :> AssessmentReview, SoftwareResource;
    part def ConfigurationSoftware :> Configuration, SoftwareResource {
        perform action :>> checkCurrency : PhysicalCheckCurrency;
        doc /* Git controls model/text revisions and signed-off manifests. Identified raw binary outputs and source/reference packages use a managed archive with digest checks and declared backup/restore. Python maintains current-context and impact indexes as rebuildable views. Git commits are not engineering authorization. One authority per field is declared. No background name-based or bidirectional overwrite is permitted. Preserve failed transfers and predecessors. */
    }
    port def BaselinePort { inout item record : ControlledData; }
    port def AdviceExchangePort { inout item input : AdviceInput; inout item batch : AdviceBatch; }
    part def EngineeringHost :> HostResource {
        ref part exchange : ExchangeSoftware;
        ref part requirements : RequirementsSoftware;
        ref part design : DesignSoftware;
        ref part analyses : AnalysisSoftware;
        ref part credibility : CredibilitySoftware;
        ref part review : ReviewSoftware;
        port revisions : BaselinePort;
        port assistance : AdviceExchangePort;
        port models : AnalysisPort;
        port hostCode : HostSoftwarePort;
    }
    part def AssistanceHost :> HostResource {
        ref part advice : AssistanceSoftware;
        port assistance : AdviceExchangePort;
        port revisions : BaselinePort;
    }
    part def ArchiveHost :> HostResource {
        ref part configuration : ConfigurationSoftware;
        port engineering : BaselinePort;
        port assistance : BaselinePort;
        port execution : BaselinePort;
    }
    part def ModelEnvironment :> HostResource {
        port requests : ~AnalysisPort;
        attribute toolSolverModelAndProfileRevisions : String;
        doc /* External electrical/thermal/applicable EMC/geometry and RAM tools execute controlled requests and return raw results and all statuses. Supplied reference data are imported through IF-02. No physical acquisition, EPS operation or live feedback exists. CPU host profiles are declared. GPU is conditional on an admitted surrogate or decision-specific visualization profile. */
    }
    part def HostToolchain :> HostResource {
        port requests : ~HostSoftwarePort;
        attribute compilerBuildSimulationDependenciesAndProfile : String;
        doc /* External declared host toolchains perform coding/builds/SIL for the exact current authorized design/interface release and software scope. Engineer selects one compatible integration profile. Plain host code, cFS and F-Prime mappings are alternatives, each requiring verification. Neither both flight frameworks nor target qualification is required. */
    }
    part def ExternalEnvironments { part models : ModelEnvironment; part hostCode : HostToolchain; }
    action def OperatingProcedure {
        attribute ownerInputsStepsOutputsFailureAndAuthority : String;
        doc /* Engineering operating procedures cover source/profile admission, field ownership and reviewed transfer, suggestion disposition, model calibration/independent assessment, exact detailed-design release, review decision, backup/restore and independent replay. Engineers/review authorities remain external. These are planned procedures, not executed V&V. */
    }
    action def EngineeringProcedure :> OperatingProcedure {
        doc /* Systems Engineer coordinates qualified EPS/domain contributors: declare field owners and source/profile rights, review proposed transfers/differences, assess and dispose assistance, authorize identified changes, establish exact detailed design/interface/software-scope release before coding, and reconstruct releases through declared restore/replay instructions. Failed access, mismatch, missing prerequisites or unauthorized decisions preserve predecessors and stop affected work. */
    }
    action def ReviewProcedure :> OperatingProcedure {
        doc /* Designated review authority receives the identified prepared package and independent reviewer findings, checks current baseline and agreed scoped criteria, decides accepted/conditional/blocked progression, and records rationale. Conditional records include limits, closure actions, owners and dates. Unauthorized, stale or inconsistent decisions are preserved without changing state. Closing conditions requires new current authority and evidence. */
    }
    action def AdmitProfiles {
        in plan : AnalysisPlan; out admittedPlan : AnalysisPlan;
        out attribute mandatoryProfilesVerified : Boolean;
        bind admittedPlan = plan;
        doc /* Recheck the exact current plan/configuration, criteria, source/model/software/scope and selected profile revisions before execution. Check selected electrical, thermal and applicable EMC/geometry profiles, RAM transformation and software profile/version against required effects, available resources/access, supported mappings and verification records. Independent reference/numerical/calibration evidence bounds intended use. An unverified mandatory profile or unresolved loss blocks admission. Framework profile verification remains pending. */
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
        in request : CodingRequest; in plan : AnalysisPlan;
        out admittedRequest : CodingRequest;
        out attribute mandatoryProfilesVerified : Boolean;
        bind admittedRequest = request;
        doc /* Check the exact authorized request, selected build/SIL toolchain, simulated plant, mappings, dependencies, numerical/resource limits and every mandatory discipline/software verification record. Recheck current design/context. Missing capability blocks the request with no coding/build/SIL call. */
    }
    item def RequestedSoftwareProduct :> HostSoftwareProduct {
        attribute built : Boolean = false;
        doc /* Identified requested product descriptor only. No source/build revision or executable is fabricated on failed admission. */
    }
    item def BlockedSoftwareResult :> SoftwareRunResult {
        ref item request : CodingRequest;
        ref item :>> product : RequestedSoftwareProduct;
        attribute :>> milSilDifferencesFailuresStatus = "blocked: profile admission failed, no coding/build/SIL execution";
        attribute externalExecutionOccurred : Boolean = false;
    }
    action def BlockHostExecution {
        in request : CodingRequest; out result : BlockedSoftwareResult;
        bind result.request = request;
    }
    action def SupportedHostExecution :> ScenarioViews::SC04External5 {
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
