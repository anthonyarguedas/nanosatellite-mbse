// Logical realization of the five approved scenarios. No scenario wording is changed.
// Native allocations, typed flows and guarded paths specify planned behavior, not execution.
package LogicalRealization {
    private import FrameworkDomain::*;
    private import BoundaryViews::*;
    private import FrameworkLogical::*;
    private import ScalarValues::*;
    metadata def LogicalStep { ref component : SysML::PartUsage; ref operation : SysML::ActionUsage; }
    metadata def ExternalStep { ref performer : SysML::PartUsage; }
    action def RequestChangeDecision { in item impact : ImpactNotice; out item decision : EngineeringDecision; doc /* The Systems Engineer accepts, declines or defers a specific engineering change with rationale. This is no technical review decision. */ }
    action def AuthorizeDetailedDesign { in item work : DesignWork; out item authorization : DetailedDesignAuthorization; doc /* The EPS Engineer authorizes or declines the exact detailed model/software design release, interface revisions and declared host code scope. Scoped CDR supports this decision. A general phase review acceptance supplies no substitute authorization. */ }
    action def ChooseCalibration { in item proposal : ChangeProposal; out item decision : EngineeringDecision; doc /* The EPS Engineer accepts, declines or defers the proposed calibration, with rationale. An accepted update is still a configuration-controlled change with repeated affected assessment. */ }
    action def SupplyReplay { out item request : ReplayRequest; doc /* The independent reviewer identifies the controlled run and approves the comparison rules before replay. */ }
    action def SupplyCalibration { out item data : ReferenceData; out item evidence : EvidenceAssessment; doc /* The engineer identifies quality-checked supplied data, its calibration purpose and the existing model assessment. No physical acquisition is performed. */ }
    action def AssistanceRealization {
        doc /* Interactive requirement assistance and contextual method/lifecycle guidance. Compatible input and exact latest-context gates precede registration, presentation and application. Draft findings are no technical approval. Independent requirement validation remains external. */
        perform action edit : ScenarioViews::SC02External1 { @ExternalStep { performer = ScenarioViews::systemsEngineer meta SysML::PartUsage; } }
        perform action receive : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action capture : CaptureContext {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::captureContext meta SysML::ActionUsage; }
        }
        perform action invalidateOnEdit : InvalidateAndReassess {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::invalidate meta SysML::ActionUsage; }
        }
        perform action acknowledge : AcknowledgeAssistance {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::acknowledge meta SysML::ActionUsage; }
        }
        perform action retainDraft : RetainRequirements {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::retainRequirements meta SysML::ActionUsage; }
        }
        perform action checkDraft : CheckDraft {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::checkDraft meta SysML::ActionUsage; }
        }
        perform action recommend : RecommendMethods {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::recommend meta SysML::ActionUsage; }
        }
        perform action checkReply : CheckCurrency {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkCurrency meta SysML::ActionUsage; }
        }
        perform action present : PresentAdvice {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::presentAdvice meta SysML::ActionUsage; }
        }
        perform action engineerDisposition : ScenarioViews::SC02External3 { @ExternalStep { performer = ScenarioViews::systemsEngineer meta SysML::PartUsage; } }
        perform action dispose : DisposeSuggestion {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::dispose meta SysML::ActionUsage; }
        }
        perform action checkApplication : CheckCurrency {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkCurrency meta SysML::ActionUsage; }
        }
        perform action derive : DeriveAllocate {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::deriveAllocate meta SysML::ActionUsage; }
        }
        perform action trace : TraceLinks {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::traceLinks meta SysML::ActionUsage; }
        }
        perform action validate : ScenarioViews::SC02External5 { @ExternalStep { performer = ScenarioViews::reviewers meta SysML::PartUsage; } }
        perform action retainValidation : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainDisposition : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action invalidate : InvalidateAndReassess {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::invalidate meta SysML::ActionUsage; }
        }
        perform action reassess : ReassessAssistance {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::reassess meta SysML::ActionUsage; }
        }
        perform action rejectTransfer : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action rejectDisposition : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        decide compatibleInput;
        decide currentReply;
        decide currentDisposition;
        decide applyCorrection;
        decide validated;
        merge complete;
        first start then edit;
        first edit then receive;
        first receive then compatibleInput;
        succession admitInput first compatibleInput if receive.compatible then capture;
        succession rejectInput first compatibleInput if not receive.compatible then rejectTransfer;
        first capture then invalidateOnEdit;
        first invalidateOnEdit then acknowledge;
        first acknowledge then retainDraft;
        first retainDraft then checkDraft;
        first checkDraft then recommend;
        first recommend then checkReply;
        first checkReply then currentReply;
        succession admitReply first currentReply if checkReply.sameContext then present;
        succession lateReply first currentReply if not checkReply.sameContext then invalidate;
        first present then engineerDisposition;
        first engineerDisposition then dispose;
        first dispose then checkApplication;
        first checkApplication then currentDisposition;
        succession admitDisposition first currentDisposition if dispose.authorized and checkApplication.sameContext then applyCorrection;
        succession rejectStaleDisposition first currentDisposition if not (dispose.authorized and checkApplication.sameContext) then rejectDisposition;
        succession applyAuthorized first applyCorrection if dispose.applyRequested then derive;
        succession keepDisposition first applyCorrection if not dispose.applyRequested then retainDisposition;
        first derive then trace;
        first trace then validate;
        first validate then validated;
        succession validRequirements first validated if validate.resolved then retainValidation;
        succession openRequirements first validated if not validate.resolved then retainDisposition;
        first invalidate then reassess;
        first reassess then complete;
        first rejectDisposition then invalidate;
        first retainValidation then complete;
        first retainDisposition then complete;
        first rejectTransfer then complete;
        first complete then done;
        flow exchange1 of EngineeringSubmission from edit.submission to receive.raw;
        flow exchange2 of CheckedTransfer from receive.checked to capture.checked;
        flow exchange3 of EngineeringArtifact from receive.checked to rejectTransfer.record;
        flow exchange4 of EngineeringSubmission from capture.submission to invalidateOnEdit.submission;
        flow exchange5 of EngineeringSubmission from invalidateOnEdit.updatedSubmission to acknowledge.submission;
        flow exchange6 of EngineeringSubmission from capture.submission to retainDraft.submission;
        flow exchange7 of AssistanceWork from acknowledge.work to checkDraft.work;
        flow exchange8 of AssistanceWork from checkDraft.updatedWork to recommend.work;
        flow exchange9 of AssistanceReport from recommend.report to checkReply.report;
        flow exchange10 of ContextRevision from capture.context to checkReply.context;
        flow exchange11 of AssistanceReport from recommend.report to present.report;
        flow exchange12 of EngineeringResponse from present.response to engineerDisposition.response;
        flow exchange13 of AssistanceReport from recommend.report to dispose.report;
        flow exchange14 of EngineeringSubmission from engineerDisposition.submission to dispose.decision;
        flow exchange15 of AssistanceReport from recommend.report to checkApplication.report;
        flow exchange16 of ContextRevision from capture.context to checkApplication.context;
        flow exchange17 of RequirementAllocation from retainDraft.proposedAllocation to derive.proposedAllocation;
        flow exchange18 of SuggestionDisposition from dispose.disposition to derive.disposition;
        flow exchange19 of RequirementAllocation from derive.updatedProposedAllocation to trace.proposedAllocation;
        flow exchange20 of ReviewPackage from derive.reviewPackage to validate.reviewPackage;
        flow exchange21 of ReviewSubmission from validate.findings to retainValidation.record;
        flow exchange22 of SuggestionDisposition from dispose.disposition to retainDisposition.record;
        flow exchange23 of SuggestionDisposition from dispose.disposition to rejectDisposition.record;
        flow exchange24 of EngineeringSubmission from capture.submission to invalidate.submission;
        flow exchange25 of ImpactNotice from invalidate.impact to reassess.impact;
    }
    allocate AssistanceRealization::edit to ScenarioViews::systemsEngineer;
    allocate AssistanceRealization::receive to logical.L06;
    allocate AssistanceRealization::capture to logical.L06;
    allocate AssistanceRealization::invalidateOnEdit to logical.L06;
    allocate AssistanceRealization::acknowledge to logical.L01;
    allocate AssistanceRealization::retainDraft to logical.L01;
    allocate AssistanceRealization::checkDraft to logical.L01;
    allocate AssistanceRealization::recommend to logical.L01;
    allocate AssistanceRealization::checkReply to logical.L06;
    allocate AssistanceRealization::present to logical.L01;
    allocate AssistanceRealization::engineerDisposition to ScenarioViews::systemsEngineer;
    allocate AssistanceRealization::dispose to logical.L01;
    allocate AssistanceRealization::checkApplication to logical.L06;
    allocate AssistanceRealization::derive to logical.L01;
    allocate AssistanceRealization::trace to logical.L01;
    allocate AssistanceRealization::validate to ScenarioViews::reviewers;
    allocate AssistanceRealization::retainValidation to logical.L06;
    allocate AssistanceRealization::retainDisposition to logical.L06;
    allocate AssistanceRealization::invalidate to logical.L06;
    allocate AssistanceRealization::reassess to logical.L01;
    allocate AssistanceRealization::rejectTransfer to logical.L06;
    allocate AssistanceRealization::rejectDisposition to logical.L06;
    #sourceTrace dependency AssistanceRealization_SC02 from AssistanceRealization to ScenarioViews::SC02;
    action def DesignRealization {
        doc /* Mission concept and preliminary design use the same mission/component/budget basis at the fidelity suited to maturity. Numerical applicability and criterion gates precede supported mandatory feasibility and engineer selection. Unknown technical quantities/rates and temporal shortages remain explicit. */
        perform action submit : ScenarioViews::SC03External1 { @ExternalStep { performer = ScenarioViews::epsEngineer meta SysML::PartUsage; } }
        perform action receive : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action configure : DefineDesign {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L02 meta SysML::PartUsage; operation = FrameworkLogical::MissionDesign::defineDesign meta SysML::ActionUsage; }
        }
        perform action budget : BudgetSize {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L02 meta SysML::PartUsage; operation = FrameworkLogical::MissionDesign::budgetSize meta SysML::ActionUsage; }
        }
        perform action planCriteria : PlanAssessment {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::planAssessment meta SysML::ActionUsage; }
        }
        perform action plan : PlanAnalysis {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::planAnalysis meta SysML::ActionUsage; }
        }
        perform action execute : ScenarioViews::SC03External3 { @ExternalStep { performer = ScenarioViews::analysisTools meta SysML::PartUsage; } }
        perform action receiveResult : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action preserve : PreserveRun {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRun meta SysML::ActionUsage; }
        }
        perform action checkCurrent : CheckResultContext {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkResultContext meta SysML::ActionUsage; }
        }
        perform action credibility : AssessModel {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L04 meta SysML::PartUsage; operation = FrameworkLogical::ModelCredibility::assessModel meta SysML::ActionUsage; }
        }
        perform action assess : AssessProduct {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::assessProduct meta SysML::ActionUsage; }
        }
        perform action compare : CompareDesigns {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L02 meta SysML::PartUsage; operation = FrameworkLogical::MissionDesign::compareDesigns meta SysML::ActionUsage; }
        }
        perform action select : ScenarioViews::SC03External5 { @ExternalStep { performer = ScenarioViews::epsEngineer meta SysML::PartUsage; } }
        perform action checkSelection : CheckEngineerSelection {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkSelection meta SysML::ActionUsage; }
        }
        perform action retainSelection : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainGaps : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainRaw_receiveResult : PreserveRecord { @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; } }
        flow raw_receiveResult of CheckedTransfer from receiveResult.checked to retainRaw_receiveResult.record;
        first retainRaw_receiveResult then complete;
        decide compatibleInput;
        decide compatibleResult;
        decide usableNumerics;
        decide supportedCriteria;
        decide selected;
        merge complete;
        first start then submit;
        first submit then receive;
        first receive then compatibleInput;
        succession admitInput first compatibleInput if receive.compatible then configure;
        succession rejectInput first compatibleInput if not receive.compatible then retainGaps;
        first configure then budget;
        first budget then planCriteria;
        first planCriteria then plan;
        first plan then execute;
        first execute then receiveResult;
        first receiveResult then compatibleResult;
        succession admitResult first compatibleResult if receiveResult.compatible then preserve;
        succession rejectResult first compatibleResult if not receiveResult.compatible then retainRaw_receiveResult;
        first preserve then checkCurrent;
        first checkCurrent then credibility;
        first credibility then usableNumerics;
        succession admitModel first usableNumerics if checkCurrent.current and credibility.numericallyValid and credibility.applicable then assess;
        succession rejectModel first usableNumerics if not (checkCurrent.current and credibility.numericallyValid and credibility.applicable) then retainGaps;
        first assess then supportedCriteria;
        succession admitCriteria first supportedCriteria if assess.claimSupported then compare;
        succession rejectCriteria first supportedCriteria if not assess.claimSupported then retainGaps;
        first compare then select;
        first select then checkSelection;
        first checkSelection then selected;
        succession admitSelection first selected if compare.feasible and select.accepted and checkSelection.authorizedCurrent then retainSelection;
        succession holdSelection first selected if not (compare.feasible and select.accepted and checkSelection.authorizedCurrent) then retainGaps;
        first retainSelection then complete;
        first complete then done;
        first retainGaps then complete;
        flow exchange1 of DesignConfiguration from submit.configuration to receive.raw;
        flow exchange2 of DesignConfiguration from submit.configuration to configure.configuration;
        flow exchange3 of DesignWork from configure.work to budget.work;
        flow exchange4 of DesignConfiguration from submit.configuration to planCriteria.configuration;
        flow exchange5 of DesignWork from budget.updatedWork to plan.work;
        flow exchange6 of AnalysisPlan from plan.plan to execute.plan;
        flow exchange7 of AnalysisResult from execute.result to receiveResult.raw;
        flow exchange8 of AnalysisResult from execute.result to preserve.result;
        flow exchange9 of RunWork from preserve.work to credibility.work;
        flow exchange10 of RunWork from preserve.work to checkCurrent.record;
        flow exchange11 of EPSAssessmentPlan from planCriteria.plan to assess.plan;
        flow exchange12 of EvidenceAssessment from credibility.evidence to assess.evidence;
        flow exchange13 of DesignWork from budget.updatedWork to compare.work;
        flow exchange14 of EvidenceAssessment from assess.updatedEvidence to compare.evidence;
        flow exchange15 of DesignStudy from compare.study to select.study;
        flow exchange16 of EngineeringDecision from select.decision to checkSelection.decision;
        flow exchange17 of DesignConfiguration from submit.configuration to checkSelection.configuration;
        flow exchange18 of EngineeringDecision from select.decision to retainSelection.record;
        flow exchange19 of EngineeringArtifact from submit.configuration to retainGaps.record;
    }
    allocate DesignRealization::retainRaw_receiveResult to logical.L06;
    allocate DesignRealization::submit to ScenarioViews::epsEngineer;
    allocate DesignRealization::receive to logical.L06;
    allocate DesignRealization::configure to logical.L02;
    allocate DesignRealization::budget to logical.L02;
    allocate DesignRealization::planCriteria to logical.L05;
    allocate DesignRealization::plan to logical.L03;
    allocate DesignRealization::execute to ScenarioViews::analysisTools;
    allocate DesignRealization::receiveResult to logical.L06;
    allocate DesignRealization::preserve to logical.L06;
    allocate DesignRealization::checkCurrent to logical.L06;
    allocate DesignRealization::credibility to logical.L04;
    allocate DesignRealization::assess to logical.L05;
    allocate DesignRealization::compare to logical.L02;
    allocate DesignRealization::select to ScenarioViews::epsEngineer;
    allocate DesignRealization::checkSelection to logical.L06;
    allocate DesignRealization::retainSelection to logical.L06;
    allocate DesignRealization::retainGaps to logical.L06;
    #sourceTrace dependency DesignRealization_SC03 from DesignRealization to ScenarioViews::SC03;
    action def ConceptRealization {
        doc /* Mission concepts use the agreed Systems Engineer mission definition, concept analysis and Systems Engineer selection authority. Numerical applicability and criterion gates precede supported mandatory feasibility and engineer selection. Unknown technical quantities/rates and temporal shortages remain explicit. */
        perform action makeConfiguration : ConfigureConcept { @LogicalStep { component = FrameworkLogical::LogicalFramework::L02 meta SysML::PartUsage; operation = FrameworkLogical::MissionDesign::configureConcept meta SysML::ActionUsage; } }
        first makeConfiguration then configure;
        perform action submit : ScenarioViews::SC01External1 { @ExternalStep { performer = ScenarioViews::systemsEngineer meta SysML::PartUsage; } }
        perform action receive : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action configure : DefineDesign {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L02 meta SysML::PartUsage; operation = FrameworkLogical::MissionDesign::defineDesign meta SysML::ActionUsage; }
        }
        perform action budget : BudgetSize {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L02 meta SysML::PartUsage; operation = FrameworkLogical::MissionDesign::budgetSize meta SysML::ActionUsage; }
        }
        perform action planCriteria : PlanAssessment {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::planAssessment meta SysML::ActionUsage; }
        }
        perform action plan : PlanAnalysis {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::planAnalysis meta SysML::ActionUsage; }
        }
        perform action execute : ScenarioViews::SC01External3 { @ExternalStep { performer = ScenarioViews::analysisTools meta SysML::PartUsage; } }
        perform action receiveResult : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action preserve : PreserveRun {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRun meta SysML::ActionUsage; }
        }
        perform action checkCurrent : CheckResultContext {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkResultContext meta SysML::ActionUsage; }
        }
        perform action credibility : AssessModel {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L04 meta SysML::PartUsage; operation = FrameworkLogical::ModelCredibility::assessModel meta SysML::ActionUsage; }
        }
        perform action assess : AssessProduct {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::assessProduct meta SysML::ActionUsage; }
        }
        perform action compare : CompareDesigns {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L02 meta SysML::PartUsage; operation = FrameworkLogical::MissionDesign::compareDesigns meta SysML::ActionUsage; }
        }
        perform action select : ScenarioViews::SC01External5 { @ExternalStep { performer = ScenarioViews::systemsEngineer meta SysML::PartUsage; } }
        perform action checkSelection : CheckEngineerSelection {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkSelection meta SysML::ActionUsage; }
        }
        perform action retainSelection : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainGaps : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainRaw_receiveResult : PreserveRecord { @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; } }
        flow raw_receiveResult of CheckedTransfer from receiveResult.checked to retainRaw_receiveResult.record;
        first retainRaw_receiveResult then complete;
        decide compatibleInput;
        decide compatibleResult;
        decide usableNumerics;
        decide supportedCriteria;
        decide selected;
        merge complete;
        first start then submit;
        first submit then receive;
        first receive then compatibleInput;
        succession admitInput first compatibleInput if receive.compatible then makeConfiguration;
        succession rejectInput first compatibleInput if not receive.compatible then retainGaps;
        first configure then budget;
        first budget then planCriteria;
        first planCriteria then plan;
        first plan then execute;
        first execute then receiveResult;
        first receiveResult then compatibleResult;
        succession admitResult first compatibleResult if receiveResult.compatible then preserve;
        succession rejectResult first compatibleResult if not receiveResult.compatible then retainRaw_receiveResult;
        first preserve then checkCurrent;
        first checkCurrent then credibility;
        first credibility then usableNumerics;
        succession admitModel first usableNumerics if checkCurrent.current and credibility.numericallyValid and credibility.applicable then assess;
        succession rejectModel first usableNumerics if not (checkCurrent.current and credibility.numericallyValid and credibility.applicable) then retainGaps;
        first assess then supportedCriteria;
        succession admitCriteria first supportedCriteria if assess.claimSupported then compare;
        succession rejectCriteria first supportedCriteria if not assess.claimSupported then retainGaps;
        first compare then select;
        first select then checkSelection;
        first checkSelection then selected;
        succession admitSelection first selected if compare.feasible and select.accepted and checkSelection.authorizedCurrent then retainSelection;
        succession holdSelection first selected if not (compare.feasible and select.accepted and checkSelection.authorizedCurrent) then retainGaps;
        first retainSelection then complete;
        first complete then done;
        first retainGaps then complete;
        flow exchange1 of MissionDefinition from submit.mission to receive.raw;
        flow exchange2 of DesignConfiguration from makeConfiguration.configuration to configure.configuration;
        flow exchange3 of DesignWork from configure.work to budget.work;
        flow exchange4 of DesignConfiguration from makeConfiguration.configuration to planCriteria.configuration;
        flow exchange5 of DesignWork from budget.updatedWork to plan.work;
        flow exchange6 of AnalysisPlan from plan.plan to execute.plan;
        flow exchange7 of AnalysisResult from execute.result to receiveResult.raw;
        flow exchange8 of AnalysisResult from execute.result to preserve.result;
        flow exchange9 of RunWork from preserve.work to credibility.work;
        flow exchange10 of RunWork from preserve.work to checkCurrent.record;
        flow exchange11 of EPSAssessmentPlan from planCriteria.plan to assess.plan;
        flow exchange12 of EvidenceAssessment from credibility.evidence to assess.evidence;
        flow exchange13 of DesignWork from budget.updatedWork to compare.work;
        flow exchange14 of EvidenceAssessment from assess.updatedEvidence to compare.evidence;
        flow exchange15 of DesignStudy from compare.study to select.study;
        flow exchange16 of EngineeringDecision from select.decision to checkSelection.decision;
        flow exchange17 of DesignConfiguration from makeConfiguration.configuration to checkSelection.configuration;
        flow exchange18 of EngineeringDecision from select.decision to retainSelection.record;
        flow exchange19 of EngineeringArtifact from submit.mission to retainGaps.record;
        flow exchange20 of MissionDefinition from submit.mission to makeConfiguration.mission;
    }
    allocate ConceptRealization::retainRaw_receiveResult to logical.L06;
    allocate ConceptRealization::submit to ScenarioViews::systemsEngineer;
    allocate ConceptRealization::receive to logical.L06;
    allocate ConceptRealization::configure to logical.L02;
    allocate ConceptRealization::budget to logical.L02;
    allocate ConceptRealization::planCriteria to logical.L05;
    allocate ConceptRealization::plan to logical.L03;
    allocate ConceptRealization::execute to ScenarioViews::analysisTools;
    allocate ConceptRealization::receiveResult to logical.L06;
    allocate ConceptRealization::preserve to logical.L06;
    allocate ConceptRealization::checkCurrent to logical.L06;
    allocate ConceptRealization::credibility to logical.L04;
    allocate ConceptRealization::assess to logical.L05;
    allocate ConceptRealization::compare to logical.L02;
    allocate ConceptRealization::select to ScenarioViews::systemsEngineer;
    allocate ConceptRealization::checkSelection to logical.L06;
    allocate ConceptRealization::retainSelection to logical.L06;
    allocate ConceptRealization::retainGaps to logical.L06;
    allocate ConceptRealization::makeConfiguration to logical.L02;
    #sourceTrace dependency ConceptRealization_SC01 from ConceptRealization to ScenarioViews::SC01;
    action def SoftwareRealization {
        doc /* Detailed interfaces/control, external model MIL and authorized external host coding/build/SIL. Specific current detailed-design release is required before a coding request exists. MIL/SIL findings and engineer product disposition precede any scoped readiness claim. */
        perform action submit : ScenarioViews::SC04External1 { @ExternalStep { performer = ScenarioViews::epsEngineer meta SysML::PartUsage; } }
        perform action receive : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action interfaces : DefineInterfaces {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L02 meta SysML::PartUsage; operation = FrameworkLogical::MissionDesign::defineInterfaces meta SysML::ActionUsage; }
        }
        perform action mapping : MapFPrime { @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::mapFPrime meta SysML::ActionUsage; } }
        flow mappedSpecification from submit.specification to mapping.specification;
        flow mappedCodingWork from mapping.work to coordinate.work;
        perform action planCriteria : PlanAssessment {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::planAssessment meta SysML::ActionUsage; }
        }
        perform action planMIL : PlanMIL {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::planMIL meta SysML::ActionUsage; }
        }
        perform action executeMIL : ScenarioViews::SC04External3 { @ExternalStep { performer = ScenarioViews::analysisTools meta SysML::PartUsage; } }
        perform action receiveMIL : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action preserveMIL : PreserveRun {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRun meta SysML::ActionUsage; }
        }
        perform action assessMIL : AssessModel {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L04 meta SysML::PartUsage; operation = FrameworkLogical::ModelCredibility::assessModel meta SysML::ActionUsage; }
        }
        perform action release : AuthorizeDetailedDesign { @ExternalStep { performer = ScenarioViews::epsEngineer meta SysML::PartUsage; } }
        perform action checkRelease : CheckDetailedDesignAuthorization {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkDesignAuthorization meta SysML::ActionUsage; }
        }
        perform action coordinate : CoordinateCoding {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::coordinateCoding meta SysML::ActionUsage; }
        }
        perform action codeBuildSil : ScenarioViews::SC04External5 { @ExternalStep { performer = ScenarioViews::hostToolchain meta SysML::PartUsage; } }
        perform action receiveSIL : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action preserveSIL : PreserveRun {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRun meta SysML::ActionUsage; }
        }
        perform action checkCurrent : CheckResultContext {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkResultContext meta SysML::ActionUsage; }
        }
        perform action compare : CompareMILSil {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::compareMILSil meta SysML::ActionUsage; }
        }
        perform action credibility : AssessModel {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L04 meta SysML::PartUsage; operation = FrameworkLogical::ModelCredibility::assessModel meta SysML::ActionUsage; }
        }
        perform action assess : AssessProduct {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::assessProduct meta SysML::ActionUsage; }
        }
        perform action present : PresentAssessment {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::presentAssessment meta SysML::ActionUsage; }
        }
        perform action approve : ScenarioViews::SC04External7 { @ExternalStep { performer = ScenarioViews::epsEngineer meta SysML::PartUsage; } }
        perform action checkProducts : CheckEngineerSelection {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkSelection meta SysML::ActionUsage; }
        }
        perform action retainProducts : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action block : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainRaw_receiveMIL : PreserveRecord { @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; } }
        flow raw_receiveMIL of CheckedTransfer from receiveMIL.checked to retainRaw_receiveMIL.record;
        first retainRaw_receiveMIL then complete;
        perform action retainRaw_receiveSIL : PreserveRecord { @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; } }
        flow raw_receiveSIL of CheckedTransfer from receiveSIL.checked to retainRaw_receiveSIL.record;
        first retainRaw_receiveSIL then complete;
        perform action rejectRelease : PreserveRecord { @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; } }
        flow rejectedRelease of DetailedDesignAuthorization from release.authorization to rejectRelease.record;
        first rejectRelease then complete;
        decide compatibleInput;
        decide compatibleMIL;
        decide codingRelease;
        decide compatibleSIL;
        decide supportedProducts;
        decide authorizedProducts;
        merge complete;
        first start then submit;
        first submit then receive;
        first receive then compatibleInput;
        succession admitInput first compatibleInput if receive.compatible then interfaces;
        succession rejectInput first compatibleInput if not receive.compatible then block;
        first interfaces then mapping;
        first mapping then planCriteria;
        first planCriteria then planMIL;
        first planMIL then executeMIL;
        first executeMIL then receiveMIL;
        first receiveMIL then compatibleMIL;
        succession admitMIL first compatibleMIL if receiveMIL.compatible then preserveMIL;
        succession rejectMIL first compatibleMIL if not receiveMIL.compatible then retainRaw_receiveMIL;
        first preserveMIL then assessMIL;
        first assessMIL then release;
        first release then checkRelease;
        first checkRelease then codingRelease;
        succession authorizeCoding first codingRelease if checkRelease.authorizedDetailedDesign and checkRelease.currentDesign and checkRelease.blockersClear and interfaces.profileCompatible and mapping.profileCompatible then coordinate;
        succession blockCoding first codingRelease if not (checkRelease.authorizedDetailedDesign and checkRelease.currentDesign and checkRelease.blockersClear and interfaces.profileCompatible and mapping.profileCompatible) then rejectRelease;
        first coordinate then codeBuildSil;
        first codeBuildSil then receiveSIL;
        first receiveSIL then compatibleSIL;
        succession admitSIL first compatibleSIL if receiveSIL.compatible then preserveSIL;
        succession rejectSIL first compatibleSIL if not receiveSIL.compatible then retainRaw_receiveSIL;
        first preserveSIL then checkCurrent;
        first checkCurrent then compare;
        first compare then credibility;
        first credibility then assess;
        first assess then supportedProducts;
        succession admitProducts first supportedProducts if checkCurrent.current and credibility.numericallyValid and credibility.applicable and assess.claimSupported then present;
        succession unsupportedProducts first supportedProducts if not (checkCurrent.current and credibility.numericallyValid and credibility.applicable and assess.claimSupported) then block;
        first present then approve;
        first approve then checkProducts;
        first checkProducts then authorizedProducts;
        succession admitApproval first authorizedProducts if checkProducts.authorizedCurrent then retainProducts;
        succession rejectApproval first authorizedProducts if not checkProducts.authorizedCurrent then block;
        first retainProducts then complete;
        first complete then done;
        first block then complete;
        flow exchange1 of EPSInterfaceSpecification from submit.specification to receive.raw;
        flow exchange2 of EPSInterfaceSpecification from submit.specification to interfaces.specification;
        flow exchange3 of DesignConfiguration from interfaces.configuration to planCriteria.configuration;
        flow exchange4 of DesignWork from interfaces.work to planMIL.work;
        flow exchange5 of AnalysisPlan from planMIL.plan to executeMIL.plan;
        flow exchange6 of AnalysisResult from executeMIL.result to receiveMIL.raw;
        flow exchange7 of AnalysisResult from executeMIL.result to preserveMIL.result;
        flow exchange8 of RunWork from preserveMIL.work to assessMIL.work;
        flow exchange9 of DesignWork from interfaces.work to release.work;
        flow exchange10 of DetailedDesignAuthorization from release.authorization to checkRelease.authorization;
        flow exchange11 of DesignWork from interfaces.work to checkRelease.work;
        flow exchange12 of DetailedDesignAuthorization from release.authorization to coordinate.authorization;
        flow exchange13 of DesignWork from mapping.work to coordinate.work;
        flow exchange14 of CodingRequest from coordinate.request to codeBuildSil.request;
        flow exchange15 of SoftwareRunResult from codeBuildSil.result to receiveSIL.raw;
        flow exchange16 of AnalysisResult from executeMIL.result to preserveSIL.result;
        flow exchange17 of SoftwareRunResult from codeBuildSil.result to preserveSIL.software;
        flow exchange18 of RunWork from preserveSIL.work to compare.work;
        flow exchange19 of RunWork from preserveSIL.work to checkCurrent.record;
        flow exchange20 of EPSAssessmentPlan from planCriteria.plan to assess.plan;
        flow exchange21 of RunWork from compare.updatedWork to credibility.work;
        flow exchange22 of EvidenceAssessment from credibility.evidence to assess.evidence;
        flow exchange23 of EvidenceAssessment from assess.updatedEvidence to present.evidence;
        flow exchange24 of EngineeringResponse from present.response to approve.response;
        flow exchange25 of EngineeringDecision from approve.decision to checkProducts.decision;
        flow exchange26 of DesignConfiguration from interfaces.configuration to checkProducts.configuration;
        flow exchange27 of EngineeringDecision from approve.decision to retainProducts.record;
        flow exchange28 of EPSInterfaceSpecification from submit.specification to block.record;
    }
    allocate SoftwareRealization::retainRaw_receiveSIL to logical.L06;
    allocate SoftwareRealization::retainRaw_receiveMIL to logical.L06;
    allocate SoftwareRealization::submit to ScenarioViews::epsEngineer;
    allocate SoftwareRealization::receive to logical.L06;
    allocate SoftwareRealization::interfaces to logical.L02;
    allocate SoftwareRealization::mapping to logical.L03;
    allocate SoftwareRealization::rejectRelease to logical.L06;
    allocate SoftwareRealization::planCriteria to logical.L05;
    allocate SoftwareRealization::planMIL to logical.L03;
    allocate SoftwareRealization::executeMIL to ScenarioViews::analysisTools;
    allocate SoftwareRealization::receiveMIL to logical.L06;
    allocate SoftwareRealization::preserveMIL to logical.L06;
    allocate SoftwareRealization::assessMIL to logical.L04;
    allocate SoftwareRealization::release to ScenarioViews::epsEngineer;
    allocate SoftwareRealization::checkRelease to logical.L06;
    allocate SoftwareRealization::coordinate to logical.L03;
    allocate SoftwareRealization::codeBuildSil to ScenarioViews::hostToolchain;
    allocate SoftwareRealization::receiveSIL to logical.L06;
    allocate SoftwareRealization::preserveSIL to logical.L06;
    allocate SoftwareRealization::checkCurrent to logical.L06;
    allocate SoftwareRealization::compare to logical.L03;
    allocate SoftwareRealization::credibility to logical.L04;
    allocate SoftwareRealization::assess to logical.L05;
    allocate SoftwareRealization::present to logical.L05;
    allocate SoftwareRealization::approve to ScenarioViews::epsEngineer;
    allocate SoftwareRealization::checkProducts to logical.L06;
    allocate SoftwareRealization::retainProducts to logical.L06;
    allocate SoftwareRealization::block to logical.L06;
    #sourceTrace dependency SoftwareRealization_SC04 from SoftwareRealization to ScenarioViews::SC04;
    action def ChangeReviewRealization {
        doc /* Controlled change and review shared by all phases and product levels. Context edits invalidate affected outputs before delayed work can be used. Only authorized current changes create successors. Current unaffected evidence can be reused, while changed assessments are repeated. Preparation and designated-authority progression are distinct. */
        perform action request : ScenarioViews::SC05External1 { @ExternalStep { performer = ScenarioViews::systemsEngineer meta SysML::PartUsage; } }
        perform action receive : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action invalidate : InvalidateAndReassess {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::invalidate meta SysML::ActionUsage; }
        }
        perform action changeDecision : RequestChangeDecision { @ExternalStep { performer = ScenarioViews::systemsEngineer meta SysML::PartUsage; } }
        perform action checkChange : CheckEngineeringChange {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkChange meta SysML::ActionUsage; }
        }
        perform action successor : RetainSuccessor {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::successor meta SysML::ActionUsage; }
        }
        perform action reassessAdvice : ReassessAssistance {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::reassess meta SysML::ActionUsage; }
        }
        perform action planRepeat : PlanRepeatedAssessment {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::planRepeat meta SysML::ActionUsage; }
        }
        perform action repeat : ScenarioViews::SC05External3 { @ExternalStep { performer = ScenarioViews::analysisTools meta SysML::PartUsage; } }
        perform action receiveResult : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action preserve : PreserveRun {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRun meta SysML::ActionUsage; }
        }
        perform action credibility : AssessModel {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L04 meta SysML::PartUsage; operation = FrameworkLogical::ModelCredibility::assessModel meta SysML::ActionUsage; }
        }
        perform action retrieve : RetrieveBaseline {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::retrieveBaseline meta SysML::ActionUsage; }
        }
        perform action assess : AssessProduct {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::assessProduct meta SysML::ActionUsage; }
        }
        perform action views : MakeViews {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::makeViews meta SysML::ActionUsage; }
        }
        perform action prepare : PrepareReviewPackage {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::prepareReview meta SysML::ActionUsage; }
        }
        perform action reviewers : ScenarioViews::SC05External5 { @ExternalStep { performer = ScenarioViews::reviewers meta SysML::PartUsage; } }
        perform action authority : ScenarioViews::SC05External6 { @ExternalStep { performer = ScenarioViews::reviewAuthority meta SysML::PartUsage; } }
        perform action checkBaseline : CheckResultContext {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkResultContext meta SysML::ActionUsage; }
        }
        perform action checkDecision : CheckReviewDecision {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::checkReviewDecision meta SysML::ActionUsage; }
        }
        perform action record : RecordReviewDecision {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::recordReview meta SysML::ActionUsage; }
        }
        perform action retain : RetainReviewedBaseline {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::retainReview meta SysML::ActionUsage; }
        }
        perform action holdChange : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action holdReview : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action rejectReview : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainRaw_receiveResult : PreserveRecord { @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; } }
        flow raw_receiveResult of CheckedTransfer from receiveResult.checked to retainRaw_receiveResult.record;
        first retainRaw_receiveResult then complete;
        decide compatibleInput;
        decide changeRequested;
        decide authorizedChange;
        decide repeatRequired;
        decide compatibleResult;
        decide entrance;
        decide reviewAuthorityGate;
        merge baselineAvailable;
        merge evidenceAvailable;
        merge complete;
        first start then request;
        first request then receive;
        first receive then compatibleInput;
        succession admitInput first compatibleInput if receive.compatible then invalidate;
        succession rejectInput first compatibleInput if not receive.compatible then holdReview;
        first invalidate then changeRequested;
        succession proposedChange first changeRequested if invalidate.hasChange then changeDecision;
        succession reviewCurrent first changeRequested if not invalidate.hasChange then retrieve;
        first changeDecision then checkChange;
        first checkChange then authorizedChange;
        succession admitChange first authorizedChange if checkChange.authorizedCurrent and checkChange.acceptedChange then successor;
        succession declineChange first authorizedChange if not (checkChange.authorizedCurrent and checkChange.acceptedChange) then holdChange;
        first holdChange then retrieve;
        first successor then reassessAdvice;
        first reassessAdvice then repeatRequired;
        succession repeatAffected first repeatRequired if checkChange.reassessmentRequired then planRepeat;
        succession reuseApplicable first repeatRequired if not checkChange.reassessmentRequired then retrieve;
        first planRepeat then repeat;
        first repeat then receiveResult;
        first receiveResult then compatibleResult;
        succession admitResult first compatibleResult if receiveResult.compatible then preserve;
        succession rejectResult first compatibleResult if not receiveResult.compatible then retainRaw_receiveResult;
        first preserve then credibility;
        first credibility then evidenceAvailable;
        first retrieve then evidenceAvailable;
        first evidenceAvailable then assess;
        first assess then views;
        first views then prepare;
        first prepare then entrance;
        succession preparePackage first entrance if prepare.entranceComplete then reviewers;
        succession incompletePackage first entrance if not prepare.entranceComplete then holdReview;
        first reviewers then authority;
        first authority then checkBaseline;
        first checkBaseline then checkDecision;
        first checkDecision then reviewAuthorityGate;
        succession admitReviewDecision first reviewAuthorityGate if checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete) then record;
        succession rejectReviewDecision first reviewAuthorityGate if not (checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete)) then rejectReview;
        first record then retain;
        first retain then complete;
        first complete then done;
        first holdReview then complete;
        first rejectReview then complete;
        flow exchange1 of EngineeringSubmission from request.submission to receive.raw;
        flow exchange2 of EngineeringSubmission from request.submission to invalidate.submission;
        flow exchange3 of ImpactNotice from invalidate.impact to changeDecision.impact;
        flow exchange4 of EngineeringSubmission from invalidate.updatedSubmission to checkChange.submission;
        flow exchange5 of EngineeringDecision from changeDecision.decision to checkChange.decision;
        flow exchange6 of EngineeringSubmission from invalidate.updatedSubmission to successor.submission;
        flow exactChangeDecision of EngineeringDecision from changeDecision.decision to successor.decision;
        flow exchange7 of ImpactNotice from invalidate.impact to reassessAdvice.impact;
        flow exchange8 of ImpactNotice from invalidate.impact to planRepeat.impact;
        flow exchange9 of AnalysisPlan from planRepeat.plan to repeat.plan;
        flow exchange10 of AnalysisResult from repeat.result to receiveResult.raw;
        flow exchange11 of AnalysisResult from repeat.result to preserve.result;
        flow exchange12 of RunWork from preserve.work to credibility.work;
        flow exchange13 of EngineeringSubmission from invalidate.updatedSubmission to retrieve.submission;
        flow exchange14 of PhaseBaseline from successor.baseline to retrieve.successorBaseline;
        flow exchange15 of EvidenceAssessment from credibility.evidence to assess.evidence;
        flow exchange16 of EvidenceAssessment from retrieve.evidence to assess.evidence;
        flow exchange17 of PhaseBaseline from successor.baseline to views.baseline;
        flow exchange18 of PhaseBaseline from retrieve.baseline to views.baseline;
        flow exchange19 of PhaseBaseline from successor.baseline to prepare.baseline;
        flow exchange20 of PhaseBaseline from retrieve.baseline to prepare.baseline;
        flow exchange21 of ReviewPackage from views.reviewPackage to prepare.views;
        flow exchange22 of EvidenceAssessment from assess.updatedEvidence to prepare.evidence;
        flow exchange23 of ReviewPackage from prepare.reviewPackage to reviewers.reviewPackage;
        flow exchange24 of ReviewSubmission from reviewers.findings to authority.findings;
        flow exchange25 of ReviewSubmission from authority.submission to checkDecision.submission;
        flow exchange26 of EvidenceAssessment from assess.updatedEvidence to checkDecision.evidence;
        flow exchange27 of PhaseBaseline from successor.baseline to checkBaseline.record;
        flow exchange28 of PhaseBaseline from retrieve.baseline to checkBaseline.record;
        flow exchange29 of Boolean from checkBaseline.current to checkDecision.baselineCurrent;
        flow exchange30 of PhaseBaseline from successor.baseline to checkDecision.baseline;
        flow exchange31 of PhaseBaseline from retrieve.baseline to checkDecision.baseline;
        flow exchange32 of ReviewWork from checkDecision.work to record.work;
        flow exchange33 of ReviewWork from record.updatedWork to retain.work;
        flow exchange34 of EngineeringSubmission from request.submission to holdReview.record;
        flow exchange35 of ReviewWork from checkDecision.work to rejectReview.record;
        flow exchange36 of EngineeringDecision from changeDecision.decision to holdChange.record;
    }
    allocate ChangeReviewRealization::retainRaw_receiveResult to logical.L06;
    allocate ChangeReviewRealization::request to ScenarioViews::systemsEngineer;
    allocate ChangeReviewRealization::receive to logical.L06;
    allocate ChangeReviewRealization::invalidate to logical.L06;
    allocate ChangeReviewRealization::changeDecision to ScenarioViews::systemsEngineer;
    allocate ChangeReviewRealization::checkChange to logical.L06;
    allocate ChangeReviewRealization::successor to logical.L06;
    allocate ChangeReviewRealization::reassessAdvice to logical.L01;
    allocate ChangeReviewRealization::planRepeat to logical.L03;
    allocate ChangeReviewRealization::repeat to ScenarioViews::analysisTools;
    allocate ChangeReviewRealization::receiveResult to logical.L06;
    allocate ChangeReviewRealization::preserve to logical.L06;
    allocate ChangeReviewRealization::credibility to logical.L04;
    allocate ChangeReviewRealization::retrieve to logical.L06;
    allocate ChangeReviewRealization::assess to logical.L05;
    allocate ChangeReviewRealization::views to logical.L05;
    allocate ChangeReviewRealization::prepare to logical.L05;
    allocate ChangeReviewRealization::reviewers to ScenarioViews::reviewers;
    allocate ChangeReviewRealization::authority to ScenarioViews::reviewAuthority;
    allocate ChangeReviewRealization::checkBaseline to logical.L06;
    allocate ChangeReviewRealization::checkDecision to logical.L05;
    allocate ChangeReviewRealization::record to logical.L05;
    allocate ChangeReviewRealization::retain to logical.L06;
    allocate ChangeReviewRealization::holdChange to logical.L06;
    allocate ChangeReviewRealization::holdReview to logical.L06;
    allocate ChangeReviewRealization::rejectReview to logical.L06;
    #sourceTrace dependency ChangeReviewRealization_SC05 from ChangeReviewRealization to ScenarioViews::SC05;
    action def ReplayRealization {
        doc /* Independent reconstruction of a designated analysis/MIL/SIL result. Fixed comparison rules and complete dependencies precede external execution. Failed replay never establishes model validity. */
        perform action request : SupplyReplay { @ExternalStep { performer = ScenarioViews::reviewers meta SysML::PartUsage; } }
        perform action prepare : PrepareReplay {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::prepareReplay meta SysML::ActionUsage; }
        }
        perform action execute : ScenarioViews::SC05External3 { @ExternalStep { performer = ScenarioViews::analysisTools meta SysML::PartUsage; } }
        perform action receive : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action preserve : PreserveRun {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRun meta SysML::ActionUsage; }
        }
        perform action compare : ReplayRun {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::replay meta SysML::ActionUsage; }
        }
        perform action retain : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action missing : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainRaw_receive : PreserveRecord { @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; } }
        flow raw_receive of CheckedTransfer from receive.checked to retainRaw_receive.record;
        first retainRaw_receive then complete;
        decide replayReady;
        decide compatibleResult;
        merge complete;
        first start then request;
        first request then prepare;
        first prepare then replayReady;
        succession admitReplay first replayReady if prepare.dependenciesComplete and prepare.rulesFixed then execute;
        succession blockReplay first replayReady if not (prepare.dependenciesComplete and prepare.rulesFixed) then missing;
        first execute then receive;
        first receive then compatibleResult;
        succession admitResult first compatibleResult if receive.compatible then preserve;
        succession rejectResult first compatibleResult if not receive.compatible then retainRaw_receive;
        first preserve then compare;
        first compare then retain;
        first retain then complete;
        first complete then done;
        first missing then complete;
        flow exchange1 of ReplayRequest from request.request to prepare.request;
        flow exchange2 of AnalysisPlan from prepare.preparation.plan to execute.plan;
        flow exchange3 of ReplayPreparation from prepare.preparation to compare.preparation;
        flow exchange4 of AnalysisResult from execute.result to compare.result;
        flow exchange5 of AnalysisResult from execute.result to receive.raw;
        flow exchange6 of AnalysisResult from execute.result to preserve.result;
        flow exchange7 of ReplayComparison from compare.comparison to retain.record;
        flow exchange8 of ReplayRequest from request.request to missing.record;
    }
    allocate ReplayRealization::retainRaw_receive to logical.L06;
    allocate ReplayRealization::request to ScenarioViews::reviewers;
    allocate ReplayRealization::prepare to logical.L06;
    allocate ReplayRealization::execute to ScenarioViews::analysisTools;
    allocate ReplayRealization::receive to logical.L06;
    allocate ReplayRealization::preserve to logical.L06;
    allocate ReplayRealization::compare to logical.L03;
    allocate ReplayRealization::retain to logical.L06;
    allocate ReplayRealization::missing to logical.L06;
    #sourceTrace dependency ReplayRealization_SC05 from ReplayRealization to ScenarioViews::SC05;
    action def CalibrationRealization {
        doc /* Supplied-data calibration proposes a change. Independent assessment remains separate. A declined update is preserved. Accepted updates re-enter the shared impact, authorization and reassessment process, with no silent model overwrite. */
        perform action supply : SupplyCalibration { @ExternalStep { performer = ScenarioViews::epsEngineer meta SysML::PartUsage; } }
        perform action receive : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action checkData : CheckReferenceData {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L04 meta SysML::PartUsage; operation = FrameworkLogical::ModelCredibility::checkReferenceData meta SysML::ActionUsage; }
        }
        perform action propose : ProposeCalibration {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L04 meta SysML::PartUsage; operation = FrameworkLogical::ModelCredibility::proposeCalibration meta SysML::ActionUsage; }
        }
        perform action choose : ChooseCalibration { @ExternalStep { performer = ScenarioViews::epsEngineer meta SysML::PartUsage; } }
        perform action prepareChange : PrepareCalibrationChange {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::prepareCalibrationChange meta SysML::ActionUsage; }
        }
        perform action invalidate : InvalidateAndReassess {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::invalidate meta SysML::ActionUsage; }
        }
        perform action checkChange : CheckEngineeringChange {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkChange meta SysML::ActionUsage; }
        }
        perform action successor : RetainSuccessor {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::successor meta SysML::ActionUsage; }
        }
        perform action reassess : ReassessAssistance {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L01 meta SysML::PartUsage; operation = FrameworkLogical::RequirementsAssistance::reassess meta SysML::ActionUsage; }
        }
        perform action planRepeat : PlanRepeatedAssessment {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L03 meta SysML::PartUsage; operation = FrameworkLogical::SimulationIntegration::planRepeat meta SysML::ActionUsage; }
        }
        perform action repeat : ScenarioViews::SC05External3 { @ExternalStep { performer = ScenarioViews::analysisTools meta SysML::PartUsage; } }
        perform action receiveResult : CheckTransfer {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::checkTransfer meta SysML::ActionUsage; }
        }
        perform action preserve : PreserveRun {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRun meta SysML::ActionUsage; }
        }
        perform action credibility : AssessModel {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L04 meta SysML::PartUsage; operation = FrameworkLogical::ModelCredibility::assessModel meta SysML::ActionUsage; }
        }
        perform action assess : AssessProduct {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L05 meta SysML::PartUsage; operation = FrameworkLogical::EvidenceReview::assessProduct meta SysML::ActionUsage; }
        }
        perform action retainEvidence : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retain : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action unusable : PreserveRecord {
            @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; }
        }
        perform action retainRaw_receiveResult : PreserveRecord { @LogicalStep { component = FrameworkLogical::LogicalFramework::L06 meta SysML::PartUsage; operation = FrameworkLogical::ConfigurationExchange::preserveRecord meta SysML::ActionUsage; } }
        flow raw_receiveResult of CheckedTransfer from receiveResult.checked to retainRaw_receiveResult.record;
        first retainRaw_receiveResult then complete;
        decide compatibleData;
        decide calibrationData;
        decide authorizedChange;
        decide compatibleResult;
        merge complete;
        first start then supply;
        first supply then receive;
        first receive then compatibleData;
        succession admitData first compatibleData if receive.compatible then checkData;
        succession rejectData first compatibleData if not receive.compatible then unusable;
        first checkData then calibrationData;
        succession admitCalibration first calibrationData if checkData.dataUsable and checkData.independentSeparation then propose;
        succession blockCalibration first calibrationData if not (checkData.dataUsable and checkData.independentSeparation) then unusable;
        first propose then choose;
        first choose then prepareChange;
        first prepareChange then invalidate;
        first invalidate then checkChange;
        first checkChange then authorizedChange;
        succession admitCalibrationChange first authorizedChange if checkChange.authorizedCurrent and checkChange.acceptedChange then successor;
        succession declineCalibrationChange first authorizedChange if not (checkChange.authorizedCurrent and checkChange.acceptedChange) then retain;
        first successor then reassess;
        first reassess then planRepeat;
        first planRepeat then repeat;
        first repeat then receiveResult;
        first receiveResult then compatibleResult;
        succession admitReassessedResult first compatibleResult if receiveResult.compatible then preserve;
        succession rejectReassessedResult first compatibleResult if not receiveResult.compatible then retainRaw_receiveResult;
        first preserve then credibility;
        first credibility then assess;
        first assess then retainEvidence;
        first retainEvidence then complete;
        first complete then done;
        first retain then complete;
        first unusable then complete;
        flow exchange1 of ReferenceData from supply.data to receive.raw;
        flow exchange2 of ReferenceData from supply.data to checkData.data;
        flow exchange3 of EvidenceAssessment from supply.evidence to checkData.evidence;
        flow exchange4 of ReferenceData from supply.data to propose.data;
        flow exchange5 of ReferenceData from supply.data to unusable.record;
        flow exchange6 of EvidenceAssessment from supply.evidence to propose.evidence;
        flow exchange7 of ChangeProposal from propose.proposal to choose.proposal;
        flow exchange8 of ChangeProposal from propose.proposal to prepareChange.proposal;
        flow exchange9 of EngineeringDecision from choose.decision to prepareChange.decision;
        flow exchange10 of EngineeringSubmission from prepareChange.submission to invalidate.submission;
        flow exchange11 of EngineeringSubmission from invalidate.updatedSubmission to checkChange.submission;
        flow exchange12 of EngineeringDecision from choose.decision to checkChange.decision;
        flow exchange13 of EngineeringSubmission from invalidate.updatedSubmission to successor.submission;
        flow exactCalibrationDecision of EngineeringDecision from choose.decision to successor.decision;
        flow exchange14 of ImpactNotice from invalidate.impact to reassess.impact;
        flow exchange15 of ImpactNotice from invalidate.impact to planRepeat.impact;
        flow exchange16 of AnalysisPlan from planRepeat.plan to repeat.plan;
        flow exchange17 of AnalysisResult from repeat.result to receiveResult.raw;
        flow exchange18 of AnalysisResult from repeat.result to preserve.result;
        flow exchange19 of RunWork from preserve.work to credibility.work;
        flow exchange20 of EvidenceAssessment from credibility.evidence to assess.evidence;
        flow exchange21 of EvidenceAssessment from assess.updatedEvidence to retainEvidence.record;
        flow exchange22 of EngineeringDecision from choose.decision to retain.record;
    }
    allocate CalibrationRealization::retainRaw_receiveResult to logical.L06;
    allocate CalibrationRealization::supply to ScenarioViews::epsEngineer;
    allocate CalibrationRealization::receive to logical.L06;
    allocate CalibrationRealization::checkData to logical.L04;
    allocate CalibrationRealization::propose to logical.L04;
    allocate CalibrationRealization::choose to ScenarioViews::epsEngineer;
    allocate CalibrationRealization::prepareChange to logical.L06;
    allocate CalibrationRealization::invalidate to logical.L06;
    allocate CalibrationRealization::checkChange to logical.L06;
    allocate CalibrationRealization::successor to logical.L06;
    allocate CalibrationRealization::reassess to logical.L01;
    allocate CalibrationRealization::planRepeat to logical.L03;
    allocate CalibrationRealization::repeat to ScenarioViews::analysisTools;
    allocate CalibrationRealization::receiveResult to logical.L06;
    allocate CalibrationRealization::preserve to logical.L06;
    allocate CalibrationRealization::credibility to logical.L04;
    allocate CalibrationRealization::assess to logical.L05;
    allocate CalibrationRealization::retainEvidence to logical.L06;
    allocate CalibrationRealization::retain to logical.L06;
    allocate CalibrationRealization::unusable to logical.L06;
    #sourceTrace dependency CalibrationRealization_SC03 from CalibrationRealization to ScenarioViews::SC03;
    #sourceTrace dependency CalibrationRealization_SC05 from CalibrationRealization to ScenarioViews::SC05;
    #sourceTrace dependency calibrationChangePath from CalibrationRealization to ChangeReviewRealization;
    #sourceTrace dependency assistanceCurrency from AssistanceRealization to ConfigurationExchange::assistanceCurrency;
    #sourceTrace dependency reviewStateAuthority from ChangeReviewRealization to EvidenceReview::reviewState;
    #sourceTrace dependency behavior_FR01_1 from FrameworkRequirements::FR_01 to LogicalRealization::AssistanceRealization::retainDraft;
    #sourceTrace dependency behavior_FR02_1 from FrameworkRequirements::FR_02 to LogicalRealization::AssistanceRealization::checkDraft;
    #sourceTrace dependency behavior_FR03_1 from FrameworkRequirements::FR_03 to LogicalRealization::AssistanceRealization::recommend;
    #sourceTrace dependency behavior_FR04_1 from FrameworkRequirements::FR_04 to LogicalRealization::AssistanceRealization::trace;
    #sourceTrace dependency behavior_FR05_1 from FrameworkRequirements::FR_05 to LogicalRealization::AssistanceRealization::invalidateOnEdit;
    #sourceTrace dependency behavior_FR05_2 from FrameworkRequirements::FR_05 to LogicalRealization::AssistanceRealization::invalidate;
    #sourceTrace dependency behavior_FR05_3 from FrameworkRequirements::FR_05 to LogicalRealization::ChangeReviewRealization::invalidate;
    #sourceTrace dependency behavior_FR05_4 from FrameworkRequirements::FR_05 to LogicalRealization::CalibrationRealization::invalidate;
    #sourceTrace dependency behavior_FR06_1 from FrameworkRequirements::FR_06 to LogicalRealization::ChangeReviewRealization::successor;
    #sourceTrace dependency behavior_FR06_2 from FrameworkRequirements::FR_06 to LogicalRealization::CalibrationRealization::successor;
    #sourceTrace dependency behavior_FR07_1 from FrameworkRequirements::FR_07 to LogicalRealization::ChangeReviewRealization::retrieve;
    #sourceTrace dependency behavior_FR08_1 from FrameworkRequirements::FR_08 to LogicalRealization::AssistanceRealization::receive;
    #sourceTrace dependency behavior_FR08_2 from FrameworkRequirements::FR_08 to LogicalRealization::DesignRealization::receive;
    #sourceTrace dependency behavior_FR08_3 from FrameworkRequirements::FR_08 to LogicalRealization::DesignRealization::receiveResult;
    #sourceTrace dependency behavior_FR08_4 from FrameworkRequirements::FR_08 to LogicalRealization::ConceptRealization::receive;
    #sourceTrace dependency behavior_FR08_5 from FrameworkRequirements::FR_08 to LogicalRealization::ConceptRealization::receiveResult;
    #sourceTrace dependency behavior_FR08_6 from FrameworkRequirements::FR_08 to LogicalRealization::SoftwareRealization::receive;
    #sourceTrace dependency behavior_FR08_7 from FrameworkRequirements::FR_08 to LogicalRealization::SoftwareRealization::receiveMIL;
    #sourceTrace dependency behavior_FR08_8 from FrameworkRequirements::FR_08 to LogicalRealization::SoftwareRealization::receiveSIL;
    #sourceTrace dependency behavior_FR08_9 from FrameworkRequirements::FR_08 to LogicalRealization::ChangeReviewRealization::receive;
    #sourceTrace dependency behavior_FR08_10 from FrameworkRequirements::FR_08 to LogicalRealization::ChangeReviewRealization::receiveResult;
    #sourceTrace dependency behavior_FR08_11 from FrameworkRequirements::FR_08 to LogicalRealization::ReplayRealization::receive;
    #sourceTrace dependency behavior_FR08_12 from FrameworkRequirements::FR_08 to LogicalRealization::CalibrationRealization::receive;
    #sourceTrace dependency behavior_FR08_13 from FrameworkRequirements::FR_08 to LogicalRealization::CalibrationRealization::receiveResult;
    #sourceTrace dependency behavior_FR09_1 from FrameworkRequirements::FR_09 to LogicalRealization::DesignRealization::preserve;
    #sourceTrace dependency behavior_FR09_2 from FrameworkRequirements::FR_09 to LogicalRealization::ConceptRealization::preserve;
    #sourceTrace dependency behavior_FR09_3 from FrameworkRequirements::FR_09 to LogicalRealization::SoftwareRealization::preserveMIL;
    #sourceTrace dependency behavior_FR09_4 from FrameworkRequirements::FR_09 to LogicalRealization::SoftwareRealization::preserveSIL;
    #sourceTrace dependency behavior_FR09_5 from FrameworkRequirements::FR_09 to LogicalRealization::ChangeReviewRealization::preserve;
    #sourceTrace dependency behavior_FR09_6 from FrameworkRequirements::FR_09 to LogicalRealization::ReplayRealization::preserve;
    #sourceTrace dependency behavior_FR09_7 from FrameworkRequirements::FR_09 to LogicalRealization::CalibrationRealization::preserve;
    #sourceTrace dependency behavior_FR10_1 from FrameworkRequirements::FR_10 to LogicalRealization::ReplayRealization::compare;
    #sourceTrace dependency behavior_FR11_1 from FrameworkRequirements::FR_11 to LogicalRealization::DesignRealization::assess;
    #sourceTrace dependency behavior_FR11_2 from FrameworkRequirements::FR_11 to LogicalRealization::ConceptRealization::assess;
    #sourceTrace dependency behavior_FR11_3 from FrameworkRequirements::FR_11 to LogicalRealization::SoftwareRealization::assess;
    #sourceTrace dependency behavior_FR11_4 from FrameworkRequirements::FR_11 to LogicalRealization::ChangeReviewRealization::assess;
    #sourceTrace dependency behavior_FR11_5 from FrameworkRequirements::FR_11 to LogicalRealization::CalibrationRealization::assess;
    #sourceTrace dependency behavior_FR13_1 from FrameworkRequirements::FR_13 to LogicalRealization::DesignRealization::budget;
    #sourceTrace dependency behavior_FR13_2 from FrameworkRequirements::FR_13 to LogicalRealization::ConceptRealization::budget;
    #sourceTrace dependency behavior_FR14_1 from FrameworkRequirements::FR_14 to LogicalRealization::DesignRealization::compare;
    #sourceTrace dependency behavior_FR14_2 from FrameworkRequirements::FR_14 to LogicalRealization::ConceptRealization::compare;
    #sourceTrace dependency behavior_FR15_1 from FrameworkRequirements::FR_15 to LogicalRealization::DesignRealization::configure;
    #sourceTrace dependency behavior_FR15_2 from FrameworkRequirements::FR_15 to LogicalRealization::ConceptRealization::configure;
    #sourceTrace dependency behavior_FR16_1 from FrameworkRequirements::FR_16 to LogicalRealization::DesignRealization::plan;
    #sourceTrace dependency behavior_FR16_2 from FrameworkRequirements::FR_16 to LogicalRealization::ConceptRealization::plan;
    #sourceTrace dependency behavior_FR17_1 from FrameworkRequirements::FR_17 to LogicalRealization::AssistanceRealization::derive;
    #sourceTrace dependency behavior_FR18_1 from FrameworkRequirements::FR_18 to LogicalRealization::DesignRealization::plan;
    #sourceTrace dependency behavior_FR18_2 from FrameworkRequirements::FR_18 to LogicalRealization::ConceptRealization::plan;
    #sourceTrace dependency behavior_FR19_1 from FrameworkRequirements::FR_19 to LogicalRealization::SoftwareRealization::planMIL;
    #sourceTrace dependency behavior_FR20_1 from FrameworkRequirements::FR_20 to LogicalRealization::DesignRealization::budget;
    #sourceTrace dependency behavior_FR20_2 from FrameworkRequirements::FR_20 to LogicalRealization::ConceptRealization::budget;
    #sourceTrace dependency behavior_FR21_1 from FrameworkRequirements::FR_21 to LogicalRealization::DesignRealization::credibility;
    #sourceTrace dependency behavior_FR21_2 from FrameworkRequirements::FR_21 to LogicalRealization::ConceptRealization::credibility;
    #sourceTrace dependency behavior_FR21_3 from FrameworkRequirements::FR_21 to LogicalRealization::SoftwareRealization::assessMIL;
    #sourceTrace dependency behavior_FR21_4 from FrameworkRequirements::FR_21 to LogicalRealization::SoftwareRealization::credibility;
    #sourceTrace dependency behavior_FR21_5 from FrameworkRequirements::FR_21 to LogicalRealization::ChangeReviewRealization::credibility;
    #sourceTrace dependency behavior_FR21_6 from FrameworkRequirements::FR_21 to LogicalRealization::CalibrationRealization::credibility;
    #sourceTrace dependency behavior_FR22_1 from FrameworkRequirements::FR_22 to LogicalRealization::CalibrationRealization::propose;
    #sourceTrace dependency behavior_FR23_1 from FrameworkRequirements::FR_23 to LogicalRealization::DesignRealization::plan;
    #sourceTrace dependency behavior_FR23_2 from FrameworkRequirements::FR_23 to LogicalRealization::ConceptRealization::plan;
    #sourceTrace dependency behavior_FR24_1 from FrameworkRequirements::FR_24 to LogicalRealization::SoftwareRealization::compare;
    #sourceTrace dependency behavior_FR25_1 from FrameworkRequirements::FR_25 to LogicalRealization::DesignRealization::configure;
    #sourceTrace dependency behavior_FR25_2 from FrameworkRequirements::FR_25 to LogicalRealization::ConceptRealization::configure;
    #sourceTrace dependency behavior_FR26_1 from FrameworkRequirements::FR_26 to LogicalRealization::DesignRealization::plan;
    #sourceTrace dependency behavior_FR26_2 from FrameworkRequirements::FR_26 to LogicalRealization::ConceptRealization::plan;
    #sourceTrace dependency behavior_FR27_1 from FrameworkRequirements::FR_27 to LogicalRealization::DesignRealization::plan;
    #sourceTrace dependency behavior_FR27_2 from FrameworkRequirements::FR_27 to LogicalRealization::ConceptRealization::plan;
    #sourceTrace dependency behavior_FR28_1 from FrameworkRequirements::FR_28 to LogicalRealization::DesignRealization::planCriteria;
    #sourceTrace dependency behavior_FR28_2 from FrameworkRequirements::FR_28 to LogicalRealization::ConceptRealization::planCriteria;
    #sourceTrace dependency behavior_FR28_3 from FrameworkRequirements::FR_28 to LogicalRealization::SoftwareRealization::planCriteria;
    #sourceTrace dependency behavior_FR29_1 from FrameworkRequirements::FR_29 to LogicalRealization::AssistanceRealization::dispose;
    #sourceTrace dependency behavior_FR30_1 from FrameworkRequirements::FR_30 to LogicalRealization::AssistanceRealization::invalidateOnEdit;
    #sourceTrace dependency behavior_FR30_2 from FrameworkRequirements::FR_30 to LogicalRealization::AssistanceRealization::invalidate;
    #sourceTrace dependency behavior_FR30_3 from FrameworkRequirements::FR_30 to LogicalRealization::ChangeReviewRealization::invalidate;
    #sourceTrace dependency behavior_FR30_4 from FrameworkRequirements::FR_30 to LogicalRealization::CalibrationRealization::invalidate;
    #sourceTrace dependency behavior_FR31_1 from FrameworkRequirements::FR_31 to LogicalRealization::DesignRealization::credibility;
    #sourceTrace dependency behavior_FR31_2 from FrameworkRequirements::FR_31 to LogicalRealization::ConceptRealization::credibility;
    #sourceTrace dependency behavior_FR31_3 from FrameworkRequirements::FR_31 to LogicalRealization::SoftwareRealization::assessMIL;
    #sourceTrace dependency behavior_FR31_4 from FrameworkRequirements::FR_31 to LogicalRealization::SoftwareRealization::credibility;
    #sourceTrace dependency behavior_FR31_5 from FrameworkRequirements::FR_31 to LogicalRealization::ChangeReviewRealization::credibility;
    #sourceTrace dependency behavior_FR31_6 from FrameworkRequirements::FR_31 to LogicalRealization::CalibrationRealization::credibility;
    #sourceTrace dependency behavior_FR32_1 from FrameworkRequirements::FR_32 to LogicalRealization::DesignRealization::credibility;
    #sourceTrace dependency behavior_FR32_2 from FrameworkRequirements::FR_32 to LogicalRealization::ConceptRealization::credibility;
    #sourceTrace dependency behavior_FR32_3 from FrameworkRequirements::FR_32 to LogicalRealization::SoftwareRealization::assessMIL;
    #sourceTrace dependency behavior_FR32_4 from FrameworkRequirements::FR_32 to LogicalRealization::SoftwareRealization::credibility;
    #sourceTrace dependency behavior_FR32_5 from FrameworkRequirements::FR_32 to LogicalRealization::ChangeReviewRealization::credibility;
    #sourceTrace dependency behavior_FR32_6 from FrameworkRequirements::FR_32 to LogicalRealization::CalibrationRealization::credibility;
    #sourceTrace dependency behavior_FR33_1 from FrameworkRequirements::FR_33 to LogicalRealization::SoftwareRealization::interfaces;
    #sourceTrace dependency behavior_FR34_1 from FrameworkRequirements::FR_34 to LogicalRealization::SoftwareRealization::mapping;
    #sourceTrace dependency behavior_FR35_1 from FrameworkRequirements::FR_35 to LogicalRealization::SoftwareRealization::interfaces;
    #sourceTrace dependency behavior_FR36_1 from FrameworkRequirements::FR_36 to LogicalRealization::SoftwareRealization::coordinate;
    #sourceTrace dependency behavior_FR37_1 from FrameworkRequirements::FR_37 to LogicalRealization::ChangeReviewRealization::views;
    #sourceTrace dependency behavior_FR38_1 from FrameworkRequirements::FR_38 to LogicalRealization::ChangeReviewRealization::prepare;
    #sourceTrace dependency behavior_FR39_1 from FrameworkRequirements::FR_39 to LogicalRealization::AssistanceRealization::recommend;
    #sourceTrace dependency behavior_FR41_1 from FrameworkRequirements::FR_41 to LogicalRealization::AssistanceRealization::acknowledge;
    #sourceTrace dependency behavior_FR42_1 from FrameworkRequirements::FR_42 to LogicalRealization::ChangeReviewRealization::record;
    #sourceTrace dependency AssistanceRealization_reviewChange from AssistanceRealization to ChangeReviewRealization;
    #sourceTrace dependency ConceptRealization_reviewChange from ConceptRealization to ChangeReviewRealization;
    #sourceTrace dependency DesignRealization_reviewChange from DesignRealization to ChangeReviewRealization;
    #sourceTrace dependency SoftwareRealization_reviewChange from SoftwareRealization to ChangeReviewRealization;
}
