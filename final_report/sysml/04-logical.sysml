// Current vendor-independent logical design. Planned responsibility is not satisfaction.
// TODO: Re-derive all PA/V&V allocations. Former L09 is retired. No old allocation is grandfathered.
package FrameworkLogical {
    private import FrameworkDomain::*;
    private import BoundaryViews::*;
    private import ScalarValues::*;
    doc /* LogicalFramework specializes the current black box, retaining its five ports, eight functions, stores and controlled states. Logical components own information meaning and operations. L08 preserves the same records and their exact revisions. No technology, executable, deployment or hardware-execution choice is made. */
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
        ref item result : AnalysisResult;
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
        ref item result : AnalysisResult;
        attribute rawAgreementResidualsMissingDependenciesFailures : String;
    }
    port def AssistancePort { inout item work : AssistanceWork; }
    port def RequirementPort { inout item work : RequirementAllocation; }
    port def DesignPort { inout item work : DesignWork; }
    port def ExecutionPort { inout item work : RunWork; }
    port def EvidencePort { inout item work : EvidenceAssessment; }
    port def ReviewPort { inout item work : ReviewWork; }
    port def ConfigurationPort { inout item work : ConfigurationWork; }
    port def ImpactPort { inout item work : ImpactNotice; }
    port def ReferencePort { inout item work : ReferenceData; }
    action def CheckTransfer {
        in raw : EngineeringArtifact;
        out checked : CheckedTransfer;
        out attribute compatible : Boolean;
        doc /* Check identity, revision, structure, quantity, unit, polarity, time/mode meaning and provenance against the active interface. Retain incompatible raw submissions and findings. compatible permits registration only, with no engineering approval. */
    }
    action def MakeViews {
        in baseline : PhaseBaseline;
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
        doc /* Acknowledge each edit/request, retain exact context and trigger/first-response/completion times in seconds. Use the approved workload and response limits. Pending and unavailable are explicit. Numerical limits remain current TBR records. */
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
        doc /* Retain accepted, modified, rejected or deferred engineer dispositions with rationale and exact suggestion/context revisions. Verify the engineering role. applyRequested is true only for an accepted/modified correction or selected derivation method whose application the engineer requested. Current context is independently rechecked by L08 before any application. */
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
        doc /* Retrieve forward/reverse links among expectations, ConOps, requirements, functions/elements, interfaces, decisions and applicable evidence. Report missing/ambiguous endpoints and coverage only over the declared reference set. L08 preserves relationship revisions while L03 owns their requirement meaning. */
    }
    action def DefineDesign {
        in configuration : DesignConfiguration;
        out work : DesignWork;
        doc /* Retain expectations, constraints, nominal/degraded ConOps, orbit, attitude, duration, environment, modes, load schedules and transitions. Configure generation/storage/conversion/regulation/protection/distribution/control variants, parameters, extensions and allocation revisions. Component descriptions bind sourced properties to actual modeled occurrences. */
    }
    action def BudgetSize {
        in work : DesignWork;
        out updatedWork : DesignWork;
        doc /* Calculate preliminary generation/demand/energy budgets and array/battery sizing from sourced efficiencies, duty cycles, eclipse, battery limits, degradation and engineer margins. Generate candidate BOM quantities/assembly/variant/source/selection revisions. Roll up mass, volume and EPS acquisition estimates with dated currencies, availability, uncertainty and unknowns. Estimates imply no procurement. */
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
        doc /* Retain endpoint ownership, commands/telemetry/events/parameters, identifiers, types, units, ranges, polarity, time/mode meanings and encodings. Check preconditions, order, effects, rejection, transitions, protection/recovery and engineer-selected host profile/version mappings. Expose unsupported/lossy meanings. No integration vendor is selected. */
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
        doc /* Coordinate declared external host coding/build/SIL only after the logical detailed-design authorization gate admits the exact design/interface revisions and software scope. Request dependencies, host configuration, source/build revisions, logs and failures. A phase review package or broad CDR status supplies no coding authorization. */
    }
    action def CompareMILSil {
        in work : RunWork;
        out updatedWork : RunWork;
        doc /* Coordinate SIL of declared host code with simulated EPS/subsystem products. Compare corresponding MIL/SIL scenarios using the same stimuli and fixed rules, retaining requirement/ConOps outcomes, discrepancies and failed/partial runs. Host execution provides no target qualification. */
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
        doc /* Quality-check supplied data for its declared calibration use. Propose prior/revised parameters with exact data revisions, residual units, uncertainty and affected analyses. Separate independent assessment data/evidence. Engineers may decline. An accepted update follows L08 change control and repeats affected assessments. */
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
        doc /* Check designated review authority, exact baseline and agreed scoped success criteria revisions using the L08 baselineCurrent check. Include affected critical evidence gaps in blocking findings. Distinguish accepted/conditional/progression-blocked decision. Blocking findings prevent progression. Conditional records require rationale, limits, closure actions, owners and dates. Unauthorized/stale decisions change no review state. decisionConsistent excludes an accepted or conditional disposition when blocking findings remain. An inconsistent authorized request is preserved without changing review state. */
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
        doc /* Resolve controlled inputs, model/software/tool/environment dependencies and replay instructions for the designated run. Fix result-specific rules and tolerances before execution. Missing dependencies or unresolved comparison rules block a reconstruction-success claim. Rules use existing TBR resolution, with no invented targets. */
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
    part def <'L01'> Exchange {
        doc /* Engineering exchange. External interface component. Connect IF-01--04 and IF-06 to engineering responsibilities. Check incoming meaning before registration and present baseline-linked views. External engineers approve technical choices. Tools execute their declared profiles. Design/assessment records establish no physical qualification. */
        port p01 : EngineeringUsePort;
        port p02 : KnowledgePort;
        port p03 : AnalysisPort;
        port p04 : HostSoftwarePort;
        port p06 : TechnicalReviewPort;
        port advice : AssistancePort;
        port requirements : RequirementPort;
        port design : DesignPort;
        port execution : ExecutionPort;
        port review : ReviewPort;
        port registration : ConfigurationPort;
        port suppliedData : ReferencePort;
        ref item receivedStore : CheckedTransfer [0..*];
        ref item viewsStore : ReviewPackage [0..*];
        perform action checkTransfer : CheckTransfer;
        perform action makeViews : MakeViews;
        perform action presentAdvice : PresentAdvice;
        perform action presentAssessment : PresentAssessment;
    }
    @SourceRecord about Exchange { identifier = "L01"; sourceText = "Connect IF-01--04 and IF-06 to engineering responsibilities. Check incoming meaning before registration and present baseline-linked views."; sourceLocator = "Define Logical Architecture, responsibilities and realization"; status = "proposed logical specification, implementation and verification pending"; citationRecord = "OOSEM 17.3.4 external interface components; NASA 6.3, 6.6--6.7"; }
    #sourceTrace dependency L01_F01 from Exchange to BoundaryViews::F01;
    #sourceTrace dependency L01_F02 from Exchange to BoundaryViews::F02;
    #sourceTrace dependency L01_F03 from Exchange to BoundaryViews::F03;
    #sourceTrace dependency L01_F04 from Exchange to BoundaryViews::F04;
    #sourceTrace dependency L01_F05 from Exchange to BoundaryViews::F05;
    #sourceTrace dependency L01_F06 from Exchange to BoundaryViews::F06;
    #sourceTrace dependency L01_F07 from Exchange to BoundaryViews::F07;
    #sourceTrace dependency L01_F08 from Exchange to BoundaryViews::F08;
    #sourceTrace dependency L01_SC01 from Exchange to ScenarioViews::SC01;
    #sourceTrace dependency L01_SC02 from Exchange to ScenarioViews::SC02;
    #sourceTrace dependency L01_SC03 from Exchange to ScenarioViews::SC03;
    #sourceTrace dependency L01_SC04 from Exchange to ScenarioViews::SC04;
    #sourceTrace dependency L01_SC05 from Exchange to ScenarioViews::SC05;
    #qualitativeContribution dependency L01_MOE03 from Exchange to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency L01_MOE04 from Exchange to FrameworkNeeds::MOE_04;
    part def <'L02'> Assistance {
        doc /* Active engineering assistance. Application component. Separate rule-based drafting checks from probable semantic findings. Recommend applicable methods, models and lifecycle activities with citations, alternatives, limits and recorded engineer dispositions. External engineers approve technical choices. Tools execute their declared profiles. Design/assessment records establish no physical qualification. */
        port requests : AssistancePort;
        port impacts : ImpactPort;
        ref item assistanceStore : AssistanceReport [0..*];
        ref item dispositionsStore : SuggestionDisposition [0..*];
        perform action acknowledge : AcknowledgeAssistance;
        perform action checkDraft : CheckDraft;
        perform action recommend : RecommendMethods;
        perform action dispose : DisposeSuggestion;
        perform action reassess : ReassessAssistance;
    }
    @SourceRecord about Assistance { identifier = "L02"; sourceText = "Separate rule-based drafting checks from probable semantic findings. Recommend applicable methods, models and lifecycle activities with citations, alternatives, limits and recorded engineer dispositions."; sourceLocator = "Define Logical Architecture, responsibilities and realization"; status = "proposed logical specification, implementation and verification pending"; citationRecord = "NASA 4.2 and Appendix C, 6.8; OOSEM 17.3.4 application components"; }
    #sourceTrace dependency L02_F01 from Assistance to BoundaryViews::F01;
    #sourceTrace dependency L02_F02 from Assistance to BoundaryViews::F02;
    #sourceTrace dependency L02_SC01 from Assistance to ScenarioViews::SC01;
    #sourceTrace dependency L02_SC02 from Assistance to ScenarioViews::SC02;
    #sourceTrace dependency L02_SC03 from Assistance to ScenarioViews::SC03;
    #sourceTrace dependency L02_SC04 from Assistance to ScenarioViews::SC04;
    #sourceTrace dependency L02_SC05 from Assistance to ScenarioViews::SC05;
    #qualitativeContribution dependency L02_MOE01 from Assistance to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency L02_MOE02 from Assistance to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency L02_MOE04 from Assistance to FrameworkNeeds::MOE_04;
    part def <'L03'> Requirements {
        doc /* Requirements and allocation. Application component. Own requirement meaning, proposed spacecraft/EPS/component allocations and bidirectional engineering links. Use sourced design quantities and the engineer-selected derivation method. External engineers approve technical choices. Tools execute their declared profiles. Design/assessment records establish no physical qualification. */
        port records : RequirementPort;
        ref item requirementsStore : RequirementRecord [0..*];
        ref item allocationsStore : RequirementAllocation [0..*];
        perform action retainRequirements : RetainRequirements;
        perform action deriveAllocate : DeriveAllocate;
        perform action traceLinks : TraceLinks;
    }
    @SourceRecord about Requirements { identifier = "L03"; sourceText = "Own requirement meaning, proposed spacecraft/EPS/component allocations and bidirectional engineering links. Use sourced design quantities and the engineer-selected derivation method."; sourceLocator = "Define Logical Architecture, responsibilities and realization"; status = "proposed logical specification, implementation and verification pending"; citationRecord = "NASA 4.1--4.3, 6.2"; }
    #sourceTrace dependency L03_F02 from Requirements to BoundaryViews::F02;
    #sourceTrace dependency L03_SC01 from Requirements to ScenarioViews::SC01;
    #sourceTrace dependency L03_SC02 from Requirements to ScenarioViews::SC02;
    #sourceTrace dependency L03_SC03 from Requirements to ScenarioViews::SC03;
    #sourceTrace dependency L03_SC05 from Requirements to ScenarioViews::SC05;
    #qualitativeContribution dependency L03_MOE02 from Requirements to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency L03_MOE03 from Requirements to FrameworkNeeds::MOE_03;
    part def <'L04'> Design {
        doc /* Mission and EPS design. Application component. Keep mission assumptions, modeled EPS occurrences, component properties, budgets, sizing and trades on one common basis. Extend the same design into detailed control and interfaces. External engineers approve technical choices. Tools execute their declared profiles. Design/assessment records establish no physical qualification. */
        port studies : DesignPort;
        port analysisInputs : DesignPort;
        ref item designsStore : DesignConfiguration [0..*];
        ref item studiesStore : DesignStudy [0..*];
        ref item interfacesStore : EPSInterfaceSpecification [0..*];
        perform action defineDesign : DefineDesign;
        perform action budgetSize : BudgetSize;
        perform action compareDesigns : CompareDesigns;
        perform action defineInterfaces : DefineInterfaces;
        perform action configureConcept : ConfigureConcept;
    }
    @SourceRecord about Design { identifier = "L04"; sourceText = "Keep mission assumptions, modeled EPS occurrences, component properties, budgets, sizing and trades on one common basis. Extend the same design into detailed control and interfaces."; sourceLocator = "Define Logical Architecture, responsibilities and realization"; status = "proposed logical specification, implementation and verification pending"; citationRecord = "NASA 3.3--3.6; El Hachimi 2--4; Boan 2--4; Girardello 2--3; Campioli 3--4"; }
    #sourceTrace dependency L04_F03 from Design to BoundaryViews::F03;
    #sourceTrace dependency L04_F05 from Design to BoundaryViews::F05;
    #sourceTrace dependency L04_SC01 from Design to ScenarioViews::SC01;
    #sourceTrace dependency L04_SC02 from Design to ScenarioViews::SC02;
    #sourceTrace dependency L04_SC03 from Design to ScenarioViews::SC03;
    #sourceTrace dependency L04_SC04 from Design to ScenarioViews::SC04;
    #sourceTrace dependency L04_SC05 from Design to ScenarioViews::SC05;
    #qualitativeContribution dependency L04_MOE01 from Design to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency L04_MOE02 from Design to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency L04_MOE04 from Design to FrameworkNeeds::MOE_04;
    part def <'L05'> Analysis {
        doc /* Analysis and host work. Application component. Form controlled coupled analysis, applicable RAM and MIL/SIL requests. Coordinate external execution, host coding/builds and independent replay under declared numerical/resource limits. External engineers approve technical choices. Tools execute their declared profiles. Design/assessment records establish no physical qualification. */
        port execution : ExecutionPort;
        port design : DesignPort;
        port results : ExecutionPort;
        ref item plansStore : AnalysisPlan [0..*];
        ref item replaysStore : ReplayComparison [0..*];
        perform action planAnalysis : PlanAnalysis;
        perform action planMIL : PlanMIL;
        perform action coordinateCoding : CoordinateCoding;
        perform action compareMILSil : CompareMILSil;
        perform action replay : ReplayRun;
        perform action planRepeat : PlanRepeatedAssessment;
    }
    @SourceRecord about Analysis { identifier = "L05"; sourceText = "Form controlled coupled analysis, applicable RAM and MIL/SIL requests. Coordinate external execution, host coding/builds and independent replay under declared numerical/resource limits."; sourceLocator = "Define Logical Architecture, responsibilities and realization"; status = "proposed logical specification, implementation and verification pending"; citationRecord = "Boan 2--4; Casado 2--4; Zhu pp.7--9; NASA 3.6, 5.3--5.4"; }
    #sourceTrace dependency L05_F04 from Analysis to BoundaryViews::F04;
    #sourceTrace dependency L05_F05 from Analysis to BoundaryViews::F05;
    #sourceTrace dependency L05_SC01 from Analysis to ScenarioViews::SC01;
    #sourceTrace dependency L05_SC03 from Analysis to ScenarioViews::SC03;
    #sourceTrace dependency L05_SC04 from Analysis to ScenarioViews::SC04;
    #sourceTrace dependency L05_SC05 from Analysis to ScenarioViews::SC05;
    #qualitativeContribution dependency L05_MOE01 from Analysis to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency L05_MOE02 from Analysis to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency L05_MOE03 from Analysis to FrameworkNeeds::MOE_03;
    part def <'L06'> Credibility {
        doc /* Model credibility. Application component. Check result numerics and history quality against intended use. Own fidelity, omissions, validity, uncertainty and proposed calibration, with independent assessment kept separate. External engineers approve technical choices. Tools execute their declared profiles. Design/assessment records establish no physical qualification. */
        port results : ExecutionPort;
        port suppliedData : ReferencePort;
        port evidence : EvidencePort;
        ref item assessmentsStore : ModelAssessment [0..*];
        ref item referenceDataStore : ReferenceData [0..*];
        perform action assessModel : AssessModel;
        perform action proposeCalibration : ProposeCalibration;
        perform action checkReferenceData : CheckReferenceData;
    }
    @SourceRecord about Credibility { identifier = "L06"; sourceText = "Check result numerics and history quality against intended use. Own fidelity, omissions, validity, uncertainty and proposed calibration, with independent assessment kept separate."; sourceLocator = "Define Logical Architecture, responsibilities and realization"; status = "proposed logical specification, implementation and verification pending"; citationRecord = "Casado 2--4 limitations; Zhu pp.7--9 calibration scope; NASA 5.3--5.4"; }
    #sourceTrace dependency L06_F04 from Credibility to BoundaryViews::F04;
    #sourceTrace dependency L06_F06 from Credibility to BoundaryViews::F06;
    #sourceTrace dependency L06_SC01 from Credibility to ScenarioViews::SC01;
    #sourceTrace dependency L06_SC03 from Credibility to ScenarioViews::SC03;
    #sourceTrace dependency L06_SC04 from Credibility to ScenarioViews::SC04;
    #sourceTrace dependency L06_SC05 from Credibility to ScenarioViews::SC05;
    #qualitativeContribution dependency L06_MOE02 from Credibility to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency L06_MOE03 from Credibility to FrameworkNeeds::MOE_03;
    part def <'L07'> AssessmentReview {
        doc /* Phase-product assessment and review. Application component. Own EPS verification/validation plans, applicable criterion assessment, critical gaps, review preparation and recording of designated-authority review decisions. External engineers approve technical choices. Tools execute their declared profiles. Design/assessment records establish no physical qualification. */
        port review : ReviewPort;
        port evidence : EvidencePort;
        port configuration : ReviewPort;
        ref item plansStore : EPSAssessmentPlan [0..*];
        ref item reviewRecordsStore : ReviewWork [0..*];
        perform action planAssessment : PlanAssessment;
        perform action assessProduct : AssessProduct;
        perform action prepareReview : PrepareReviewPackage;
        perform action checkReviewDecision : CheckReviewDecision;
        perform action recordReview : RecordReviewDecision;
        exhibit state reviewState : ScenarioViews::BaselineControl;
    }
    @SourceRecord about AssessmentReview { identifier = "L07"; sourceText = "Own EPS verification/validation plans, applicable criterion assessment, critical gaps, review preparation and recording of designated-authority review decisions."; sourceLocator = "Define Logical Architecture, responsibilities and realization"; status = "proposed logical specification, implementation and verification pending"; citationRecord = "NASA 2.4, 5.3--5.4, 6.7--6.8"; }
    #sourceTrace dependency L07_F06 from AssessmentReview to BoundaryViews::F06;
    #sourceTrace dependency L07_F08 from AssessmentReview to BoundaryViews::F08;
    #sourceTrace dependency L07_SC01 from AssessmentReview to ScenarioViews::SC01;
    #sourceTrace dependency L07_SC02 from AssessmentReview to ScenarioViews::SC02;
    #sourceTrace dependency L07_SC03 from AssessmentReview to ScenarioViews::SC03;
    #sourceTrace dependency L07_SC04 from AssessmentReview to ScenarioViews::SC04;
    #sourceTrace dependency L07_SC05 from AssessmentReview to ScenarioViews::SC05;
    #qualitativeContribution dependency L07_MOE02 from AssessmentReview to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency L07_MOE03 from AssessmentReview to FrameworkNeeds::MOE_03;
    part def <'L08'> Configuration {
        doc /* Configuration and currency. Infrastructure component. Preserve exact revisions and raw submissions/results. Check current context, invalidate affected outputs, identify reciprocal impacts and retain authorized successor baselines and replay dependencies. External engineers approve technical choices. Tools execute their declared profiles. Design/assessment records establish no physical qualification. */
        port registration : ConfigurationPort;
        port review : ReviewPort;
        port impacts : ImpactPort;
        ref item baselinesStore : PhaseBaseline [0..*];
        ref item contextsStore : ContextRevision [0..*];
        ref item runsStore : RunWork [0..*];
        ref item impactsStore : ImpactNotice [0..*];
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
        exhibit state assistanceCurrency : ScenarioViews::GuidanceControl;
        ref item responseLimits : FrameworkRequirements::PerformanceMeasure = FrameworkRequirements::MOP_01;
        ref item impactMeasures : FrameworkRequirements::PerformanceMeasure = FrameworkRequirements::MOP_04;
    }
    @SourceRecord about Configuration { identifier = "L08"; sourceText = "Preserve exact revisions and raw submissions/results. Check current context, invalidate affected outputs, identify reciprocal impacts and retain authorized successor baselines and replay dependencies."; sourceLocator = "Define Logical Architecture, responsibilities and realization"; status = "proposed logical specification, implementation and verification pending"; citationRecord = "NASA 6.2--6.6; Gateau 3.2, 5--6; Campioli 3--4; OOSEM 17.3.4 infrastructure components"; }
    #sourceTrace dependency L08_F07 from Configuration to BoundaryViews::F07;
    #sourceTrace dependency L08_F04 from Configuration to BoundaryViews::F04;
    #sourceTrace dependency L08_SC01 from Configuration to ScenarioViews::SC01;
    #sourceTrace dependency L08_SC02 from Configuration to ScenarioViews::SC02;
    #sourceTrace dependency L08_SC03 from Configuration to ScenarioViews::SC03;
    #sourceTrace dependency L08_SC04 from Configuration to ScenarioViews::SC04;
    #sourceTrace dependency L08_SC05 from Configuration to ScenarioViews::SC05;
    #qualitativeContribution dependency L08_MOE01 from Configuration to FrameworkNeeds::MOE_01;
    #qualitativeContribution dependency L08_MOE02 from Configuration to FrameworkNeeds::MOE_02;
    #qualitativeContribution dependency L08_MOE03 from Configuration to FrameworkNeeds::MOE_03;
    #qualitativeContribution dependency L08_MOE04 from Configuration to FrameworkNeeds::MOE_04;
    part def LogicalFramework :> ToBe::FutureFramework {
        part L01 : Exchange;
        part L02 : Assistance;
        part L03 : Requirements;
        part L04 : Design;
        part L05 : Analysis;
        part L06 : Credibility;
        part L07 : AssessmentReview;
        part L08 : Configuration;
        bind p01 = L01.p01;
        bind p02 = L01.p02;
        bind p03 = L01.p03;
        bind p04 = L01.p04;
        bind p06 = L01.p06;
        interface advice connect L01.advice to L02.requests;
        interface requirements connect L01.requirements to L03.records;
        interface design connect L01.design to L04.studies;
        interface execution connect L01.execution to L05.execution;
        interface review connect L01.review to L07.review;
        interface registration connect L01.registration to L08.registration;
        #detailedExchange interface designInputs connect L04.analysisInputs to L05.design;
        #detailedExchange interface rawResults connect L05.results to L06.results;
        interface suppliedData connect L01.suppliedData to L06.suppliedData;
        #detailedExchange interface assessedEvidence connect L06.evidence to L07.evidence;
        #detailedExchange interface reviewRecord connect L07.configuration to L08.review;
        #detailedExchange interface invalidation connect L08.impacts to L02.impacts;
    }
    part logical : LogicalFramework;
    allocation guidanceControlOwner allocate logical.guidanceControl to logical.L08.assistanceCurrency;
    allocation baselineControlOwner allocate logical.baselineControl to logical.L07.reviewState;
    #primaryResponsibility allocation responsibility_FR_01_L03 allocate FrameworkRequirements::FR_01 to logical.L03 {
        @LogicalAllocation { rationale = "Requirement semantics and unresolved fields belong with the allocated requirement record."; plannedCheck = "I,T: Round-trip quantitative and qualitative records, including unresolved criteria."; operation = Requirements::retainRequirements meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_01_L08 allocate FrameworkRequirements::FR_01 to logical.L08;
    #sourceTrace dependency operation_FR01 from FrameworkRequirements::FR_01 to Requirements::retainRequirements;
    #sourceTrace dependency interface_FR01_01 from FrameworkRequirements::FR_01 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_02_L02 allocate FrameworkRequirements::FR_02 to logical.L02 {
        @LogicalAllocation { rationale = "Active rule and probable semantic checks share explained assistance, separate from technical approval."; plannedCheck = "A,T: Compare clean and seeded drafts with an independent expert reference, including valid similar requirements and missed defects."; operation = Assistance::checkDraft meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_02_L03 allocate FrameworkRequirements::FR_02 to logical.L03;
    #sourceTrace dependency operation_FR02 from FrameworkRequirements::FR_02 to Assistance::checkDraft;
    #sourceTrace dependency interface_FR02_01 from FrameworkRequirements::FR_02 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_03_L02 allocate FrameworkRequirements::FR_03 to logical.L02 {
        @LogicalAllocation { rationale = "Contextual eligibility and explained alternatives belong to assistance, with model validity supplied by credibility."; plannedCheck = "A,T: Use contextual queries whose eligible methods change with inputs, maturity or intended use."; operation = Assistance::recommend meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_03_L06 allocate FrameworkRequirements::FR_03 to logical.L06;
    #sourceTrace dependency operation_FR03 from FrameworkRequirements::FR_03 to Assistance::recommend;
    #sourceTrace dependency interface_FR03_01 from FrameworkRequirements::FR_03 to Exchange::p01;
    #sourceTrace dependency interface_FR03_02 from FrameworkRequirements::FR_03 to Exchange::p02;
    #primaryResponsibility allocation responsibility_FR_04_L03 allocate FrameworkRequirements::FR_04 to logical.L03 {
        @LogicalAllocation { rationale = "Requirements ownership defines link/coverage meaning while configuration preserves exact endpoints."; plannedCheck = "T: Compare both query directions and coverage with a known relationship set."; operation = Requirements::traceLinks meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_04_L08 allocate FrameworkRequirements::FR_04 to logical.L08;
    #sourceTrace dependency operation_FR04 from FrameworkRequirements::FR_04 to Requirements::traceLinks;
    #sourceTrace dependency interface_FR04_01 from FrameworkRequirements::FR_04 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_05_L08 allocate FrameworkRequirements::FR_05 to logical.L08 {
        @LogicalAllocation { rationale = "Cross-domain revision dependencies determine impacts and repeated work."; plannedCheck = "A,T: Compare the impact set of coupled load, pointing and interface changes with an expert reference."; operation = Configuration::invalidate meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_05_L03 allocate FrameworkRequirements::FR_05 to logical.L03;
    #supportingResponsibility allocation support_FR_05_L04 allocate FrameworkRequirements::FR_05 to logical.L04;
    #sourceTrace dependency operation_FR05 from FrameworkRequirements::FR_05 to Configuration::invalidate;
    #sourceTrace dependency interface_FR05_01 from FrameworkRequirements::FR_05 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_06_L08 allocate FrameworkRequirements::FR_06 to logical.L08 {
        @LogicalAllocation { rationale = "Only configuration can preserve predecessors and issue an authorized distinct successor."; plannedCheck = "T: Accept, decline and interrupt changes without erasing the predecessor."; operation = Configuration::successor meta SysML::ActionUsage; }
    }
    #sourceTrace dependency operation_FR06 from FrameworkRequirements::FR_06 to Configuration::successor;
    #sourceTrace dependency interface_FR06_01 from FrameworkRequirements::FR_06 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_07_L08 allocate FrameworkRequirements::FR_07 to logical.L08 {
        @LogicalAllocation { rationale = "Exact product/evidence revisions and decisions define a reconstructible baseline."; plannedCheck = "I,T: Reconstruct predecessor and successor manifests and all applicable products."; operation = Configuration::retrieveBaseline meta SysML::ActionUsage; }
    }
    #sourceTrace dependency operation_FR07 from FrameworkRequirements::FR_07 to Configuration::retrieveBaseline;
    #sourceTrace dependency interface_FR07_01 from FrameworkRequirements::FR_07 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_08_L01 allocate FrameworkRequirements::FR_08 to logical.L01 {
        @LogicalAllocation { rationale = "The external receiving responsibility checks meaning before controlled registration."; plannedCheck = "T: Inject identity, unit, sign and revision mismatches at each active interface."; operation = Exchange::checkTransfer meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_08_L08 allocate FrameworkRequirements::FR_08 to logical.L08;
    #sourceTrace dependency operation_FR08 from FrameworkRequirements::FR_08 to Exchange::checkTransfer;
    #sourceTrace dependency interface_FR08_01 from FrameworkRequirements::FR_08 to Exchange::p01;
    #sourceTrace dependency interface_FR08_02 from FrameworkRequirements::FR_08 to Exchange::p02;
    #sourceTrace dependency interface_FR08_03 from FrameworkRequirements::FR_08 to Exchange::p03;
    #sourceTrace dependency interface_FR08_04 from FrameworkRequirements::FR_08 to Exchange::p04;
    #sourceTrace dependency interface_FR08_06 from FrameworkRequirements::FR_08 to Exchange::p06;
    #primaryResponsibility allocation responsibility_FR_09_L08 allocate FrameworkRequirements::FR_09 to logical.L08 {
        @LogicalAllocation { rationale = "Preservation links every status and raw output to its execution configuration."; plannedCheck = "I,T: Trace successful, failed, cancelled and partial outputs to their configurations."; operation = Configuration::preserveRun meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_09_L05 allocate FrameworkRequirements::FR_09 to logical.L05;
    #sourceTrace dependency operation_FR09 from FrameworkRequirements::FR_09 to Configuration::preserveRun;
    #sourceTrace dependency interface_FR09_03 from FrameworkRequirements::FR_09 to Exchange::p03;
    #sourceTrace dependency interface_FR09_04 from FrameworkRequirements::FR_09 to Exchange::p04;
    #primaryResponsibility allocation responsibility_FR_10_L05 allocate FrameworkRequirements::FR_10 to logical.L05 {
        @LogicalAllocation { rationale = "Analysis coordination owns replay and comparison, configuration supplies fixed dependencies."; plannedCheck = "D,T: Independently replay in the declared host environment and compare under fixed tolerances."; operation = Analysis::replay meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_10_L08 allocate FrameworkRequirements::FR_10 to logical.L08;
    #sourceTrace dependency operation_FR10 from FrameworkRequirements::FR_10 to Analysis::replay;
    #sourceTrace dependency interface_FR10_03 from FrameworkRequirements::FR_10 to Exchange::p03;
    #sourceTrace dependency interface_FR10_04 from FrameworkRequirements::FR_10 to Exchange::p04;
    #primaryResponsibility allocation responsibility_FR_11_L07 allocate FrameworkRequirements::FR_11 to logical.L07 {
        @LogicalAllocation { rationale = "Applicability and critical evidence gaps govern phase-product claims."; plannedCheck = "T: Seed every evidence status and attempt a current claim with a blocking gap."; operation = AssessmentReview::assessProduct meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_11_L06 allocate FrameworkRequirements::FR_11 to logical.L06;
    #supportingResponsibility allocation support_FR_11_L08 allocate FrameworkRequirements::FR_11 to logical.L08;
    #sourceTrace dependency operation_FR11 from FrameworkRequirements::FR_11 to AssessmentReview::assessProduct;
    #sourceTrace dependency interface_FR11_01 from FrameworkRequirements::FR_11 to Exchange::p01;
    #sourceTrace dependency interface_FR11_06 from FrameworkRequirements::FR_11 to Exchange::p06;
    #primaryResponsibility allocation responsibility_FR_12_L04 allocate FrameworkRequirements::FR_12 to logical.L04 {
        @LogicalAllocation { rationale = "BOM occurrences are the modeled design, distinct from component catalogue definitions."; plannedCheck = "A,T: Compare quantities and substitutions with a reference assembly."; operation = Design::budgetSize meta SysML::ActionUsage; }
    }
    #sourceTrace dependency operation_FR12 from FrameworkRequirements::FR_12 to Design::budgetSize;
    #sourceTrace dependency interface_FR12_01 from FrameworkRequirements::FR_12 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_13_L04 allocate FrameworkRequirements::FR_13 to logical.L04 {
        @LogicalAllocation { rationale = "The same occurrence basis supports consistent dated resource and acquisition estimates."; plannedCheck = "A,T: Recalculate after a substitution and preserve unknown prices and availability."; operation = Design::budgetSize meta SysML::ActionUsage; }
    }
    #sourceTrace dependency operation_FR13 from FrameworkRequirements::FR_13 to Design::budgetSize;
    #sourceTrace dependency interface_FR13_01 from FrameworkRequirements::FR_13 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_14_L04 allocate FrameworkRequirements::FR_14 to logical.L04 {
        @LogicalAllocation { rationale = "Mandatory supported feasibility precedes engineer preference ranking."; plannedCheck = "A,T: Use infeasible and closely ranked alternatives with uncertain inputs."; operation = Design::compareDesigns meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_14_L06 allocate FrameworkRequirements::FR_14 to logical.L06;
    #sourceTrace dependency operation_FR14 from FrameworkRequirements::FR_14 to Design::compareDesigns;
    #sourceTrace dependency interface_FR14_01 from FrameworkRequirements::FR_14 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_15_L04 allocate FrameworkRequirements::FR_15 to logical.L04 {
        @LogicalAllocation { rationale = "EPS variants and extensions remain coherent with design allocations."; plannedCheck = "I,D: Configure alternate EPS topologies and retain the distinct allocation and extension revisions."; operation = Design::defineDesign meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_15_L03 allocate FrameworkRequirements::FR_15 to logical.L03;
    #sourceTrace dependency operation_FR15 from FrameworkRequirements::FR_15 to Design::defineDesign;
    #sourceTrace dependency interface_FR15_01 from FrameworkRequirements::FR_15 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_16_L05 allocate FrameworkRequirements::FR_16 to logical.L05 {
        @LogicalAllocation { rationale = "Coupled temporal composition and controlled tool execution realize mission-load/EPS analysis."; plannedCheck = "A,T: Use a temporal shortage hidden by an average power budget and check coupling against a reference."; operation = Analysis::planAnalysis meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_16_L04 allocate FrameworkRequirements::FR_16 to logical.L04;
    #sourceTrace dependency operation_FR16 from FrameworkRequirements::FR_16 to Analysis::planAnalysis;
    #sourceTrace dependency interface_FR16_01 from FrameworkRequirements::FR_16 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_17_L03 allocate FrameworkRequirements::FR_17 to logical.L03 {
        @LogicalAllocation { rationale = "Derivation connects spacecraft parents to EPS/component quantities and dispositions."; plannedCheck = "A,T: Recalculate an allocation and follow it to the parent and source quantities."; operation = Requirements::deriveAllocate meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_17_L04 allocate FrameworkRequirements::FR_17 to logical.L04;
    #sourceTrace dependency operation_FR17 from FrameworkRequirements::FR_17 to Requirements::deriveAllocate;
    #sourceTrace dependency interface_FR17_01 from FrameworkRequirements::FR_17 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_18_L05 allocate FrameworkRequirements::FR_18 to logical.L05 {
        @LogicalAllocation { rationale = "Discipline execution profiles expose tool/version mappings and unsupported transfers."; plannedCheck = "D,T: Exercise each required discipline profile and incompatible mappings."; operation = Analysis::planAnalysis meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_18_L01 allocate FrameworkRequirements::FR_18 to logical.L01;
    #supportingResponsibility allocation support_FR_18_L04 allocate FrameworkRequirements::FR_18 to logical.L04;
    #sourceTrace dependency operation_FR18 from FrameworkRequirements::FR_18 to Analysis::planAnalysis;
    #sourceTrace dependency interface_FR18_03 from FrameworkRequirements::FR_18 to Exchange::p03;
    #primaryResponsibility allocation responsibility_FR_19_L05 allocate FrameworkRequirements::FR_19 to logical.L05 {
        @LogicalAllocation { rationale = "Controlled MIL stimuli and responses follow the detailed design and assessment criteria."; plannedCheck = "D,T: Run declared nominal and fault sequences with a simulated plant and retain failed criteria."; operation = Analysis::planMIL meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_19_L04 allocate FrameworkRequirements::FR_19 to logical.L04;
    #supportingResponsibility allocation support_FR_19_L07 allocate FrameworkRequirements::FR_19 to logical.L07;
    #sourceTrace dependency operation_FR19 from FrameworkRequirements::FR_19 to Analysis::planMIL;
    #sourceTrace dependency interface_FR19_03 from FrameworkRequirements::FR_19 to Exchange::p03;
    #primaryResponsibility allocation responsibility_FR_20_L04 allocate FrameworkRequirements::FR_20 to logical.L04 {
        @LogicalAllocation { rationale = "Preliminary equations and margins belong with mission assumptions and candidate sizing."; plannedCheck = "A,T: Compare sizing and energy balance with independent calculations, including an infeasible eclipse case."; operation = Design::budgetSize meta SysML::ActionUsage; }
    }
    #sourceTrace dependency operation_FR20 from FrameworkRequirements::FR_20 to Design::budgetSize;
    #sourceTrace dependency interface_FR20_01 from FrameworkRequirements::FR_20 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_21_L06 allocate FrameworkRequirements::FR_21 to logical.L06 {
        @LogicalAllocation { rationale = "Intended use, numerics, omissions and independent evidence bound model-supported conclusions."; plannedCheck = "I,T: Attempt conclusions outside validity and with missing independent evidence."; operation = Credibility::assessModel meta SysML::ActionUsage; }
    }
    #sourceTrace dependency operation_FR21 from FrameworkRequirements::FR_21 to Credibility::assessModel;
    #sourceTrace dependency interface_FR21_02 from FrameworkRequirements::FR_21 to Exchange::p02;
    #sourceTrace dependency interface_FR21_03 from FrameworkRequirements::FR_21 to Exchange::p03;
    #primaryResponsibility allocation responsibility_FR_22_L06 allocate FrameworkRequirements::FR_22 to logical.L06 {
        @LogicalAllocation { rationale = "Calibration proposals preserve prior values and independent assessment separation."; plannedCheck = "A,T: Calibrate from supplied data, retain separate assessment data and decline an update."; operation = Credibility::proposeCalibration meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_22_L08 allocate FrameworkRequirements::FR_22 to logical.L08;
    #sourceTrace dependency operation_FR22 from FrameworkRequirements::FR_22 to Credibility::proposeCalibration;
    #sourceTrace dependency interface_FR22_01 from FrameworkRequirements::FR_22 to Exchange::p01;
    #sourceTrace dependency interface_FR22_02 from FrameworkRequirements::FR_22 to Exchange::p02;
    #primaryResponsibility allocation responsibility_FR_23_L05 allocate FrameworkRequirements::FR_23 to logical.L05 {
        @LogicalAllocation { rationale = "Every execution plan retains solver/coupling/resource settings, later joined to measured results."; plannedCheck = "I,T: Change the time step, solver and resource limits and inspect the run configuration and findings."; operation = Analysis::planAnalysis meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_23_L08 allocate FrameworkRequirements::FR_23 to logical.L08;
    #sourceTrace dependency operation_FR23 from FrameworkRequirements::FR_23 to Analysis::planAnalysis;
    #sourceTrace dependency interface_FR23_03 from FrameworkRequirements::FR_23 to Exchange::p03;
    #sourceTrace dependency interface_FR23_04 from FrameworkRequirements::FR_23 to Exchange::p04;
    #primaryResponsibility allocation responsibility_FR_24_L05 allocate FrameworkRequirements::FR_24 to logical.L05 {
        @LogicalAllocation { rationale = "Corresponding declared host SIL and MIL scenarios support meaningful differences."; plannedCheck = "A,T: Use matching MIL/SIL inputs and a seeded code/interface discrepancy."; operation = Analysis::compareMILSil meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_24_L06 allocate FrameworkRequirements::FR_24 to logical.L06;
    #supportingResponsibility allocation support_FR_24_L07 allocate FrameworkRequirements::FR_24 to logical.L07;
    #sourceTrace dependency operation_FR24 from FrameworkRequirements::FR_24 to Analysis::compareMILSil;
    #sourceTrace dependency interface_FR24_03 from FrameworkRequirements::FR_24 to Exchange::p03;
    #sourceTrace dependency interface_FR24_04 from FrameworkRequirements::FR_24 to Exchange::p04;
    #primaryResponsibility allocation responsibility_FR_25_L04 allocate FrameworkRequirements::FR_25 to logical.L04 {
        @LogicalAllocation { rationale = "Mission and degraded ConOps revisions supply the common design and analysis basis."; plannedCheck = "I,T: Revise a degraded mode and trace its requirement and analysis inputs."; operation = Design::defineDesign meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_25_L03 allocate FrameworkRequirements::FR_25 to logical.L03;
    #sourceTrace dependency operation_FR25 from FrameworkRequirements::FR_25 to Design::defineDesign;
    #sourceTrace dependency interface_FR25_01 from FrameworkRequirements::FR_25 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_26_L05 allocate FrameworkRequirements::FR_26 to logical.L05 {
        @LogicalAllocation { rationale = "RAM applicability follows requirements, ConOps, risks and justified exclusions."; plannedCheck = "I,T: Assess applicability with and without repair or redundancy assumptions."; operation = Analysis::planAnalysis meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_26_L02 allocate FrameworkRequirements::FR_26 to logical.L02;
    #sourceTrace dependency operation_FR26 from FrameworkRequirements::FR_26 to Analysis::planAnalysis;
    #sourceTrace dependency interface_FR26_01 from FrameworkRequirements::FR_26 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_27_L05 allocate FrameworkRequirements::FR_27 to logical.L05 {
        @LogicalAllocation { rationale = "Selected RAM transformations follow design failure dependencies without invented rates."; plannedCheck = "A,T: Compare transformations and results with a reference and leave missing rates unresolved."; operation = Analysis::planAnalysis meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_27_L04 allocate FrameworkRequirements::FR_27 to logical.L04;
    #sourceTrace dependency operation_FR27 from FrameworkRequirements::FR_27 to Analysis::planAnalysis;
    #sourceTrace dependency interface_FR27_03 from FrameworkRequirements::FR_27 to Exchange::p03;
    #primaryResponsibility allocation responsibility_FR_28_L07 allocate FrameworkRequirements::FR_28 to logical.L07 {
        @LogicalAllocation { rationale = "Verification requirements and validation expectations need distinct phase-product plans."; plannedCheck = "I,T: Distinguish planned activities from results and verification criteria from validation expectations."; operation = AssessmentReview::planAssessment meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_28_L03 allocate FrameworkRequirements::FR_28 to logical.L03;
    #sourceTrace dependency operation_FR28 from FrameworkRequirements::FR_28 to AssessmentReview::planAssessment;
    #sourceTrace dependency interface_FR28_01 from FrameworkRequirements::FR_28 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_29_L02 allocate FrameworkRequirements::FR_29 to logical.L02 {
        @LogicalAllocation { rationale = "All assistance dispositions retain human authority and exact suggestion/context identity."; plannedCheck = "I,T: Exercise all dispositions and an unauthorized attempt to apply a suggestion."; operation = Assistance::dispose meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_29_L01 allocate FrameworkRequirements::FR_29 to logical.L01;
    #supportingResponsibility allocation support_FR_29_L08 allocate FrameworkRequirements::FR_29 to logical.L08;
    #sourceTrace dependency operation_FR29 from FrameworkRequirements::FR_29 to Assistance::dispose;
    #sourceTrace dependency interface_FR29_01 from FrameworkRequirements::FR_29 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_30_L08 allocate FrameworkRequirements::FR_30 to logical.L08 {
        @LogicalAllocation { rationale = "Revision and pending-work currency require immediate invalidation and delayed-response checks."; plannedCheck = "T: Edit during a delayed response and check that the old response cannot replace current guidance."; operation = Configuration::invalidate meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_30_L02 allocate FrameworkRequirements::FR_30 to logical.L02;
    #sourceTrace dependency operation_FR30 from FrameworkRequirements::FR_30 to Configuration::invalidate;
    #sourceTrace dependency interface_FR30_01 from FrameworkRequirements::FR_30 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_31_L06 allocate FrameworkRequirements::FR_31 to logical.L06 {
        @LogicalAllocation { rationale = "History comparison needs explicit sample/receipt time bases and known delays."; plannedCheck = "A,T: Compare aligned and skewed histories with declared time tolerances."; operation = Credibility::assessModel meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_31_L05 allocate FrameworkRequirements::FR_31 to logical.L05;
    #sourceTrace dependency operation_FR31 from FrameworkRequirements::FR_31 to Credibility::assessModel;
    #sourceTrace dependency interface_FR31_02 from FrameworkRequirements::FR_31 to Exchange::p02;
    #sourceTrace dependency interface_FR31_03 from FrameworkRequirements::FR_31 to Exchange::p03;
    #sourceTrace dependency interface_FR31_04 from FrameworkRequirements::FR_31 to Exchange::p04;
    #primaryResponsibility allocation responsibility_FR_32_L06 allocate FrameworkRequirements::FR_32 to logical.L06 {
        @LogicalAllocation { rationale = "History validity and masks must preserve missing/inactive values rather than zero filling."; plannedCheck = "T: Inject missing, inactive, invalid and wrong-unit data and compare masks."; operation = Credibility::assessModel meta SysML::ActionUsage; }
    }
    #sourceTrace dependency operation_FR32 from FrameworkRequirements::FR_32 to Credibility::assessModel;
    #sourceTrace dependency interface_FR32_02 from FrameworkRequirements::FR_32 to Exchange::p02;
    #sourceTrace dependency interface_FR32_03 from FrameworkRequirements::FR_32 to Exchange::p03;
    #sourceTrace dependency interface_FR32_04 from FrameworkRequirements::FR_32 to Exchange::p04;
    #primaryResponsibility allocation responsibility_FR_33_L04 allocate FrameworkRequirements::FR_33 to logical.L04 {
        @LogicalAllocation { rationale = "Detailed interface meaning and ownership belong to the modeled EPS design."; plannedCheck = "I,T: Round-trip interface definitions and reject inconsistent endpoint meanings."; operation = Design::defineInterfaces meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_33_L03 allocate FrameworkRequirements::FR_33 to logical.L03;
    #sourceTrace dependency operation_FR33 from FrameworkRequirements::FR_33 to Design::defineInterfaces;
    #sourceTrace dependency interface_FR33_01 from FrameworkRequirements::FR_33 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_34_L04 allocate FrameworkRequirements::FR_34 to logical.L04 {
        @LogicalAllocation { rationale = "Engineer-selected integration mappings preserve detailed interface meanings and version gaps."; plannedCheck = "D,T: Check a selected profile and expose omitted or incompatible meanings."; operation = Design::defineInterfaces meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_34_L05 allocate FrameworkRequirements::FR_34 to logical.L05;
    #sourceTrace dependency operation_FR34 from FrameworkRequirements::FR_34 to Design::defineInterfaces;
    #sourceTrace dependency interface_FR34_01 from FrameworkRequirements::FR_34 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_35_L04 allocate FrameworkRequirements::FR_35 to logical.L04 {
        @LogicalAllocation { rationale = "Control preconditions/effects/recovery are detailed design responsibilities checked in simulation."; plannedCheck = "A,T: Exercise nominal, rejected, protection and recovery sequences in simulated conditions."; operation = Design::defineInterfaces meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_35_L05 allocate FrameworkRequirements::FR_35 to logical.L05;
    #sourceTrace dependency operation_FR35 from FrameworkRequirements::FR_35 to Design::defineInterfaces;
    #sourceTrace dependency interface_FR35_01 from FrameworkRequirements::FR_35 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_36_L05 allocate FrameworkRequirements::FR_36 to logical.L05 {
        @LogicalAllocation { rationale = "External host coordination is gated by a current specific detailed-design authorization."; plannedCheck = "D,T: Attempt an unreleased build and then build the released design, including a toolchain failure."; operation = Analysis::coordinateCoding meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_36_L08 allocate FrameworkRequirements::FR_36 to logical.L08;
    #sourceTrace dependency operation_FR36 from FrameworkRequirements::FR_36 to Analysis::coordinateCoding;
    #sourceTrace dependency interface_FR36_04 from FrameworkRequirements::FR_36 to Exchange::p04;
    #primaryResponsibility allocation responsibility_FR_37_L01 allocate FrameworkRequirements::FR_37 to logical.L01 {
        @LogicalAllocation { rationale = "User-facing views derive from controlled records and never define an independent baseline."; plannedCheck = "I,D: Compare views with their source baseline and follow represented record links."; operation = Exchange::makeViews meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_37_L08 allocate FrameworkRequirements::FR_37 to logical.L08;
    #sourceTrace dependency operation_FR37 from FrameworkRequirements::FR_37 to Exchange::makeViews;
    #sourceTrace dependency interface_FR37_01 from FrameworkRequirements::FR_37 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_38_L07 allocate FrameworkRequirements::FR_38 to logical.L07 {
        @LogicalAllocation { rationale = "Scoped entrance/success evidence needs coherent phase-product assessment, not automatic acceptance."; plannedCheck = "I,D: Prepare phase-specific packages, including CDR design release and SIR released-product evidence."; operation = AssessmentReview::prepareReview meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_38_L01 allocate FrameworkRequirements::FR_38 to logical.L01;
    #supportingResponsibility allocation support_FR_38_L08 allocate FrameworkRequirements::FR_38 to logical.L08;
    #sourceTrace dependency operation_FR38 from FrameworkRequirements::FR_38 to AssessmentReview::prepareReview;
    #sourceTrace dependency interface_FR38_01 from FrameworkRequirements::FR_38 to Exchange::p01;
    #sourceTrace dependency interface_FR38_06 from FrameworkRequirements::FR_38 to Exchange::p06;
    #primaryResponsibility allocation responsibility_FR_39_L02 allocate FrameworkRequirements::FR_39 to logical.L02 {
        @LogicalAllocation { rationale = "Activity advice uses maturity, dependencies, findings and review prerequisites."; plannedCheck = "A,D: Change maturity and blocking findings and inspect the revised activity proposals."; operation = Assistance::recommend meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_39_L07 allocate FrameworkRequirements::FR_39 to logical.L07;
    #supportingResponsibility allocation support_FR_39_L08 allocate FrameworkRequirements::FR_39 to logical.L08;
    #sourceTrace dependency operation_FR39 from FrameworkRequirements::FR_39 to Assistance::recommend;
    #sourceTrace dependency interface_FR39_01 from FrameworkRequirements::FR_39 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_41_L02 allocate FrameworkRequirements::FR_41 to logical.L02 {
        @LogicalAllocation { rationale = "Interactive assistance owns trigger/response/completion status while infrastructure supplies time/context."; plannedCheck = "T: Measure response delay under the declared workload, including outage and superseded edits."; operation = Assistance::acknowledge meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_41_L01 allocate FrameworkRequirements::FR_41 to logical.L01;
    #supportingResponsibility allocation support_FR_41_L08 allocate FrameworkRequirements::FR_41 to logical.L08;
    #sourceTrace dependency operation_FR41 from FrameworkRequirements::FR_41 to Assistance::acknowledge;
    #sourceTrace dependency interface_FR41_01 from FrameworkRequirements::FR_41 to Exchange::p01;
    #primaryResponsibility allocation responsibility_FR_42_L07 allocate FrameworkRequirements::FR_42 to logical.L07 {
        @LogicalAllocation { rationale = "Only designated-authority current decisions change review disposition, separately from preparation."; plannedCheck = "I,T: Reject unauthorized or stale-baseline decisions and exercise blocking and conditional findings."; operation = AssessmentReview::recordReview meta SysML::ActionUsage; }
    }
    #supportingResponsibility allocation support_FR_42_L08 allocate FrameworkRequirements::FR_42 to logical.L08;
    #sourceTrace dependency operation_FR42 from FrameworkRequirements::FR_42 to AssessmentReview::recordReview;
    #sourceTrace dependency interface_FR42_06 from FrameworkRequirements::FR_42 to Exchange::p06;
    allocation function_F01_L02 allocate logical.f01 to logical.L02;
    allocation function_F02_L03 allocate logical.f02 to logical.L03;
    allocation function_F02_L02 allocate logical.f02 to logical.L02;
    allocation function_F03_L04 allocate logical.f03 to logical.L04;
    allocation function_F04_L05 allocate logical.f04 to logical.L05;
    allocation function_F04_L06 allocate logical.f04 to logical.L06;
    allocation function_F05_L04 allocate logical.f05 to logical.L04;
    allocation function_F05_L05 allocate logical.f05 to logical.L05;
    allocation function_F06_L07 allocate logical.f06 to logical.L07;
    allocation function_F06_L06 allocate logical.f06 to logical.L06;
    allocation function_F07_L08 allocate logical.f07 to logical.L08;
    allocation function_F07_L01 allocate logical.f07 to logical.L01;
    allocation function_F08_L07 allocate logical.f08 to logical.L07;
    allocation function_F08_L01 allocate logical.f08 to logical.L01;
}
