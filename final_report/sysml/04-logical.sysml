// Current vendor-independent logical design. Planned responsibility is not satisfaction.
// Six logical responsibility groups. Physical candidates must migrate explicitly.
package FrameworkLogical {
    private import FrameworkDomain::*;
    private import BoundaryViews::*;
    private import ScalarValues::*;
    doc /* Six input/output-derived responsibility groups specialize the current black box. Planned allocation establishes no empirical satisfaction. Directed subjects retain identity, revision, source and status. */
    metadata def detailedExchange;
    metadata def LogicalAllocation { attribute rationale : String; attribute plannedCheck : String; ref operation : SysML::ActionUsage; }
    item def CheckedTransfer :> EngineeringArtifact {
        ref item raw : EngineeringArtifact;
        ref item context : ContextRevision [0..1];
        attribute interfaceRevisionAndFindings : String;
    }
    item def AssistanceWork :> EngineeringArtifact {
        ref item submission : EngineeringSubmission;
        ref item request : GuidanceRequest;
        ref item drafts : RequirementRecord [0..*];
        ref item findings : AssistanceFinding [0..*];
        ref item report : AssistanceReport [0..1];
        ref item dispositions : SuggestionDisposition [0..*];
        attribute triggerAcknowledgementCompletion : String;
    }
    item def SuggestionDisposition :> EngineeringArtifact {
        ref item report : AssistanceReport;
        ref item decision : EngineeringDecision;
        ref item context : ContextRevision;
        attribute acceptedModifiedRejectedDeferred : String;
    }
    item def TraceLink :> EngineeringArtifact {
        ref item source : EngineeringArtifact;
        ref item target : EngineeringArtifact;
        attribute relationAndEndpointRevisions : String;
    }
    item def RequirementAllocation :> EngineeringArtifact {
        ref item requirements : RequirementRecord [0..*];
        ref item designQuantities : DesignStudy [0..*];
        ref item links : TraceLink [0..*];
        ref item dispositions : SuggestionDisposition [0..*];
        attribute methodAssumptionsUncertaintyDisposition : String;
    }
    item def DesignWork :> EngineeringArtifact {
        ref item configuration : DesignConfiguration;
        ref item study : DesignStudy [0..1];
        ref item specification : EPSInterfaceSpecification [0..1];
        ref item authorizations : DetailedDesignAuthorization [0..*];
        attribute sourcedOccurrencesAndSelectedProfile : String;
    }
    item def RunWork :> EngineeringArtifact {
        ref item plan : AnalysisPlan;
        ref item result : AnalysisResult [0..1];
        ref item milResult : AnalysisResult [0..1];
        ref item softwareResult : SoftwareRunResult [0..1];
        ref item referenceData : ReferenceData [0..*];
        ref item codingRequest : CodingRequest [0..1];
        ref item softwareProducts : HostSoftwareProduct [0..*];
    }
    item def EvidenceAssessment :> EngineeringArtifact {
        ref item plan : EPSAssessmentPlan [0..1];
        ref item model : ModelAssessment [0..1];
        ref item runs : RunWork [0..*];
        ref item requirements : RequirementRecord [0..*];
        attribute expectationsConOpsAndApplicability : String;
        attribute criterionResultsCriticalGapsOwnersDispositions : String;
    }
    item def ReviewWork :> EngineeringArtifact {
        ref item reviewPackage : ReviewPackage [0..1];
        ref item submission : ReviewSubmission;
        ref item baseline : PhaseBaseline;
        attribute exactCriteriaAndAuthorizedDisposition : String;
    }
    item def ImpactNotice :> EngineeringArtifact {
        ref item previousContext : ContextRevision;
        ref item currentContext : ContextRevision;
        ref item affected : EngineeringArtifact [0..*];
        attribute unresolvedDependenciesStaleOutputsReassessments : String;
    }
    item def ConfigurationWork :> EngineeringArtifact {
        ref item checked : CheckedTransfer [0..1];
        ref item baseline : PhaseBaseline [0..1];
        ref item impact : ImpactNotice [0..1];
        ref item review : ReviewWork [0..1];
    }
    item def DetailedDesignAuthorization :> EngineeringArtifact {
        ref item decision : EngineeringDecision;
        ref item design : DesignConfiguration;
        ref item specification : EPSInterfaceSpecification;
        ref item context : ContextRevision;
        attribute declaredHostCodeScopeReleaseConditions : String;
    }
    item def ReplayRequest :> EngineeringArtifact {
        ref item run : RunWork;
        attribute resultSpecificRulesTolerancesRevision : String;
    }
    item def ReplayPreparation :> EngineeringArtifact {
        ref item request : ReplayRequest;
        ref item plan : AnalysisPlan;
        attribute exactDependenciesHostProfileInstructions : String;
    }
    item def ReplayComparison :> EngineeringArtifact {
        ref item preparation : ReplayPreparation;
        ref item result : AnalysisResult [0..1];
        attribute rawAgreementResidualsMissingDependenciesFailures : String;
    }
    action def CheckTransfer {
        in raw : EngineeringArtifact;
        out checked : CheckedTransfer;
        out attribute compatible : Boolean;
        doc /* Check identity, revision, structure, quantity, unit, polarity, time/mode meaning and provenance against the active interface. Retain incompatible raw submissions and findings. compatible permits registration only, with no engineering approval. */
    }
    action def MakeViews {
        in baseline : PhaseBaseline;
        in selection : ViewSelection [0..1];
        out reviewPackage : ReviewPackage;
        doc /* Generate filtered mission, allocation, design, interface and analysis views from the identified controlled baseline. Include readable units, legends and resolvable record links. */
    }
    action def PresentAdvice {
        in report : AssistanceReport;
        out response : EngineeringResponse;
        doc /* Present only the report admitted by the current-context gate. Show pending/unavailable status, uncertainty, citations and unassessed scope without promoting suggestions to conformity claims. */
    }
    action def AcknowledgeAssistance {
        in submission : EngineeringSubmission;
        out work : AssistanceWork;
        doc /* Acknowledge each edit/request, retain exact context and trigger/first-response/completion times in seconds. Use the approved workload and response limits. Pending and unavailable are explicit. Response limits are declared by the engineer. MOP target cells remain empty. */
    }
    action def CheckDraft {
        in work : AssistanceWork;
        out updatedWork : AssistanceWork;
        doc /* Apply deterministic declared rules to identifiers, modal wording, required fields, responsible product, units and limits. Separately assess probable duplicates, gaps and source conflicts using level, subject, mode, conditions and quantity. Return affected records, cited rule/passage, correction/question, uncertainty and assessment scope. Unavailable differs from assessed with no finding. No algorithm or score establishes technical correctness. */
    }
    action def RecommendMethods {
        in work : AssistanceWork;
        out report : AssistanceReport;
        doc /* Recommend derivation, analysis, verification and validation methods/models from current phase, question, requirements, available inputs, validity, resources and scope. Retain applicability, cited rationale, alternatives and rejection reasons. Next activities and repeated assessments expose maturity, dependencies, open findings, review criteria and unmet prerequisites. */
    }
    action def DisposeSuggestion {
        in report : AssistanceReport;
        in decision : EngineeringSubmission;
        out disposition : SuggestionDisposition;
        out attribute authorized : Boolean;
        out attribute applyRequested : Boolean;
        doc /* Retain accepted, modified, rejected or deferred engineer dispositions with rationale and exact suggestion/context revisions. Verify the engineering role. applyRequested is true only for an accepted/modified correction or selected derivation method whose application the engineer requested. Current context is independently rechecked by L06 before any application. */
    }
    action def RetainRequirements {
        in submission : EngineeringSubmission;
        out proposedAllocation : RequirementAllocation;
        doc /* Retain complete quantitative/qualitative requirement records with owner, level, sources/parents, rationale, conditions, units, criteria, method and resolution status. Unknown or inapplicable fields require reasons. Keep proposals separate from controlled predecessors. */
    }
    action def DeriveAllocate {
        in proposedAllocation : RequirementAllocation;
        in disposition : SuggestionDisposition;
        out updatedProposedAllocation : RequirementAllocation;
        out reviewPackage : ReviewPackage;
        doc /* Apply only an admitted current authorized correction. Derive proposed EPS/component allocations using the declared method and sourced design quantities, with parents, units, assumptions, uncertainty and engineer dispositions. Prepare requirement/interface material for independent validation. Rejected/deferred suggestions do not alter requirements. */
    }
    action def TraceLinks {
        in proposedAllocation : RequirementAllocation;
        out updatedProposedAllocation : RequirementAllocation;
        doc /* Retrieve forward/reverse links among expectations, ConOps, requirements, functions/elements, interfaces, decisions and applicable evidence. Report missing/ambiguous endpoints and coverage only over the declared reference set. L06 preserves relationship revisions while L01 owns their requirement meaning. */
    }
    action def DefineDesign {
        in configuration : DesignConfiguration;
        out work : DesignWork;
        doc /* Retain expectations, constraints, nominal/degraded ConOps, orbit, attitude, duration, environment, modes, load schedules and transitions. Configure generation/storage/conversion/regulation/protection/distribution/control variants, parameters, extensions and allocation revisions. Component descriptions bind sourced properties to actual modeled occurrences. */
    }
    action def BudgetSize {
        in work : DesignWork;
        out updatedWork : DesignWork;
        doc /* Calculate preliminary generation/demand/energy budgets and array/battery sizing from sourced efficiencies, duty cycles, eclipse, battery limits, degradation and engineer margins. Calculate mass and volume from sourced modeled component/design data, retaining units, aggregation assumptions, uncertainty and unknowns. No BOM or acquisition estimate is required. */
    }
    action def CompareDesigns {
        in work : DesignWork;
        in evidence : EvidenceAssessment;
        out study : DesignStudy;
        out attribute feasible : Boolean;
        doc /* Compare alternatives on common mission assumptions, requirements and engineer-approved criteria. Mandatory supported feasibility precedes preference ranking. Retain raw measures, margins, sensitivity, uncertain close alternatives, risks and selection rationale. feasible excludes unsupported required effects or failed mandatory criteria. */
    }
    action def DefineInterfaces {
        in specification : EPSInterfaceSpecification;
        out work : DesignWork;
        out attribute profileCompatible : Boolean;
        out configuration : DesignConfiguration;
        doc /* Retain endpoint ownership, commands/telemetry/events/parameters, identifiers, types, units, ranges, polarity, time/mode meanings and encodings. Check preconditions, order, effects, rejection, transitions, protection/recovery and modeled interface behavior. Expose unsupported/lossy meanings. F Prime mappings are owned by SimulationIntegration::mapFPrime. */
    }
    action def PlanAnalysis {
        in work : DesignWork;
        out plan : AnalysisPlan;
        doc /* Compose orbit/attitude/illumination/eclipse/thermal conditions with subsystem load schedules, transitions and EPS generation/storage/loss/protection. Identify electrical, thermal, applicable EMC/geometry profiles and retain supported mappings, tool versions and omissions. Decide RAM applicability from requirements, ConOps and risks with exclusion reasons. Generate the selected RAM representation from function/component/failure dependencies and declared transformation rules, preserving missing rates and uncertainty. Retain solver, fidelity, coupling, time step, convergence rules, resources and estimated/measured runtime. */
    }
    action def PlanMIL {
        in work : DesignWork;
        out plan : AnalysisPlan;
        doc /* Form a controlled MIL plan with modeled controller, simulated plant, mission stimuli, expected/actual response criteria, nominal load/supply changes, modes, selected faults, protection and recovery. Execution belongs to the external model tool. Plan numerical/resource settings as for other analyses. */
    }
    action def CoordinateCoding {
        in work : DesignWork;
        in authorization : DetailedDesignAuthorization;
        out request : CodingRequest;
        doc /* Coordinate required external F Prime host coding/build/SIL only after the logical detailed-design authorization gate admits the exact design/interface revisions and software scope. Request dependencies, host configuration, source/build revisions, logs and failures. A phase review package or broad CDR status supplies no coding authorization. */
    }
    action def CompareMILSil {
        in work : RunWork;
        out updatedWork : RunWork;
        doc /* Coordinate SIL of released F Prime host code coupled to the same whole-CUBICS Omniverse scenario with simulated EPS/subsystem products. Compare corresponding MIL/SIL scenarios using the same stimuli and fixed rules, retaining requirement/ConOps outcomes, discrepancies and failed/partial runs. Host execution provides no target qualification. */
    }
    action def ReplayRun {
        in preparation : ReplayPreparation;
        in result : AnalysisResult;
        out comparison : ReplayComparison;
        doc /* Provide controlled reconstruction instructions, invoke external execution under the identified host profile and compare raw outputs against result-specific rules/tolerances fixed before replay. Retain missing dependencies and failed comparisons. Successful replay establishes reproducibility within the rules, independently of predictive validity. */
    }
    action def AssessModel {
        in work : RunWork;
        out evidence : EvidenceAssessment;
        out attribute numericallyValid : Boolean;
        out attribute applicable : Boolean;
        doc /* Check numerical completion, convergence and result limits, channel identities/units/timing/completeness/validity and declared time alignment. Preserve raw samples, inactive/invalid values, missing intervals and processing masks without zero filling. Retain sample/receipt time, synchronization and calculation/interface delays. Associate each conclusion with intended use, fidelity, included/omitted mechanisms, validity domain, uncertainty, calibration and independent assessment or explicit gaps. Engineer-approved prediction-error rules govern the supported scope. */
    }
    action def ProposeCalibration {
        in evidence : EvidenceAssessment;
        in data : ReferenceData;
        out proposal : ChangeProposal;
        doc /* Quality-check supplied data for its declared calibration use. Propose prior/revised parameters with exact data revisions, residual units, uncertainty and affected analyses. Separate independent assessment data/evidence. Engineers may decline. An accepted update follows L06 change control and repeats affected assessments. */
    }
    action def PlanAssessment {
        in configuration : DesignConfiguration;
        out plan : EPSAssessmentPlan;
        doc /* Specify EPS phase-product verification against applicable requirements and validation against expectations/ConOps under representative simulated conditions. Retain subject configuration, methods, conditions, inputs, expected responses, criteria, observations, limits and planned/executed status. Framework V&V, model credibility and research evaluation are separate subjects. */
    }
    action def AssessProduct {
        in evidence : EvidenceAssessment;
        out updatedEvidence : EvidenceAssessment;
        out attribute claimSupported : Boolean;
        in plan : EPSAssessmentPlan [0..1];
        doc /* Assess applicable requirement and expectation criteria using current admissible evidence. Report missing/rejected/stale/failed/out-of-domain/unresolved evidence with criticality, owner and disposition. claimSupported requires no affected critical gap. Execution success, calibration fit or replay alone cannot support an unqualified conformity claim. */
    }
    action def PrepareReviewPackage {
        in baseline : PhaseBaseline;
        in views : ReviewPackage;
        in evidence : EvidenceAssessment;
        out reviewPackage : ReviewPackage;
        out attribute entranceComplete : Boolean;
        doc /* Assemble MCR/SRR/MDR-SDR/PDR/scoped CDR/scoped SIR material against exact agreed entrance/success criteria. Include applicable coverage, decisions, design, evidence, model limits, risks, gaps and findings. Scoped CDR design release and end-of-C SIR released-product evidence remain distinct. Entrance completion produces prepared status only. */
    }
    action def CheckReviewDecision {
        in submission : ReviewSubmission;
        in baseline : PhaseBaseline;
        out work : ReviewWork;
        out attribute authorized : Boolean;
        out attribute current : Boolean;
        out attribute blocking : Boolean;
        out attribute conditional : Boolean;
        out attribute conditionsComplete : Boolean;
        in evidence : EvidenceAssessment;
        in attribute baselineCurrent : Boolean;
        out attribute decisionConsistent : Boolean;
        doc /* Check designated review authority, exact baseline and agreed scoped success criteria revisions using the L06 baselineCurrent check. Include affected critical evidence gaps in blocking findings. Distinguish accepted/conditional/progression-blocked decision. Blocking findings prevent progression. Conditional records require rationale, limits, closure actions, owners and dates. Unauthorized/stale decisions change no review state. decisionConsistent excludes an accepted or conditional disposition when blocking findings remain. An inconsistent authorized request is preserved without changing review state. */
    }
    action def RecordReviewDecision {
        in work : ReviewWork;
        out updatedWork : ReviewWork;
        doc /* Record only the admitted designated-authority decision and findings, preserving prepared/accepted/conditional/progression-blocked distinctions. The external authority chooses the disposition. Closing conditions needs closure evidence and a renewed current authorized decision. */
    }
    action def CaptureContext {
        in checked : CheckedTransfer;
        out submission : EngineeringSubmission;
        out context : ContextRevision;
        doc /* Resolve exact latest mission/requirements/design/source/criterion/scope revisions from a compatible engineering submission. Pin this context for work. Preserve raw data and predecessors. No submission is registered before the receiving compatibility gate. */
    }
    action def CheckCurrency {
        in report : AssistanceReport;
        in context : ContextRevision;
        out attribute sameContext : Boolean;
        doc /* Compare response/suggestion context with the latest six revisions, not merely the request snapshot. A concurrent edit makes sameContext false immediately. Preserve late replies as stale without replacing newer guidance. */
    }
    action def InvalidateAndReassess {
        in submission : EngineeringSubmission;
        out impact : ImpactNotice;
        out updatedSubmission : EngineeringSubmission;
        out attribute hasChange : Boolean;
        doc /* Detect reciprocal EPS/non-EPS impacts across allocations, budgets, trades, plans, guidance and evidence. Include unresolved dependencies. On requirement/mission/design/source/criterion/scope edits mark affected guidance and evidence stale immediately, including pending requests. Propose reassessment for the new context. Iteration and component recursion use this same path. */
    }
    action def CheckEngineeringChange {
        in submission : EngineeringSubmission;
        in decision : EngineeringDecision;
        out attribute authorizedCurrent : Boolean;
        out attribute acceptedChange : Boolean;
        out attribute reassessmentRequired : Boolean;
        doc /* Check assigned engineering authority and exact proposal/predecessor/context revisions. acceptedChange means the engineer accepted this change. Declined, deferred, stale or unauthorized proposals preserve the predecessor. Expose required reassessments and unresolved dependencies. */
    }
    action def RetainSuccessor {
        in submission : EngineeringSubmission;
        in decision : EngineeringDecision;
        out baseline : PhaseBaseline;
        doc /* Issue a distinct successor proposal only after current authorized change acceptance. Preserve predecessor/request/rationale/findings/dispositions. Resolve exact mission, requirements, design, interfaces, models, software and evidence revisions with regenerated/stale/unresolved statuses. A successor is no review acceptance. */
    }
    action def PreserveRun {
        in result : AnalysisResult;
        in software : SoftwareRunResult [0..1];
        out work : RunWork;
        doc /* Preserve results with requirement/expectation, method/scenario, exact design/model/software/input/parameter revisions, producer, host environment, raw outputs, logs and success/failed/cancelled/partial status. Registration does not erase earlier or incompatible raw material. */
    }
    action def CheckDetailedDesignAuthorization {
        in authorization : DetailedDesignAuthorization;
        in work : DesignWork;
        out attribute authorizedDetailedDesign : Boolean;
        out attribute currentDesign : Boolean;
        out attribute blockersClear : Boolean;
        doc /* Check an engineer-authorized detailed design release for exact current design/interface revisions, declared host code scope and applicable release conditions. Confirm no blocking design finding. A prepared or accepted phase-product CDR record is insufficient without this specific release decision. */
    }
    action def RetrieveBaseline {
        in submission : EngineeringSubmission;
        out baseline : PhaseBaseline;
        out evidence : EvidenceAssessment;
        in successorBaseline : PhaseBaseline [0..1];
        doc /* Retrieve exact current or predecessor baseline products and authorized decisions, using the explicit successorBaseline when an authorized change has just created one. Reuse evidence only within its current applicability. Missing/stale products remain explicit gaps and never acquire current status by retrieval. */
    }
    action def RetainReviewedBaseline {
        in work : ReviewWork;
        out baseline : PhaseBaseline;
        doc /* Preserve the admitted review record and its exact baseline/criteria/findings/conditions separately from package preparation. Update progression only to the disposition chosen by the designated authority. Retain predecessor and later draft successor separately. */
    }
    action def PrepareReplay {
        in request : ReplayRequest;
        out preparation : ReplayPreparation;
        out attribute dependenciesComplete : Boolean;
        out attribute rulesFixed : Boolean;
        doc /* Resolve controlled inputs, model/software/tool/environment dependencies and replay instructions for the designated run. Fix result-specific rules and tolerances before execution. Missing dependencies or unresolved comparison rules block a reconstruction-success claim. Rules are explicitly fixed for the replay, with no invented targets. */
    }
    action def PreserveRecord {
        in record : EngineeringArtifact;
        out retained : ConfigurationWork;
        doc /* Preserve identified proposals, decisions, rejected raw records and open findings without replacing controlled predecessors or changing review progression. Invalid outputs retain their status and cannot be reused as current evidence. */
    }
    action def ReassessAssistance {
        in impact : ImpactNotice;
        out work : AssistanceWork;
        doc /* Initiate a new assistance request for the revised context after invalidation, including affected drafts, methods, lifecycle activities and repeated assessments. Keep the superseded request/report and dispositions distinct. */
    }
    action def PlanRepeatedAssessment {
        in impact : ImpactNotice;
        out plan : AnalysisPlan;
        doc /* Select affected analysis/MIL/SIL and EPS product assessments from reciprocal impacts, open findings, current methods and dependencies. This request repeats model/MIL/SIL assessments of existing products and requests no new coding. A needed code revision returns through SoftwareRealization and its current detailed-design authorization gate. Configuration must resolve new inputs and applicable criteria before execution. */
    }
    action def CheckEngineerSelection {
        in decision : EngineeringDecision;
        in configuration : DesignConfiguration;
        out attribute authorizedCurrent : Boolean;
        doc /* Check the engineer decision against assigned authority and exact latest mission/design/requirement/interface context. An admitted selection controls a proposal only. Phase progression still requires designated technical review authority. */
    }
    action def PresentAssessment {
        in evidence : EvidenceAssessment;
        out response : EngineeringResponse;
        doc /* Present supported criterion outcomes and explicit limitations/gaps to the engineer for disposition. Critical gaps prevent an unqualified conformity or integration-readiness claim. */
    }
    action def CheckResultContext {
        in record : EngineeringArtifact;
        out attribute current : Boolean;
        doc /* Check recorded result/evidence/baseline dependency revisions against the latest controlled context. Preserve stale results and identify the affected products. current is false if any required dependency changed or remains unresolved. Domain applicability and review authority remain separate checks. */
    }
    action def CheckReferenceData {
        in data : ReferenceData;
        in evidence : EvidenceAssessment;
        out attribute dataUsable : Boolean;
        out attribute independentSeparation : Boolean;
        doc /* Check supplied channel identity, units, sample/receipt time, completeness, validity and calibration purpose. Preserve raw invalid/missing samples and masks. independentSeparation confirms distinct identified calibration/assessment uses or an explicit independent-assessment gap. Calibration fit is never relabeled independent validation. Missing separation or unusable data blocks a calibration proposal supported as qualified. */
    }
    action def PrepareCalibrationChange {
        in proposal : ChangeProposal;
        in decision : EngineeringDecision;
        out submission : EngineeringSubmission;
        doc /* Form the exact proposed calibration change request and engineer disposition for shared configuration control. Retain prior/revised values, source data, residuals and affected dependencies. This preparation applies no parameter update. Current assigned engineering authority and acceptance are checked before a successor can be issued. */
    }
    action def ConfigureConcept {
        in mission : MissionDefinition;
        out configuration : DesignConfiguration;
        doc /* Form identified concept design configurations from the Systems Engineer mission definition and agreed expectations/constraints. Retain nominal/degraded ConOps, assumptions, source revisions and unresolved properties. This transformation grants no concept selection or MCR acceptance. Reuse the same design, budget and analysis responsibilities at the fidelity needed by concept feasibility. */
    }

    metadata def NativeIO { attribute fr : String; attribute primary : String; attribute inputs : String [0..*]; attribute outputs : String [0..*]; attribute sourceLocator : String; ref operation : SysML::ActionUsage; }
    metadata def Subject { attribute fr : String; attribute direction : String; attribute exactField : String; attribute provenance : String; }
    metadata def ExchangeField { attribute sourceFR : String; attribute sourceOutput : String; attribute targetFR : String; attribute targetInput : String; attribute mapping : String; }
    item def RuleRecord :> EngineeringArtifact { attribute declaredRuleRevisionScope : String; ref item limits : Quantity [0..*]; }
    item def ResourceRecord :> EngineeringArtifact { attribute declaredResourcesLimits : String; ref item observations : Quantity [0..*]; }
    item def ScopeRecord :> EngineeringArtifact { attribute declaredSoftwareModelSubjectScope : String; ref item context : ContextRevision [0..1]; }
    item def TraceQueryRecord :> EngineeringArtifact { attribute forwardReverseQueryReferenceSet : String; ref item endpoints : EngineeringArtifact [0..*]; }
    item def MaturityRecord :> EngineeringArtifact { attribute declaredPhaseProductMaturity : String; ref item currentBaseline : PhaseBaseline [0..1]; }
    item def ReviewCriterionRecord :> EngineeringArtifact { attribute exactScopedCriteriaBaselineAuthorityRevision : String; attribute entranceSuccessClosureRules : String; }
    item def ConclusionRecord :> EngineeringArtifact { attribute intendedUseClaimAndLimitations : String; ref item supportingRuns : RunWork [0..*]; }
    item def EnvironmentRecord :> EngineeringArtifact { attribute hostPlatformToolchainRepresentationVersions : String; ref item exactDependencies : EngineeringArtifact [0..*]; }
    item def RiskRecord :> EngineeringArtifact { attribute riskCriticalityDisposition : String; ref item affectedSubjects : EngineeringArtifact [0..*]; }
    item def FailureDependencyRecord :> EngineeringArtifact { attribute functionsComponentsFailureRepairDependencies : String; ref item sourcedOrMissingRates : Quantity [0..*]; }
    item def TimingRecord :> EngineeringArtifact { attribute scenarioSampleReceiptTimeBaseRules : String; attribute delaySeconds : Real [0..1]; attribute timingGapsLimitFindings : String; }
    item def BaselineQueryRecord :> EngineeringArtifact { attribute currentPredecessorExactRevisionRequest : String; }
    item def ViewSelectionRecord :> EngineeringArtifact { attribute filteredSubjectsSelectionUnitsLegends : String; }
    item def MappingFindingRecord :> EngineeringArtifact { attribute entityChannelUnitRevisionAdmissionLimitFindings : String; ref item rejectedRaw : EngineeringArtifact [0..*]; }
    item def ExecutionStatusRecord :> EngineeringArtifact { attribute successFailedCancelledPartial : String; attribute logsFailures : String [0..*]; ref item numericalPayload : ReferenceData [0..*]; }
    item def ComponentDesignData :> EPSModelArtifact { ref item configuration : DesignConfiguration [0..1]; ref item sourcedMassVolumeProperties : Quantity [0..*]; ref item sources : SourceSubmission [0..*]; attribute aggregationAssumptionsUnknowns : String; }
    item def CommonDesignBasis :> EPSModelArtifact { ref item mission : MissionDefinition [0..1]; ref item requirements : RequirementRecord [0..*]; attribute commonAssumptions : String; }
    action def ProjectComponentProperties { in source : SourceSubmission; out configuration : ComponentDesignData; doc /* FR-13 project sourced technical mass/volume properties onto identified modeled component/design occurrences. Preserve unknowns, uncertainty and source revisions. Compatibility is checked by L06 before registration. */ }
    action def MapFPrime { in specification : EPSInterfaceSpecification; out work : DesignWork; out attribute profileCompatible : Boolean; doc /* Check required versioned F Prime component, instance, port, topology, command, telemetry, event and parameter mappings. Retain compatibility, unsupported behavior and lossy translations. Native structure/type checks grant no behavior verdict. */ }
    item def FR01Inputs :> EngineeringArtifact {
        ref item field01 : RequirementRecord [0..*] { @Subject { fr = "FR-01"; direction = "inputs"; exactField = "Requirement submissions"; provenance = "final_report/requirements.tex, FR-01 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RequirementRecord [0..*] { @Subject { fr = "FR-01"; direction = "inputs"; exactField = "source/parent revisions"; provenance = "final_report/requirements.tex, FR-01 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR01Outputs :> EngineeringArtifact {
        ref item field01 : RequirementRecord [0..*] { @Subject { fr = "FR-01"; direction = "outputs"; exactField = "Retained requirement records"; provenance = "final_report/requirements.tex, FR-01 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RequirementRecord [0..*] { @Subject { fr = "FR-01"; direction = "outputs"; exactField = "field resolution status"; provenance = "final_report/requirements.tex, FR-01 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR01 { in subjects : FR01Inputs; out products : FR01Outputs; doc /* Complete FR-01 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR02Inputs :> EngineeringArtifact {
        ref item field01 : EngineeringSubmission [0..*] { @Subject { fr = "FR-02"; direction = "inputs"; exactField = "Draft edits/requests"; provenance = "final_report/requirements.tex, FR-02 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RequirementRecord [0..*] { @Subject { fr = "FR-02"; direction = "inputs"; exactField = "current requirements"; provenance = "final_report/requirements.tex, FR-02 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : RuleRecord [0..*] { @Subject { fr = "FR-02"; direction = "inputs"; exactField = "rules"; provenance = "final_report/requirements.tex, FR-02 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : SourceSubmission [0..*] { @Subject { fr = "FR-02"; direction = "inputs"; exactField = "sources"; provenance = "final_report/requirements.tex, FR-02 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : RequirementAllocation [0..*] { @Subject { fr = "FR-02"; direction = "inputs"; exactField = "coverage references"; provenance = "final_report/requirements.tex, FR-02 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR02Outputs :> EngineeringArtifact {
        ref item field01 : AssistanceFinding [0..*] { @Subject { fr = "FR-02"; direction = "outputs"; exactField = "Explained findings"; provenance = "final_report/requirements.tex, FR-02 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : AssistanceFinding [0..*] { @Subject { fr = "FR-02"; direction = "outputs"; exactField = "corrections/questions"; provenance = "final_report/requirements.tex, FR-02 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : AssistanceFinding [0..*] { @Subject { fr = "FR-02"; direction = "outputs"; exactField = "assessment limits"; provenance = "final_report/requirements.tex, FR-02 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR02 { in subjects : FR02Inputs; out products : FR02Outputs; doc /* Complete FR-02 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR03Inputs :> EngineeringArtifact {
        ref item field01 : GuidanceRequest [0..*] { @Subject { fr = "FR-03"; direction = "inputs"; exactField = "Current phase/question"; provenance = "final_report/requirements.tex, FR-03 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RequirementRecord [0..*] { @Subject { fr = "FR-03"; direction = "inputs"; exactField = "requirements"; provenance = "final_report/requirements.tex, FR-03 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EngineeringArtifact [0..*] { @Subject { fr = "FR-03"; direction = "inputs"; exactField = "inputs"; provenance = "final_report/requirements.tex, FR-03 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : ModelAssessment [0..*] { @Subject { fr = "FR-03"; direction = "inputs"; exactField = "validity"; provenance = "final_report/requirements.tex, FR-03 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : ResourceRecord [0..*] { @Subject { fr = "FR-03"; direction = "inputs"; exactField = "resources"; provenance = "final_report/requirements.tex, FR-03 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field06 : ScopeRecord [0..*] { @Subject { fr = "FR-03"; direction = "inputs"; exactField = "scope"; provenance = "final_report/requirements.tex, FR-03 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR03Outputs :> EngineeringArtifact {
        ref item field01 : MethodRecommendation [0..*] { @Subject { fr = "FR-03"; direction = "outputs"; exactField = "Cited method/model recommendations"; provenance = "final_report/requirements.tex, FR-03 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MethodRecommendation [0..*] { @Subject { fr = "FR-03"; direction = "outputs"; exactField = "alternatives"; provenance = "final_report/requirements.tex, FR-03 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : MethodRecommendation [0..*] { @Subject { fr = "FR-03"; direction = "outputs"; exactField = "rejection records"; provenance = "final_report/requirements.tex, FR-03 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR03 { in subjects : FR03Inputs; out products : FR03Outputs; doc /* Complete FR-03 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR04Inputs :> EngineeringArtifact {
        ref item field01 : TraceQuery [0..*] { @Subject { fr = "FR-04"; direction = "inputs"; exactField = "Trace query"; provenance = "final_report/requirements.tex, FR-04 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EngineeringArtifact [0..*] { @Subject { fr = "FR-04"; direction = "inputs"; exactField = "linked records"; provenance = "final_report/requirements.tex, FR-04 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : RequirementAllocation [0..*] { @Subject { fr = "FR-04"; direction = "inputs"; exactField = "declared reference set"; provenance = "final_report/requirements.tex, FR-04 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR04Outputs :> EngineeringArtifact {
        ref item field01 : TraceLink [0..*] { @Subject { fr = "FR-04"; direction = "outputs"; exactField = "Forward/reverse links"; provenance = "final_report/requirements.tex, FR-04 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : TraceLink [0..*] { @Subject { fr = "FR-04"; direction = "outputs"; exactField = "endpoint gaps"; provenance = "final_report/requirements.tex, FR-04 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : RequirementAllocation [0..*] { @Subject { fr = "FR-04"; direction = "outputs"; exactField = "coverage"; provenance = "final_report/requirements.tex, FR-04 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR04 { in subjects : FR04Inputs; out products : FR04Outputs; doc /* Complete FR-04 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR05Inputs :> EngineeringArtifact {
        ref item field01 : ChangeProposal [0..*] { @Subject { fr = "FR-05"; direction = "inputs"; exactField = "Proposed change"; provenance = "final_report/requirements.tex, FR-05 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EngineeringArtifact [0..*] { @Subject { fr = "FR-05"; direction = "inputs"; exactField = "current engineering dependencies"; provenance = "final_report/requirements.tex, FR-05 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR05Outputs :> EngineeringArtifact {
        ref item field01 : ImpactNotice [0..*] { @Subject { fr = "FR-05"; direction = "outputs"; exactField = "Reciprocal impacts"; provenance = "final_report/requirements.tex, FR-05 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ImpactNotice [0..*] { @Subject { fr = "FR-05"; direction = "outputs"; exactField = "unresolved dependencies"; provenance = "final_report/requirements.tex, FR-05 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ImpactNotice [0..*] { @Subject { fr = "FR-05"; direction = "outputs"; exactField = "required reassessments"; provenance = "final_report/requirements.tex, FR-05 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR05 { in subjects : FR05Inputs; out products : FR05Outputs; doc /* Complete FR-05 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR06Inputs :> EngineeringArtifact {
        ref item field01 : PhaseBaseline [0..*] { @Subject { fr = "FR-06"; direction = "inputs"; exactField = "Predecessor baseline"; provenance = "final_report/requirements.tex, FR-06 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ChangeProposal [0..*] { @Subject { fr = "FR-06"; direction = "inputs"; exactField = "change request"; provenance = "final_report/requirements.tex, FR-06 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EngineeringDecision [0..*] { @Subject { fr = "FR-06"; direction = "inputs"; exactField = "authorized change acceptance"; provenance = "final_report/requirements.tex, FR-06 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR06Outputs :> EngineeringArtifact {
        ref item field01 : PhaseBaseline [0..*] { @Subject { fr = "FR-06"; direction = "outputs"; exactField = "Successor baseline"; provenance = "final_report/requirements.tex, FR-06 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : PhaseBaseline [0..*] { @Subject { fr = "FR-06"; direction = "outputs"; exactField = "preserved predecessor"; provenance = "final_report/requirements.tex, FR-06 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-06"; direction = "outputs"; exactField = "product/evidence status"; provenance = "final_report/requirements.tex, FR-06 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR06 { in subjects : FR06Inputs; out products : FR06Outputs; doc /* Complete FR-06 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR07Inputs :> EngineeringArtifact {
        ref item field01 : EngineeringArtifact [0..*] { @Subject { fr = "FR-07"; direction = "inputs"; exactField = "Product/evidence revisions"; provenance = "final_report/requirements.tex, FR-07 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EngineeringDecision [0..*] { @Subject { fr = "FR-07"; direction = "inputs"; exactField = "decisions"; provenance = "final_report/requirements.tex, FR-07 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : BaselineRetrieval [0..*] { @Subject { fr = "FR-07"; direction = "inputs"; exactField = "baseline retrieval request"; provenance = "final_report/requirements.tex, FR-07 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR07Outputs :> EngineeringArtifact {
        ref item field01 : PhaseBaseline [0..*] { @Subject { fr = "FR-07"; direction = "outputs"; exactField = "Retrievable exact baselines"; provenance = "final_report/requirements.tex, FR-07 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : PhaseBaseline [0..*] { @Subject { fr = "FR-07"; direction = "outputs"; exactField = "revision/decision histories"; provenance = "final_report/requirements.tex, FR-07 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR07 { in subjects : FR07Inputs; out products : FR07Outputs; doc /* Complete FR-07 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR08Inputs :> EngineeringArtifact {
        ref item field01 : EngineeringArtifact [0..*] { @Subject { fr = "FR-08"; direction = "inputs"; exactField = "Raw submissions"; provenance = "final_report/requirements.tex, FR-08 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-08"; direction = "inputs"; exactField = "declared interface specification"; provenance = "final_report/requirements.tex, FR-08 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR08Outputs :> EngineeringArtifact {
        ref item field01 : CheckedTransfer [0..*] { @Subject { fr = "FR-08"; direction = "outputs"; exactField = "Admitted transfers or retained rejections with unchanged controlled content"; provenance = "final_report/requirements.tex, FR-08 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR08 { in subjects : FR08Inputs; out products : FR08Outputs; doc /* Complete FR-08 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR09Inputs :> EngineeringArtifact {
        ref item field01 : RunWork [0..*] { @Subject { fr = "FR-09"; direction = "inputs"; exactField = "Analysis/software results"; provenance = "final_report/requirements.tex, FR-09 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EngineeringArtifact [0..*] { @Subject { fr = "FR-09"; direction = "inputs"; exactField = "exact dependencies"; provenance = "final_report/requirements.tex, FR-09 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-09"; direction = "inputs"; exactField = "logs"; provenance = "final_report/requirements.tex, FR-09 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-09"; direction = "inputs"; exactField = "status"; provenance = "final_report/requirements.tex, FR-09 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR09Outputs :> EngineeringArtifact {
        ref item field01 : RunWork [0..*] { @Subject { fr = "FR-09"; direction = "outputs"; exactField = "Configuration-linked results"; provenance = "final_report/requirements.tex, FR-09 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RunWork [0..*] { @Subject { fr = "FR-09"; direction = "outputs"; exactField = "provenance"; provenance = "final_report/requirements.tex, FR-09 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-09"; direction = "outputs"; exactField = "execution status"; provenance = "final_report/requirements.tex, FR-09 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR09 { in subjects : FR09Inputs; out products : FR09Outputs; doc /* Complete FR-09 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR10Inputs :> EngineeringArtifact {
        ref item field01 : ReplayRequest [0..*] { @Subject { fr = "FR-10"; direction = "inputs"; exactField = "Replay request"; provenance = "final_report/requirements.tex, FR-10 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RunWork [0..*] { @Subject { fr = "FR-10"; direction = "inputs"; exactField = "preserved run/dependencies"; provenance = "final_report/requirements.tex, FR-10 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : AnalysisResult [0..*] { @Subject { fr = "FR-10"; direction = "inputs"; exactField = "returned outputs"; provenance = "final_report/requirements.tex, FR-10 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : RuleRecord [0..*] { @Subject { fr = "FR-10"; direction = "inputs"; exactField = "fixed comparison rules"; provenance = "final_report/requirements.tex, FR-10 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR10Outputs :> EngineeringArtifact {
        ref item field01 : ReplayPreparation [0..*] { @Subject { fr = "FR-10"; direction = "outputs"; exactField = "Replay inputs/instructions"; provenance = "final_report/requirements.tex, FR-10 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReplayComparison [0..*] { @Subject { fr = "FR-10"; direction = "outputs"; exactField = "comparisons"; provenance = "final_report/requirements.tex, FR-10 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ReplayComparison [0..*] { @Subject { fr = "FR-10"; direction = "outputs"; exactField = "dependency/failure findings"; provenance = "final_report/requirements.tex, FR-10 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR10 { in subjects : FR10Inputs; out products : FR10Outputs; doc /* Complete FR-10 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR11Inputs :> EngineeringArtifact {
        ref item field01 : EvidenceAssessment [0..*] { @Subject { fr = "FR-11"; direction = "inputs"; exactField = "Evidence/status"; provenance = "final_report/requirements.tex, FR-11 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RequirementAllocation [0..*] { @Subject { fr = "FR-11"; direction = "inputs"; exactField = "affected requirements/expectations"; provenance = "final_report/requirements.tex, FR-11 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : RuleRecord [0..*] { @Subject { fr = "FR-11"; direction = "inputs"; exactField = "criticality rules"; provenance = "final_report/requirements.tex, FR-11 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR11Outputs :> EngineeringArtifact {
        ref item field01 : EvidenceAssessment [0..*] { @Subject { fr = "FR-11"; direction = "outputs"; exactField = "Gap reports"; provenance = "final_report/requirements.tex, FR-11 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EvidenceAssessment [0..*] { @Subject { fr = "FR-11"; direction = "outputs"; exactField = "blocked unsupported conformity claims"; provenance = "final_report/requirements.tex, FR-11 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR11 { in subjects : FR11Inputs; out products : FR11Outputs; doc /* Complete FR-11 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR13Inputs :> EngineeringArtifact {
        ref item field01 : ComponentDesignData [0..*] { @Subject { fr = "FR-13"; direction = "inputs"; exactField = "Modeled component and design data with sourced mass and volume properties"; provenance = "final_report/requirements.tex, FR-13 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR13Outputs :> EngineeringArtifact {
        ref item field01 : DesignStudy [0..*] { @Subject { fr = "FR-13"; direction = "outputs"; exactField = "Mass and volume estimates with uncertainty and unknowns"; provenance = "final_report/requirements.tex, FR-13 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR13 { in subjects : FR13Inputs; out products : FR13Outputs; doc /* Complete FR-13 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR14Inputs :> EngineeringArtifact {
        ref item field01 : DesignConfiguration [0..*] { @Subject { fr = "FR-14"; direction = "inputs"; exactField = "EPS alternatives"; provenance = "final_report/requirements.tex, FR-14 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : CommonDesignBasis [0..*] { @Subject { fr = "FR-14"; direction = "inputs"; exactField = "common mission/requirements"; provenance = "final_report/requirements.tex, FR-14 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ReviewCriterionRecord [0..*] { @Subject { fr = "FR-14"; direction = "inputs"; exactField = "approved criteria"; provenance = "final_report/requirements.tex, FR-14 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR14Outputs :> EngineeringArtifact {
        ref item field01 : DesignStudy [0..*] { @Subject { fr = "FR-14"; direction = "outputs"; exactField = "Feasibility"; provenance = "final_report/requirements.tex, FR-14 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : DesignStudy [0..*] { @Subject { fr = "FR-14"; direction = "outputs"; exactField = "ranking"; provenance = "final_report/requirements.tex, FR-14 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : DesignStudy [0..*] { @Subject { fr = "FR-14"; direction = "outputs"; exactField = "sensitivity"; provenance = "final_report/requirements.tex, FR-14 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : EngineeringDecision [0..*] { @Subject { fr = "FR-14"; direction = "outputs"; exactField = "selection rationale"; provenance = "final_report/requirements.tex, FR-14 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR14 { in subjects : FR14Inputs; out products : FR14Outputs; doc /* Complete FR-14 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR15Inputs :> EngineeringArtifact {
        ref item field01 : DesignConfiguration [0..*] { @Subject { fr = "FR-15"; direction = "inputs"; exactField = "Design parameters"; provenance = "final_report/requirements.tex, FR-15 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : DesignConfiguration [0..*] { @Subject { fr = "FR-15"; direction = "inputs"; exactField = "component variants"; provenance = "final_report/requirements.tex, FR-15 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : DesignConfiguration [0..*] { @Subject { fr = "FR-15"; direction = "inputs"; exactField = "extensions"; provenance = "final_report/requirements.tex, FR-15 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : RequirementAllocation [0..*] { @Subject { fr = "FR-15"; direction = "inputs"; exactField = "allocations"; provenance = "final_report/requirements.tex, FR-15 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR15Outputs :> EngineeringArtifact {
        ref item field01 : DesignConfiguration [0..*] { @Subject { fr = "FR-15"; direction = "outputs"; exactField = "Configured EPS design representations"; provenance = "final_report/requirements.tex, FR-15 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR15 { in subjects : FR15Inputs; out products : FR15Outputs; doc /* Complete FR-15 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR16Inputs :> EngineeringArtifact {
        ref item field01 : ReferenceData [0..*] { @Subject { fr = "FR-16"; direction = "inputs"; exactField = "Whole-CUBICS mission/subsystem load and mode histories"; provenance = "final_report/requirements.tex, FR-16 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReferenceData [0..*] { @Subject { fr = "FR-16"; direction = "inputs"; exactField = "orbit/attitude/illumination/thermal histories"; provenance = "final_report/requirements.tex, FR-16 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : DesignConfiguration [0..*] { @Subject { fr = "FR-16"; direction = "inputs"; exactField = "EPS models"; provenance = "final_report/requirements.tex, FR-16 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR16Outputs :> EngineeringArtifact {
        ref item field01 : AnalysisResult [0..*] { @Subject { fr = "FR-16"; direction = "outputs"; exactField = "Power/energy balance"; provenance = "final_report/requirements.tex, FR-16 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : AnalysisResult [0..*] { @Subject { fr = "FR-16"; direction = "outputs"; exactField = "bus quantities"; provenance = "final_report/requirements.tex, FR-16 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ReferenceData [0..*] { @Subject { fr = "FR-16"; direction = "outputs"; exactField = "battery state histories"; provenance = "final_report/requirements.tex, FR-16 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR16 { in subjects : FR16Inputs; out products : FR16Outputs; doc /* Complete FR-16 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR17Inputs :> EngineeringArtifact {
        ref item field01 : RequirementRecord [0..*] { @Subject { fr = "FR-17"; direction = "inputs"; exactField = "Spacecraft requirements"; provenance = "final_report/requirements.tex, FR-17 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MissionDefinition [0..*] { @Subject { fr = "FR-17"; direction = "inputs"; exactField = "scenarios"; provenance = "final_report/requirements.tex, FR-17 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : DesignStudy [0..*] { @Subject { fr = "FR-17"; direction = "inputs"; exactField = "quantities"; provenance = "final_report/requirements.tex, FR-17 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : MethodRecommendation [0..*] { @Subject { fr = "FR-17"; direction = "inputs"; exactField = "derivation method"; provenance = "final_report/requirements.tex, FR-17 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR17Outputs :> EngineeringArtifact {
        ref item field01 : RequirementAllocation [0..*] { @Subject { fr = "FR-17"; direction = "outputs"; exactField = "Proposed EPS/component allocations"; provenance = "final_report/requirements.tex, FR-17 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : TraceLink [0..*] { @Subject { fr = "FR-17"; direction = "outputs"; exactField = "traces"; provenance = "final_report/requirements.tex, FR-17 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : SuggestionDisposition [0..*] { @Subject { fr = "FR-17"; direction = "outputs"; exactField = "dispositions"; provenance = "final_report/requirements.tex, FR-17 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR17 { in subjects : FR17Inputs; out products : FR17Outputs; doc /* Complete FR-17 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR18Inputs :> EngineeringArtifact {
        ref item field01 : DesignConfiguration [0..*] { @Subject { fr = "FR-18"; direction = "inputs"; exactField = "Component/design model revisions"; provenance = "final_report/requirements.tex, FR-18 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : SimulationCouplingProfile [0..*] { @Subject { fr = "FR-18"; direction = "inputs"; exactField = "discipline and Omniverse coupling profiles"; provenance = "final_report/requirements.tex, FR-18 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : SimulationCouplingProfile [0..*] { @Subject { fr = "FR-18"; direction = "inputs"; exactField = "whole-CUBICS model/scenario revisions"; provenance = "final_report/requirements.tex, FR-18 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : ReferenceData [0..*] { @Subject { fr = "FR-18"; direction = "inputs"; exactField = "spacecraft/subsystem scenario histories"; provenance = "final_report/requirements.tex, FR-18 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : SimulationCouplingProfile [0..*] { @Subject { fr = "FR-18"; direction = "inputs"; exactField = "directed mappings"; provenance = "final_report/requirements.tex, FR-18 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field06 : AnalysisResponse [0..*] { @Subject { fr = "FR-18"; direction = "inputs"; exactField = "returned tool responses"; provenance = "final_report/requirements.tex, FR-18 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR18Outputs :> EngineeringArtifact {
        ref item field01 : DesignConfiguration [0..*] { @Subject { fr = "FR-18"; direction = "outputs"; exactField = "Exchanged component/design models"; provenance = "final_report/requirements.tex, FR-18 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReferenceData [0..*] { @Subject { fr = "FR-18"; direction = "outputs"; exactField = "mapped EPS analysis inputs"; provenance = "final_report/requirements.tex, FR-18 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : AnalysisResult [0..*] { @Subject { fr = "FR-18"; direction = "outputs"; exactField = "EPS states/results returned to the same whole-CUBICS scenario"; provenance = "final_report/requirements.tex, FR-18 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : MappingFindingRecord [0..*] { @Subject { fr = "FR-18"; direction = "outputs"; exactField = "mapping findings"; provenance = "final_report/requirements.tex, FR-18 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-18"; direction = "outputs"; exactField = "execution status"; provenance = "final_report/requirements.tex, FR-18 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field06 : MappingFindingRecord [0..*] { @Subject { fr = "FR-18"; direction = "outputs"; exactField = "transfer limitations"; provenance = "final_report/requirements.tex, FR-18 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR18 { in subjects : FR18Inputs; out products : FR18Outputs; doc /* Complete FR-18 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR19Inputs :> EngineeringArtifact {
        ref item field01 : DesignConfiguration [0..*] { @Subject { fr = "FR-19"; direction = "inputs"; exactField = "Controller/plant models"; provenance = "final_report/requirements.tex, FR-19 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MissionDefinition [0..*] { @Subject { fr = "FR-19"; direction = "inputs"; exactField = "mission scenarios"; provenance = "final_report/requirements.tex, FR-19 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EPSAssessmentPlan [0..*] { @Subject { fr = "FR-19"; direction = "inputs"; exactField = "MIL criteria"; provenance = "final_report/requirements.tex, FR-19 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR19Outputs :> EngineeringArtifact {
        ref item field01 : AnalysisRequest [0..*] { @Subject { fr = "FR-19"; direction = "outputs"; exactField = "MIL requests"; provenance = "final_report/requirements.tex, FR-19 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReferenceData [0..*] { @Subject { fr = "FR-19"; direction = "outputs"; exactField = "retained stimuli/responses"; provenance = "final_report/requirements.tex, FR-19 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : AnalysisResult [0..*] { @Subject { fr = "FR-19"; direction = "outputs"; exactField = "criterion outcomes/failures"; provenance = "final_report/requirements.tex, FR-19 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR19 { in subjects : FR19Inputs; out products : FR19Outputs; doc /* Complete FR-19 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR20Inputs :> EngineeringArtifact {
        ref item field01 : MissionDefinition [0..*] { @Subject { fr = "FR-20"; direction = "inputs"; exactField = "Mission modes/loads"; provenance = "final_report/requirements.tex, FR-20 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : DesignStudy [0..*] { @Subject { fr = "FR-20"; direction = "inputs"; exactField = "efficiencies"; provenance = "final_report/requirements.tex, FR-20 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : DesignStudy [0..*] { @Subject { fr = "FR-20"; direction = "inputs"; exactField = "duty cycles"; provenance = "final_report/requirements.tex, FR-20 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : MissionDefinition [0..*] { @Subject { fr = "FR-20"; direction = "inputs"; exactField = "eclipse"; provenance = "final_report/requirements.tex, FR-20 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : DesignStudy [0..*] { @Subject { fr = "FR-20"; direction = "inputs"; exactField = "battery limits"; provenance = "final_report/requirements.tex, FR-20 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field06 : DesignStudy [0..*] { @Subject { fr = "FR-20"; direction = "inputs"; exactField = "degradation"; provenance = "final_report/requirements.tex, FR-20 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field07 : DesignStudy [0..*] { @Subject { fr = "FR-20"; direction = "inputs"; exactField = "margins"; provenance = "final_report/requirements.tex, FR-20 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR20Outputs :> EngineeringArtifact {
        ref item field01 : DesignStudy [0..*] { @Subject { fr = "FR-20"; direction = "outputs"; exactField = "Power/energy budgets"; provenance = "final_report/requirements.tex, FR-20 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : DesignStudy [0..*] { @Subject { fr = "FR-20"; direction = "outputs"; exactField = "array/battery sizing"; provenance = "final_report/requirements.tex, FR-20 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR20 { in subjects : FR20Inputs; out products : FR20Outputs; doc /* Complete FR-20 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR21Inputs :> EngineeringArtifact {
        ref item field01 : ConclusionRecord [0..*] { @Subject { fr = "FR-21"; direction = "inputs"; exactField = "Conclusions"; provenance = "final_report/requirements.tex, FR-21 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ModelAssessment [0..*] { @Subject { fr = "FR-21"; direction = "inputs"; exactField = "model scope"; provenance = "final_report/requirements.tex, FR-21 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EvidenceAssessment [0..*] { @Subject { fr = "FR-21"; direction = "inputs"; exactField = "credibility evidence"; provenance = "final_report/requirements.tex, FR-21 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : RuleRecord [0..*] { @Subject { fr = "FR-21"; direction = "inputs"; exactField = "error rules"; provenance = "final_report/requirements.tex, FR-21 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR21Outputs :> EngineeringArtifact {
        ref item field01 : ModelAssessment [0..*] { @Subject { fr = "FR-21"; direction = "outputs"; exactField = "Conclusion-linked credibility records"; provenance = "final_report/requirements.tex, FR-21 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ModelAssessment [0..*] { @Subject { fr = "FR-21"; direction = "outputs"; exactField = "explicit gaps"; provenance = "final_report/requirements.tex, FR-21 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR21 { in subjects : FR21Inputs; out products : FR21Outputs; doc /* Complete FR-21 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR22Inputs :> EngineeringArtifact {
        ref item field01 : DesignConfiguration [0..*] { @Subject { fr = "FR-22"; direction = "inputs"; exactField = "Current parameters"; provenance = "final_report/requirements.tex, FR-22 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReferenceData [0..*] { @Subject { fr = "FR-22"; direction = "inputs"; exactField = "quality-checked supplied reference data"; provenance = "final_report/requirements.tex, FR-22 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR22Outputs :> EngineeringArtifact {
        ref item field01 : ChangeProposal [0..*] { @Subject { fr = "FR-22"; direction = "outputs"; exactField = "Calibration proposals"; provenance = "final_report/requirements.tex, FR-22 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ModelAssessment [0..*] { @Subject { fr = "FR-22"; direction = "outputs"; exactField = "residuals"; provenance = "final_report/requirements.tex, FR-22 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ModelAssessment [0..*] { @Subject { fr = "FR-22"; direction = "outputs"; exactField = "uncertainty"; provenance = "final_report/requirements.tex, FR-22 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : ImpactNotice [0..*] { @Subject { fr = "FR-22"; direction = "outputs"; exactField = "affected analyses"; provenance = "final_report/requirements.tex, FR-22 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR22 { in subjects : FR22Inputs; out products : FR22Outputs; doc /* Complete FR-22 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR23Inputs :> EngineeringArtifact {
        ref item field01 : AnalysisPlan [0..*] { @Subject { fr = "FR-23"; direction = "inputs"; exactField = "Run settings"; provenance = "final_report/requirements.tex, FR-23 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EnvironmentRecord [0..*] { @Subject { fr = "FR-23"; direction = "inputs"; exactField = "environment"; provenance = "final_report/requirements.tex, FR-23 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ResourceRecord [0..*] { @Subject { fr = "FR-23"; direction = "inputs"; exactField = "resource limits"; provenance = "final_report/requirements.tex, FR-23 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : AnalysisResult [0..*] { @Subject { fr = "FR-23"; direction = "inputs"; exactField = "observations"; provenance = "final_report/requirements.tex, FR-23 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR23Outputs :> EngineeringArtifact {
        ref item field01 : AnalysisPlan [0..*] { @Subject { fr = "FR-23"; direction = "outputs"; exactField = "Run configuration/runtime records"; provenance = "final_report/requirements.tex, FR-23 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MappingFindingRecord [0..*] { @Subject { fr = "FR-23"; direction = "outputs"; exactField = "numerical/resource findings"; provenance = "final_report/requirements.tex, FR-23 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR23 { in subjects : FR23Inputs; out products : FR23Outputs; doc /* Complete FR-23 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR24Inputs :> EngineeringArtifact {
        ref item field01 : HostSoftwareProduct [0..*] { @Subject { fr = "FR-24"; direction = "inputs"; exactField = "Released F Prime host code/build"; provenance = "final_report/requirements.tex, FR-24 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : DesignConfiguration [0..*] { @Subject { fr = "FR-24"; direction = "inputs"; exactField = "simulated EPS/subsystem products"; provenance = "final_report/requirements.tex, FR-24 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : SimulationCouplingProfile [0..*] { @Subject { fr = "FR-24"; direction = "inputs"; exactField = "whole-CUBICS scenario and coupling-profile revisions"; provenance = "final_report/requirements.tex, FR-24 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : AnalysisResult [0..*] { @Subject { fr = "FR-24"; direction = "inputs"; exactField = "matched MIL results"; provenance = "final_report/requirements.tex, FR-24 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : RuleRecord [0..*] { @Subject { fr = "FR-24"; direction = "inputs"; exactField = "fixed comparison rules"; provenance = "final_report/requirements.tex, FR-24 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR24Outputs :> EngineeringArtifact {
        ref item field01 : CodingRequest [0..*] { @Subject { fr = "FR-24"; direction = "outputs"; exactField = "SIL requests"; provenance = "final_report/requirements.tex, FR-24 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : SoftwareRunResult [0..*] { @Subject { fr = "FR-24"; direction = "outputs"; exactField = "retained host responses"; provenance = "final_report/requirements.tex, FR-24 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : SoftwareAssessment [0..*] { @Subject { fr = "FR-24"; direction = "outputs"; exactField = "requirement/ConOps outcomes"; provenance = "final_report/requirements.tex, FR-24 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : SoftwareAssessment [0..*] { @Subject { fr = "FR-24"; direction = "outputs"; exactField = "MIL/SIL differences with execution status and limits"; provenance = "final_report/requirements.tex, FR-24 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR24 { in subjects : FR24Inputs; out products : FR24Outputs; doc /* Complete FR-24 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR25Inputs :> EngineeringArtifact {
        ref item field01 : MissionDefinition [0..*] { @Subject { fr = "FR-25"; direction = "inputs"; exactField = "Mission expectations"; provenance = "final_report/requirements.tex, FR-25 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MissionDefinition [0..*] { @Subject { fr = "FR-25"; direction = "inputs"; exactField = "constraints"; provenance = "final_report/requirements.tex, FR-25 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : MissionDefinition [0..*] { @Subject { fr = "FR-25"; direction = "inputs"; exactField = "nominal/degraded ConOps"; provenance = "final_report/requirements.tex, FR-25 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR25Outputs :> EngineeringArtifact {
        ref item field01 : MissionDefinition [0..*] { @Subject { fr = "FR-25"; direction = "outputs"; exactField = "Revision-linked mission and ConOps records"; provenance = "final_report/requirements.tex, FR-25 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR25 { in subjects : FR25Inputs; out products : FR25Outputs; doc /* Complete FR-25 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR26Inputs :> EngineeringArtifact {
        ref item field01 : RequirementRecord [0..*] { @Subject { fr = "FR-26"; direction = "inputs"; exactField = "EPS requirements"; provenance = "final_report/requirements.tex, FR-26 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MissionDefinition [0..*] { @Subject { fr = "FR-26"; direction = "inputs"; exactField = "ConOps"; provenance = "final_report/requirements.tex, FR-26 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : RiskRecord [0..*] { @Subject { fr = "FR-26"; direction = "inputs"; exactField = "risks"; provenance = "final_report/requirements.tex, FR-26 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : FailureDependencyRecord [0..*] { @Subject { fr = "FR-26"; direction = "inputs"; exactField = "failure/repair assumptions"; provenance = "final_report/requirements.tex, FR-26 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR26Outputs :> EngineeringArtifact {
        ref item field01 : MethodRecommendation [0..*] { @Subject { fr = "FR-26"; direction = "outputs"; exactField = "Applicable RAM methods"; provenance = "final_report/requirements.tex, FR-26 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MethodRecommendation [0..*] { @Subject { fr = "FR-26"; direction = "outputs"; exactField = "measures"; provenance = "final_report/requirements.tex, FR-26 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : MethodRecommendation [0..*] { @Subject { fr = "FR-26"; direction = "outputs"; exactField = "coverage"; provenance = "final_report/requirements.tex, FR-26 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : MethodRecommendation [0..*] { @Subject { fr = "FR-26"; direction = "outputs"; exactField = "exclusions"; provenance = "final_report/requirements.tex, FR-26 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR26 { in subjects : FR26Inputs; out products : FR26Outputs; doc /* Complete FR-26 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR27Inputs :> EngineeringArtifact {
        ref item field01 : DesignConfiguration [0..*] { @Subject { fr = "FR-27"; direction = "inputs"; exactField = "Functions"; provenance = "final_report/requirements.tex, FR-27 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : DesignConfiguration [0..*] { @Subject { fr = "FR-27"; direction = "inputs"; exactField = "components"; provenance = "final_report/requirements.tex, FR-27 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : FailureDependencyRecord [0..*] { @Subject { fr = "FR-27"; direction = "inputs"; exactField = "failure dependencies"; provenance = "final_report/requirements.tex, FR-27 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : ReferenceData [0..*] { @Subject { fr = "FR-27"; direction = "inputs"; exactField = "data"; provenance = "final_report/requirements.tex, FR-27 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : RuleRecord [0..*] { @Subject { fr = "FR-27"; direction = "inputs"; exactField = "transformation rules"; provenance = "final_report/requirements.tex, FR-27 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR27Outputs :> EngineeringArtifact {
        ref item field01 : AnalysisResult [0..*] { @Subject { fr = "FR-27"; direction = "outputs"; exactField = "RAM representations/results with uncertainty and missing data"; provenance = "final_report/requirements.tex, FR-27 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR27 { in subjects : FR27Inputs; out products : FR27Outputs; doc /* Complete FR-27 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR28Inputs :> EngineeringArtifact {
        ref item field01 : RequirementAllocation [0..*] { @Subject { fr = "FR-28"; direction = "inputs"; exactField = "EPS requirements/expectations"; provenance = "final_report/requirements.tex, FR-28 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EPSAssessmentPlan [0..*] { @Subject { fr = "FR-28"; direction = "inputs"; exactField = "assessment plans"; provenance = "final_report/requirements.tex, FR-28 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : AnalysisResult [0..*] { @Subject { fr = "FR-28"; direction = "inputs"; exactField = "observations"; provenance = "final_report/requirements.tex, FR-28 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR28Outputs :> EngineeringArtifact {
        ref item field01 : EPSAssessmentPlan [0..*] { @Subject { fr = "FR-28"; direction = "outputs"; exactField = "Retained EPS V&V plans"; provenance = "final_report/requirements.tex, FR-28 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RequirementAllocation [0..*] { @Subject { fr = "FR-28"; direction = "outputs"; exactField = "separate references"; provenance = "final_report/requirements.tex, FR-28 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-28"; direction = "outputs"; exactField = "planned/executed status"; provenance = "final_report/requirements.tex, FR-28 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR28 { in subjects : FR28Inputs; out products : FR28Outputs; doc /* Complete FR-28 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR29Inputs :> EngineeringArtifact {
        ref item field01 : AssistanceReport [0..*] { @Subject { fr = "FR-29"; direction = "inputs"; exactField = "Suggestion/context revisions"; provenance = "final_report/requirements.tex, FR-29 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EngineeringDecision [0..*] { @Subject { fr = "FR-29"; direction = "inputs"; exactField = "authorized engineer decision"; provenance = "final_report/requirements.tex, FR-29 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR29Outputs :> EngineeringArtifact {
        ref item field01 : SuggestionDisposition [0..*] { @Subject { fr = "FR-29"; direction = "outputs"; exactField = "Recorded disposition"; provenance = "final_report/requirements.tex, FR-29 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EngineeringDecision [0..*] { @Subject { fr = "FR-29"; direction = "outputs"; exactField = "rationale"; provenance = "final_report/requirements.tex, FR-29 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : TraceLink [0..*] { @Subject { fr = "FR-29"; direction = "outputs"; exactField = "revision links"; provenance = "final_report/requirements.tex, FR-29 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR29 { in subjects : FR29Inputs; out products : FR29Outputs; doc /* Complete FR-29 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR30Inputs :> EngineeringArtifact {
        ref item field01 : ContextRevision [0..*] { @Subject { fr = "FR-30"; direction = "inputs"; exactField = "Changed context revisions"; provenance = "final_report/requirements.tex, FR-30 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : AssistanceReport [0..*] { @Subject { fr = "FR-30"; direction = "inputs"; exactField = "affected assistance"; provenance = "final_report/requirements.tex, FR-30 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR30Outputs :> EngineeringArtifact {
        ref item field01 : ImpactNotice [0..*] { @Subject { fr = "FR-30"; direction = "outputs"; exactField = "Stale status"; provenance = "final_report/requirements.tex, FR-30 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ImpactNotice [0..*] { @Subject { fr = "FR-30"; direction = "outputs"; exactField = "blocked application"; provenance = "final_report/requirements.tex, FR-30 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ImpactNotice [0..*] { @Subject { fr = "FR-30"; direction = "outputs"; exactField = "reassessment request"; provenance = "final_report/requirements.tex, FR-30 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR30 { in subjects : FR30Inputs; out products : FR30Outputs; doc /* Complete FR-30 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR31Inputs :> EngineeringArtifact {
        ref item field01 : ReferenceData [0..*] { @Subject { fr = "FR-31"; direction = "inputs"; exactField = "Exchanged/simulated/reference histories"; provenance = "final_report/requirements.tex, FR-31 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : TimingRecord [0..*] { @Subject { fr = "FR-31"; direction = "inputs"; exactField = "scenario time references"; provenance = "final_report/requirements.tex, FR-31 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : TimingRecord [0..*] { @Subject { fr = "FR-31"; direction = "inputs"; exactField = "sampling/exchange timing"; provenance = "final_report/requirements.tex, FR-31 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : RuleRecord [0..*] { @Subject { fr = "FR-31"; direction = "inputs"; exactField = "synchronization rules and limits"; provenance = "final_report/requirements.tex, FR-31 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : TimingRecord [0..*] { @Subject { fr = "FR-31"; direction = "inputs"; exactField = "known delays"; provenance = "final_report/requirements.tex, FR-31 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR31Outputs :> EngineeringArtifact {
        ref item field01 : TimingRecord [0..*] { @Subject { fr = "FR-31"; direction = "outputs"; exactField = "Timing and synchronization records"; provenance = "final_report/requirements.tex, FR-31 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : TimingRecord [0..*] { @Subject { fr = "FR-31"; direction = "outputs"; exactField = "checked alignments"; provenance = "final_report/requirements.tex, FR-31 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : TimingRecord [0..*] { @Subject { fr = "FR-31"; direction = "outputs"; exactField = "timing gaps"; provenance = "final_report/requirements.tex, FR-31 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : TimingRecord [0..*] { @Subject { fr = "FR-31"; direction = "outputs"; exactField = "limit findings"; provenance = "final_report/requirements.tex, FR-31 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR31 { in subjects : FR31Inputs; out products : FR31Outputs; doc /* Complete FR-31 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR32Inputs :> EngineeringArtifact {
        ref item field01 : ReferenceData [0..*] { @Subject { fr = "FR-32"; direction = "inputs"; exactField = "Exchanged/simulated/reference histories"; provenance = "final_report/requirements.tex, FR-32 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : SimulationCouplingProfile [0..*] { @Subject { fr = "FR-32"; direction = "inputs"; exactField = "entity/channel mappings"; provenance = "final_report/requirements.tex, FR-32 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : Quantity [0..*] { @Subject { fr = "FR-32"; direction = "inputs"; exactField = "quantity/unit definitions"; provenance = "final_report/requirements.tex, FR-32 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : TimingRecord [0..*] { @Subject { fr = "FR-32"; direction = "inputs"; exactField = "timing metadata"; provenance = "final_report/requirements.tex, FR-32 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : RuleRecord [0..*] { @Subject { fr = "FR-32"; direction = "inputs"; exactField = "validity rules"; provenance = "final_report/requirements.tex, FR-32 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR32Outputs :> EngineeringArtifact {
        ref item field01 : MappingFindingRecord [0..*] { @Subject { fr = "FR-32"; direction = "outputs"; exactField = "Admission/quality findings"; provenance = "final_report/requirements.tex, FR-32 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReferenceData [0..*] { @Subject { fr = "FR-32"; direction = "outputs"; exactField = "preserved raw histories"; provenance = "final_report/requirements.tex, FR-32 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-32"; direction = "outputs"; exactField = "invalid/missing/inactive status"; provenance = "final_report/requirements.tex, FR-32 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : ReferenceData [0..*] { @Subject { fr = "FR-32"; direction = "outputs"; exactField = "processing masks"; provenance = "final_report/requirements.tex, FR-32 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR32 { in subjects : FR32Inputs; out products : FR32Outputs; doc /* Complete FR-32 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR33Inputs :> EngineeringArtifact {
        ref item field01 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-33"; direction = "inputs"; exactField = "Modeled EPS endpoint/port interfaces"; provenance = "final_report/requirements.tex, FR-33 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-33"; direction = "inputs"; exactField = "command, telemetry, event and parameter definitions"; provenance = "final_report/requirements.tex, FR-33 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR33Outputs :> EngineeringArtifact {
        ref item field01 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-33"; direction = "outputs"; exactField = "Revision-linked EPS interface and ground-definition specifications"; provenance = "final_report/requirements.tex, FR-33 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR33 { in subjects : FR33Inputs; out products : FR33Outputs; doc /* Complete FR-33 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR34Inputs :> EngineeringArtifact {
        ref item field01 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-34"; direction = "inputs"; exactField = "EPS interface specification"; provenance = "final_report/requirements.tex, FR-34 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-34"; direction = "inputs"; exactField = "software component/instance ownership and connectivity"; provenance = "final_report/requirements.tex, FR-34 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-34"; direction = "inputs"; exactField = "required F Prime profile"; provenance = "final_report/requirements.tex, FR-34 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : EnvironmentRecord [0..*] { @Subject { fr = "FR-34"; direction = "inputs"; exactField = "supported representation/tool versions"; provenance = "final_report/requirements.tex, FR-34 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR34Outputs :> EngineeringArtifact {
        ref item field01 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-34"; direction = "outputs"; exactField = "Checked F Prime mappings and definitions"; provenance = "final_report/requirements.tex, FR-34 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MappingFindingRecord [0..*] { @Subject { fr = "FR-34"; direction = "outputs"; exactField = "compatibility findings"; provenance = "final_report/requirements.tex, FR-34 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : MappingFindingRecord [0..*] { @Subject { fr = "FR-34"; direction = "outputs"; exactField = "unsupported/lossy-translation records"; provenance = "final_report/requirements.tex, FR-34 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR34 { in subjects : FR34Inputs; out products : FR34Outputs; doc /* Complete FR-34 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR35Inputs :> EngineeringArtifact {
        ref item field01 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-35"; direction = "inputs"; exactField = "Modeled command/control behavior"; provenance = "final_report/requirements.tex, FR-35 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : RequirementRecord [0..*] { @Subject { fr = "FR-35"; direction = "inputs"; exactField = "control/interface requirements"; provenance = "final_report/requirements.tex, FR-35 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR35Outputs :> EngineeringArtifact {
        ref item field01 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-35"; direction = "outputs"; exactField = "Checked behavior specifications"; provenance = "final_report/requirements.tex, FR-35 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReviewFinding [0..*] { @Subject { fr = "FR-35"; direction = "outputs"; exactField = "discrepancy findings"; provenance = "final_report/requirements.tex, FR-35 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR35 { in subjects : FR35Inputs; out products : FR35Outputs; doc /* Complete FR-35 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR36Inputs :> EngineeringArtifact {
        ref item field01 : DetailedDesignAuthorization [0..*] { @Subject { fr = "FR-36"; direction = "inputs"; exactField = "Current authorized design/interface release"; provenance = "final_report/requirements.tex, FR-36 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ScopeRecord [0..*] { @Subject { fr = "FR-36"; direction = "inputs"; exactField = "declared software scope"; provenance = "final_report/requirements.tex, FR-36 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EPSInterfaceSpecification [0..*] { @Subject { fr = "FR-36"; direction = "inputs"; exactField = "F Prime mappings"; provenance = "final_report/requirements.tex, FR-36 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : EnvironmentRecord [0..*] { @Subject { fr = "FR-36"; direction = "inputs"; exactField = "host/toolchain/dependency configuration"; provenance = "final_report/requirements.tex, FR-36 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : CodingResponse [0..*] { @Subject { fr = "FR-36"; direction = "inputs"; exactField = "returned tool responses"; provenance = "final_report/requirements.tex, FR-36 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR36Outputs :> EngineeringArtifact {
        ref item field01 : CodingRequest [0..*] { @Subject { fr = "FR-36"; direction = "outputs"; exactField = "Authorized coding/build requests"; provenance = "final_report/requirements.tex, FR-36 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : HostSoftwareProduct [0..*] { @Subject { fr = "FR-36"; direction = "outputs"; exactField = "retained source/build products"; provenance = "final_report/requirements.tex, FR-36 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EnvironmentRecord [0..*] { @Subject { fr = "FR-36"; direction = "outputs"; exactField = "exact configuration records"; provenance = "final_report/requirements.tex, FR-36 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-36"; direction = "outputs"; exactField = "logs"; provenance = "final_report/requirements.tex, FR-36 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : ExecutionStatusRecord [0..*] { @Subject { fr = "FR-36"; direction = "outputs"; exactField = "failures"; provenance = "final_report/requirements.tex, FR-36 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR36 { in subjects : FR36Inputs; out products : FR36Outputs; doc /* Complete FR-36 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR37Inputs :> EngineeringArtifact {
        ref item field01 : PhaseBaseline [0..*] { @Subject { fr = "FR-37"; direction = "inputs"; exactField = "Controlled EPS baseline"; provenance = "final_report/requirements.tex, FR-37 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ViewSelection [0..*] { @Subject { fr = "FR-37"; direction = "inputs"; exactField = "view selection"; provenance = "final_report/requirements.tex, FR-37 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR37Outputs :> EngineeringArtifact {
        ref item field01 : ReviewPackage [0..*] { @Subject { fr = "FR-37"; direction = "outputs"; exactField = "Readable baseline-linked engineering views"; provenance = "final_report/requirements.tex, FR-37 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR37 { in subjects : FR37Inputs; out products : FR37Outputs; doc /* Complete FR-37 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR38Inputs :> EngineeringArtifact {
        ref item field01 : PhaseBaseline [0..*] { @Subject { fr = "FR-38"; direction = "inputs"; exactField = "Phase baseline"; provenance = "final_report/requirements.tex, FR-38 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReviewCriterionRecord [0..*] { @Subject { fr = "FR-38"; direction = "inputs"; exactField = "review criteria"; provenance = "final_report/requirements.tex, FR-38 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EvidenceAssessment [0..*] { @Subject { fr = "FR-38"; direction = "inputs"; exactField = "applicable records/evidence"; provenance = "final_report/requirements.tex, FR-38 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR38Outputs :> EngineeringArtifact {
        ref item field01 : ReviewPackage [0..*] { @Subject { fr = "FR-38"; direction = "outputs"; exactField = "Prepared review package with coverage, limits and findings"; provenance = "final_report/requirements.tex, FR-38 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR38 { in subjects : FR38Inputs; out products : FR38Outputs; doc /* Complete FR-38 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR39Inputs :> EngineeringArtifact {
        ref item field01 : GuidanceRequest [0..*] { @Subject { fr = "FR-39"; direction = "inputs"; exactField = "Phase"; provenance = "final_report/requirements.tex, FR-39 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : MaturityRecord [0..*] { @Subject { fr = "FR-39"; direction = "inputs"; exactField = "maturity"; provenance = "final_report/requirements.tex, FR-39 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : EngineeringArtifact [0..*] { @Subject { fr = "FR-39"; direction = "inputs"; exactField = "dependencies"; provenance = "final_report/requirements.tex, FR-39 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field04 : ReviewFinding [0..*] { @Subject { fr = "FR-39"; direction = "inputs"; exactField = "findings"; provenance = "final_report/requirements.tex, FR-39 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field05 : ReviewCriterionRecord [0..*] { @Subject { fr = "FR-39"; direction = "inputs"; exactField = "review criteria"; provenance = "final_report/requirements.tex, FR-39 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR39Outputs :> EngineeringArtifact {
        ref item field01 : AssistanceReport [0..*] { @Subject { fr = "FR-39"; direction = "outputs"; exactField = "Proposed activities/reassessments"; provenance = "final_report/requirements.tex, FR-39 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : AssistanceReport [0..*] { @Subject { fr = "FR-39"; direction = "outputs"; exactField = "prerequisites"; provenance = "final_report/requirements.tex, FR-39 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : AssistanceReport [0..*] { @Subject { fr = "FR-39"; direction = "outputs"; exactField = "rationale"; provenance = "final_report/requirements.tex, FR-39 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR39 { in subjects : FR39Inputs; out products : FR39Outputs; doc /* Complete FR-39 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR41Inputs :> EngineeringArtifact {
        ref item field01 : GuidanceRequest [0..*] { @Subject { fr = "FR-41"; direction = "inputs"; exactField = "Assistance trigger"; provenance = "final_report/requirements.tex, FR-41 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ContextRevision [0..*] { @Subject { fr = "FR-41"; direction = "inputs"; exactField = "current context"; provenance = "final_report/requirements.tex, FR-41 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ResourceRecord [0..*] { @Subject { fr = "FR-41"; direction = "inputs"; exactField = "response limits"; provenance = "final_report/requirements.tex, FR-41 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR41Outputs :> EngineeringArtifact {
        ref item field01 : AssistanceWork [0..*] { @Subject { fr = "FR-41"; direction = "outputs"; exactField = "Acknowledgement"; provenance = "final_report/requirements.tex, FR-41 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : AssistanceReport [0..*] { @Subject { fr = "FR-41"; direction = "outputs"; exactField = "guidance/status"; provenance = "final_report/requirements.tex, FR-41 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : TimingRecord [0..*] { @Subject { fr = "FR-41"; direction = "outputs"; exactField = "response timestamps"; provenance = "final_report/requirements.tex, FR-41 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR41 { in subjects : FR41Inputs; out products : FR41Outputs; doc /* Complete FR-41 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    item def FR42Inputs :> EngineeringArtifact {
        ref item field01 : PhaseBaseline [0..*] { @Subject { fr = "FR-42"; direction = "inputs"; exactField = "Identified baseline"; provenance = "final_report/requirements.tex, FR-42 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReviewCriterionRecord [0..*] { @Subject { fr = "FR-42"; direction = "inputs"; exactField = "criteria"; provenance = "final_report/requirements.tex, FR-42 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : TechnicalReviewDecision [0..*] { @Subject { fr = "FR-42"; direction = "inputs"; exactField = "designated-authority review decision"; provenance = "final_report/requirements.tex, FR-42 inputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    item def FR42Outputs :> EngineeringArtifact {
        ref item field01 : ReviewWork [0..*] { @Subject { fr = "FR-42"; direction = "outputs"; exactField = "Recorded disposition"; provenance = "final_report/requirements.tex, FR-42 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field02 : ReviewWork [0..*] { @Subject { fr = "FR-42"; direction = "outputs"; exactField = "progression status"; provenance = "final_report/requirements.tex, FR-42 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
        ref item field03 : ReviewWork [0..*] { @Subject { fr = "FR-42"; direction = "outputs"; exactField = "closure obligations"; provenance = "final_report/requirements.tex, FR-42 outputs; exact source/subject revisions inherited from EngineeringArtifact"; } }
    }
    action def ContractFR42 { in subjects : FR42Inputs; out products : FR42Outputs; doc /* Complete FR-42 operation subject union. Real admission and authority routes are in LogicalRealization. This signature alone grants no application, execution or review permission. */ }
    port def L01Subjects {
        in item fr01Inputs : FR01Inputs;
        out item fr01Outputs : FR01Outputs;
        in item fr02Inputs : FR02Inputs;
        out item fr02Outputs : FR02Outputs;
        in item fr03Inputs : FR03Inputs;
        out item fr03Outputs : FR03Outputs;
        in item fr04Inputs : FR04Inputs;
        out item fr04Outputs : FR04Outputs;
        in item fr17Inputs : FR17Inputs;
        out item fr17Outputs : FR17Outputs;
        in item fr29Inputs : FR29Inputs;
        out item fr29Outputs : FR29Outputs;
        in item fr39Inputs : FR39Inputs;
        out item fr39Outputs : FR39Outputs;
        in item fr41Inputs : FR41Inputs;
        out item fr41Outputs : FR41Outputs;
    }
    action def RequestApplicableSource { in request : GuidanceRequest [0..1]; out query : SourceQuery; doc /* FR-03 available-input and cited-source eligibility, with FR-13 unknown sourced technical properties. Request only a missing applicable source/property identified by these operations. No general search capability or assertion of truth is required. */ }
    part def <'L01'> RequirementsAssistance {
        port io : L01Subjects;
        perform action sourceQuery : RequestApplicableSource;
        perform action acknowledge : AcknowledgeAssistance;
        perform action checkDraft : CheckDraft;
        perform action recommend : RecommendMethods;
        perform action dispose : DisposeSuggestion;
        perform action reassess : ReassessAssistance;
        perform action retainRequirements : RetainRequirements;
        perform action deriveAllocate : DeriveAllocate;
        perform action traceLinks : TraceLinks;
        perform action presentAdvice : PresentAdvice;
        perform action contractFR01 : ContractFR01;
        bind io.fr01Inputs = contractFR01.subjects;
        bind contractFR01.products = io.fr01Outputs;
        perform action contractFR02 : ContractFR02;
        bind io.fr02Inputs = contractFR02.subjects;
        bind contractFR02.products = io.fr02Outputs;
        perform action contractFR03 : ContractFR03;
        bind io.fr03Inputs = contractFR03.subjects;
        bind contractFR03.products = io.fr03Outputs;
        perform action contractFR04 : ContractFR04;
        bind io.fr04Inputs = contractFR04.subjects;
        bind contractFR04.products = io.fr04Outputs;
        perform action contractFR17 : ContractFR17;
        bind io.fr17Inputs = contractFR17.subjects;
        bind contractFR17.products = io.fr17Outputs;
        perform action contractFR29 : ContractFR29;
        bind io.fr29Inputs = contractFR29.subjects;
        bind contractFR29.products = io.fr29Outputs;
        perform action contractFR39 : ContractFR39;
        bind io.fr39Inputs = contractFR39.subjects;
        bind contractFR39.products = io.fr39Outputs;
        perform action contractFR41 : ContractFR41;
        bind io.fr41Inputs = contractFR41.subjects;
        bind contractFR41.products = io.fr41Outputs;
    }
    port def L02Subjects {
        in item fr13Inputs : FR13Inputs;
        out item fr13Outputs : FR13Outputs;
        in item fr14Inputs : FR14Inputs;
        out item fr14Outputs : FR14Outputs;
        in item fr15Inputs : FR15Inputs;
        out item fr15Outputs : FR15Outputs;
        in item fr20Inputs : FR20Inputs;
        out item fr20Outputs : FR20Outputs;
        in item fr25Inputs : FR25Inputs;
        out item fr25Outputs : FR25Outputs;
        in item fr33Inputs : FR33Inputs;
        out item fr33Outputs : FR33Outputs;
        in item fr35Inputs : FR35Inputs;
        out item fr35Outputs : FR35Outputs;
    }
    part def <'L02'> MissionDesign {
        port io : L02Subjects;
        perform action defineDesign : DefineDesign;
        perform action budgetSize : BudgetSize;
        perform action compareDesigns : CompareDesigns;
        perform action defineInterfaces : DefineInterfaces;
        perform action configureConcept : ConfigureConcept;
        perform action contractFR13 : ContractFR13;
        bind io.fr13Inputs = contractFR13.subjects;
        bind contractFR13.products = io.fr13Outputs;
        perform action contractFR14 : ContractFR14;
        bind io.fr14Inputs = contractFR14.subjects;
        bind contractFR14.products = io.fr14Outputs;
        perform action contractFR15 : ContractFR15;
        bind io.fr15Inputs = contractFR15.subjects;
        bind contractFR15.products = io.fr15Outputs;
        perform action contractFR20 : ContractFR20;
        bind io.fr20Inputs = contractFR20.subjects;
        bind contractFR20.products = io.fr20Outputs;
        perform action contractFR25 : ContractFR25;
        bind io.fr25Inputs = contractFR25.subjects;
        bind contractFR25.products = io.fr25Outputs;
        perform action contractFR33 : ContractFR33;
        bind io.fr33Inputs = contractFR33.subjects;
        bind contractFR33.products = io.fr33Outputs;
        perform action contractFR35 : ContractFR35;
        bind io.fr35Inputs = contractFR35.subjects;
        bind contractFR35.products = io.fr35Outputs;
    }
    port def L03Subjects {
        in item fr10Inputs : FR10Inputs;
        out item fr10Outputs : FR10Outputs;
        in item fr16Inputs : FR16Inputs;
        out item fr16Outputs : FR16Outputs;
        in item fr18Inputs : FR18Inputs;
        out item fr18Outputs : FR18Outputs;
        in item fr19Inputs : FR19Inputs;
        out item fr19Outputs : FR19Outputs;
        in item fr23Inputs : FR23Inputs;
        out item fr23Outputs : FR23Outputs;
        in item fr24Inputs : FR24Inputs;
        out item fr24Outputs : FR24Outputs;
        in item fr26Inputs : FR26Inputs;
        out item fr26Outputs : FR26Outputs;
        in item fr27Inputs : FR27Inputs;
        out item fr27Outputs : FR27Outputs;
        in item fr34Inputs : FR34Inputs;
        out item fr34Outputs : FR34Outputs;
        in item fr36Inputs : FR36Inputs;
        out item fr36Outputs : FR36Outputs;
    }
    part def <'L03'> SimulationIntegration {
        port io : L03Subjects;
        port p03 : AnalysisPort;
        port p04 : HostSoftwarePort;
        perform action planAnalysis : PlanAnalysis;
        perform action planMIL : PlanMIL;
        perform action coordinateCoding : CoordinateCoding;
        perform action compareMILSil : CompareMILSil;
        perform action replay : ReplayRun;
        perform action planRepeat : PlanRepeatedAssessment;
        perform action mapFPrime : MapFPrime;
        perform action contractFR10 : ContractFR10;
        bind io.fr10Inputs = contractFR10.subjects;
        bind contractFR10.products = io.fr10Outputs;
        perform action contractFR16 : ContractFR16;
        bind io.fr16Inputs = contractFR16.subjects;
        bind contractFR16.products = io.fr16Outputs;
        perform action contractFR18 : ContractFR18;
        bind io.fr18Inputs = contractFR18.subjects;
        bind contractFR18.products = io.fr18Outputs;
        perform action contractFR19 : ContractFR19;
        bind io.fr19Inputs = contractFR19.subjects;
        bind contractFR19.products = io.fr19Outputs;
        perform action contractFR23 : ContractFR23;
        bind io.fr23Inputs = contractFR23.subjects;
        bind contractFR23.products = io.fr23Outputs;
        perform action contractFR24 : ContractFR24;
        bind io.fr24Inputs = contractFR24.subjects;
        bind contractFR24.products = io.fr24Outputs;
        perform action contractFR26 : ContractFR26;
        bind io.fr26Inputs = contractFR26.subjects;
        bind contractFR26.products = io.fr26Outputs;
        perform action contractFR27 : ContractFR27;
        bind io.fr27Inputs = contractFR27.subjects;
        bind contractFR27.products = io.fr27Outputs;
        perform action contractFR34 : ContractFR34;
        bind io.fr34Inputs = contractFR34.subjects;
        bind contractFR34.products = io.fr34Outputs;
        perform action contractFR36 : ContractFR36;
        bind io.fr36Inputs = contractFR36.subjects;
        bind contractFR36.products = io.fr36Outputs;
    }
    port def L04Subjects {
        in item fr21Inputs : FR21Inputs;
        out item fr21Outputs : FR21Outputs;
        in item fr22Inputs : FR22Inputs;
        out item fr22Outputs : FR22Outputs;
        in item fr31Inputs : FR31Inputs;
        out item fr31Outputs : FR31Outputs;
        in item fr32Inputs : FR32Inputs;
        out item fr32Outputs : FR32Outputs;
    }
    part def <'L04'> ModelCredibility {
        port io : L04Subjects;
        perform action assessModel : AssessModel;
        perform action proposeCalibration : ProposeCalibration;
        perform action checkReferenceData : CheckReferenceData;
        perform action contractFR21 : ContractFR21;
        bind io.fr21Inputs = contractFR21.subjects;
        bind contractFR21.products = io.fr21Outputs;
        perform action contractFR22 : ContractFR22;
        bind io.fr22Inputs = contractFR22.subjects;
        bind contractFR22.products = io.fr22Outputs;
        perform action contractFR31 : ContractFR31;
        bind io.fr31Inputs = contractFR31.subjects;
        bind contractFR31.products = io.fr31Outputs;
        perform action contractFR32 : ContractFR32;
        bind io.fr32Inputs = contractFR32.subjects;
        bind contractFR32.products = io.fr32Outputs;
    }
    port def L05Subjects {
        in item fr11Inputs : FR11Inputs;
        out item fr11Outputs : FR11Outputs;
        in item fr28Inputs : FR28Inputs;
        out item fr28Outputs : FR28Outputs;
        in item fr37Inputs : FR37Inputs;
        out item fr37Outputs : FR37Outputs;
        in item fr38Inputs : FR38Inputs;
        out item fr38Outputs : FR38Outputs;
        in item fr42Inputs : FR42Inputs;
        out item fr42Outputs : FR42Outputs;
    }
    part def <'L05'> EvidenceReview {
        port io : L05Subjects;
        port p06 : TechnicalReviewPort;
        perform action planAssessment : PlanAssessment;
        perform action assessProduct : AssessProduct;
        perform action prepareReview : PrepareReviewPackage;
        perform action checkReviewDecision : CheckReviewDecision;
        perform action recordReview : RecordReviewDecision;
        perform action makeViews : MakeViews;
        perform action presentAssessment : PresentAssessment;
        perform action contractFR11 : ContractFR11;
        bind io.fr11Inputs = contractFR11.subjects;
        bind contractFR11.products = io.fr11Outputs;
        perform action contractFR28 : ContractFR28;
        bind io.fr28Inputs = contractFR28.subjects;
        bind contractFR28.products = io.fr28Outputs;
        perform action contractFR37 : ContractFR37;
        bind io.fr37Inputs = contractFR37.subjects;
        bind contractFR37.products = io.fr37Outputs;
        perform action contractFR38 : ContractFR38;
        bind io.fr38Inputs = contractFR38.subjects;
        bind contractFR38.products = io.fr38Outputs;
        perform action contractFR42 : ContractFR42;
        bind io.fr42Inputs = contractFR42.subjects;
        bind contractFR42.products = io.fr42Outputs;
        bind io.fr37Inputs.field02 = makeViews.selection;
        exhibit state reviewState : ScenarioViews::BaselineControl;
    }
    port def L06Subjects {
        in item fr05Inputs : FR05Inputs;
        out item fr05Outputs : FR05Outputs;
        in item fr06Inputs : FR06Inputs;
        out item fr06Outputs : FR06Outputs;
        in item fr07Inputs : FR07Inputs;
        out item fr07Outputs : FR07Outputs;
        in item fr08Inputs : FR08Inputs;
        out item fr08Outputs : FR08Outputs;
        in item fr09Inputs : FR09Inputs;
        out item fr09Outputs : FR09Outputs;
        in item fr30Inputs : FR30Inputs;
        out item fr30Outputs : FR30Outputs;
    }
    part def <'L06'> ConfigurationExchange {
        port io : L06Subjects;
        perform action captureContext : CaptureContext;
        perform action checkCurrency : CheckCurrency;
        perform action invalidate : InvalidateAndReassess;
        perform action checkChange : CheckEngineeringChange;
        perform action successor : RetainSuccessor;
        perform action preserveRun : PreserveRun;
        perform action checkDesignAuthorization : CheckDetailedDesignAuthorization;
        perform action retrieveBaseline : RetrieveBaseline;
        perform action retainReview : RetainReviewedBaseline;
        perform action prepareReplay : PrepareReplay;
        perform action preserveRecord : PreserveRecord;
        perform action checkSelection : CheckEngineerSelection;
        perform action checkResultContext : CheckResultContext;
        perform action prepareCalibrationChange : PrepareCalibrationChange;
        perform action checkTransfer : CheckTransfer;
        perform action checkEngineeringTransfer : CheckTransfer;
        perform action checkSourceTransfer : CheckTransfer;
        perform action contractFR05 : ContractFR05;
        bind io.fr05Inputs = contractFR05.subjects;
        bind contractFR05.products = io.fr05Outputs;
        perform action contractFR06 : ContractFR06;
        bind io.fr06Inputs = contractFR06.subjects;
        bind contractFR06.products = io.fr06Outputs;
        perform action contractFR07 : ContractFR07;
        bind io.fr07Inputs = contractFR07.subjects;
        bind contractFR07.products = io.fr07Outputs;
        perform action contractFR08 : ContractFR08;
        bind io.fr08Inputs = contractFR08.subjects;
        bind contractFR08.products = io.fr08Outputs;
        perform action contractFR09 : ContractFR09;
        bind io.fr09Inputs = contractFR09.subjects;
        bind contractFR09.products = io.fr09Outputs;
        perform action contractFR30 : ContractFR30;
        bind io.fr30Inputs = contractFR30.subjects;
        bind contractFR30.products = io.fr30Outputs;
        exhibit state assistanceCurrency : ScenarioViews::GuidanceControl;
        ref item responseLimits : FrameworkRequirements::PerformanceMeasure = FrameworkRequirements::MOP_FR41;
        ref item impactMeasures : FrameworkRequirements::PerformanceMeasure = FrameworkRequirements::MOP_FR05;
    }
    item def RequirementsAllocationsExchange :> EngineeringArtifact {
        ref item field001 : RequirementRecord [0..*] { @ExchangeField { sourceFR = "FR-01"; sourceOutput = "Retained requirement records"; targetFR = "FR-14"; targetInput = "common mission/requirements"; mapping = "Extract retained common requirement basis"; } }
        ref item field002 : RequirementAllocation [0..*] { @ExchangeField { sourceFR = "FR-17"; sourceOutput = "Proposed EPS/component allocations"; targetFR = "FR-15"; targetInput = "allocations"; mapping = "Proposed EPS/component allocations inform design proposals"; } }
        ref item field003 : RequirementRecord [0..*] { @ExchangeField { sourceFR = "FR-01"; sourceOutput = "Retained requirement records"; targetFR = "FR-35"; targetInput = "control/interface requirements"; mapping = "Select control/interface requirements"; } }
    }
    action def Map_requirementsAllocations_001 { in source : RequirementRecord [0..*]; out target : CommonDesignBasis [0..*]; doc /* Extract retained common requirement basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_requirementsAllocations_002 { in source : RequirementAllocation [0..*]; out target : RequirementAllocation [0..*]; doc /* Proposed EPS/component allocations inform design proposals. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_requirementsAllocations_003 { in source : RequirementRecord [0..*]; out target : RequirementRecord [0..*]; doc /* Select control/interface requirements. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def ScenariosDesignQuantitiesExchange :> EngineeringArtifact {
        ref item field001 : MissionDefinition [0..*] { @ExchangeField { sourceFR = "FR-25"; sourceOutput = "Revision-linked mission and ConOps records"; targetFR = "FR-17"; targetInput = "scenarios"; mapping = "Select mission/ConOps scenarios"; } }
        ref item field002 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-20"; sourceOutput = "Power/energy budgets"; targetFR = "FR-17"; targetInput = "quantities"; mapping = "Select budget/sizing design quantities"; } }
        ref item field003 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-13"; sourceOutput = "Mass and volume estimates with uncertainty and unknowns"; targetFR = "FR-17"; targetInput = "quantities"; mapping = "Select sourced mass/volume quantities"; } }
        ref item field004 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-13"; sourceOutput = "Mass and volume estimates with uncertainty and unknowns"; targetFR = "FR-03"; targetInput = "inputs"; mapping = "Available design quantities and unknowns inform eligibility"; } }
        ref item field005 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-20"; sourceOutput = "Power/energy budgets"; targetFR = "FR-03"; targetInput = "inputs"; mapping = "Available budgets inform method applicability"; } }
    }
    action def Map_scenariosDesignQuantities_001 { in source : MissionDefinition [0..*]; out target : MissionDefinition [0..*]; doc /* Select mission/ConOps scenarios. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_scenariosDesignQuantities_002 { in source : DesignStudy [0..*]; out target : DesignStudy [0..*]; doc /* Select budget/sizing design quantities. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_scenariosDesignQuantities_003 { in source : DesignStudy [0..*]; out target : DesignStudy [0..*]; doc /* Select sourced mass/volume quantities. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_scenariosDesignQuantities_004 { in source : DesignStudy [0..*]; out target : EngineeringArtifact [0..*]; doc /* Available design quantities and unknowns inform eligibility. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_scenariosDesignQuantities_005 { in source : DesignStudy [0..*]; out target : EngineeringArtifact [0..*]; doc /* Available budgets inform method applicability. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def ModelsScenariosExchange :> EngineeringArtifact {
        ref item field001 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-16"; targetInput = "EPS models"; mapping = "Configured EPS models"; } }
        ref item field002 : MissionDefinition [0..*] { @ExchangeField { sourceFR = "FR-25"; sourceOutput = "Revision-linked mission and ConOps records"; targetFR = "FR-16"; targetInput = "Whole-CUBICS mission/subsystem load and mode histories"; mapping = "Mission modes/load schedules projected to scenario histories"; } }
        ref item field003 : MissionDefinition [0..*] { @ExchangeField { sourceFR = "FR-25"; sourceOutput = "Revision-linked mission and ConOps records"; targetFR = "FR-16"; targetInput = "orbit/attitude/illumination/thermal histories"; mapping = "Mission orbit/attitude/environment projected to histories"; } }
        ref item field004 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-18"; targetInput = "Component/design model revisions"; mapping = "Exact component/design model revisions"; } }
        ref item field005 : MissionDefinition [0..*] { @ExchangeField { sourceFR = "FR-25"; sourceOutput = "Revision-linked mission and ConOps records"; targetFR = "FR-18"; targetInput = "whole-CUBICS model/scenario revisions"; mapping = "Exact whole-CUBICS mission scenario basis"; } }
        ref item field006 : MissionDefinition [0..*] { @ExchangeField { sourceFR = "FR-25"; sourceOutput = "Revision-linked mission and ConOps records"; targetFR = "FR-19"; targetInput = "mission scenarios"; mapping = "Mission scenario basis"; } }
        ref item field007 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-19"; targetInput = "Controller/plant models"; mapping = "Controller/plant model basis"; } }
        ref item field008 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-26"; targetInput = "EPS requirements"; mapping = "Design requirement allocations"; } }
        ref item field009 : MissionDefinition [0..*] { @ExchangeField { sourceFR = "FR-25"; sourceOutput = "Revision-linked mission and ConOps records"; targetFR = "FR-26"; targetInput = "ConOps"; mapping = "RAM ConOps basis"; } }
        ref item field010 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-27"; targetInput = "Functions"; mapping = "Function allocation basis"; } }
        ref item field011 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-27"; targetInput = "components"; mapping = "Component occurrence basis"; } }
        ref item field012 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-33"; sourceOutput = "Revision-linked EPS interface and ground-definition specifications"; targetFR = "FR-34"; targetInput = "EPS interface specification"; mapping = "EPS interface specification"; } }
        ref item field013 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-35"; sourceOutput = "Checked behavior specifications"; targetFR = "FR-34"; targetInput = "EPS interface specification"; mapping = "Checked behavior supplements EPS interface specification"; } }
        ref item field014 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-35"; sourceOutput = "Checked behavior specifications"; targetFR = "FR-19"; targetInput = "Controller/plant models"; mapping = "Modeled controller behavior specification"; } }
        ref item field015 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-33"; sourceOutput = "Revision-linked EPS interface and ground-definition specifications"; targetFR = "FR-18"; targetInput = "directed mappings"; mapping = "Endpoint direction/quantity/unit mapping basis"; } }
        ref item field016 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-33"; sourceOutput = "Revision-linked EPS interface and ground-definition specifications"; targetFR = "FR-36"; targetInput = "Current authorized design/interface release"; mapping = "Interface identity only. Release requires L06 exact authorization check"; } }
    }
    action def Map_modelsScenarios_001 { in source : DesignConfiguration [0..*]; out target : DesignConfiguration [0..*]; doc /* Configured EPS models. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_002 { in source : MissionDefinition [0..*]; out target : ReferenceData [0..*]; doc /* Mission modes/load schedules projected to scenario histories. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_003 { in source : MissionDefinition [0..*]; out target : ReferenceData [0..*]; doc /* Mission orbit/attitude/environment projected to histories. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_004 { in source : DesignConfiguration [0..*]; out target : DesignConfiguration [0..*]; doc /* Exact component/design model revisions. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_005 { in source : MissionDefinition [0..*]; out target : SimulationCouplingProfile [0..*]; doc /* Exact whole-CUBICS mission scenario basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_006 { in source : MissionDefinition [0..*]; out target : MissionDefinition [0..*]; doc /* Mission scenario basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_007 { in source : DesignConfiguration [0..*]; out target : DesignConfiguration [0..*]; doc /* Controller/plant model basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_008 { in source : DesignConfiguration [0..*]; out target : RequirementRecord [0..*]; doc /* Design requirement allocations. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_009 { in source : MissionDefinition [0..*]; out target : MissionDefinition [0..*]; doc /* RAM ConOps basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_010 { in source : DesignConfiguration [0..*]; out target : DesignConfiguration [0..*]; doc /* Function allocation basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_011 { in source : DesignConfiguration [0..*]; out target : DesignConfiguration [0..*]; doc /* Component occurrence basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_012 { in source : EPSInterfaceSpecification [0..*]; out target : EPSInterfaceSpecification [0..*]; doc /* EPS interface specification. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_013 { in source : EPSInterfaceSpecification [0..*]; out target : EPSInterfaceSpecification [0..*]; doc /* Checked behavior supplements EPS interface specification. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_014 { in source : EPSInterfaceSpecification [0..*]; out target : DesignConfiguration [0..*]; doc /* Modeled controller behavior specification. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_015 { in source : EPSInterfaceSpecification [0..*]; out target : SimulationCouplingProfile [0..*]; doc /* Endpoint direction/quantity/unit mapping basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelsScenarios_016 { in source : EPSInterfaceSpecification [0..*]; out target : DetailedDesignAuthorization [0..*]; doc /* Interface identity only. Release requires L06 exact authorization check. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def DesignStudyResultsExchange :> EngineeringArtifact {
        ref item field001 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "Power/energy balance"; targetFR = "FR-14"; targetInput = "EPS alternatives"; mapping = "Alternative temporal balance measures"; } }
        ref item field002 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "bus quantities"; targetFR = "FR-14"; targetInput = "EPS alternatives"; mapping = "Bus measures"; } }
        ref item field003 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "battery state histories"; targetFR = "FR-14"; targetInput = "EPS alternatives"; mapping = "Battery histories inform alternatives"; } }
        ref item field004 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-27"; sourceOutput = "RAM representations/results with uncertainty and missing data"; targetFR = "FR-14"; targetInput = "EPS alternatives"; mapping = "RAM risk/uncertainty evidence"; } }
        ref item field005 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "transfer limitations"; targetFR = "FR-14"; targetInput = "EPS alternatives"; mapping = "Transfer limitations bound trade applicability"; } }
        ref item field006 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "Power/energy balance"; targetFR = "FR-15"; targetInput = "Design parameters"; mapping = "Inform proposed parameter revision only. FR06 authority is required to apply"; } }
    }
    action def Map_designStudyResults_001 { in source : AnalysisResult [0..*]; out target : DesignConfiguration [0..*]; doc /* Alternative temporal balance measures. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designStudyResults_002 { in source : AnalysisResult [0..*]; out target : DesignConfiguration [0..*]; doc /* Bus measures. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designStudyResults_003 { in source : ReferenceData [0..*]; out target : DesignConfiguration [0..*]; doc /* Battery histories inform alternatives. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designStudyResults_004 { in source : AnalysisResult [0..*]; out target : DesignConfiguration [0..*]; doc /* RAM risk/uncertainty evidence. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designStudyResults_005 { in source : MappingFindingRecord [0..*]; out target : DesignConfiguration [0..*]; doc /* Transfer limitations bound trade applicability. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designStudyResults_006 { in source : AnalysisResult [0..*]; out target : DesignConfiguration [0..*]; doc /* Inform proposed parameter revision only. FR06 authority is required to apply. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def RunHistoriesExchange :> EngineeringArtifact {
        ref item field001 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "Power/energy balance"; targetFR = "FR-21"; targetInput = "Conclusions"; mapping = "Balance conclusion"; } }
        ref item field002 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "bus quantities"; targetFR = "FR-21"; targetInput = "credibility evidence"; mapping = "Bus numerical evidence"; } }
        ref item field003 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "battery state histories"; targetFR = "FR-32"; targetInput = "Exchanged/simulated/reference histories"; mapping = "Raw battery histories"; } }
        ref item field004 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "battery state histories"; targetFR = "FR-31"; targetInput = "Exchanged/simulated/reference histories"; mapping = "Raw sample/receipt timing accompanies battery histories"; } }
        ref item field005 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "EPS states/results returned to the same whole-CUBICS scenario"; targetFR = "FR-31"; targetInput = "Exchanged/simulated/reference histories"; mapping = "Coupled result time bases and delays"; } }
        ref item field006 : SoftwareRunResult [0..*] { @ExchangeField { sourceFR = "FR-24"; sourceOutput = "retained host responses"; targetFR = "FR-31"; targetInput = "Exchanged/simulated/reference histories"; mapping = "Host SIL response timing"; } }
        ref item field007 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "EPS states/results returned to the same whole-CUBICS scenario"; targetFR = "FR-21"; targetInput = "credibility evidence"; mapping = "Returned EPS results and same scenario identity"; } }
        ref item field008 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "transfer limitations"; targetFR = "FR-21"; targetInput = "model scope"; mapping = "Supported/unsupported scope limitations"; } }
        ref item field009 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-19"; sourceOutput = "retained stimuli/responses"; targetFR = "FR-32"; targetInput = "Exchanged/simulated/reference histories"; mapping = "Retained MIL stimuli/responses"; } }
        ref item field010 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-19"; sourceOutput = "criterion outcomes/failures"; targetFR = "FR-21"; targetInput = "Conclusions"; mapping = "MIL criterion conclusion"; } }
        ref item field011 : AnalysisPlan [0..*] { @ExchangeField { sourceFR = "FR-23"; sourceOutput = "Run configuration/runtime records"; targetFR = "FR-31"; targetInput = "sampling/exchange timing"; mapping = "As-run sample/exchange timing"; } }
        ref item field012 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-23"; sourceOutput = "numerical/resource findings"; targetFR = "FR-21"; targetInput = "credibility evidence"; mapping = "Runtime/numerical/resource findings"; } }
        ref item field013 : SoftwareRunResult [0..*] { @ExchangeField { sourceFR = "FR-24"; sourceOutput = "retained host responses"; targetFR = "FR-32"; targetInput = "Exchanged/simulated/reference histories"; mapping = "Retained host SIL responses"; } }
        ref item field014 : SoftwareAssessment [0..*] { @ExchangeField { sourceFR = "FR-24"; sourceOutput = "MIL/SIL differences with execution status and limits"; targetFR = "FR-21"; targetInput = "Conclusions"; mapping = "MIL/SIL differences with failed/partial status"; } }
        ref item field015 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-27"; sourceOutput = "RAM representations/results with uncertainty and missing data"; targetFR = "FR-21"; targetInput = "Conclusions"; mapping = "RAM conclusions with missing-data/uncertainty limits"; } }
    }
    action def Map_runHistories_001 { in source : AnalysisResult [0..*]; out target : ConclusionRecord [0..*]; doc /* Balance conclusion. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_002 { in source : AnalysisResult [0..*]; out target : EvidenceAssessment [0..*]; doc /* Bus numerical evidence. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_003 { in source : ReferenceData [0..*]; out target : ReferenceData [0..*]; doc /* Raw battery histories. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_004 { in source : ReferenceData [0..*]; out target : ReferenceData [0..*]; doc /* Raw sample/receipt timing accompanies battery histories. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_005 { in source : AnalysisResult [0..*]; out target : ReferenceData [0..*]; doc /* Coupled result time bases and delays. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_006 { in source : SoftwareRunResult [0..*]; out target : ReferenceData [0..*]; doc /* Host SIL response timing. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_007 { in source : AnalysisResult [0..*]; out target : EvidenceAssessment [0..*]; doc /* Returned EPS results and same scenario identity. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_008 { in source : MappingFindingRecord [0..*]; out target : ModelAssessment [0..*]; doc /* Supported/unsupported scope limitations. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_009 { in source : ReferenceData [0..*]; out target : ReferenceData [0..*]; doc /* Retained MIL stimuli/responses. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_010 { in source : AnalysisResult [0..*]; out target : ConclusionRecord [0..*]; doc /* MIL criterion conclusion. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_011 { in source : AnalysisPlan [0..*]; out target : TimingRecord [0..*]; doc /* As-run sample/exchange timing. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_012 { in source : MappingFindingRecord [0..*]; out target : EvidenceAssessment [0..*]; doc /* Runtime/numerical/resource findings. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_013 { in source : SoftwareRunResult [0..*]; out target : ReferenceData [0..*]; doc /* Retained host SIL responses. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_014 { in source : SoftwareAssessment [0..*]; out target : ConclusionRecord [0..*]; doc /* MIL/SIL differences with failed/partial status. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_runHistories_015 { in source : AnalysisResult [0..*]; out target : ConclusionRecord [0..*]; doc /* RAM conclusions with missing-data/uncertainty limits. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def ModelAssessmentExchange :> EngineeringArtifact {
        ref item field001 : ModelAssessment [0..*] { @ExchangeField { sourceFR = "FR-21"; sourceOutput = "Conclusion-linked credibility records"; targetFR = "FR-11"; targetInput = "Evidence/status"; mapping = "Conclusion-linked credibility and gaps"; } }
        ref item field002 : ModelAssessment [0..*] { @ExchangeField { sourceFR = "FR-21"; sourceOutput = "explicit gaps"; targetFR = "FR-11"; targetInput = "Evidence/status"; mapping = "Explicit independent-assessment and validity gaps"; } }
        ref item field003 : TimingRecord [0..*] { @ExchangeField { sourceFR = "FR-31"; sourceOutput = "Timing and synchronization records"; targetFR = "FR-28"; targetInput = "observations"; mapping = "Timing/synchronization observations"; } }
        ref item field004 : TimingRecord [0..*] { @ExchangeField { sourceFR = "FR-31"; sourceOutput = "timing gaps"; targetFR = "FR-11"; targetInput = "Evidence/status"; mapping = "Timing gaps are evidence gaps"; } }
        ref item field005 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-32"; sourceOutput = "Admission/quality findings"; targetFR = "FR-11"; targetInput = "Evidence/status"; mapping = "Quality/admission findings"; } }
        ref item field006 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-32"; sourceOutput = "preserved raw histories"; targetFR = "FR-28"; targetInput = "observations"; mapping = "Raw histories retained as observations"; } }
        ref item field007 : ExecutionStatusRecord [0..*] { @ExchangeField { sourceFR = "FR-32"; sourceOutput = "invalid/missing/inactive status"; targetFR = "FR-11"; targetInput = "Evidence/status"; mapping = "Invalid/missing/inactive status"; } }
        ref item field008 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-32"; sourceOutput = "processing masks"; targetFR = "FR-28"; targetInput = "observations"; mapping = "Processing masks accompany observations"; } }
        ref item field009 : ModelAssessment [0..*] { @ExchangeField { sourceFR = "FR-21"; sourceOutput = "Conclusion-linked credibility records"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Model limits and independent-assessment gaps bound review claims"; } }
    }
    action def Map_modelAssessment_001 { in source : ModelAssessment [0..*]; out target : EvidenceAssessment [0..*]; doc /* Conclusion-linked credibility and gaps. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelAssessment_002 { in source : ModelAssessment [0..*]; out target : EvidenceAssessment [0..*]; doc /* Explicit independent-assessment and validity gaps. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelAssessment_003 { in source : TimingRecord [0..*]; out target : AnalysisResult [0..*]; doc /* Timing/synchronization observations. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelAssessment_004 { in source : TimingRecord [0..*]; out target : EvidenceAssessment [0..*]; doc /* Timing gaps are evidence gaps. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelAssessment_005 { in source : MappingFindingRecord [0..*]; out target : EvidenceAssessment [0..*]; doc /* Quality/admission findings. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelAssessment_006 { in source : ReferenceData [0..*]; out target : AnalysisResult [0..*]; doc /* Raw histories retained as observations. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelAssessment_007 { in source : ExecutionStatusRecord [0..*]; out target : EvidenceAssessment [0..*]; doc /* Invalid/missing/inactive status. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelAssessment_008 { in source : ReferenceData [0..*]; out target : AnalysisResult [0..*]; doc /* Processing masks accompany observations. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_modelAssessment_009 { in source : ModelAssessment [0..*]; out target : EvidenceAssessment [0..*]; doc /* Model limits and independent-assessment gaps bound review claims. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def RequirementBasisCoverageExchange :> EngineeringArtifact {
        ref item field001 : RequirementRecord [0..*] { @ExchangeField { sourceFR = "FR-01"; sourceOutput = "Retained requirement records"; targetFR = "FR-28"; targetInput = "EPS requirements/expectations"; mapping = "Requirement verification basis"; } }
        ref item field002 : TraceLink [0..*] { @ExchangeField { sourceFR = "FR-04"; sourceOutput = "Forward/reverse links"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Applicable trace links"; } }
        ref item field003 : TraceLink [0..*] { @ExchangeField { sourceFR = "FR-04"; sourceOutput = "endpoint gaps"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Endpoint gaps"; } }
        ref item field004 : RequirementAllocation [0..*] { @ExchangeField { sourceFR = "FR-04"; sourceOutput = "coverage"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Declared coverage basis"; } }
        ref item field005 : RequirementAllocation [0..*] { @ExchangeField { sourceFR = "FR-17"; sourceOutput = "Proposed EPS/component allocations"; targetFR = "FR-28"; targetInput = "EPS requirements/expectations"; mapping = "EPS/component allocation basis"; } }
    }
    action def Map_requirementBasisCoverage_001 { in source : RequirementRecord [0..*]; out target : RequirementAllocation [0..*]; doc /* Requirement verification basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_requirementBasisCoverage_002 { in source : TraceLink [0..*]; out target : EvidenceAssessment [0..*]; doc /* Applicable trace links. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_requirementBasisCoverage_003 { in source : TraceLink [0..*]; out target : EvidenceAssessment [0..*]; doc /* Endpoint gaps. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_requirementBasisCoverage_004 { in source : RequirementAllocation [0..*]; out target : EvidenceAssessment [0..*]; doc /* Declared coverage basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_requirementBasisCoverage_005 { in source : RequirementAllocation [0..*]; out target : RequirementAllocation [0..*]; doc /* EPS/component allocation basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def DesignConOpsProductsExchange :> EngineeringArtifact {
        ref item field001 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-13"; sourceOutput = "Mass and volume estimates with uncertainty and unknowns"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Technical mass/volume measures"; } }
        ref item field002 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-14"; sourceOutput = "Feasibility"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Feasibility findings"; } }
        ref item field003 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-28"; targetInput = "EPS requirements/expectations"; mapping = "Configured EPS requirement/expectation basis"; } }
        ref item field004 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-20"; sourceOutput = "Power/energy budgets"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Power/energy budgets"; } }
        ref item field005 : MissionDefinition [0..*] { @ExchangeField { sourceFR = "FR-25"; sourceOutput = "Revision-linked mission and ConOps records"; targetFR = "FR-28"; targetInput = "EPS requirements/expectations"; mapping = "Expectation/ConOps validation basis"; } }
        ref item field006 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-33"; sourceOutput = "Revision-linked EPS interface and ground-definition specifications"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Interface products"; } }
        ref item field007 : ReviewFinding [0..*] { @ExchangeField { sourceFR = "FR-35"; sourceOutput = "discrepancy findings"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Behavior discrepancies"; } }
        ref item field008 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-37"; targetInput = "Controlled EPS baseline"; mapping = "Controlled design records selected from exact baseline. FR07 resolves identity"; } }
    }
    action def Map_designConOpsProducts_001 { in source : DesignStudy [0..*]; out target : EvidenceAssessment [0..*]; doc /* Technical mass/volume measures. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designConOpsProducts_002 { in source : DesignStudy [0..*]; out target : EvidenceAssessment [0..*]; doc /* Feasibility findings. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designConOpsProducts_003 { in source : DesignConfiguration [0..*]; out target : RequirementAllocation [0..*]; doc /* Configured EPS requirement/expectation basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designConOpsProducts_004 { in source : DesignStudy [0..*]; out target : EvidenceAssessment [0..*]; doc /* Power/energy budgets. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designConOpsProducts_005 { in source : MissionDefinition [0..*]; out target : RequirementAllocation [0..*]; doc /* Expectation/ConOps validation basis. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designConOpsProducts_006 { in source : EPSInterfaceSpecification [0..*]; out target : EvidenceAssessment [0..*]; doc /* Interface products. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designConOpsProducts_007 { in source : ReviewFinding [0..*]; out target : EvidenceAssessment [0..*]; doc /* Behavior discrepancies. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_designConOpsProducts_008 { in source : DesignConfiguration [0..*]; out target : PhaseBaseline [0..*]; doc /* Controlled design records selected from exact baseline. FR07 resolves identity. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def AssessmentCriteriaExchange :> EngineeringArtifact {
        ref item field001 : EPSAssessmentPlan [0..*] { @ExchangeField { sourceFR = "FR-28"; sourceOutput = "Retained EPS V&V plans"; targetFR = "FR-19"; targetInput = "MIL criteria"; mapping = "MIL conditions/inputs/expected responses/criteria"; } }
        ref item field002 : EPSAssessmentPlan [0..*] { @ExchangeField { sourceFR = "FR-28"; sourceOutput = "Retained EPS V&V plans"; targetFR = "FR-24"; targetInput = "fixed comparison rules"; mapping = "Matched SIL comparison rules and expectation criteria"; } }
    }
    action def Map_assessmentCriteria_001 { in source : EPSAssessmentPlan [0..*]; out target : EPSAssessmentPlan [0..*]; doc /* MIL conditions/inputs/expected responses/criteria. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_assessmentCriteria_002 { in source : EPSAssessmentPlan [0..*]; out target : RuleRecord [0..*]; doc /* Matched SIL comparison rules and expectation criteria. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def MaturityFindingsExchange :> EngineeringArtifact {
        ref item field001 : EvidenceAssessment [0..*] { @ExchangeField { sourceFR = "FR-11"; sourceOutput = "Gap reports"; targetFR = "FR-39"; targetInput = "findings"; mapping = "Gaps/dispositions"; } }
        ref item field002 : ReviewPackage [0..*] { @ExchangeField { sourceFR = "FR-38"; sourceOutput = "Prepared review package with coverage, limits and findings"; targetFR = "FR-39"; targetInput = "findings"; mapping = "Prepared package findings and unmet prerequisites"; } }
        ref item field003 : ReviewWork [0..*] { @ExchangeField { sourceFR = "FR-42"; sourceOutput = "Recorded disposition"; targetFR = "FR-39"; targetInput = "review criteria"; mapping = "Authorized exact review disposition"; } }
        ref item field004 : ReviewWork [0..*] { @ExchangeField { sourceFR = "FR-42"; sourceOutput = "progression status"; targetFR = "FR-03"; targetInput = "Current phase/question"; mapping = "Progression status informs phase/question scope"; } }
        ref item field005 : ReviewWork [0..*] { @ExchangeField { sourceFR = "FR-42"; sourceOutput = "closure obligations"; targetFR = "FR-39"; targetInput = "findings"; mapping = "Closure conditions remain distinct from renewed authority"; } }
    }
    action def Map_maturityFindings_001 { in source : EvidenceAssessment [0..*]; out target : ReviewFinding [0..*]; doc /* Gaps/dispositions. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_maturityFindings_002 { in source : ReviewPackage [0..*]; out target : ReviewFinding [0..*]; doc /* Prepared package findings and unmet prerequisites. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_maturityFindings_003 { in source : ReviewWork [0..*]; out target : ReviewCriterionRecord [0..*]; doc /* Authorized exact review disposition. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_maturityFindings_004 { in source : ReviewWork [0..*]; out target : GuidanceRequest [0..*]; doc /* Progression status informs phase/question scope. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_maturityFindings_005 { in source : ReviewWork [0..*]; out target : ReviewFinding [0..*]; doc /* Closure conditions remain distinct from renewed authority. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def PreserveL01Exchange :> EngineeringArtifact {
        ref item field001 : RequirementRecord [0..*] { @ExchangeField { sourceFR = "FR-01"; sourceOutput = "Retained requirement records"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field002 : RequirementRecord [0..*] { @ExchangeField { sourceFR = "FR-01"; sourceOutput = "field resolution status"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field003 : AssistanceFinding [0..*] { @ExchangeField { sourceFR = "FR-02"; sourceOutput = "Explained findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field004 : AssistanceFinding [0..*] { @ExchangeField { sourceFR = "FR-02"; sourceOutput = "corrections/questions"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field005 : AssistanceFinding [0..*] { @ExchangeField { sourceFR = "FR-02"; sourceOutput = "assessment limits"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field006 : MethodRecommendation [0..*] { @ExchangeField { sourceFR = "FR-03"; sourceOutput = "Cited method/model recommendations"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field007 : MethodRecommendation [0..*] { @ExchangeField { sourceFR = "FR-03"; sourceOutput = "alternatives"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field008 : MethodRecommendation [0..*] { @ExchangeField { sourceFR = "FR-03"; sourceOutput = "rejection records"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field009 : TraceLink [0..*] { @ExchangeField { sourceFR = "FR-04"; sourceOutput = "Forward/reverse links"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field010 : TraceLink [0..*] { @ExchangeField { sourceFR = "FR-04"; sourceOutput = "endpoint gaps"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field011 : RequirementAllocation [0..*] { @ExchangeField { sourceFR = "FR-04"; sourceOutput = "coverage"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field012 : RequirementAllocation [0..*] { @ExchangeField { sourceFR = "FR-17"; sourceOutput = "Proposed EPS/component allocations"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field013 : TraceLink [0..*] { @ExchangeField { sourceFR = "FR-17"; sourceOutput = "traces"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field014 : SuggestionDisposition [0..*] { @ExchangeField { sourceFR = "FR-17"; sourceOutput = "dispositions"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field015 : SuggestionDisposition [0..*] { @ExchangeField { sourceFR = "FR-29"; sourceOutput = "Recorded disposition"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field016 : EngineeringDecision [0..*] { @ExchangeField { sourceFR = "FR-29"; sourceOutput = "rationale"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field017 : TraceLink [0..*] { @ExchangeField { sourceFR = "FR-29"; sourceOutput = "revision links"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field018 : AssistanceReport [0..*] { @ExchangeField { sourceFR = "FR-39"; sourceOutput = "Proposed activities/reassessments"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field019 : AssistanceReport [0..*] { @ExchangeField { sourceFR = "FR-39"; sourceOutput = "prerequisites"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field020 : AssistanceReport [0..*] { @ExchangeField { sourceFR = "FR-39"; sourceOutput = "rationale"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field021 : AssistanceWork [0..*] { @ExchangeField { sourceFR = "FR-41"; sourceOutput = "Acknowledgement"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field022 : AssistanceReport [0..*] { @ExchangeField { sourceFR = "FR-41"; sourceOutput = "guidance/status"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field023 : TimingRecord [0..*] { @ExchangeField { sourceFR = "FR-41"; sourceOutput = "response timestamps"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field024 : SuggestionDisposition [0..*] { @ExchangeField { sourceFR = "FR-29"; sourceOutput = "Recorded disposition"; targetFR = "FR-07"; targetInput = "decisions"; mapping = "Preserve exact authorized engineer dispositions and rationale"; } }
        ref item field025 : SuggestionDisposition [0..*] { @ExchangeField { sourceFR = "FR-17"; sourceOutput = "dispositions"; targetFR = "FR-06"; targetInput = "authorized change acceptance"; mapping = "Preserve allocation dispositions. Only exact requested accepted change can create successor"; } }
    }
    action def Map_preserveL01_001 { in source : RequirementRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_002 { in source : RequirementRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_003 { in source : AssistanceFinding [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_004 { in source : AssistanceFinding [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_005 { in source : AssistanceFinding [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_006 { in source : MethodRecommendation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_007 { in source : MethodRecommendation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_008 { in source : MethodRecommendation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_009 { in source : TraceLink [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_010 { in source : TraceLink [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_011 { in source : RequirementAllocation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_012 { in source : RequirementAllocation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_013 { in source : TraceLink [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_014 { in source : SuggestionDisposition [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_015 { in source : SuggestionDisposition [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_016 { in source : EngineeringDecision [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_017 { in source : TraceLink [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_018 { in source : AssistanceReport [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_019 { in source : AssistanceReport [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_020 { in source : AssistanceReport [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_021 { in source : AssistanceWork [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_022 { in source : AssistanceReport [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_023 { in source : TimingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_024 { in source : SuggestionDisposition [0..*]; out target : EngineeringDecision [0..*]; doc /* Preserve exact authorized engineer dispositions and rationale. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL01_025 { in source : SuggestionDisposition [0..*]; out target : EngineeringDecision [0..*]; doc /* Preserve allocation dispositions. Only exact requested accepted change can create successor. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def PreserveL02Exchange :> EngineeringArtifact {
        ref item field001 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-13"; sourceOutput = "Mass and volume estimates with uncertainty and unknowns"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field002 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-14"; sourceOutput = "Feasibility"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field003 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-14"; sourceOutput = "ranking"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field004 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-14"; sourceOutput = "sensitivity"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field005 : EngineeringDecision [0..*] { @ExchangeField { sourceFR = "FR-14"; sourceOutput = "selection rationale"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field006 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-15"; sourceOutput = "Configured EPS design representations"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field007 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-20"; sourceOutput = "Power/energy budgets"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field008 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-20"; sourceOutput = "array/battery sizing"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field009 : MissionDefinition [0..*] { @ExchangeField { sourceFR = "FR-25"; sourceOutput = "Revision-linked mission and ConOps records"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field010 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-33"; sourceOutput = "Revision-linked EPS interface and ground-definition specifications"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field011 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-35"; sourceOutput = "Checked behavior specifications"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field012 : ReviewFinding [0..*] { @ExchangeField { sourceFR = "FR-35"; sourceOutput = "discrepancy findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field013 : EngineeringDecision [0..*] { @ExchangeField { sourceFR = "FR-14"; sourceOutput = "selection rationale"; targetFR = "FR-07"; targetInput = "decisions"; mapping = "Preserve engineer selection rationale without review progression"; } }
        ref item field014 : DesignStudy [0..*] { @ExchangeField { sourceFR = "FR-14"; sourceOutput = "Feasibility"; targetFR = "FR-05"; targetInput = "Proposed change"; mapping = "Trade findings inform proposed design change, never automatic application"; } }
    }
    action def Map_preserveL02_001 { in source : DesignStudy [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_002 { in source : DesignStudy [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_003 { in source : DesignStudy [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_004 { in source : DesignStudy [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_005 { in source : EngineeringDecision [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_006 { in source : DesignConfiguration [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_007 { in source : DesignStudy [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_008 { in source : DesignStudy [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_009 { in source : MissionDefinition [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_010 { in source : EPSInterfaceSpecification [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_011 { in source : EPSInterfaceSpecification [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_012 { in source : ReviewFinding [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_013 { in source : EngineeringDecision [0..*]; out target : EngineeringDecision [0..*]; doc /* Preserve engineer selection rationale without review progression. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL02_014 { in source : DesignStudy [0..*]; out target : ChangeProposal [0..*]; doc /* Trade findings inform proposed design change, never automatic application. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def PreserveL03Exchange :> EngineeringArtifact {
        ref item field001 : ReplayPreparation [0..*] { @ExchangeField { sourceFR = "FR-10"; sourceOutput = "Replay inputs/instructions"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field002 : ReplayComparison [0..*] { @ExchangeField { sourceFR = "FR-10"; sourceOutput = "comparisons"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field003 : ReplayComparison [0..*] { @ExchangeField { sourceFR = "FR-10"; sourceOutput = "dependency/failure findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field004 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "Power/energy balance"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field005 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "bus quantities"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field006 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "battery state histories"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field007 : DesignConfiguration [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "Exchanged component/design models"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field008 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "mapped EPS analysis inputs"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field009 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "EPS states/results returned to the same whole-CUBICS scenario"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field010 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "mapping findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field011 : ExecutionStatusRecord [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "execution status"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field012 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-18"; sourceOutput = "transfer limitations"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field013 : AnalysisRequest [0..*] { @ExchangeField { sourceFR = "FR-19"; sourceOutput = "MIL requests"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field014 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-19"; sourceOutput = "retained stimuli/responses"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field015 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-19"; sourceOutput = "criterion outcomes/failures"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field016 : AnalysisPlan [0..*] { @ExchangeField { sourceFR = "FR-23"; sourceOutput = "Run configuration/runtime records"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field017 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-23"; sourceOutput = "numerical/resource findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field018 : CodingRequest [0..*] { @ExchangeField { sourceFR = "FR-24"; sourceOutput = "SIL requests"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field019 : SoftwareRunResult [0..*] { @ExchangeField { sourceFR = "FR-24"; sourceOutput = "retained host responses"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field020 : SoftwareAssessment [0..*] { @ExchangeField { sourceFR = "FR-24"; sourceOutput = "requirement/ConOps outcomes"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field021 : SoftwareAssessment [0..*] { @ExchangeField { sourceFR = "FR-24"; sourceOutput = "MIL/SIL differences with execution status and limits"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field022 : MethodRecommendation [0..*] { @ExchangeField { sourceFR = "FR-26"; sourceOutput = "Applicable RAM methods"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field023 : MethodRecommendation [0..*] { @ExchangeField { sourceFR = "FR-26"; sourceOutput = "measures"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field024 : MethodRecommendation [0..*] { @ExchangeField { sourceFR = "FR-26"; sourceOutput = "coverage"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field025 : MethodRecommendation [0..*] { @ExchangeField { sourceFR = "FR-26"; sourceOutput = "exclusions"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field026 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-27"; sourceOutput = "RAM representations/results with uncertainty and missing data"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field027 : EPSInterfaceSpecification [0..*] { @ExchangeField { sourceFR = "FR-34"; sourceOutput = "Checked F Prime mappings and definitions"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field028 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-34"; sourceOutput = "compatibility findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field029 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-34"; sourceOutput = "unsupported/lossy-translation records"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field030 : CodingRequest [0..*] { @ExchangeField { sourceFR = "FR-36"; sourceOutput = "Authorized coding/build requests"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field031 : HostSoftwareProduct [0..*] { @ExchangeField { sourceFR = "FR-36"; sourceOutput = "retained source/build products"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field032 : EnvironmentRecord [0..*] { @ExchangeField { sourceFR = "FR-36"; sourceOutput = "exact configuration records"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field033 : ExecutionStatusRecord [0..*] { @ExchangeField { sourceFR = "FR-36"; sourceOutput = "logs"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field034 : ExecutionStatusRecord [0..*] { @ExchangeField { sourceFR = "FR-36"; sourceOutput = "failures"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field035 : AnalysisResult [0..*] { @ExchangeField { sourceFR = "FR-16"; sourceOutput = "Power/energy balance"; targetFR = "FR-09"; targetInput = "Analysis/software results"; mapping = "Preserve run outputs"; } }
        ref item field036 : AnalysisPlan [0..*] { @ExchangeField { sourceFR = "FR-23"; sourceOutput = "Run configuration/runtime records"; targetFR = "FR-09"; targetInput = "exact dependencies"; mapping = "Preserve exact as-run dependencies"; } }
        ref item field037 : SoftwareAssessment [0..*] { @ExchangeField { sourceFR = "FR-24"; sourceOutput = "MIL/SIL differences with execution status and limits"; targetFR = "FR-09"; targetInput = "status"; mapping = "Preserve failed/partial SIL logs/status"; } }
    }
    action def Map_preserveL03_001 { in source : ReplayPreparation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_002 { in source : ReplayComparison [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_003 { in source : ReplayComparison [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_004 { in source : AnalysisResult [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_005 { in source : AnalysisResult [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_006 { in source : ReferenceData [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_007 { in source : DesignConfiguration [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_008 { in source : ReferenceData [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_009 { in source : AnalysisResult [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_010 { in source : MappingFindingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_011 { in source : ExecutionStatusRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_012 { in source : MappingFindingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_013 { in source : AnalysisRequest [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_014 { in source : ReferenceData [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_015 { in source : AnalysisResult [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_016 { in source : AnalysisPlan [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_017 { in source : MappingFindingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_018 { in source : CodingRequest [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_019 { in source : SoftwareRunResult [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_020 { in source : SoftwareAssessment [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_021 { in source : SoftwareAssessment [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_022 { in source : MethodRecommendation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_023 { in source : MethodRecommendation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_024 { in source : MethodRecommendation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_025 { in source : MethodRecommendation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_026 { in source : AnalysisResult [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_027 { in source : EPSInterfaceSpecification [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_028 { in source : MappingFindingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_029 { in source : MappingFindingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_030 { in source : CodingRequest [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_031 { in source : HostSoftwareProduct [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_032 { in source : EnvironmentRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_033 { in source : ExecutionStatusRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_034 { in source : ExecutionStatusRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_035 { in source : AnalysisResult [0..*]; out target : RunWork [0..*]; doc /* Preserve run outputs. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_036 { in source : AnalysisPlan [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve exact as-run dependencies. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL03_037 { in source : SoftwareAssessment [0..*]; out target : ExecutionStatusRecord [0..*]; doc /* Preserve failed/partial SIL logs/status. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def PreserveL04Exchange :> EngineeringArtifact {
        ref item field001 : ModelAssessment [0..*] { @ExchangeField { sourceFR = "FR-21"; sourceOutput = "Conclusion-linked credibility records"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field002 : ModelAssessment [0..*] { @ExchangeField { sourceFR = "FR-21"; sourceOutput = "explicit gaps"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field003 : ChangeProposal [0..*] { @ExchangeField { sourceFR = "FR-22"; sourceOutput = "Calibration proposals"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field004 : ModelAssessment [0..*] { @ExchangeField { sourceFR = "FR-22"; sourceOutput = "residuals"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field005 : ModelAssessment [0..*] { @ExchangeField { sourceFR = "FR-22"; sourceOutput = "uncertainty"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field006 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-22"; sourceOutput = "affected analyses"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field007 : TimingRecord [0..*] { @ExchangeField { sourceFR = "FR-31"; sourceOutput = "Timing and synchronization records"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field008 : TimingRecord [0..*] { @ExchangeField { sourceFR = "FR-31"; sourceOutput = "checked alignments"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field009 : TimingRecord [0..*] { @ExchangeField { sourceFR = "FR-31"; sourceOutput = "timing gaps"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field010 : TimingRecord [0..*] { @ExchangeField { sourceFR = "FR-31"; sourceOutput = "limit findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field011 : MappingFindingRecord [0..*] { @ExchangeField { sourceFR = "FR-32"; sourceOutput = "Admission/quality findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field012 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-32"; sourceOutput = "preserved raw histories"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field013 : ExecutionStatusRecord [0..*] { @ExchangeField { sourceFR = "FR-32"; sourceOutput = "invalid/missing/inactive status"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field014 : ReferenceData [0..*] { @ExchangeField { sourceFR = "FR-32"; sourceOutput = "processing masks"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field015 : ChangeProposal [0..*] { @ExchangeField { sourceFR = "FR-22"; sourceOutput = "Calibration proposals"; targetFR = "FR-05"; targetInput = "Proposed change"; mapping = "Calibration proposal goes through impact/authority checks"; } }
        ref item field016 : ChangeProposal [0..*] { @ExchangeField { sourceFR = "FR-22"; sourceOutput = "Calibration proposals"; targetFR = "FR-06"; targetInput = "change request"; mapping = "No automatic parameter update"; } }
    }
    action def Map_preserveL04_001 { in source : ModelAssessment [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_002 { in source : ModelAssessment [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_003 { in source : ChangeProposal [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_004 { in source : ModelAssessment [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_005 { in source : ModelAssessment [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_006 { in source : ImpactNotice [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_007 { in source : TimingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_008 { in source : TimingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_009 { in source : TimingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_010 { in source : TimingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_011 { in source : MappingFindingRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_012 { in source : ReferenceData [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_013 { in source : ExecutionStatusRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_014 { in source : ReferenceData [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_015 { in source : ChangeProposal [0..*]; out target : ChangeProposal [0..*]; doc /* Calibration proposal goes through impact/authority checks. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_preserveL04_016 { in source : ChangeProposal [0..*]; out target : ChangeProposal [0..*]; doc /* No automatic parameter update. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def BaselineDecisionsExchange :> EngineeringArtifact {
        ref item field001 : EvidenceAssessment [0..*] { @ExchangeField { sourceFR = "FR-11"; sourceOutput = "Gap reports"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field002 : EvidenceAssessment [0..*] { @ExchangeField { sourceFR = "FR-11"; sourceOutput = "blocked unsupported conformity claims"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field003 : EPSAssessmentPlan [0..*] { @ExchangeField { sourceFR = "FR-28"; sourceOutput = "Retained EPS V&V plans"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field004 : RequirementAllocation [0..*] { @ExchangeField { sourceFR = "FR-28"; sourceOutput = "separate references"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field005 : ExecutionStatusRecord [0..*] { @ExchangeField { sourceFR = "FR-28"; sourceOutput = "planned/executed status"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field006 : ReviewPackage [0..*] { @ExchangeField { sourceFR = "FR-37"; sourceOutput = "Readable baseline-linked engineering views"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field007 : ReviewPackage [0..*] { @ExchangeField { sourceFR = "FR-38"; sourceOutput = "Prepared review package with coverage, limits and findings"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field008 : ReviewWork [0..*] { @ExchangeField { sourceFR = "FR-42"; sourceOutput = "Recorded disposition"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field009 : ReviewWork [0..*] { @ExchangeField { sourceFR = "FR-42"; sourceOutput = "progression status"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field010 : ReviewWork [0..*] { @ExchangeField { sourceFR = "FR-42"; sourceOutput = "closure obligations"; targetFR = "FR-07"; targetInput = "Product/evidence revisions"; mapping = "Preserve identified product/evidence revision without promotion to current or accepted"; } }
        ref item field011 : ReviewWork [0..*] { @ExchangeField { sourceFR = "FR-42"; sourceOutput = "Recorded disposition"; targetFR = "FR-07"; targetInput = "decisions"; mapping = "Preserve designated authority decision"; } }
        ref item field012 : ReviewWork [0..*] { @ExchangeField { sourceFR = "FR-42"; sourceOutput = "Recorded disposition"; targetFR = "FR-06"; targetInput = "authorized change acceptance"; mapping = "Review disposition is retained. It substitutes for no engineering change authorization"; } }
    }
    action def Map_baselineDecisions_001 { in source : EvidenceAssessment [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_002 { in source : EvidenceAssessment [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_003 { in source : EPSAssessmentPlan [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_004 { in source : RequirementAllocation [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_005 { in source : ExecutionStatusRecord [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_006 { in source : ReviewPackage [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_007 { in source : ReviewPackage [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_008 { in source : ReviewWork [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_009 { in source : ReviewWork [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_010 { in source : ReviewWork [0..*]; out target : EngineeringArtifact [0..*]; doc /* Preserve identified product/evidence revision without promotion to current or accepted. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_011 { in source : ReviewWork [0..*]; out target : EngineeringDecision [0..*]; doc /* Preserve designated authority decision. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_baselineDecisions_012 { in source : ReviewWork [0..*]; out target : EngineeringDecision [0..*]; doc /* Review disposition is retained. It substitutes for no engineering change authorization. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def CurrentContextExchange :> EngineeringArtifact {
        ref item field001 : PhaseBaseline [0..*] { @ExchangeField { sourceFR = "FR-07"; sourceOutput = "Retrievable exact baselines"; targetFR = "FR-03"; targetInput = "inputs"; mapping = "Resolve current available input revisions"; } }
        ref item field002 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-05"; sourceOutput = "required reassessments"; targetFR = "FR-39"; targetInput = "dependencies"; mapping = "Impacts/reassessment dependencies"; } }
        ref item field003 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-30"; sourceOutput = "Stale status"; targetFR = "FR-41"; targetInput = "current context"; mapping = "Immediately invalidate changed context before latest-context response checks"; } }
        ref item field004 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-30"; sourceOutput = "reassessment request"; targetFR = "FR-41"; targetInput = "Assistance trigger"; mapping = "Reassessment trigger"; } }
        ref item field005 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-30"; sourceOutput = "reassessment request"; targetFR = "FR-02"; targetInput = "Draft edits/requests"; mapping = "New draft check request"; } }
        ref item field006 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-30"; sourceOutput = "reassessment request"; targetFR = "FR-03"; targetInput = "Current phase/question"; mapping = "New method request"; } }
        ref item field007 : CheckedTransfer [0..*] { @ExchangeField { sourceFR = "FR-08"; sourceOutput = "Admitted transfers or retained rejections with unchanged controlled content"; targetFR = "FR-01"; targetInput = "Requirement submissions"; mapping = "Admitted requirement submission only"; } }
        ref item field008 : PhaseBaseline [0..*] { @ExchangeField { sourceFR = "FR-07"; sourceOutput = "Retrievable exact baselines"; targetFR = "FR-41"; targetInput = "current context"; mapping = "Latest six-revision context resolved before presentation and application"; } }
    }
    action def Map_currentContext_001 { in source : PhaseBaseline [0..*]; out target : EngineeringArtifact [0..*]; doc /* Resolve current available input revisions. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentContext_002 { in source : ImpactNotice [0..*]; out target : EngineeringArtifact [0..*]; doc /* Impacts/reassessment dependencies. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentContext_003 { in source : ImpactNotice [0..*]; out target : ContextRevision [0..*]; doc /* Immediately invalidate changed context before latest-context response checks. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentContext_004 { in source : ImpactNotice [0..*]; out target : GuidanceRequest [0..*]; doc /* Reassessment trigger. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentContext_005 { in source : ImpactNotice [0..*]; out target : EngineeringSubmission [0..*]; doc /* New draft check request. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentContext_006 { in source : ImpactNotice [0..*]; out target : GuidanceRequest [0..*]; doc /* New method request. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentContext_007 { in source : CheckedTransfer [0..*]; out target : RequirementRecord [0..*]; doc /* Admitted requirement submission only. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentContext_008 { in source : PhaseBaseline [0..*]; out target : ContextRevision [0..*]; doc /* Latest six-revision context resolved before presentation and application. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def ReleaseRevisionsExchange :> EngineeringArtifact {
        ref item field001 : PhaseBaseline [0..*] { @ExchangeField { sourceFR = "FR-07"; sourceOutput = "Retrievable exact baselines"; targetFR = "FR-36"; targetInput = "Current authorized design/interface release"; mapping = "Resolve exact current engineer-authorized detailed design/interface/software-scope release. Broad CDR insufficient"; } }
        ref item field002 : PhaseBaseline [0..*] { @ExchangeField { sourceFR = "FR-06"; sourceOutput = "Successor baseline"; targetFR = "FR-36"; targetInput = "host/toolchain/dependency configuration"; mapping = "Distinct authorized successor dependencies"; } }
        ref item field003 : RunWork [0..*] { @ExchangeField { sourceFR = "FR-09"; sourceOutput = "Configuration-linked results"; targetFR = "FR-10"; targetInput = "preserved run/dependencies"; mapping = "Preserved exact replay run/dependencies"; } }
        ref item field004 : CheckedTransfer [0..*] { @ExchangeField { sourceFR = "FR-08"; sourceOutput = "Admitted transfers or retained rejections with unchanged controlled content"; targetFR = "FR-18"; targetInput = "returned tool responses"; mapping = "Admitted tool response only"; } }
        ref item field005 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-30"; sourceOutput = "blocked application"; targetFR = "FR-24"; targetInput = "Released F Prime host code/build"; mapping = "Stale released-build revisions block current SIL use"; } }
    }
    action def Map_releaseRevisions_001 { in source : PhaseBaseline [0..*]; out target : DetailedDesignAuthorization [0..*]; doc /* Resolve exact current engineer-authorized detailed design/interface/software-scope release. Broad CDR insufficient. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_releaseRevisions_002 { in source : PhaseBaseline [0..*]; out target : EnvironmentRecord [0..*]; doc /* Distinct authorized successor dependencies. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_releaseRevisions_003 { in source : RunWork [0..*]; out target : RunWork [0..*]; doc /* Preserved exact replay run/dependencies. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_releaseRevisions_004 { in source : CheckedTransfer [0..*]; out target : AnalysisResponse [0..*]; doc /* Admitted tool response only. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_releaseRevisions_005 { in source : ImpactNotice [0..*]; out target : HostSoftwareProduct [0..*]; doc /* Stale released-build revisions block current SIL use. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def CurrentRecordsL02Exchange :> EngineeringArtifact {
        ref item field001 : CheckedTransfer [0..*] { @ExchangeField { sourceFR = "FR-08"; sourceOutput = "Admitted transfers or retained rejections with unchanged controlled content"; targetFR = "FR-15"; targetInput = "Design parameters"; mapping = "Admitted matching subject only. Rejections retained and do not replace controlled content"; } }
        ref item field002 : PhaseBaseline [0..*] { @ExchangeField { sourceFR = "FR-07"; sourceOutput = "Retrievable exact baselines"; targetFR = "FR-15"; targetInput = "Design parameters"; mapping = "Resolve exact current baseline subject"; } }
        ref item field003 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-05"; sourceOutput = "Reciprocal impacts"; targetFR = "FR-15"; targetInput = "Design parameters"; mapping = "Impacts bound use and reassessment"; } }
        ref item field004 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-30"; sourceOutput = "Stale status"; targetFR = "FR-15"; targetInput = "Design parameters"; mapping = "Changed dependencies mark affected records stale"; } }
    }
    action def Map_currentRecordsL02_001 { in source : CheckedTransfer [0..*]; out target : DesignConfiguration [0..*]; doc /* Admitted matching subject only. Rejections retained and do not replace controlled content. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL02_002 { in source : PhaseBaseline [0..*]; out target : DesignConfiguration [0..*]; doc /* Resolve exact current baseline subject. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL02_003 { in source : ImpactNotice [0..*]; out target : DesignConfiguration [0..*]; doc /* Impacts bound use and reassessment. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL02_004 { in source : ImpactNotice [0..*]; out target : DesignConfiguration [0..*]; doc /* Changed dependencies mark affected records stale. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def CurrentRecordsL04Exchange :> EngineeringArtifact {
        ref item field001 : CheckedTransfer [0..*] { @ExchangeField { sourceFR = "FR-08"; sourceOutput = "Admitted transfers or retained rejections with unchanged controlled content"; targetFR = "FR-21"; targetInput = "credibility evidence"; mapping = "Admitted matching subject only. Rejections retained and do not replace controlled content"; } }
        ref item field002 : PhaseBaseline [0..*] { @ExchangeField { sourceFR = "FR-07"; sourceOutput = "Retrievable exact baselines"; targetFR = "FR-21"; targetInput = "credibility evidence"; mapping = "Resolve exact current baseline subject"; } }
        ref item field003 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-05"; sourceOutput = "Reciprocal impacts"; targetFR = "FR-21"; targetInput = "credibility evidence"; mapping = "Impacts bound use and reassessment"; } }
        ref item field004 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-30"; sourceOutput = "Stale status"; targetFR = "FR-21"; targetInput = "credibility evidence"; mapping = "Changed dependencies mark affected records stale"; } }
    }
    action def Map_currentRecordsL04_001 { in source : CheckedTransfer [0..*]; out target : EvidenceAssessment [0..*]; doc /* Admitted matching subject only. Rejections retained and do not replace controlled content. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL04_002 { in source : PhaseBaseline [0..*]; out target : EvidenceAssessment [0..*]; doc /* Resolve exact current baseline subject. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL04_003 { in source : ImpactNotice [0..*]; out target : EvidenceAssessment [0..*]; doc /* Impacts bound use and reassessment. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL04_004 { in source : ImpactNotice [0..*]; out target : EvidenceAssessment [0..*]; doc /* Changed dependencies mark affected records stale. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    item def CurrentRecordsL05Exchange :> EngineeringArtifact {
        ref item field001 : CheckedTransfer [0..*] { @ExchangeField { sourceFR = "FR-08"; sourceOutput = "Admitted transfers or retained rejections with unchanged controlled content"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Admitted matching subject only. Rejections retained and do not replace controlled content"; } }
        ref item field002 : PhaseBaseline [0..*] { @ExchangeField { sourceFR = "FR-07"; sourceOutput = "Retrievable exact baselines"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Resolve exact current baseline subject"; } }
        ref item field003 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-05"; sourceOutput = "Reciprocal impacts"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Impacts bound use and reassessment"; } }
        ref item field004 : ImpactNotice [0..*] { @ExchangeField { sourceFR = "FR-30"; sourceOutput = "Stale status"; targetFR = "FR-38"; targetInput = "applicable records/evidence"; mapping = "Changed dependencies mark affected records stale"; } }
    }
    action def Map_currentRecordsL05_001 { in source : CheckedTransfer [0..*]; out target : EvidenceAssessment [0..*]; doc /* Admitted matching subject only. Rejections retained and do not replace controlled content. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL05_002 { in source : PhaseBaseline [0..*]; out target : EvidenceAssessment [0..*]; doc /* Resolve exact current baseline subject. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL05_003 { in source : ImpactNotice [0..*]; out target : EvidenceAssessment [0..*]; doc /* Impacts bound use and reassessment. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    action def Map_currentRecordsL05_004 { in source : ImpactNotice [0..*]; out target : EvidenceAssessment [0..*]; doc /* Changed dependencies mark affected records stale. Retain exact source/dependency identity, status and provenance. Projection is no registration or engineering authorization. */ }
    part def LogicalFramework :> ToBe::FutureFramework {
        part L01 : RequirementsAssistance;
        part L02 : MissionDesign;
        part L03 : SimulationIntegration;
        part L04 : ModelCredibility;
        part L05 : EvidenceReview;
        part L06 : ConfigurationExchange;
        bind p03 = L03.p03;
        bind p04 = L03.p04;
        bind p06 = L05.p06;
        bind L01.sourceQuery.request = L01.io.fr03Inputs.field01;
        ref item fPrimeRequests : CodingRequest [0..*]; // requests, out, FR-24, FR-36
        bind fPrimeRequests = L03.p04.codingRequest;
        ref item fPrimeProducts : HostSoftwareProduct [0..*]; // products / results, in, FR-36
        bind fPrimeProducts = L03.p04.softwareProduct;
        ref item fPrimeResults : SoftwareRunResult [0..*]; // products / results, in, FR-24
        bind fPrimeResults = L03.p04.softwareResult;
        ref item wholeCUBICSScenarios : ReferenceData [0..*]; // whole-CUBICS scenarios, in, FR-16, FR-18
        bind wholeCUBICSScenarios = L03.p03.spacecraftInputs;
        ref item epsStatesResults : AnalysisResult [0..*]; // EPS states / results, out, FR-18
        bind epsStatesResults = L03.p03.epsResponses;
        bind L03.p03.spacecraftInputs = L03.io.fr18Inputs.field04;
        bind L03.p03.spacecraftInputs = L03.io.fr16Inputs.field01;
        bind L03.io.fr18Outputs.field03 = L03.p03.epsResponses;
        bind L03.io.fr36Outputs.field01 = L03.p04.codingRequest;
        bind L03.io.fr24Outputs.field01 = L03.p04.codingRequest;
        bind L03.p04.softwareProduct = L03.io.fr24Inputs.field01;
        bind L03.p04.softwareProduct = L03.io.fr36Outputs.field02;
        bind L03.p04.softwareResult = L03.io.fr24Outputs.field02;
        bind L03.p04.codingResponse = L03.io.fr36Inputs.field05;
        bind L03.p03.analysisResponse = L03.io.fr18Inputs.field06;
        bind p01.engineeringSubmission = L06.checkEngineeringTransfer.raw;
        flow guidanceSubmission of GuidanceRequest from p01.engineeringSubmission.guidance to L01.io.fr41Inputs.field01;
        flow traceQuerySubmission of TraceQuery from p01.engineeringSubmission.traceQuery to L01.io.fr04Inputs.field01;
        flow viewSelectionSubmission of ViewSelection from p01.engineeringSubmission.viewSelection to L05.io.fr37Inputs.field02;
        flow baselineRetrievalSubmission of BaselineRetrieval from p01.engineeringSubmission.baselineRetrieval to L06.io.fr07Inputs.field03;
        flow assessmentPlanSubmission of EPSAssessmentPlan from p01.engineeringSubmission.assessmentPlans to L05.io.fr28Inputs.field02;
        flow requirementSubmission of RequirementRecord from p01.engineeringSubmission.requirements to L01.io.fr01Inputs.field01;
        flow missionSubmission of MissionDefinition from p01.engineeringSubmission.mission to L02.io.fr25Inputs.field01;
        flow designSubmission of DesignConfiguration from p01.engineeringSubmission.design to L02.io.fr15Inputs.field01;
        flow changeSubmission of ChangeProposal from p01.engineeringSubmission.changes to L06.io.fr05Inputs.field01;
        flow reviewRequestSubmission of PhaseBaseline from p01.engineeringSubmission.review.baseline to L05.prepareReview.baseline;
        bind L01.presentAdvice.response.assistance = p01.engineeringResponse.assistance;
        bind L05.presentAssessment.response.assessment = p01.engineeringResponse.assessment;
        bind p02.sourceSubmission = L06.checkSourceTransfer.raw;
        flow referenceSubmission of ReferenceData from p02.sourceSubmission.referenceData to L04.checkReferenceData.data;
        bind p02.sourceSubmission = L01.io.fr02Inputs.field04;
        perform action projectComponentProperties : ProjectComponentProperties;
        bind p02.sourceSubmission = projectComponentProperties.source;
        flow componentProperties of ComponentDesignData from projectComponentProperties.configuration to L02.io.fr13Inputs.field01;
        bind L01.sourceQuery.query = p02.sourceQuery;
        ref item requirementsAllocations : RequirementsAllocationsExchange [0..*]; // requirements / allocations
        perform action requirementsAllocations_001 : Map_requirementsAllocations_001;
        flow requirementsAllocations_001_source from L01.io.fr01Outputs.field01 to requirementsAllocations_001.source;
        flow requirementsAllocations_001_target from requirementsAllocations_001.target to L02.io.fr14Inputs.field02;
        bind requirementsAllocations.field001 = requirementsAllocations_001.source;
        perform action requirementsAllocations_002 : Map_requirementsAllocations_002;
        flow requirementsAllocations_002_source from L01.io.fr17Outputs.field01 to requirementsAllocations_002.source;
        flow requirementsAllocations_002_target from requirementsAllocations_002.target to L02.io.fr15Inputs.field04;
        bind requirementsAllocations.field002 = requirementsAllocations_002.source;
        perform action requirementsAllocations_003 : Map_requirementsAllocations_003;
        flow requirementsAllocations_003_source from L01.io.fr01Outputs.field01 to requirementsAllocations_003.source;
        flow requirementsAllocations_003_target from requirementsAllocations_003.target to L02.io.fr35Inputs.field02;
        bind requirementsAllocations.field003 = requirementsAllocations_003.source;
        ref item scenariosDesignQuantities : ScenariosDesignQuantitiesExchange [0..*]; // scenarios / design quantities
        perform action scenariosDesignQuantities_001 : Map_scenariosDesignQuantities_001;
        flow scenariosDesignQuantities_001_source from L02.io.fr25Outputs.field01 to scenariosDesignQuantities_001.source;
        flow scenariosDesignQuantities_001_target from scenariosDesignQuantities_001.target to L01.io.fr17Inputs.field02;
        bind scenariosDesignQuantities.field001 = scenariosDesignQuantities_001.source;
        perform action scenariosDesignQuantities_002 : Map_scenariosDesignQuantities_002;
        flow scenariosDesignQuantities_002_source from L02.io.fr20Outputs.field01 to scenariosDesignQuantities_002.source;
        flow scenariosDesignQuantities_002_target from scenariosDesignQuantities_002.target to L01.io.fr17Inputs.field03;
        bind scenariosDesignQuantities.field002 = scenariosDesignQuantities_002.source;
        perform action scenariosDesignQuantities_003 : Map_scenariosDesignQuantities_003;
        flow scenariosDesignQuantities_003_source from L02.io.fr13Outputs.field01 to scenariosDesignQuantities_003.source;
        flow scenariosDesignQuantities_003_target from scenariosDesignQuantities_003.target to L01.io.fr17Inputs.field03;
        bind scenariosDesignQuantities.field003 = scenariosDesignQuantities_003.source;
        perform action scenariosDesignQuantities_004 : Map_scenariosDesignQuantities_004;
        flow scenariosDesignQuantities_004_source from L02.io.fr13Outputs.field01 to scenariosDesignQuantities_004.source;
        flow scenariosDesignQuantities_004_target from scenariosDesignQuantities_004.target to L01.io.fr03Inputs.field03;
        bind scenariosDesignQuantities.field004 = scenariosDesignQuantities_004.source;
        perform action scenariosDesignQuantities_005 : Map_scenariosDesignQuantities_005;
        flow scenariosDesignQuantities_005_source from L02.io.fr20Outputs.field01 to scenariosDesignQuantities_005.source;
        flow scenariosDesignQuantities_005_target from scenariosDesignQuantities_005.target to L01.io.fr03Inputs.field03;
        bind scenariosDesignQuantities.field005 = scenariosDesignQuantities_005.source;
        ref item modelsScenarios : ModelsScenariosExchange [0..*]; // models / scenarios
        perform action modelsScenarios_001 : Map_modelsScenarios_001;
        flow modelsScenarios_001_source from L02.io.fr15Outputs.field01 to modelsScenarios_001.source;
        flow modelsScenarios_001_target from modelsScenarios_001.target to L03.io.fr16Inputs.field03;
        bind modelsScenarios.field001 = modelsScenarios_001.source;
        perform action modelsScenarios_002 : Map_modelsScenarios_002;
        flow modelsScenarios_002_source from L02.io.fr25Outputs.field01 to modelsScenarios_002.source;
        flow modelsScenarios_002_target from modelsScenarios_002.target to L03.io.fr16Inputs.field01;
        bind modelsScenarios.field002 = modelsScenarios_002.source;
        perform action modelsScenarios_003 : Map_modelsScenarios_003;
        flow modelsScenarios_003_source from L02.io.fr25Outputs.field01 to modelsScenarios_003.source;
        flow modelsScenarios_003_target from modelsScenarios_003.target to L03.io.fr16Inputs.field02;
        bind modelsScenarios.field003 = modelsScenarios_003.source;
        perform action modelsScenarios_004 : Map_modelsScenarios_004;
        flow modelsScenarios_004_source from L02.io.fr15Outputs.field01 to modelsScenarios_004.source;
        flow modelsScenarios_004_target from modelsScenarios_004.target to L03.io.fr18Inputs.field01;
        bind modelsScenarios.field004 = modelsScenarios_004.source;
        perform action modelsScenarios_005 : Map_modelsScenarios_005;
        flow modelsScenarios_005_source from L02.io.fr25Outputs.field01 to modelsScenarios_005.source;
        flow modelsScenarios_005_target from modelsScenarios_005.target to L03.io.fr18Inputs.field03;
        bind modelsScenarios.field005 = modelsScenarios_005.source;
        perform action modelsScenarios_006 : Map_modelsScenarios_006;
        flow modelsScenarios_006_source from L02.io.fr25Outputs.field01 to modelsScenarios_006.source;
        flow modelsScenarios_006_target from modelsScenarios_006.target to L03.io.fr19Inputs.field02;
        bind modelsScenarios.field006 = modelsScenarios_006.source;
        perform action modelsScenarios_007 : Map_modelsScenarios_007;
        flow modelsScenarios_007_source from L02.io.fr15Outputs.field01 to modelsScenarios_007.source;
        flow modelsScenarios_007_target from modelsScenarios_007.target to L03.io.fr19Inputs.field01;
        bind modelsScenarios.field007 = modelsScenarios_007.source;
        perform action modelsScenarios_008 : Map_modelsScenarios_008;
        flow modelsScenarios_008_source from L02.io.fr15Outputs.field01 to modelsScenarios_008.source;
        flow modelsScenarios_008_target from modelsScenarios_008.target to L03.io.fr26Inputs.field01;
        bind modelsScenarios.field008 = modelsScenarios_008.source;
        perform action modelsScenarios_009 : Map_modelsScenarios_009;
        flow modelsScenarios_009_source from L02.io.fr25Outputs.field01 to modelsScenarios_009.source;
        flow modelsScenarios_009_target from modelsScenarios_009.target to L03.io.fr26Inputs.field02;
        bind modelsScenarios.field009 = modelsScenarios_009.source;
        perform action modelsScenarios_010 : Map_modelsScenarios_010;
        flow modelsScenarios_010_source from L02.io.fr15Outputs.field01 to modelsScenarios_010.source;
        flow modelsScenarios_010_target from modelsScenarios_010.target to L03.io.fr27Inputs.field01;
        bind modelsScenarios.field010 = modelsScenarios_010.source;
        perform action modelsScenarios_011 : Map_modelsScenarios_011;
        flow modelsScenarios_011_source from L02.io.fr15Outputs.field01 to modelsScenarios_011.source;
        flow modelsScenarios_011_target from modelsScenarios_011.target to L03.io.fr27Inputs.field02;
        bind modelsScenarios.field011 = modelsScenarios_011.source;
        perform action modelsScenarios_012 : Map_modelsScenarios_012;
        flow modelsScenarios_012_source from L02.io.fr33Outputs.field01 to modelsScenarios_012.source;
        flow modelsScenarios_012_target from modelsScenarios_012.target to L03.io.fr34Inputs.field01;
        bind modelsScenarios.field012 = modelsScenarios_012.source;
        perform action modelsScenarios_013 : Map_modelsScenarios_013;
        flow modelsScenarios_013_source from L02.io.fr35Outputs.field01 to modelsScenarios_013.source;
        flow modelsScenarios_013_target from modelsScenarios_013.target to L03.io.fr34Inputs.field01;
        bind modelsScenarios.field013 = modelsScenarios_013.source;
        perform action modelsScenarios_014 : Map_modelsScenarios_014;
        flow modelsScenarios_014_source from L02.io.fr35Outputs.field01 to modelsScenarios_014.source;
        flow modelsScenarios_014_target from modelsScenarios_014.target to L03.io.fr19Inputs.field01;
        bind modelsScenarios.field014 = modelsScenarios_014.source;
        perform action modelsScenarios_015 : Map_modelsScenarios_015;
        flow modelsScenarios_015_source from L02.io.fr33Outputs.field01 to modelsScenarios_015.source;
        flow modelsScenarios_015_target from modelsScenarios_015.target to L03.io.fr18Inputs.field05;
        bind modelsScenarios.field015 = modelsScenarios_015.source;
        perform action modelsScenarios_016 : Map_modelsScenarios_016;
        flow modelsScenarios_016_source from L02.io.fr33Outputs.field01 to modelsScenarios_016.source;
        flow modelsScenarios_016_target from modelsScenarios_016.target to L03.io.fr36Inputs.field01;
        bind modelsScenarios.field016 = modelsScenarios_016.source;
        ref item designStudyResults : DesignStudyResultsExchange [0..*]; // design-study results
        perform action designStudyResults_001 : Map_designStudyResults_001;
        flow designStudyResults_001_source from L03.io.fr16Outputs.field01 to designStudyResults_001.source;
        flow designStudyResults_001_target from designStudyResults_001.target to L02.io.fr14Inputs.field01;
        bind designStudyResults.field001 = designStudyResults_001.source;
        perform action designStudyResults_002 : Map_designStudyResults_002;
        flow designStudyResults_002_source from L03.io.fr16Outputs.field02 to designStudyResults_002.source;
        flow designStudyResults_002_target from designStudyResults_002.target to L02.io.fr14Inputs.field01;
        bind designStudyResults.field002 = designStudyResults_002.source;
        perform action designStudyResults_003 : Map_designStudyResults_003;
        flow designStudyResults_003_source from L03.io.fr16Outputs.field03 to designStudyResults_003.source;
        flow designStudyResults_003_target from designStudyResults_003.target to L02.io.fr14Inputs.field01;
        bind designStudyResults.field003 = designStudyResults_003.source;
        perform action designStudyResults_004 : Map_designStudyResults_004;
        flow designStudyResults_004_source from L03.io.fr27Outputs.field01 to designStudyResults_004.source;
        flow designStudyResults_004_target from designStudyResults_004.target to L02.io.fr14Inputs.field01;
        bind designStudyResults.field004 = designStudyResults_004.source;
        perform action designStudyResults_005 : Map_designStudyResults_005;
        flow designStudyResults_005_source from L03.io.fr18Outputs.field06 to designStudyResults_005.source;
        flow designStudyResults_005_target from designStudyResults_005.target to L02.io.fr14Inputs.field01;
        bind designStudyResults.field005 = designStudyResults_005.source;
        perform action designStudyResults_006 : Map_designStudyResults_006;
        flow designStudyResults_006_source from L03.io.fr16Outputs.field01 to designStudyResults_006.source;
        flow designStudyResults_006_target from designStudyResults_006.target to L02.io.fr15Inputs.field01;
        bind designStudyResults.field006 = designStudyResults_006.source;
        ref item runHistories : RunHistoriesExchange [0..*]; // run histories
        perform action runHistories_001 : Map_runHistories_001;
        flow runHistories_001_source from L03.io.fr16Outputs.field01 to runHistories_001.source;
        flow runHistories_001_target from runHistories_001.target to L04.io.fr21Inputs.field01;
        bind runHistories.field001 = runHistories_001.source;
        perform action runHistories_002 : Map_runHistories_002;
        flow runHistories_002_source from L03.io.fr16Outputs.field02 to runHistories_002.source;
        flow runHistories_002_target from runHistories_002.target to L04.io.fr21Inputs.field03;
        bind runHistories.field002 = runHistories_002.source;
        perform action runHistories_003 : Map_runHistories_003;
        flow runHistories_003_source from L03.io.fr16Outputs.field03 to runHistories_003.source;
        flow runHistories_003_target from runHistories_003.target to L04.io.fr32Inputs.field01;
        bind runHistories.field003 = runHistories_003.source;
        perform action runHistories_004 : Map_runHistories_004;
        flow runHistories_004_source from L03.io.fr16Outputs.field03 to runHistories_004.source;
        flow runHistories_004_target from runHistories_004.target to L04.io.fr31Inputs.field01;
        bind runHistories.field004 = runHistories_004.source;
        perform action runHistories_005 : Map_runHistories_005;
        flow runHistories_005_source from L03.io.fr18Outputs.field03 to runHistories_005.source;
        flow runHistories_005_target from runHistories_005.target to L04.io.fr31Inputs.field01;
        bind runHistories.field005 = runHistories_005.source;
        perform action runHistories_006 : Map_runHistories_006;
        flow runHistories_006_source from L03.io.fr24Outputs.field02 to runHistories_006.source;
        flow runHistories_006_target from runHistories_006.target to L04.io.fr31Inputs.field01;
        bind runHistories.field006 = runHistories_006.source;
        perform action runHistories_007 : Map_runHistories_007;
        flow runHistories_007_source from L03.io.fr18Outputs.field03 to runHistories_007.source;
        flow runHistories_007_target from runHistories_007.target to L04.io.fr21Inputs.field03;
        bind runHistories.field007 = runHistories_007.source;
        perform action runHistories_008 : Map_runHistories_008;
        flow runHistories_008_source from L03.io.fr18Outputs.field06 to runHistories_008.source;
        flow runHistories_008_target from runHistories_008.target to L04.io.fr21Inputs.field02;
        bind runHistories.field008 = runHistories_008.source;
        perform action runHistories_009 : Map_runHistories_009;
        flow runHistories_009_source from L03.io.fr19Outputs.field02 to runHistories_009.source;
        flow runHistories_009_target from runHistories_009.target to L04.io.fr32Inputs.field01;
        bind runHistories.field009 = runHistories_009.source;
        perform action runHistories_010 : Map_runHistories_010;
        flow runHistories_010_source from L03.io.fr19Outputs.field03 to runHistories_010.source;
        flow runHistories_010_target from runHistories_010.target to L04.io.fr21Inputs.field01;
        bind runHistories.field010 = runHistories_010.source;
        perform action runHistories_011 : Map_runHistories_011;
        flow runHistories_011_source from L03.io.fr23Outputs.field01 to runHistories_011.source;
        flow runHistories_011_target from runHistories_011.target to L04.io.fr31Inputs.field03;
        bind runHistories.field011 = runHistories_011.source;
        perform action runHistories_012 : Map_runHistories_012;
        flow runHistories_012_source from L03.io.fr23Outputs.field02 to runHistories_012.source;
        flow runHistories_012_target from runHistories_012.target to L04.io.fr21Inputs.field03;
        bind runHistories.field012 = runHistories_012.source;
        perform action runHistories_013 : Map_runHistories_013;
        flow runHistories_013_source from L03.io.fr24Outputs.field02 to runHistories_013.source;
        flow runHistories_013_target from runHistories_013.target to L04.io.fr32Inputs.field01;
        bind runHistories.field013 = runHistories_013.source;
        perform action runHistories_014 : Map_runHistories_014;
        flow runHistories_014_source from L03.io.fr24Outputs.field04 to runHistories_014.source;
        flow runHistories_014_target from runHistories_014.target to L04.io.fr21Inputs.field01;
        bind runHistories.field014 = runHistories_014.source;
        perform action runHistories_015 : Map_runHistories_015;
        flow runHistories_015_source from L03.io.fr27Outputs.field01 to runHistories_015.source;
        flow runHistories_015_target from runHistories_015.target to L04.io.fr21Inputs.field01;
        bind runHistories.field015 = runHistories_015.source;
        ref item modelAssessment : ModelAssessmentExchange [0..*]; // model assessment
        perform action modelAssessment_001 : Map_modelAssessment_001;
        flow modelAssessment_001_source from L04.io.fr21Outputs.field01 to modelAssessment_001.source;
        flow modelAssessment_001_target from modelAssessment_001.target to L05.io.fr11Inputs.field01;
        bind modelAssessment.field001 = modelAssessment_001.source;
        perform action modelAssessment_002 : Map_modelAssessment_002;
        flow modelAssessment_002_source from L04.io.fr21Outputs.field02 to modelAssessment_002.source;
        flow modelAssessment_002_target from modelAssessment_002.target to L05.io.fr11Inputs.field01;
        bind modelAssessment.field002 = modelAssessment_002.source;
        perform action modelAssessment_003 : Map_modelAssessment_003;
        flow modelAssessment_003_source from L04.io.fr31Outputs.field01 to modelAssessment_003.source;
        flow modelAssessment_003_target from modelAssessment_003.target to L05.io.fr28Inputs.field03;
        bind modelAssessment.field003 = modelAssessment_003.source;
        perform action modelAssessment_004 : Map_modelAssessment_004;
        flow modelAssessment_004_source from L04.io.fr31Outputs.field03 to modelAssessment_004.source;
        flow modelAssessment_004_target from modelAssessment_004.target to L05.io.fr11Inputs.field01;
        bind modelAssessment.field004 = modelAssessment_004.source;
        perform action modelAssessment_005 : Map_modelAssessment_005;
        flow modelAssessment_005_source from L04.io.fr32Outputs.field01 to modelAssessment_005.source;
        flow modelAssessment_005_target from modelAssessment_005.target to L05.io.fr11Inputs.field01;
        bind modelAssessment.field005 = modelAssessment_005.source;
        perform action modelAssessment_006 : Map_modelAssessment_006;
        flow modelAssessment_006_source from L04.io.fr32Outputs.field02 to modelAssessment_006.source;
        flow modelAssessment_006_target from modelAssessment_006.target to L05.io.fr28Inputs.field03;
        bind modelAssessment.field006 = modelAssessment_006.source;
        perform action modelAssessment_007 : Map_modelAssessment_007;
        flow modelAssessment_007_source from L04.io.fr32Outputs.field03 to modelAssessment_007.source;
        flow modelAssessment_007_target from modelAssessment_007.target to L05.io.fr11Inputs.field01;
        bind modelAssessment.field007 = modelAssessment_007.source;
        perform action modelAssessment_008 : Map_modelAssessment_008;
        flow modelAssessment_008_source from L04.io.fr32Outputs.field04 to modelAssessment_008.source;
        flow modelAssessment_008_target from modelAssessment_008.target to L05.io.fr28Inputs.field03;
        bind modelAssessment.field008 = modelAssessment_008.source;
        perform action modelAssessment_009 : Map_modelAssessment_009;
        flow modelAssessment_009_source from L04.io.fr21Outputs.field01 to modelAssessment_009.source;
        flow modelAssessment_009_target from modelAssessment_009.target to L05.io.fr38Inputs.field03;
        bind modelAssessment.field009 = modelAssessment_009.source;
        ref item requirementBasisCoverage : RequirementBasisCoverageExchange [0..*]; // requirement basis / coverage
        perform action requirementBasisCoverage_001 : Map_requirementBasisCoverage_001;
        flow requirementBasisCoverage_001_source from L01.io.fr01Outputs.field01 to requirementBasisCoverage_001.source;
        flow requirementBasisCoverage_001_target from requirementBasisCoverage_001.target to L05.io.fr28Inputs.field01;
        bind requirementBasisCoverage.field001 = requirementBasisCoverage_001.source;
        perform action requirementBasisCoverage_002 : Map_requirementBasisCoverage_002;
        flow requirementBasisCoverage_002_source from L01.io.fr04Outputs.field01 to requirementBasisCoverage_002.source;
        flow requirementBasisCoverage_002_target from requirementBasisCoverage_002.target to L05.io.fr38Inputs.field03;
        bind requirementBasisCoverage.field002 = requirementBasisCoverage_002.source;
        perform action requirementBasisCoverage_003 : Map_requirementBasisCoverage_003;
        flow requirementBasisCoverage_003_source from L01.io.fr04Outputs.field02 to requirementBasisCoverage_003.source;
        flow requirementBasisCoverage_003_target from requirementBasisCoverage_003.target to L05.io.fr38Inputs.field03;
        bind requirementBasisCoverage.field003 = requirementBasisCoverage_003.source;
        perform action requirementBasisCoverage_004 : Map_requirementBasisCoverage_004;
        flow requirementBasisCoverage_004_source from L01.io.fr04Outputs.field03 to requirementBasisCoverage_004.source;
        flow requirementBasisCoverage_004_target from requirementBasisCoverage_004.target to L05.io.fr38Inputs.field03;
        bind requirementBasisCoverage.field004 = requirementBasisCoverage_004.source;
        perform action requirementBasisCoverage_005 : Map_requirementBasisCoverage_005;
        flow requirementBasisCoverage_005_source from L01.io.fr17Outputs.field01 to requirementBasisCoverage_005.source;
        flow requirementBasisCoverage_005_target from requirementBasisCoverage_005.target to L05.io.fr28Inputs.field01;
        bind requirementBasisCoverage.field005 = requirementBasisCoverage_005.source;
        ref item designConOpsProducts : DesignConOpsProductsExchange [0..*]; // design / ConOps products
        perform action designConOpsProducts_001 : Map_designConOpsProducts_001;
        flow designConOpsProducts_001_source from L02.io.fr13Outputs.field01 to designConOpsProducts_001.source;
        flow designConOpsProducts_001_target from designConOpsProducts_001.target to L05.io.fr38Inputs.field03;
        bind designConOpsProducts.field001 = designConOpsProducts_001.source;
        perform action designConOpsProducts_002 : Map_designConOpsProducts_002;
        flow designConOpsProducts_002_source from L02.io.fr14Outputs.field01 to designConOpsProducts_002.source;
        flow designConOpsProducts_002_target from designConOpsProducts_002.target to L05.io.fr38Inputs.field03;
        bind designConOpsProducts.field002 = designConOpsProducts_002.source;
        perform action designConOpsProducts_003 : Map_designConOpsProducts_003;
        flow designConOpsProducts_003_source from L02.io.fr15Outputs.field01 to designConOpsProducts_003.source;
        flow designConOpsProducts_003_target from designConOpsProducts_003.target to L05.io.fr28Inputs.field01;
        bind designConOpsProducts.field003 = designConOpsProducts_003.source;
        perform action designConOpsProducts_004 : Map_designConOpsProducts_004;
        flow designConOpsProducts_004_source from L02.io.fr20Outputs.field01 to designConOpsProducts_004.source;
        flow designConOpsProducts_004_target from designConOpsProducts_004.target to L05.io.fr38Inputs.field03;
        bind designConOpsProducts.field004 = designConOpsProducts_004.source;
        perform action designConOpsProducts_005 : Map_designConOpsProducts_005;
        flow designConOpsProducts_005_source from L02.io.fr25Outputs.field01 to designConOpsProducts_005.source;
        flow designConOpsProducts_005_target from designConOpsProducts_005.target to L05.io.fr28Inputs.field01;
        bind designConOpsProducts.field005 = designConOpsProducts_005.source;
        perform action designConOpsProducts_006 : Map_designConOpsProducts_006;
        flow designConOpsProducts_006_source from L02.io.fr33Outputs.field01 to designConOpsProducts_006.source;
        flow designConOpsProducts_006_target from designConOpsProducts_006.target to L05.io.fr38Inputs.field03;
        bind designConOpsProducts.field006 = designConOpsProducts_006.source;
        perform action designConOpsProducts_007 : Map_designConOpsProducts_007;
        flow designConOpsProducts_007_source from L02.io.fr35Outputs.field02 to designConOpsProducts_007.source;
        flow designConOpsProducts_007_target from designConOpsProducts_007.target to L05.io.fr38Inputs.field03;
        bind designConOpsProducts.field007 = designConOpsProducts_007.source;
        perform action designConOpsProducts_008 : Map_designConOpsProducts_008;
        flow designConOpsProducts_008_source from L02.io.fr15Outputs.field01 to designConOpsProducts_008.source;
        flow designConOpsProducts_008_target from designConOpsProducts_008.target to L05.io.fr37Inputs.field01;
        bind designConOpsProducts.field008 = designConOpsProducts_008.source;
        ref item assessmentCriteria : AssessmentCriteriaExchange [0..*]; // assessment criteria
        perform action assessmentCriteria_001 : Map_assessmentCriteria_001;
        flow assessmentCriteria_001_source from L05.io.fr28Outputs.field01 to assessmentCriteria_001.source;
        flow assessmentCriteria_001_target from assessmentCriteria_001.target to L03.io.fr19Inputs.field03;
        bind assessmentCriteria.field001 = assessmentCriteria_001.source;
        perform action assessmentCriteria_002 : Map_assessmentCriteria_002;
        flow assessmentCriteria_002_source from L05.io.fr28Outputs.field01 to assessmentCriteria_002.source;
        flow assessmentCriteria_002_target from assessmentCriteria_002.target to L03.io.fr24Inputs.field05;
        bind assessmentCriteria.field002 = assessmentCriteria_002.source;
        ref item maturityFindings : MaturityFindingsExchange [0..*]; // maturity / findings
        perform action maturityFindings_001 : Map_maturityFindings_001;
        flow maturityFindings_001_source from L05.io.fr11Outputs.field01 to maturityFindings_001.source;
        flow maturityFindings_001_target from maturityFindings_001.target to L01.io.fr39Inputs.field04;
        bind maturityFindings.field001 = maturityFindings_001.source;
        perform action maturityFindings_002 : Map_maturityFindings_002;
        flow maturityFindings_002_source from L05.io.fr38Outputs.field01 to maturityFindings_002.source;
        flow maturityFindings_002_target from maturityFindings_002.target to L01.io.fr39Inputs.field04;
        bind maturityFindings.field002 = maturityFindings_002.source;
        perform action maturityFindings_003 : Map_maturityFindings_003;
        flow maturityFindings_003_source from L05.io.fr42Outputs.field01 to maturityFindings_003.source;
        flow maturityFindings_003_target from maturityFindings_003.target to L01.io.fr39Inputs.field05;
        bind maturityFindings.field003 = maturityFindings_003.source;
        perform action maturityFindings_004 : Map_maturityFindings_004;
        flow maturityFindings_004_source from L05.io.fr42Outputs.field02 to maturityFindings_004.source;
        flow maturityFindings_004_target from maturityFindings_004.target to L01.io.fr03Inputs.field01;
        bind maturityFindings.field004 = maturityFindings_004.source;
        perform action maturityFindings_005 : Map_maturityFindings_005;
        flow maturityFindings_005_source from L05.io.fr42Outputs.field03 to maturityFindings_005.source;
        flow maturityFindings_005_target from maturityFindings_005.target to L01.io.fr39Inputs.field04;
        bind maturityFindings.field005 = maturityFindings_005.source;
        ref item preserveL01 : PreserveL01Exchange [0..*]; // identified records / decisions
        perform action preserveL01_001 : Map_preserveL01_001;
        flow preserveL01_001_source from L01.io.fr01Outputs.field01 to preserveL01_001.source;
        flow preserveL01_001_target from preserveL01_001.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field001 = preserveL01_001.source;
        perform action preserveL01_002 : Map_preserveL01_002;
        flow preserveL01_002_source from L01.io.fr01Outputs.field02 to preserveL01_002.source;
        flow preserveL01_002_target from preserveL01_002.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field002 = preserveL01_002.source;
        perform action preserveL01_003 : Map_preserveL01_003;
        flow preserveL01_003_source from L01.io.fr02Outputs.field01 to preserveL01_003.source;
        flow preserveL01_003_target from preserveL01_003.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field003 = preserveL01_003.source;
        perform action preserveL01_004 : Map_preserveL01_004;
        flow preserveL01_004_source from L01.io.fr02Outputs.field02 to preserveL01_004.source;
        flow preserveL01_004_target from preserveL01_004.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field004 = preserveL01_004.source;
        perform action preserveL01_005 : Map_preserveL01_005;
        flow preserveL01_005_source from L01.io.fr02Outputs.field03 to preserveL01_005.source;
        flow preserveL01_005_target from preserveL01_005.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field005 = preserveL01_005.source;
        perform action preserveL01_006 : Map_preserveL01_006;
        flow preserveL01_006_source from L01.io.fr03Outputs.field01 to preserveL01_006.source;
        flow preserveL01_006_target from preserveL01_006.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field006 = preserveL01_006.source;
        perform action preserveL01_007 : Map_preserveL01_007;
        flow preserveL01_007_source from L01.io.fr03Outputs.field02 to preserveL01_007.source;
        flow preserveL01_007_target from preserveL01_007.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field007 = preserveL01_007.source;
        perform action preserveL01_008 : Map_preserveL01_008;
        flow preserveL01_008_source from L01.io.fr03Outputs.field03 to preserveL01_008.source;
        flow preserveL01_008_target from preserveL01_008.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field008 = preserveL01_008.source;
        perform action preserveL01_009 : Map_preserveL01_009;
        flow preserveL01_009_source from L01.io.fr04Outputs.field01 to preserveL01_009.source;
        flow preserveL01_009_target from preserveL01_009.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field009 = preserveL01_009.source;
        perform action preserveL01_010 : Map_preserveL01_010;
        flow preserveL01_010_source from L01.io.fr04Outputs.field02 to preserveL01_010.source;
        flow preserveL01_010_target from preserveL01_010.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field010 = preserveL01_010.source;
        perform action preserveL01_011 : Map_preserveL01_011;
        flow preserveL01_011_source from L01.io.fr04Outputs.field03 to preserveL01_011.source;
        flow preserveL01_011_target from preserveL01_011.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field011 = preserveL01_011.source;
        perform action preserveL01_012 : Map_preserveL01_012;
        flow preserveL01_012_source from L01.io.fr17Outputs.field01 to preserveL01_012.source;
        flow preserveL01_012_target from preserveL01_012.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field012 = preserveL01_012.source;
        perform action preserveL01_013 : Map_preserveL01_013;
        flow preserveL01_013_source from L01.io.fr17Outputs.field02 to preserveL01_013.source;
        flow preserveL01_013_target from preserveL01_013.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field013 = preserveL01_013.source;
        perform action preserveL01_014 : Map_preserveL01_014;
        flow preserveL01_014_source from L01.io.fr17Outputs.field03 to preserveL01_014.source;
        flow preserveL01_014_target from preserveL01_014.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field014 = preserveL01_014.source;
        perform action preserveL01_015 : Map_preserveL01_015;
        flow preserveL01_015_source from L01.io.fr29Outputs.field01 to preserveL01_015.source;
        flow preserveL01_015_target from preserveL01_015.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field015 = preserveL01_015.source;
        perform action preserveL01_016 : Map_preserveL01_016;
        flow preserveL01_016_source from L01.io.fr29Outputs.field02 to preserveL01_016.source;
        flow preserveL01_016_target from preserveL01_016.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field016 = preserveL01_016.source;
        perform action preserveL01_017 : Map_preserveL01_017;
        flow preserveL01_017_source from L01.io.fr29Outputs.field03 to preserveL01_017.source;
        flow preserveL01_017_target from preserveL01_017.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field017 = preserveL01_017.source;
        perform action preserveL01_018 : Map_preserveL01_018;
        flow preserveL01_018_source from L01.io.fr39Outputs.field01 to preserveL01_018.source;
        flow preserveL01_018_target from preserveL01_018.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field018 = preserveL01_018.source;
        perform action preserveL01_019 : Map_preserveL01_019;
        flow preserveL01_019_source from L01.io.fr39Outputs.field02 to preserveL01_019.source;
        flow preserveL01_019_target from preserveL01_019.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field019 = preserveL01_019.source;
        perform action preserveL01_020 : Map_preserveL01_020;
        flow preserveL01_020_source from L01.io.fr39Outputs.field03 to preserveL01_020.source;
        flow preserveL01_020_target from preserveL01_020.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field020 = preserveL01_020.source;
        perform action preserveL01_021 : Map_preserveL01_021;
        flow preserveL01_021_source from L01.io.fr41Outputs.field01 to preserveL01_021.source;
        flow preserveL01_021_target from preserveL01_021.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field021 = preserveL01_021.source;
        perform action preserveL01_022 : Map_preserveL01_022;
        flow preserveL01_022_source from L01.io.fr41Outputs.field02 to preserveL01_022.source;
        flow preserveL01_022_target from preserveL01_022.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field022 = preserveL01_022.source;
        perform action preserveL01_023 : Map_preserveL01_023;
        flow preserveL01_023_source from L01.io.fr41Outputs.field03 to preserveL01_023.source;
        flow preserveL01_023_target from preserveL01_023.target to L06.io.fr07Inputs.field01;
        bind preserveL01.field023 = preserveL01_023.source;
        perform action preserveL01_024 : Map_preserveL01_024;
        flow preserveL01_024_source from L01.io.fr29Outputs.field01 to preserveL01_024.source;
        flow preserveL01_024_target from preserveL01_024.target to L06.io.fr07Inputs.field02;
        bind preserveL01.field024 = preserveL01_024.source;
        perform action preserveL01_025 : Map_preserveL01_025;
        flow preserveL01_025_source from L01.io.fr17Outputs.field03 to preserveL01_025.source;
        flow preserveL01_025_target from preserveL01_025.target to L06.io.fr06Inputs.field03;
        bind preserveL01.field025 = preserveL01_025.source;
        ref item preserveL02 : PreserveL02Exchange [0..*]; // identified records / decisions
        perform action preserveL02_001 : Map_preserveL02_001;
        flow preserveL02_001_source from L02.io.fr13Outputs.field01 to preserveL02_001.source;
        flow preserveL02_001_target from preserveL02_001.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field001 = preserveL02_001.source;
        perform action preserveL02_002 : Map_preserveL02_002;
        flow preserveL02_002_source from L02.io.fr14Outputs.field01 to preserveL02_002.source;
        flow preserveL02_002_target from preserveL02_002.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field002 = preserveL02_002.source;
        perform action preserveL02_003 : Map_preserveL02_003;
        flow preserveL02_003_source from L02.io.fr14Outputs.field02 to preserveL02_003.source;
        flow preserveL02_003_target from preserveL02_003.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field003 = preserveL02_003.source;
        perform action preserveL02_004 : Map_preserveL02_004;
        flow preserveL02_004_source from L02.io.fr14Outputs.field03 to preserveL02_004.source;
        flow preserveL02_004_target from preserveL02_004.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field004 = preserveL02_004.source;
        perform action preserveL02_005 : Map_preserveL02_005;
        flow preserveL02_005_source from L02.io.fr14Outputs.field04 to preserveL02_005.source;
        flow preserveL02_005_target from preserveL02_005.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field005 = preserveL02_005.source;
        perform action preserveL02_006 : Map_preserveL02_006;
        flow preserveL02_006_source from L02.io.fr15Outputs.field01 to preserveL02_006.source;
        flow preserveL02_006_target from preserveL02_006.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field006 = preserveL02_006.source;
        perform action preserveL02_007 : Map_preserveL02_007;
        flow preserveL02_007_source from L02.io.fr20Outputs.field01 to preserveL02_007.source;
        flow preserveL02_007_target from preserveL02_007.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field007 = preserveL02_007.source;
        perform action preserveL02_008 : Map_preserveL02_008;
        flow preserveL02_008_source from L02.io.fr20Outputs.field02 to preserveL02_008.source;
        flow preserveL02_008_target from preserveL02_008.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field008 = preserveL02_008.source;
        perform action preserveL02_009 : Map_preserveL02_009;
        flow preserveL02_009_source from L02.io.fr25Outputs.field01 to preserveL02_009.source;
        flow preserveL02_009_target from preserveL02_009.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field009 = preserveL02_009.source;
        perform action preserveL02_010 : Map_preserveL02_010;
        flow preserveL02_010_source from L02.io.fr33Outputs.field01 to preserveL02_010.source;
        flow preserveL02_010_target from preserveL02_010.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field010 = preserveL02_010.source;
        perform action preserveL02_011 : Map_preserveL02_011;
        flow preserveL02_011_source from L02.io.fr35Outputs.field01 to preserveL02_011.source;
        flow preserveL02_011_target from preserveL02_011.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field011 = preserveL02_011.source;
        perform action preserveL02_012 : Map_preserveL02_012;
        flow preserveL02_012_source from L02.io.fr35Outputs.field02 to preserveL02_012.source;
        flow preserveL02_012_target from preserveL02_012.target to L06.io.fr07Inputs.field01;
        bind preserveL02.field012 = preserveL02_012.source;
        perform action preserveL02_013 : Map_preserveL02_013;
        flow preserveL02_013_source from L02.io.fr14Outputs.field04 to preserveL02_013.source;
        flow preserveL02_013_target from preserveL02_013.target to L06.io.fr07Inputs.field02;
        bind preserveL02.field013 = preserveL02_013.source;
        perform action preserveL02_014 : Map_preserveL02_014;
        flow preserveL02_014_source from L02.io.fr14Outputs.field01 to preserveL02_014.source;
        flow preserveL02_014_target from preserveL02_014.target to L06.io.fr05Inputs.field01;
        bind preserveL02.field014 = preserveL02_014.source;
        ref item preserveL03 : PreserveL03Exchange [0..*]; // identified records / decisions
        perform action preserveL03_001 : Map_preserveL03_001;
        flow preserveL03_001_source from L03.io.fr10Outputs.field01 to preserveL03_001.source;
        flow preserveL03_001_target from preserveL03_001.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field001 = preserveL03_001.source;
        perform action preserveL03_002 : Map_preserveL03_002;
        flow preserveL03_002_source from L03.io.fr10Outputs.field02 to preserveL03_002.source;
        flow preserveL03_002_target from preserveL03_002.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field002 = preserveL03_002.source;
        perform action preserveL03_003 : Map_preserveL03_003;
        flow preserveL03_003_source from L03.io.fr10Outputs.field03 to preserveL03_003.source;
        flow preserveL03_003_target from preserveL03_003.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field003 = preserveL03_003.source;
        perform action preserveL03_004 : Map_preserveL03_004;
        flow preserveL03_004_source from L03.io.fr16Outputs.field01 to preserveL03_004.source;
        flow preserveL03_004_target from preserveL03_004.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field004 = preserveL03_004.source;
        perform action preserveL03_005 : Map_preserveL03_005;
        flow preserveL03_005_source from L03.io.fr16Outputs.field02 to preserveL03_005.source;
        flow preserveL03_005_target from preserveL03_005.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field005 = preserveL03_005.source;
        perform action preserveL03_006 : Map_preserveL03_006;
        flow preserveL03_006_source from L03.io.fr16Outputs.field03 to preserveL03_006.source;
        flow preserveL03_006_target from preserveL03_006.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field006 = preserveL03_006.source;
        perform action preserveL03_007 : Map_preserveL03_007;
        flow preserveL03_007_source from L03.io.fr18Outputs.field01 to preserveL03_007.source;
        flow preserveL03_007_target from preserveL03_007.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field007 = preserveL03_007.source;
        perform action preserveL03_008 : Map_preserveL03_008;
        flow preserveL03_008_source from L03.io.fr18Outputs.field02 to preserveL03_008.source;
        flow preserveL03_008_target from preserveL03_008.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field008 = preserveL03_008.source;
        perform action preserveL03_009 : Map_preserveL03_009;
        flow preserveL03_009_source from L03.io.fr18Outputs.field03 to preserveL03_009.source;
        flow preserveL03_009_target from preserveL03_009.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field009 = preserveL03_009.source;
        perform action preserveL03_010 : Map_preserveL03_010;
        flow preserveL03_010_source from L03.io.fr18Outputs.field04 to preserveL03_010.source;
        flow preserveL03_010_target from preserveL03_010.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field010 = preserveL03_010.source;
        perform action preserveL03_011 : Map_preserveL03_011;
        flow preserveL03_011_source from L03.io.fr18Outputs.field05 to preserveL03_011.source;
        flow preserveL03_011_target from preserveL03_011.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field011 = preserveL03_011.source;
        perform action preserveL03_012 : Map_preserveL03_012;
        flow preserveL03_012_source from L03.io.fr18Outputs.field06 to preserveL03_012.source;
        flow preserveL03_012_target from preserveL03_012.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field012 = preserveL03_012.source;
        perform action preserveL03_013 : Map_preserveL03_013;
        flow preserveL03_013_source from L03.io.fr19Outputs.field01 to preserveL03_013.source;
        flow preserveL03_013_target from preserveL03_013.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field013 = preserveL03_013.source;
        perform action preserveL03_014 : Map_preserveL03_014;
        flow preserveL03_014_source from L03.io.fr19Outputs.field02 to preserveL03_014.source;
        flow preserveL03_014_target from preserveL03_014.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field014 = preserveL03_014.source;
        perform action preserveL03_015 : Map_preserveL03_015;
        flow preserveL03_015_source from L03.io.fr19Outputs.field03 to preserveL03_015.source;
        flow preserveL03_015_target from preserveL03_015.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field015 = preserveL03_015.source;
        perform action preserveL03_016 : Map_preserveL03_016;
        flow preserveL03_016_source from L03.io.fr23Outputs.field01 to preserveL03_016.source;
        flow preserveL03_016_target from preserveL03_016.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field016 = preserveL03_016.source;
        perform action preserveL03_017 : Map_preserveL03_017;
        flow preserveL03_017_source from L03.io.fr23Outputs.field02 to preserveL03_017.source;
        flow preserveL03_017_target from preserveL03_017.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field017 = preserveL03_017.source;
        perform action preserveL03_018 : Map_preserveL03_018;
        flow preserveL03_018_source from L03.io.fr24Outputs.field01 to preserveL03_018.source;
        flow preserveL03_018_target from preserveL03_018.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field018 = preserveL03_018.source;
        perform action preserveL03_019 : Map_preserveL03_019;
        flow preserveL03_019_source from L03.io.fr24Outputs.field02 to preserveL03_019.source;
        flow preserveL03_019_target from preserveL03_019.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field019 = preserveL03_019.source;
        perform action preserveL03_020 : Map_preserveL03_020;
        flow preserveL03_020_source from L03.io.fr24Outputs.field03 to preserveL03_020.source;
        flow preserveL03_020_target from preserveL03_020.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field020 = preserveL03_020.source;
        perform action preserveL03_021 : Map_preserveL03_021;
        flow preserveL03_021_source from L03.io.fr24Outputs.field04 to preserveL03_021.source;
        flow preserveL03_021_target from preserveL03_021.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field021 = preserveL03_021.source;
        perform action preserveL03_022 : Map_preserveL03_022;
        flow preserveL03_022_source from L03.io.fr26Outputs.field01 to preserveL03_022.source;
        flow preserveL03_022_target from preserveL03_022.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field022 = preserveL03_022.source;
        perform action preserveL03_023 : Map_preserveL03_023;
        flow preserveL03_023_source from L03.io.fr26Outputs.field02 to preserveL03_023.source;
        flow preserveL03_023_target from preserveL03_023.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field023 = preserveL03_023.source;
        perform action preserveL03_024 : Map_preserveL03_024;
        flow preserveL03_024_source from L03.io.fr26Outputs.field03 to preserveL03_024.source;
        flow preserveL03_024_target from preserveL03_024.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field024 = preserveL03_024.source;
        perform action preserveL03_025 : Map_preserveL03_025;
        flow preserveL03_025_source from L03.io.fr26Outputs.field04 to preserveL03_025.source;
        flow preserveL03_025_target from preserveL03_025.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field025 = preserveL03_025.source;
        perform action preserveL03_026 : Map_preserveL03_026;
        flow preserveL03_026_source from L03.io.fr27Outputs.field01 to preserveL03_026.source;
        flow preserveL03_026_target from preserveL03_026.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field026 = preserveL03_026.source;
        perform action preserveL03_027 : Map_preserveL03_027;
        flow preserveL03_027_source from L03.io.fr34Outputs.field01 to preserveL03_027.source;
        flow preserveL03_027_target from preserveL03_027.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field027 = preserveL03_027.source;
        perform action preserveL03_028 : Map_preserveL03_028;
        flow preserveL03_028_source from L03.io.fr34Outputs.field02 to preserveL03_028.source;
        flow preserveL03_028_target from preserveL03_028.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field028 = preserveL03_028.source;
        perform action preserveL03_029 : Map_preserveL03_029;
        flow preserveL03_029_source from L03.io.fr34Outputs.field03 to preserveL03_029.source;
        flow preserveL03_029_target from preserveL03_029.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field029 = preserveL03_029.source;
        perform action preserveL03_030 : Map_preserveL03_030;
        flow preserveL03_030_source from L03.io.fr36Outputs.field01 to preserveL03_030.source;
        flow preserveL03_030_target from preserveL03_030.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field030 = preserveL03_030.source;
        perform action preserveL03_031 : Map_preserveL03_031;
        flow preserveL03_031_source from L03.io.fr36Outputs.field02 to preserveL03_031.source;
        flow preserveL03_031_target from preserveL03_031.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field031 = preserveL03_031.source;
        perform action preserveL03_032 : Map_preserveL03_032;
        flow preserveL03_032_source from L03.io.fr36Outputs.field03 to preserveL03_032.source;
        flow preserveL03_032_target from preserveL03_032.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field032 = preserveL03_032.source;
        perform action preserveL03_033 : Map_preserveL03_033;
        flow preserveL03_033_source from L03.io.fr36Outputs.field04 to preserveL03_033.source;
        flow preserveL03_033_target from preserveL03_033.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field033 = preserveL03_033.source;
        perform action preserveL03_034 : Map_preserveL03_034;
        flow preserveL03_034_source from L03.io.fr36Outputs.field05 to preserveL03_034.source;
        flow preserveL03_034_target from preserveL03_034.target to L06.io.fr07Inputs.field01;
        bind preserveL03.field034 = preserveL03_034.source;
        perform action preserveL03_035 : Map_preserveL03_035;
        flow preserveL03_035_source from L03.io.fr16Outputs.field01 to preserveL03_035.source;
        flow preserveL03_035_target from preserveL03_035.target to L06.io.fr09Inputs.field01;
        bind preserveL03.field035 = preserveL03_035.source;
        perform action preserveL03_036 : Map_preserveL03_036;
        flow preserveL03_036_source from L03.io.fr23Outputs.field01 to preserveL03_036.source;
        flow preserveL03_036_target from preserveL03_036.target to L06.io.fr09Inputs.field02;
        bind preserveL03.field036 = preserveL03_036.source;
        perform action preserveL03_037 : Map_preserveL03_037;
        flow preserveL03_037_source from L03.io.fr24Outputs.field04 to preserveL03_037.source;
        flow preserveL03_037_target from preserveL03_037.target to L06.io.fr09Inputs.field04;
        bind preserveL03.field037 = preserveL03_037.source;
        ref item preserveL04 : PreserveL04Exchange [0..*]; // identified records / decisions
        perform action preserveL04_001 : Map_preserveL04_001;
        flow preserveL04_001_source from L04.io.fr21Outputs.field01 to preserveL04_001.source;
        flow preserveL04_001_target from preserveL04_001.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field001 = preserveL04_001.source;
        perform action preserveL04_002 : Map_preserveL04_002;
        flow preserveL04_002_source from L04.io.fr21Outputs.field02 to preserveL04_002.source;
        flow preserveL04_002_target from preserveL04_002.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field002 = preserveL04_002.source;
        perform action preserveL04_003 : Map_preserveL04_003;
        flow preserveL04_003_source from L04.io.fr22Outputs.field01 to preserveL04_003.source;
        flow preserveL04_003_target from preserveL04_003.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field003 = preserveL04_003.source;
        perform action preserveL04_004 : Map_preserveL04_004;
        flow preserveL04_004_source from L04.io.fr22Outputs.field02 to preserveL04_004.source;
        flow preserveL04_004_target from preserveL04_004.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field004 = preserveL04_004.source;
        perform action preserveL04_005 : Map_preserveL04_005;
        flow preserveL04_005_source from L04.io.fr22Outputs.field03 to preserveL04_005.source;
        flow preserveL04_005_target from preserveL04_005.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field005 = preserveL04_005.source;
        perform action preserveL04_006 : Map_preserveL04_006;
        flow preserveL04_006_source from L04.io.fr22Outputs.field04 to preserveL04_006.source;
        flow preserveL04_006_target from preserveL04_006.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field006 = preserveL04_006.source;
        perform action preserveL04_007 : Map_preserveL04_007;
        flow preserveL04_007_source from L04.io.fr31Outputs.field01 to preserveL04_007.source;
        flow preserveL04_007_target from preserveL04_007.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field007 = preserveL04_007.source;
        perform action preserveL04_008 : Map_preserveL04_008;
        flow preserveL04_008_source from L04.io.fr31Outputs.field02 to preserveL04_008.source;
        flow preserveL04_008_target from preserveL04_008.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field008 = preserveL04_008.source;
        perform action preserveL04_009 : Map_preserveL04_009;
        flow preserveL04_009_source from L04.io.fr31Outputs.field03 to preserveL04_009.source;
        flow preserveL04_009_target from preserveL04_009.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field009 = preserveL04_009.source;
        perform action preserveL04_010 : Map_preserveL04_010;
        flow preserveL04_010_source from L04.io.fr31Outputs.field04 to preserveL04_010.source;
        flow preserveL04_010_target from preserveL04_010.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field010 = preserveL04_010.source;
        perform action preserveL04_011 : Map_preserveL04_011;
        flow preserveL04_011_source from L04.io.fr32Outputs.field01 to preserveL04_011.source;
        flow preserveL04_011_target from preserveL04_011.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field011 = preserveL04_011.source;
        perform action preserveL04_012 : Map_preserveL04_012;
        flow preserveL04_012_source from L04.io.fr32Outputs.field02 to preserveL04_012.source;
        flow preserveL04_012_target from preserveL04_012.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field012 = preserveL04_012.source;
        perform action preserveL04_013 : Map_preserveL04_013;
        flow preserveL04_013_source from L04.io.fr32Outputs.field03 to preserveL04_013.source;
        flow preserveL04_013_target from preserveL04_013.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field013 = preserveL04_013.source;
        perform action preserveL04_014 : Map_preserveL04_014;
        flow preserveL04_014_source from L04.io.fr32Outputs.field04 to preserveL04_014.source;
        flow preserveL04_014_target from preserveL04_014.target to L06.io.fr07Inputs.field01;
        bind preserveL04.field014 = preserveL04_014.source;
        perform action preserveL04_015 : Map_preserveL04_015;
        flow preserveL04_015_source from L04.io.fr22Outputs.field01 to preserveL04_015.source;
        flow preserveL04_015_target from preserveL04_015.target to L06.io.fr05Inputs.field01;
        bind preserveL04.field015 = preserveL04_015.source;
        perform action preserveL04_016 : Map_preserveL04_016;
        flow preserveL04_016_source from L04.io.fr22Outputs.field01 to preserveL04_016.source;
        flow preserveL04_016_target from preserveL04_016.target to L06.io.fr06Inputs.field02;
        bind preserveL04.field016 = preserveL04_016.source;
        ref item baselineDecisions : BaselineDecisionsExchange [0..*]; // baseline / decisions
        perform action baselineDecisions_001 : Map_baselineDecisions_001;
        flow baselineDecisions_001_source from L05.io.fr11Outputs.field01 to baselineDecisions_001.source;
        flow baselineDecisions_001_target from baselineDecisions_001.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field001 = baselineDecisions_001.source;
        perform action baselineDecisions_002 : Map_baselineDecisions_002;
        flow baselineDecisions_002_source from L05.io.fr11Outputs.field02 to baselineDecisions_002.source;
        flow baselineDecisions_002_target from baselineDecisions_002.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field002 = baselineDecisions_002.source;
        perform action baselineDecisions_003 : Map_baselineDecisions_003;
        flow baselineDecisions_003_source from L05.io.fr28Outputs.field01 to baselineDecisions_003.source;
        flow baselineDecisions_003_target from baselineDecisions_003.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field003 = baselineDecisions_003.source;
        perform action baselineDecisions_004 : Map_baselineDecisions_004;
        flow baselineDecisions_004_source from L05.io.fr28Outputs.field02 to baselineDecisions_004.source;
        flow baselineDecisions_004_target from baselineDecisions_004.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field004 = baselineDecisions_004.source;
        perform action baselineDecisions_005 : Map_baselineDecisions_005;
        flow baselineDecisions_005_source from L05.io.fr28Outputs.field03 to baselineDecisions_005.source;
        flow baselineDecisions_005_target from baselineDecisions_005.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field005 = baselineDecisions_005.source;
        perform action baselineDecisions_006 : Map_baselineDecisions_006;
        flow baselineDecisions_006_source from L05.io.fr37Outputs.field01 to baselineDecisions_006.source;
        flow baselineDecisions_006_target from baselineDecisions_006.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field006 = baselineDecisions_006.source;
        perform action baselineDecisions_007 : Map_baselineDecisions_007;
        flow baselineDecisions_007_source from L05.io.fr38Outputs.field01 to baselineDecisions_007.source;
        flow baselineDecisions_007_target from baselineDecisions_007.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field007 = baselineDecisions_007.source;
        perform action baselineDecisions_008 : Map_baselineDecisions_008;
        flow baselineDecisions_008_source from L05.io.fr42Outputs.field01 to baselineDecisions_008.source;
        flow baselineDecisions_008_target from baselineDecisions_008.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field008 = baselineDecisions_008.source;
        perform action baselineDecisions_009 : Map_baselineDecisions_009;
        flow baselineDecisions_009_source from L05.io.fr42Outputs.field02 to baselineDecisions_009.source;
        flow baselineDecisions_009_target from baselineDecisions_009.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field009 = baselineDecisions_009.source;
        perform action baselineDecisions_010 : Map_baselineDecisions_010;
        flow baselineDecisions_010_source from L05.io.fr42Outputs.field03 to baselineDecisions_010.source;
        flow baselineDecisions_010_target from baselineDecisions_010.target to L06.io.fr07Inputs.field01;
        bind baselineDecisions.field010 = baselineDecisions_010.source;
        perform action baselineDecisions_011 : Map_baselineDecisions_011;
        flow baselineDecisions_011_source from L05.io.fr42Outputs.field01 to baselineDecisions_011.source;
        flow baselineDecisions_011_target from baselineDecisions_011.target to L06.io.fr07Inputs.field02;
        bind baselineDecisions.field011 = baselineDecisions_011.source;
        perform action baselineDecisions_012 : Map_baselineDecisions_012;
        flow baselineDecisions_012_source from L05.io.fr42Outputs.field01 to baselineDecisions_012.source;
        flow baselineDecisions_012_target from baselineDecisions_012.target to L06.io.fr06Inputs.field03;
        bind baselineDecisions.field012 = baselineDecisions_012.source;
        ref item currentContext : CurrentContextExchange [0..*]; // current context
        perform action currentContext_001 : Map_currentContext_001;
        flow currentContext_001_source from L06.io.fr07Outputs.field01 to currentContext_001.source;
        flow currentContext_001_target from currentContext_001.target to L01.io.fr03Inputs.field03;
        bind currentContext.field001 = currentContext_001.source;
        perform action currentContext_002 : Map_currentContext_002;
        flow currentContext_002_source from L06.io.fr05Outputs.field03 to currentContext_002.source;
        flow currentContext_002_target from currentContext_002.target to L01.io.fr39Inputs.field03;
        bind currentContext.field002 = currentContext_002.source;
        perform action currentContext_003 : Map_currentContext_003;
        flow currentContext_003_source from L06.io.fr30Outputs.field01 to currentContext_003.source;
        flow currentContext_003_target from currentContext_003.target to L01.io.fr41Inputs.field02;
        bind currentContext.field003 = currentContext_003.source;
        perform action currentContext_004 : Map_currentContext_004;
        flow currentContext_004_source from L06.io.fr30Outputs.field03 to currentContext_004.source;
        flow currentContext_004_target from currentContext_004.target to L01.io.fr41Inputs.field01;
        bind currentContext.field004 = currentContext_004.source;
        perform action currentContext_005 : Map_currentContext_005;
        flow currentContext_005_source from L06.io.fr30Outputs.field03 to currentContext_005.source;
        flow currentContext_005_target from currentContext_005.target to L01.io.fr02Inputs.field01;
        bind currentContext.field005 = currentContext_005.source;
        perform action currentContext_006 : Map_currentContext_006;
        flow currentContext_006_source from L06.io.fr30Outputs.field03 to currentContext_006.source;
        flow currentContext_006_target from currentContext_006.target to L01.io.fr03Inputs.field01;
        bind currentContext.field006 = currentContext_006.source;
        perform action currentContext_007 : Map_currentContext_007;
        flow currentContext_007_source from L06.io.fr08Outputs.field01 to currentContext_007.source;
        flow currentContext_007_target from currentContext_007.target to L01.io.fr01Inputs.field01;
        bind currentContext.field007 = currentContext_007.source;
        perform action currentContext_008 : Map_currentContext_008;
        flow currentContext_008_source from L06.io.fr07Outputs.field01 to currentContext_008.source;
        flow currentContext_008_target from currentContext_008.target to L01.io.fr41Inputs.field02;
        bind currentContext.field008 = currentContext_008.source;
        ref item releaseRevisions : ReleaseRevisionsExchange [0..*]; // release / revisions
        perform action releaseRevisions_001 : Map_releaseRevisions_001;
        flow releaseRevisions_001_source from L06.io.fr07Outputs.field01 to releaseRevisions_001.source;
        flow releaseRevisions_001_target from releaseRevisions_001.target to L03.io.fr36Inputs.field01;
        bind releaseRevisions.field001 = releaseRevisions_001.source;
        perform action releaseRevisions_002 : Map_releaseRevisions_002;
        flow releaseRevisions_002_source from L06.io.fr06Outputs.field01 to releaseRevisions_002.source;
        flow releaseRevisions_002_target from releaseRevisions_002.target to L03.io.fr36Inputs.field04;
        bind releaseRevisions.field002 = releaseRevisions_002.source;
        perform action releaseRevisions_003 : Map_releaseRevisions_003;
        flow releaseRevisions_003_source from L06.io.fr09Outputs.field01 to releaseRevisions_003.source;
        flow releaseRevisions_003_target from releaseRevisions_003.target to L03.io.fr10Inputs.field02;
        bind releaseRevisions.field003 = releaseRevisions_003.source;
        perform action releaseRevisions_004 : Map_releaseRevisions_004;
        flow releaseRevisions_004_source from L06.io.fr08Outputs.field01 to releaseRevisions_004.source;
        flow releaseRevisions_004_target from releaseRevisions_004.target to L03.io.fr18Inputs.field06;
        bind releaseRevisions.field004 = releaseRevisions_004.source;
        perform action releaseRevisions_005 : Map_releaseRevisions_005;
        flow releaseRevisions_005_source from L06.io.fr30Outputs.field02 to releaseRevisions_005.source;
        flow releaseRevisions_005_target from releaseRevisions_005.target to L03.io.fr24Inputs.field01;
        bind releaseRevisions.field005 = releaseRevisions_005.source;
        ref item currentRecordsL02 : CurrentRecordsL02Exchange [0..*]; // admitted / current records
        perform action currentRecordsL02_001 : Map_currentRecordsL02_001;
        flow currentRecordsL02_001_source from L06.io.fr08Outputs.field01 to currentRecordsL02_001.source;
        flow currentRecordsL02_001_target from currentRecordsL02_001.target to L02.io.fr15Inputs.field01;
        bind currentRecordsL02.field001 = currentRecordsL02_001.source;
        perform action currentRecordsL02_002 : Map_currentRecordsL02_002;
        flow currentRecordsL02_002_source from L06.io.fr07Outputs.field01 to currentRecordsL02_002.source;
        flow currentRecordsL02_002_target from currentRecordsL02_002.target to L02.io.fr15Inputs.field01;
        bind currentRecordsL02.field002 = currentRecordsL02_002.source;
        perform action currentRecordsL02_003 : Map_currentRecordsL02_003;
        flow currentRecordsL02_003_source from L06.io.fr05Outputs.field01 to currentRecordsL02_003.source;
        flow currentRecordsL02_003_target from currentRecordsL02_003.target to L02.io.fr15Inputs.field01;
        bind currentRecordsL02.field003 = currentRecordsL02_003.source;
        perform action currentRecordsL02_004 : Map_currentRecordsL02_004;
        flow currentRecordsL02_004_source from L06.io.fr30Outputs.field01 to currentRecordsL02_004.source;
        flow currentRecordsL02_004_target from currentRecordsL02_004.target to L02.io.fr15Inputs.field01;
        bind currentRecordsL02.field004 = currentRecordsL02_004.source;
        ref item currentRecordsL04 : CurrentRecordsL04Exchange [0..*]; // admitted / current records
        perform action currentRecordsL04_001 : Map_currentRecordsL04_001;
        flow currentRecordsL04_001_source from L06.io.fr08Outputs.field01 to currentRecordsL04_001.source;
        flow currentRecordsL04_001_target from currentRecordsL04_001.target to L04.io.fr21Inputs.field03;
        bind currentRecordsL04.field001 = currentRecordsL04_001.source;
        perform action currentRecordsL04_002 : Map_currentRecordsL04_002;
        flow currentRecordsL04_002_source from L06.io.fr07Outputs.field01 to currentRecordsL04_002.source;
        flow currentRecordsL04_002_target from currentRecordsL04_002.target to L04.io.fr21Inputs.field03;
        bind currentRecordsL04.field002 = currentRecordsL04_002.source;
        perform action currentRecordsL04_003 : Map_currentRecordsL04_003;
        flow currentRecordsL04_003_source from L06.io.fr05Outputs.field01 to currentRecordsL04_003.source;
        flow currentRecordsL04_003_target from currentRecordsL04_003.target to L04.io.fr21Inputs.field03;
        bind currentRecordsL04.field003 = currentRecordsL04_003.source;
        perform action currentRecordsL04_004 : Map_currentRecordsL04_004;
        flow currentRecordsL04_004_source from L06.io.fr30Outputs.field01 to currentRecordsL04_004.source;
        flow currentRecordsL04_004_target from currentRecordsL04_004.target to L04.io.fr21Inputs.field03;
        bind currentRecordsL04.field004 = currentRecordsL04_004.source;
        ref item currentRecordsL05 : CurrentRecordsL05Exchange [0..*]; // admitted / current records
        perform action currentRecordsL05_001 : Map_currentRecordsL05_001;
        flow currentRecordsL05_001_source from L06.io.fr08Outputs.field01 to currentRecordsL05_001.source;
        flow currentRecordsL05_001_target from currentRecordsL05_001.target to L05.io.fr38Inputs.field03;
        bind currentRecordsL05.field001 = currentRecordsL05_001.source;
        perform action currentRecordsL05_002 : Map_currentRecordsL05_002;
        flow currentRecordsL05_002_source from L06.io.fr07Outputs.field01 to currentRecordsL05_002.source;
        flow currentRecordsL05_002_target from currentRecordsL05_002.target to L05.io.fr38Inputs.field03;
        bind currentRecordsL05.field002 = currentRecordsL05_002.source;
        perform action currentRecordsL05_003 : Map_currentRecordsL05_003;
        flow currentRecordsL05_003_source from L06.io.fr05Outputs.field01 to currentRecordsL05_003.source;
        flow currentRecordsL05_003_target from currentRecordsL05_003.target to L05.io.fr38Inputs.field03;
        bind currentRecordsL05.field003 = currentRecordsL05_003.source;
        perform action currentRecordsL05_004 : Map_currentRecordsL05_004;
        flow currentRecordsL05_004_source from L06.io.fr30Outputs.field01 to currentRecordsL05_004.source;
        flow currentRecordsL05_004_target from currentRecordsL05_004.target to L05.io.fr38Inputs.field03;
        bind currentRecordsL05.field004 = currentRecordsL05_004.source;
    }
    part logical : LogicalFramework;
    allocation guidanceControlOwner allocate logical.guidanceControl to logical.L06.assistanceCurrency;
    allocation baselineControlOwner allocate logical.baselineControl to logical.L05.reviewState;
    #primaryResponsibility allocation responsibility_FR_01_L01 allocate FrameworkRequirements::FR_01 to logical.L01 { @LogicalAllocation { rationale = "Shared complete typed FR-01 subjects and engineering meaning"; plannedCheck = "I,T: Round-trip quantitative and qualitative records, including unresolved criteria."; operation = RequirementsAssistance::retainRequirements meta SysML::ActionUsage; } }
    @NativeIO about RequirementsAssistance::contractFR01 { fr = "FR-01"; primary = "L01"; inputs = ("Requirement submissions", "source/parent revisions"); outputs = ("Retained requirement records", "field resolution status"); sourceLocator = "final_report/requirements.tex, FR-01 Inputs/Outputs; FrameworkRequirements::FR_01"; operation = RequirementsAssistance::retainRequirements meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR01 from FrameworkRequirements::FR_01 to RequirementsAssistance::retainRequirements;
    #primaryResponsibility allocation responsibility_FR_02_L01 allocate FrameworkRequirements::FR_02 to logical.L01 { @LogicalAllocation { rationale = "Shared complete typed FR-02 subjects and engineering meaning"; plannedCheck = "A,T: Compare clean and seeded drafts with an independent expert reference, including valid similar requirements and missed defects."; operation = RequirementsAssistance::checkDraft meta SysML::ActionUsage; } }
    @NativeIO about RequirementsAssistance::contractFR02 { fr = "FR-02"; primary = "L01"; inputs = ("Draft edits/requests", "current requirements", "rules", "sources", "coverage references"); outputs = ("Explained findings", "corrections/questions", "assessment limits"); sourceLocator = "final_report/requirements.tex, FR-02 Inputs/Outputs; FrameworkRequirements::FR_02"; operation = RequirementsAssistance::checkDraft meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR02 from FrameworkRequirements::FR_02 to RequirementsAssistance::checkDraft;
    #primaryResponsibility allocation responsibility_FR_03_L01 allocate FrameworkRequirements::FR_03 to logical.L01 { @LogicalAllocation { rationale = "Shared complete typed FR-03 subjects and engineering meaning"; plannedCheck = "A,T: Use contextual queries whose eligible methods change with inputs, maturity or intended use."; operation = RequirementsAssistance::recommend meta SysML::ActionUsage; } }
    @NativeIO about RequirementsAssistance::contractFR03 { fr = "FR-03"; primary = "L01"; inputs = ("Current phase/question", "requirements", "inputs", "validity", "resources", "scope"); outputs = ("Cited method/model recommendations", "alternatives", "rejection records"); sourceLocator = "final_report/requirements.tex, FR-03 Inputs/Outputs; FrameworkRequirements::FR_03"; operation = RequirementsAssistance::recommend meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR03 from FrameworkRequirements::FR_03 to RequirementsAssistance::recommend;
    #primaryResponsibility allocation responsibility_FR_04_L01 allocate FrameworkRequirements::FR_04 to logical.L01 { @LogicalAllocation { rationale = "Shared complete typed FR-04 subjects and engineering meaning"; plannedCheck = "T: Compare both query directions and coverage with a known relationship set."; operation = RequirementsAssistance::traceLinks meta SysML::ActionUsage; } }
    @NativeIO about RequirementsAssistance::contractFR04 { fr = "FR-04"; primary = "L01"; inputs = ("Trace query", "linked records", "declared reference set"); outputs = ("Forward/reverse links", "endpoint gaps", "coverage"); sourceLocator = "final_report/requirements.tex, FR-04 Inputs/Outputs; FrameworkRequirements::FR_04"; operation = RequirementsAssistance::traceLinks meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR04 from FrameworkRequirements::FR_04 to RequirementsAssistance::traceLinks;
    #primaryResponsibility allocation responsibility_FR_05_L06 allocate FrameworkRequirements::FR_05 to logical.L06 { @LogicalAllocation { rationale = "Shared complete typed FR-05 subjects and engineering meaning"; plannedCheck = "A,T: Compare the impact set of coupled load, pointing and interface changes with an expert reference."; operation = ConfigurationExchange::invalidate meta SysML::ActionUsage; } }
    @NativeIO about ConfigurationExchange::contractFR05 { fr = "FR-05"; primary = "L06"; inputs = ("Proposed change", "current engineering dependencies"); outputs = ("Reciprocal impacts", "unresolved dependencies", "required reassessments"); sourceLocator = "final_report/requirements.tex, FR-05 Inputs/Outputs; FrameworkRequirements::FR_05"; operation = ConfigurationExchange::invalidate meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR05 from FrameworkRequirements::FR_05 to ConfigurationExchange::invalidate;
    #primaryResponsibility allocation responsibility_FR_06_L06 allocate FrameworkRequirements::FR_06 to logical.L06 { @LogicalAllocation { rationale = "Shared complete typed FR-06 subjects and engineering meaning"; plannedCheck = "T: Accept, decline and interrupt changes without erasing the predecessor."; operation = ConfigurationExchange::successor meta SysML::ActionUsage; } }
    @NativeIO about ConfigurationExchange::contractFR06 { fr = "FR-06"; primary = "L06"; inputs = ("Predecessor baseline", "change request", "authorized change acceptance"); outputs = ("Successor baseline", "preserved predecessor", "product/evidence status"); sourceLocator = "final_report/requirements.tex, FR-06 Inputs/Outputs; FrameworkRequirements::FR_06"; operation = ConfigurationExchange::successor meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR06 from FrameworkRequirements::FR_06 to ConfigurationExchange::successor;
    #primaryResponsibility allocation responsibility_FR_07_L06 allocate FrameworkRequirements::FR_07 to logical.L06 { @LogicalAllocation { rationale = "Shared complete typed FR-07 subjects and engineering meaning"; plannedCheck = "I,T: Reconstruct predecessor and successor manifests and all applicable products."; operation = ConfigurationExchange::retrieveBaseline meta SysML::ActionUsage; } }
    @NativeIO about ConfigurationExchange::contractFR07 { fr = "FR-07"; primary = "L06"; inputs = ("Product/evidence revisions", "decisions", "baseline retrieval request"); outputs = ("Retrievable exact baselines", "revision/decision histories"); sourceLocator = "final_report/requirements.tex, FR-07 Inputs/Outputs; FrameworkRequirements::FR_07"; operation = ConfigurationExchange::retrieveBaseline meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR07 from FrameworkRequirements::FR_07 to ConfigurationExchange::retrieveBaseline;
    #primaryResponsibility allocation responsibility_FR_08_L06 allocate FrameworkRequirements::FR_08 to logical.L06 { @LogicalAllocation { rationale = "Shared complete typed FR-08 subjects and engineering meaning"; plannedCheck = "T: Inject identity, unit, sign and revision mismatches at each active interface."; operation = ConfigurationExchange::checkTransfer meta SysML::ActionUsage; } }
    @NativeIO about ConfigurationExchange::contractFR08 { fr = "FR-08"; primary = "L06"; inputs = ("Raw submissions", "declared interface specification"); outputs = ("Admitted transfers or retained rejections with unchanged controlled content"); sourceLocator = "final_report/requirements.tex, FR-08 Inputs/Outputs; FrameworkRequirements::FR_08"; operation = ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR08 from FrameworkRequirements::FR_08 to ConfigurationExchange::checkTransfer;
    #primaryResponsibility allocation responsibility_FR_09_L06 allocate FrameworkRequirements::FR_09 to logical.L06 { @LogicalAllocation { rationale = "Shared complete typed FR-09 subjects and engineering meaning"; plannedCheck = "I,T: Trace successful, failed, cancelled and partial outputs to their configurations."; operation = ConfigurationExchange::preserveRun meta SysML::ActionUsage; } }
    @NativeIO about ConfigurationExchange::contractFR09 { fr = "FR-09"; primary = "L06"; inputs = ("Analysis/software results", "exact dependencies", "logs", "status"); outputs = ("Configuration-linked results", "provenance", "execution status"); sourceLocator = "final_report/requirements.tex, FR-09 Inputs/Outputs; FrameworkRequirements::FR_09"; operation = ConfigurationExchange::preserveRun meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR09 from FrameworkRequirements::FR_09 to ConfigurationExchange::preserveRun;
    #primaryResponsibility allocation responsibility_FR_10_L03 allocate FrameworkRequirements::FR_10 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-10 subjects and engineering meaning"; plannedCheck = "D,T: Independently replay in the declared host environment and compare under fixed tolerances."; operation = SimulationIntegration::replay meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR10 { fr = "FR-10"; primary = "L03"; inputs = ("Replay request", "preserved run/dependencies", "returned outputs", "fixed comparison rules"); outputs = ("Replay inputs/instructions", "comparisons", "dependency/failure findings"); sourceLocator = "final_report/requirements.tex, FR-10 Inputs/Outputs; FrameworkRequirements::FR_10"; operation = SimulationIntegration::replay meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR10 from FrameworkRequirements::FR_10 to SimulationIntegration::replay;
    #primaryResponsibility allocation responsibility_FR_11_L05 allocate FrameworkRequirements::FR_11 to logical.L05 { @LogicalAllocation { rationale = "Shared complete typed FR-11 subjects and engineering meaning"; plannedCheck = "T: Seed every evidence status and attempt a current claim with a blocking gap."; operation = EvidenceReview::assessProduct meta SysML::ActionUsage; } }
    @NativeIO about EvidenceReview::contractFR11 { fr = "FR-11"; primary = "L05"; inputs = ("Evidence/status", "affected requirements/expectations", "criticality rules"); outputs = ("Gap reports", "blocked unsupported conformity claims"); sourceLocator = "final_report/requirements.tex, FR-11 Inputs/Outputs; FrameworkRequirements::FR_11"; operation = EvidenceReview::assessProduct meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR11 from FrameworkRequirements::FR_11 to EvidenceReview::assessProduct;
    #primaryResponsibility allocation responsibility_FR_13_L02 allocate FrameworkRequirements::FR_13 to logical.L02 { @LogicalAllocation { rationale = "Shared complete typed FR-13 subjects and engineering meaning"; plannedCheck = "A,T: Recalculate mass and volume after a component substitution and preserve unknown properties and aggregation assumptions."; operation = MissionDesign::budgetSize meta SysML::ActionUsage; } }
    @NativeIO about MissionDesign::contractFR13 { fr = "FR-13"; primary = "L02"; inputs = ("Modeled component and design data with sourced mass and volume properties"); outputs = ("Mass and volume estimates with uncertainty and unknowns"); sourceLocator = "final_report/requirements.tex, FR-13 Inputs/Outputs; FrameworkRequirements::FR_13"; operation = MissionDesign::budgetSize meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR13 from FrameworkRequirements::FR_13 to MissionDesign::budgetSize;
    #primaryResponsibility allocation responsibility_FR_14_L02 allocate FrameworkRequirements::FR_14 to logical.L02 { @LogicalAllocation { rationale = "Shared complete typed FR-14 subjects and engineering meaning"; plannedCheck = "A,T: Use infeasible and closely ranked alternatives with uncertain inputs."; operation = MissionDesign::compareDesigns meta SysML::ActionUsage; } }
    @NativeIO about MissionDesign::contractFR14 { fr = "FR-14"; primary = "L02"; inputs = ("EPS alternatives", "common mission/requirements", "approved criteria"); outputs = ("Feasibility", "ranking", "sensitivity", "selection rationale"); sourceLocator = "final_report/requirements.tex, FR-14 Inputs/Outputs; FrameworkRequirements::FR_14"; operation = MissionDesign::compareDesigns meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR14 from FrameworkRequirements::FR_14 to MissionDesign::compareDesigns;
    #primaryResponsibility allocation responsibility_FR_15_L02 allocate FrameworkRequirements::FR_15 to logical.L02 { @LogicalAllocation { rationale = "Shared complete typed FR-15 subjects and engineering meaning"; plannedCheck = "I,D: Configure alternate EPS topologies and retain the distinct allocation and extension revisions."; operation = MissionDesign::defineDesign meta SysML::ActionUsage; } }
    @NativeIO about MissionDesign::contractFR15 { fr = "FR-15"; primary = "L02"; inputs = ("Design parameters", "component variants", "extensions", "allocations"); outputs = ("Configured EPS design representations"); sourceLocator = "final_report/requirements.tex, FR-15 Inputs/Outputs; FrameworkRequirements::FR_15"; operation = MissionDesign::defineDesign meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR15 from FrameworkRequirements::FR_15 to MissionDesign::defineDesign;
    #primaryResponsibility allocation responsibility_FR_16_L03 allocate FrameworkRequirements::FR_16 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-16 subjects and engineering meaning"; plannedCheck = "A,T: Use whole-CUBICS histories with a temporal shortage hidden by an average budget. Perturb load, mode or illumination and compare the mapped EPS numerical response with an independent reference within model scope."; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR16 { fr = "FR-16"; primary = "L03"; inputs = ("Whole-CUBICS mission/subsystem load and mode histories", "orbit/attitude/illumination/thermal histories", "EPS models"); outputs = ("Power/energy balance", "bus quantities", "battery state histories"); sourceLocator = "final_report/requirements.tex, FR-16 Inputs/Outputs; FrameworkRequirements::FR_16"; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR16 from FrameworkRequirements::FR_16 to SimulationIntegration::planAnalysis;
    #primaryResponsibility allocation responsibility_FR_17_L01 allocate FrameworkRequirements::FR_17 to logical.L01 { @LogicalAllocation { rationale = "Shared complete typed FR-17 subjects and engineering meaning"; plannedCheck = "A,T: Recalculate an allocation and follow it to the parent and source quantities."; operation = RequirementsAssistance::deriveAllocate meta SysML::ActionUsage; } }
    @NativeIO about RequirementsAssistance::contractFR17 { fr = "FR-17"; primary = "L01"; inputs = ("Spacecraft requirements", "scenarios", "quantities", "derivation method"); outputs = ("Proposed EPS/component allocations", "traces", "dispositions"); sourceLocator = "final_report/requirements.tex, FR-17 Inputs/Outputs; FrameworkRequirements::FR_17"; operation = RequirementsAssistance::deriveAllocate meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR17 from FrameworkRequirements::FR_17 to RequirementsAssistance::deriveAllocate;
    #primaryResponsibility allocation responsibility_FR_18_L03 allocate FrameworkRequirements::FR_18 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-18 subjects and engineering meaning"; plannedCheck = "D,T: Exercise each discipline profile and incompatible mappings. Perturb an incoming whole-CUBICS history, compare the EPS numerical effect independently and return its identified response to the same scenario. Scene-only updates or missing numerical exchange cannot pass. Retain failed/partial status and transfer limits."; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR18 { fr = "FR-18"; primary = "L03"; inputs = ("Component/design model revisions", "discipline and Omniverse coupling profiles", "whole-CUBICS model/scenario revisions", "spacecraft/subsystem scenario histories", "directed mappings", "returned tool responses"); outputs = ("Exchanged component/design models", "mapped EPS analysis inputs", "EPS states/results returned to the same whole-CUBICS scenario", "mapping findings", "execution status", "transfer limitations"); sourceLocator = "final_report/requirements.tex, FR-18 Inputs/Outputs; FrameworkRequirements::FR_18"; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR18 from FrameworkRequirements::FR_18 to SimulationIntegration::planAnalysis;
    #primaryResponsibility allocation responsibility_FR_19_L03 allocate FrameworkRequirements::FR_19 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-19 subjects and engineering meaning"; plannedCheck = "D,T: Run declared nominal and fault sequences with a simulated plant and retain stimuli, expected/actual state/event responses and failed criteria for matched SIL comparison."; operation = SimulationIntegration::planMIL meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR19 { fr = "FR-19"; primary = "L03"; inputs = ("Controller/plant models", "mission scenarios", "MIL criteria"); outputs = ("MIL requests", "retained stimuli/responses", "criterion outcomes/failures"); sourceLocator = "final_report/requirements.tex, FR-19 Inputs/Outputs; FrameworkRequirements::FR_19"; operation = SimulationIntegration::planMIL meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR19 from FrameworkRequirements::FR_19 to SimulationIntegration::planMIL;
    #primaryResponsibility allocation responsibility_FR_20_L02 allocate FrameworkRequirements::FR_20 to logical.L02 { @LogicalAllocation { rationale = "Shared complete typed FR-20 subjects and engineering meaning"; plannedCheck = "A,T: Compare sizing and energy balance with independent calculations, including an infeasible eclipse case."; operation = MissionDesign::budgetSize meta SysML::ActionUsage; } }
    @NativeIO about MissionDesign::contractFR20 { fr = "FR-20"; primary = "L02"; inputs = ("Mission modes/loads", "efficiencies", "duty cycles", "eclipse", "battery limits", "degradation", "margins"); outputs = ("Power/energy budgets", "array/battery sizing"); sourceLocator = "final_report/requirements.tex, FR-20 Inputs/Outputs; FrameworkRequirements::FR_20"; operation = MissionDesign::budgetSize meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR20 from FrameworkRequirements::FR_20 to MissionDesign::budgetSize;
    #primaryResponsibility allocation responsibility_FR_21_L04 allocate FrameworkRequirements::FR_21 to logical.L04 { @LogicalAllocation { rationale = "Shared complete typed FR-21 subjects and engineering meaning"; plannedCheck = "I,T: Attempt conclusions outside validity and with missing independent evidence."; operation = ModelCredibility::assessModel meta SysML::ActionUsage; } }
    @NativeIO about ModelCredibility::contractFR21 { fr = "FR-21"; primary = "L04"; inputs = ("Conclusions", "model scope", "credibility evidence", "error rules"); outputs = ("Conclusion-linked credibility records", "explicit gaps"); sourceLocator = "final_report/requirements.tex, FR-21 Inputs/Outputs; FrameworkRequirements::FR_21"; operation = ModelCredibility::assessModel meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR21 from FrameworkRequirements::FR_21 to ModelCredibility::assessModel;
    #primaryResponsibility allocation responsibility_FR_22_L04 allocate FrameworkRequirements::FR_22 to logical.L04 { @LogicalAllocation { rationale = "Shared complete typed FR-22 subjects and engineering meaning"; plannedCheck = "A,T: Calibrate from supplied data, retain separate assessment data and decline an update."; operation = ModelCredibility::proposeCalibration meta SysML::ActionUsage; } }
    @NativeIO about ModelCredibility::contractFR22 { fr = "FR-22"; primary = "L04"; inputs = ("Current parameters", "quality-checked supplied reference data"); outputs = ("Calibration proposals", "residuals", "uncertainty", "affected analyses"); sourceLocator = "final_report/requirements.tex, FR-22 Inputs/Outputs; FrameworkRequirements::FR_22"; operation = ModelCredibility::proposeCalibration meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR22 from FrameworkRequirements::FR_22 to ModelCredibility::proposeCalibration;
    #primaryResponsibility allocation responsibility_FR_23_L03 allocate FrameworkRequirements::FR_23 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-23 subjects and engineering meaning"; plannedCheck = "I,T: Change the time step, solver and resource limits and inspect the run configuration and findings."; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR23 { fr = "FR-23"; primary = "L03"; inputs = ("Run settings", "environment", "resource limits", "observations"); outputs = ("Run configuration/runtime records", "numerical/resource findings"); sourceLocator = "final_report/requirements.tex, FR-23 Inputs/Outputs; FrameworkRequirements::FR_23"; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR23 from FrameworkRequirements::FR_23 to SimulationIntegration::planAnalysis;
    #primaryResponsibility allocation responsibility_FR_24_L03 allocate FrameworkRequirements::FR_24 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-24 subjects and engineering meaning"; plannedCheck = "A,T: Execute released F Prime host software with simulated EPS/subsystem products connected to the same whole-CUBICS scenario. Use matched MIL results and fixed comparison rules. Seed a code/interface discrepancy and failed/partial runs. Retain raw host responses, requirement/ConOps outcomes, differences, status and limits. Builds and scene updates supply no SIL evidence."; operation = SimulationIntegration::compareMILSil meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR24 { fr = "FR-24"; primary = "L03"; inputs = ("Released F Prime host code/build", "simulated EPS/subsystem products", "whole-CUBICS scenario and coupling-profile revisions", "matched MIL results", "fixed comparison rules"); outputs = ("SIL requests", "retained host responses", "requirement/ConOps outcomes", "MIL/SIL differences with execution status and limits"); sourceLocator = "final_report/requirements.tex, FR-24 Inputs/Outputs; FrameworkRequirements::FR_24"; operation = SimulationIntegration::compareMILSil meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR24 from FrameworkRequirements::FR_24 to SimulationIntegration::compareMILSil;
    #primaryResponsibility allocation responsibility_FR_25_L02 allocate FrameworkRequirements::FR_25 to logical.L02 { @LogicalAllocation { rationale = "Shared complete typed FR-25 subjects and engineering meaning"; plannedCheck = "I,T: Revise a degraded mode and trace its requirement and analysis inputs."; operation = MissionDesign::defineDesign meta SysML::ActionUsage; } }
    @NativeIO about MissionDesign::contractFR25 { fr = "FR-25"; primary = "L02"; inputs = ("Mission expectations", "constraints", "nominal/degraded ConOps"); outputs = ("Revision-linked mission and ConOps records"); sourceLocator = "final_report/requirements.tex, FR-25 Inputs/Outputs; FrameworkRequirements::FR_25"; operation = MissionDesign::defineDesign meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR25 from FrameworkRequirements::FR_25 to MissionDesign::defineDesign;
    #primaryResponsibility allocation responsibility_FR_26_L03 allocate FrameworkRequirements::FR_26 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-26 subjects and engineering meaning"; plannedCheck = "I,T: Assess applicability with and without repair or redundancy assumptions."; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR26 { fr = "FR-26"; primary = "L03"; inputs = ("EPS requirements", "ConOps", "risks", "failure/repair assumptions"); outputs = ("Applicable RAM methods", "measures", "coverage", "exclusions"); sourceLocator = "final_report/requirements.tex, FR-26 Inputs/Outputs; FrameworkRequirements::FR_26"; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR26 from FrameworkRequirements::FR_26 to SimulationIntegration::planAnalysis;
    #primaryResponsibility allocation responsibility_FR_27_L03 allocate FrameworkRequirements::FR_27 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-27 subjects and engineering meaning"; plannedCheck = "A,T: Compare transformations and results with a reference and leave missing rates unresolved."; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR27 { fr = "FR-27"; primary = "L03"; inputs = ("Functions", "components", "failure dependencies", "data", "transformation rules"); outputs = ("RAM representations/results with uncertainty and missing data"); sourceLocator = "final_report/requirements.tex, FR-27 Inputs/Outputs; FrameworkRequirements::FR_27"; operation = SimulationIntegration::planAnalysis meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR27 from FrameworkRequirements::FR_27 to SimulationIntegration::planAnalysis;
    #primaryResponsibility allocation responsibility_FR_28_L05 allocate FrameworkRequirements::FR_28 to logical.L05 { @LogicalAllocation { rationale = "Shared complete typed FR-28 subjects and engineering meaning"; plannedCheck = "I,T: Distinguish planned activities from results and verification criteria from validation expectations."; operation = EvidenceReview::planAssessment meta SysML::ActionUsage; } }
    @NativeIO about EvidenceReview::contractFR28 { fr = "FR-28"; primary = "L05"; inputs = ("EPS requirements/expectations", "assessment plans", "observations"); outputs = ("Retained EPS V&V plans", "separate references", "planned/executed status"); sourceLocator = "final_report/requirements.tex, FR-28 Inputs/Outputs; FrameworkRequirements::FR_28"; operation = EvidenceReview::planAssessment meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR28 from FrameworkRequirements::FR_28 to EvidenceReview::planAssessment;
    #primaryResponsibility allocation responsibility_FR_29_L01 allocate FrameworkRequirements::FR_29 to logical.L01 { @LogicalAllocation { rationale = "Shared complete typed FR-29 subjects and engineering meaning"; plannedCheck = "I,T: Exercise all dispositions and an unauthorized attempt to apply a suggestion."; operation = RequirementsAssistance::dispose meta SysML::ActionUsage; } }
    @NativeIO about RequirementsAssistance::contractFR29 { fr = "FR-29"; primary = "L01"; inputs = ("Suggestion/context revisions", "authorized engineer decision"); outputs = ("Recorded disposition", "rationale", "revision links"); sourceLocator = "final_report/requirements.tex, FR-29 Inputs/Outputs; FrameworkRequirements::FR_29"; operation = RequirementsAssistance::dispose meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR29 from FrameworkRequirements::FR_29 to RequirementsAssistance::dispose;
    #primaryResponsibility allocation responsibility_FR_30_L06 allocate FrameworkRequirements::FR_30 to logical.L06 { @LogicalAllocation { rationale = "Shared complete typed FR-30 subjects and engineering meaning"; plannedCheck = "T: Edit during a delayed response and check that the old response cannot replace current guidance."; operation = ConfigurationExchange::invalidate meta SysML::ActionUsage; } }
    @NativeIO about ConfigurationExchange::contractFR30 { fr = "FR-30"; primary = "L06"; inputs = ("Changed context revisions", "affected assistance"); outputs = ("Stale status", "blocked application", "reassessment request"); sourceLocator = "final_report/requirements.tex, FR-30 Inputs/Outputs; FrameworkRequirements::FR_30"; operation = ConfigurationExchange::invalidate meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR30 from FrameworkRequirements::FR_30 to ConfigurationExchange::invalidate;
    #primaryResponsibility allocation responsibility_FR_31_L04 allocate FrameworkRequirements::FR_31 to logical.L04 { @LogicalAllocation { rationale = "Shared complete typed FR-31 subjects and engineering meaning"; plannedCheck = "A,T: Seed clock offset, delayed/out-of-order samples and missing timing. Compare checked alignments, delays and exceeded/unknown limits with fixed timing references. Distinguish scenario/sample/receipt times, scene update rate and numerical time step."; operation = ModelCredibility::assessModel meta SysML::ActionUsage; } }
    @NativeIO about ModelCredibility::contractFR31 { fr = "FR-31"; primary = "L04"; inputs = ("Exchanged/simulated/reference histories", "scenario time references", "sampling/exchange timing", "synchronization rules and limits", "known delays"); outputs = ("Timing and synchronization records", "checked alignments", "timing gaps", "limit findings"); sourceLocator = "final_report/requirements.tex, FR-31 Inputs/Outputs; FrameworkRequirements::FR_31"; operation = ModelCredibility::assessModel meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR31 from FrameworkRequirements::FR_31 to ModelCredibility::assessModel;
    #primaryResponsibility allocation responsibility_FR_32_L04 allocate FrameworkRequirements::FR_32 to logical.L04 { @LogicalAllocation { rationale = "Shared complete typed FR-32 subjects and engineering meaning"; plannedCheck = "T: Seed wrong entity/channel/revision, unit/sign/frame mismatch and missing, inactive or invalid samples. Compare admission findings and masks with a fixed reference before numerical use. Preserve raw histories and unchanged controlled content for rejected transfers."; operation = ModelCredibility::assessModel meta SysML::ActionUsage; } }
    @NativeIO about ModelCredibility::contractFR32 { fr = "FR-32"; primary = "L04"; inputs = ("Exchanged/simulated/reference histories", "entity/channel mappings", "quantity/unit definitions", "timing metadata", "validity rules"); outputs = ("Admission/quality findings", "preserved raw histories", "invalid/missing/inactive status", "processing masks"); sourceLocator = "final_report/requirements.tex, FR-32 Inputs/Outputs; FrameworkRequirements::FR_32"; operation = ModelCredibility::assessModel meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR32 from FrameworkRequirements::FR_32 to ModelCredibility::assessModel;
    #primaryResponsibility allocation responsibility_FR_33_L02 allocate FrameworkRequirements::FR_33 to logical.L02 { @LogicalAllocation { rationale = "Shared complete typed FR-33 subjects and engineering meaning"; plannedCheck = "I,T: Round-trip endpoint ownership/directions and all interface and ground-definition fields. Reject inconsistent identifiers, types, units, ranges, polarity and temporal meanings against an independent reference. Structural checks supply no behavior verdict."; operation = MissionDesign::defineInterfaces meta SysML::ActionUsage; } }
    @NativeIO about MissionDesign::contractFR33 { fr = "FR-33"; primary = "L02"; inputs = ("Modeled EPS endpoint/port interfaces", "command, telemetry, event and parameter definitions"); outputs = ("Revision-linked EPS interface and ground-definition specifications"); sourceLocator = "final_report/requirements.tex, FR-33 Inputs/Outputs; FrameworkRequirements::FR_33"; operation = MissionDesign::defineInterfaces meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR33 from FrameworkRequirements::FR_33 to MissionDesign::defineInterfaces;
    #primaryResponsibility allocation responsibility_FR_34_L03 allocate FrameworkRequirements::FR_34 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-34 subjects and engineering meaning"; plannedCheck = "D,T: Compare required F Prime component/instance/port/topology and command/telemetry/event/parameter mappings with an independent reference at declared actual profile/tool/representation versions. Seed conflicts, wrong directions/types, missing meanings and incompatible versions. Retain unsupported behavior and lossy translations."; operation = SimulationIntegration::mapFPrime meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR34 { fr = "FR-34"; primary = "L03"; inputs = ("EPS interface specification", "software component/instance ownership and connectivity", "required F Prime profile", "supported representation/tool versions"); outputs = ("Checked F Prime mappings and definitions", "compatibility findings", "unsupported/lossy-translation records"); sourceLocator = "final_report/requirements.tex, FR-34 Inputs/Outputs; FrameworkRequirements::FR_34"; operation = SimulationIntegration::mapFPrime meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR34 from FrameworkRequirements::FR_34 to SimulationIntegration::mapFPrime;
    #primaryResponsibility allocation responsibility_FR_35_L02 allocate FrameworkRequirements::FR_35 to logical.L02 { @LogicalAllocation { rationale = "Shared complete typed FR-35 subjects and engineering meaning"; plannedCheck = "A,T: Exercise nominal, rejected, protection and recovery sequences in simulated conditions."; operation = MissionDesign::defineInterfaces meta SysML::ActionUsage; } }
    @NativeIO about MissionDesign::contractFR35 { fr = "FR-35"; primary = "L02"; inputs = ("Modeled command/control behavior", "control/interface requirements"); outputs = ("Checked behavior specifications", "discrepancy findings"); sourceLocator = "final_report/requirements.tex, FR-35 Inputs/Outputs; FrameworkRequirements::FR_35"; operation = MissionDesign::defineInterfaces meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR35 from FrameworkRequirements::FR_35 to MissionDesign::defineInterfaces;
    #primaryResponsibility allocation responsibility_FR_36_L03 allocate FrameworkRequirements::FR_36 to logical.L03 { @LogicalAllocation { rationale = "Shared complete typed FR-36 subjects and engineering meaning"; plannedCheck = "D,T: Reject stale, unreleased and unauthorized design requests. Coordinate an authorized current-release F Prime host build, retaining exact source/build, toolchain/dependency/host revisions, logs and generation/compilation failures. Review acceptance cannot replace exact authorization. Build success supplies no SIL verdict."; operation = SimulationIntegration::coordinateCoding meta SysML::ActionUsage; } }
    @NativeIO about SimulationIntegration::contractFR36 { fr = "FR-36"; primary = "L03"; inputs = ("Current authorized design/interface release", "declared software scope", "F Prime mappings", "host/toolchain/dependency configuration", "returned tool responses"); outputs = ("Authorized coding/build requests", "retained source/build products", "exact configuration records", "logs", "failures"); sourceLocator = "final_report/requirements.tex, FR-36 Inputs/Outputs; FrameworkRequirements::FR_36"; operation = SimulationIntegration::coordinateCoding meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR36 from FrameworkRequirements::FR_36 to SimulationIntegration::coordinateCoding;
    #primaryResponsibility allocation responsibility_FR_37_L05 allocate FrameworkRequirements::FR_37 to logical.L05 { @LogicalAllocation { rationale = "Shared complete typed FR-37 subjects and engineering meaning"; plannedCheck = "I,D: Compare views with their source baseline and follow represented record links."; operation = EvidenceReview::makeViews meta SysML::ActionUsage; } }
    @NativeIO about EvidenceReview::contractFR37 { fr = "FR-37"; primary = "L05"; inputs = ("Controlled EPS baseline", "view selection"); outputs = ("Readable baseline-linked engineering views"); sourceLocator = "final_report/requirements.tex, FR-37 Inputs/Outputs; FrameworkRequirements::FR_37"; operation = EvidenceReview::makeViews meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR37 from FrameworkRequirements::FR_37 to EvidenceReview::makeViews;
    #primaryResponsibility allocation responsibility_FR_38_L05 allocate FrameworkRequirements::FR_38 to logical.L05 { @LogicalAllocation { rationale = "Shared complete typed FR-38 subjects and engineering meaning"; plannedCheck = "I,D: Prepare phase-specific packages, including CDR design release and SIR released-product evidence."; operation = EvidenceReview::prepareReview meta SysML::ActionUsage; } }
    @NativeIO about EvidenceReview::contractFR38 { fr = "FR-38"; primary = "L05"; inputs = ("Phase baseline", "review criteria", "applicable records/evidence"); outputs = ("Prepared review package with coverage, limits and findings"); sourceLocator = "final_report/requirements.tex, FR-38 Inputs/Outputs; FrameworkRequirements::FR_38"; operation = EvidenceReview::prepareReview meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR38 from FrameworkRequirements::FR_38 to EvidenceReview::prepareReview;
    #primaryResponsibility allocation responsibility_FR_39_L01 allocate FrameworkRequirements::FR_39 to logical.L01 { @LogicalAllocation { rationale = "Shared complete typed FR-39 subjects and engineering meaning"; plannedCheck = "A,D: Change maturity and blocking findings and inspect the revised activity proposals."; operation = RequirementsAssistance::recommend meta SysML::ActionUsage; } }
    @NativeIO about RequirementsAssistance::contractFR39 { fr = "FR-39"; primary = "L01"; inputs = ("Phase", "maturity", "dependencies", "findings", "review criteria"); outputs = ("Proposed activities/reassessments", "prerequisites", "rationale"); sourceLocator = "final_report/requirements.tex, FR-39 Inputs/Outputs; FrameworkRequirements::FR_39"; operation = RequirementsAssistance::recommend meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR39 from FrameworkRequirements::FR_39 to RequirementsAssistance::recommend;
    #primaryResponsibility allocation responsibility_FR_41_L01 allocate FrameworkRequirements::FR_41 to logical.L01 { @LogicalAllocation { rationale = "Shared complete typed FR-41 subjects and engineering meaning"; plannedCheck = "T: Measure response delay under the declared workload, including outage and superseded edits."; operation = RequirementsAssistance::acknowledge meta SysML::ActionUsage; } }
    @NativeIO about RequirementsAssistance::contractFR41 { fr = "FR-41"; primary = "L01"; inputs = ("Assistance trigger", "current context", "response limits"); outputs = ("Acknowledgement", "guidance/status", "response timestamps"); sourceLocator = "final_report/requirements.tex, FR-41 Inputs/Outputs; FrameworkRequirements::FR_41"; operation = RequirementsAssistance::acknowledge meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR41 from FrameworkRequirements::FR_41 to RequirementsAssistance::acknowledge;
    #primaryResponsibility allocation responsibility_FR_42_L05 allocate FrameworkRequirements::FR_42 to logical.L05 { @LogicalAllocation { rationale = "Shared complete typed FR-42 subjects and engineering meaning"; plannedCheck = "I,T: Reject unauthorized or stale-baseline decisions and exercise blocking and conditional findings."; operation = EvidenceReview::recordReview meta SysML::ActionUsage; } }
    @NativeIO about EvidenceReview::contractFR42 { fr = "FR-42"; primary = "L05"; inputs = ("Identified baseline", "criteria", "designated-authority review decision"); outputs = ("Recorded disposition", "progression status", "closure obligations"); sourceLocator = "final_report/requirements.tex, FR-42 Inputs/Outputs; FrameworkRequirements::FR_42"; operation = EvidenceReview::recordReview meta SysML::ActionUsage; }
    #sourceTrace dependency operation_FR42 from FrameworkRequirements::FR_42 to EvidenceReview::recordReview;
    #sourceTrace dependency L01_F01 from RequirementsAssistance to BoundaryViews::F01;
    #sourceTrace dependency L01_F02 from RequirementsAssistance to BoundaryViews::F02;
    #sourceTrace dependency L02_F03 from MissionDesign to BoundaryViews::F03;
    #sourceTrace dependency L02_F05 from MissionDesign to BoundaryViews::F05;
    #sourceTrace dependency L03_F04 from SimulationIntegration to BoundaryViews::F04;
    #sourceTrace dependency L03_F05 from SimulationIntegration to BoundaryViews::F05;
    #sourceTrace dependency L04_F04 from ModelCredibility to BoundaryViews::F04;
    #sourceTrace dependency L05_F06 from EvidenceReview to BoundaryViews::F06;
    #sourceTrace dependency L05_F08 from EvidenceReview to BoundaryViews::F08;
    #sourceTrace dependency L06_F07 from ConfigurationExchange to BoundaryViews::F07;
}
