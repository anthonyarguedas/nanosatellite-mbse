// Proposed six-component physical candidate. Empirical status: proposed/unexecuted.
package CandidateVS {
    private import PhysicalVocabulary::*;
    private import FrameworkDomain::*;
    private import BoundaryViews::*;
    private import FrameworkLogical::*;
    private import ScalarValues::*;
    doc /* PA-VS: Capella/Valispace composite. Every cited method supplies a bounded subset. All joins, missing capabilities and whole-CUBICS/F Prime adapters are proposed completion. There is no selected candidate or empirical comparison outcome. */
    part def <'VS-C01'> C01 :> RequirementsGuidanceSoftware {
        doc /* Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed. */
        part authoring : CapellaValispaceAuthoringProfile {
            attribute :>> qualityRulesSemanticChecksAndLimitations = "Imported requirement text and Capella architecture context feed proposed quality checks.";
            attribute :>> recommendationContextAndApplicability = "Architecture, modes and requirements feed a sourced method service with eligibility checks.";
        }
        perform action :>> acknowledge;
        perform action :>> checkDraft : PhysicalCheckDraft {
            bind authoring = C01::authoring;
        }
        perform action :>> recommend : PhysicalRecommendMethods {
            bind authoring = C01::authoring;
        }
        perform action :>> dispose;
        perform action :>> reassess : PhysicalReassessAssistance {
            perform action :>> checkDraft references CandidateVS::C01::checkDraft;
            perform action :>> recommend references CandidateVS::C01::recommend;
        }
        perform action :>> retainRequirements;
        perform action :>> deriveAllocate;
        perform action :>> traceLinks;
        perform action :>> presentAdvice;
        perform action :>> sourceQuery;
    }
    @ComponentSpecification about C01 { tools = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; logical = "L01"; sourceMethods = ("L01.AR2"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C01 { identifier = "VS-C01"; sourceText = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; sourceLocator = "OOSEM L01 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "citation-4690"; status = "proposed/unexecuted"; }
    part def <'VS-C02'> C02 :> MissionDesignSoftware {
        doc /* Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification. */
        part designMethods : DesignMethodProfile {
            attribute :>> publishedSizingPlantEnergyOrCSRMMethods = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification.";
            attribute :>> missingEffectsUnknownsAndProposedCompletion = "Declare missing source data, dynamic/thermal/aging/EMC/RAM effects, uncertainty and applicability. No complete tool workflow is established.";
        }
        perform action :>> defineDesign;
        perform action :>> budgetSize : PhysicalBudgetSize {
            bind profile = C02::designMethods;
        }
        perform action :>> compareDesigns;
        perform action :>> defineInterfaces;
        perform action :>> configureConcept;
    }
    @ComponentSpecification about C02 { tools = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; logical = "L02"; sourceMethods = ("L02.EP5"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C02 { identifier = "VS-C02"; sourceText = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; sourceLocator = "OOSEM L02 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "review-0573"; status = "proposed/unexecuted"; }
    part def <'VS-C03'> C03 :> SimulationIntegrationSoftware {
        doc /* F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions. */
        part :>> mapping {
            attribute :>> authoringDesignToPythonPlantUSDOrFMIMappings = "Capella/Valispace definitions -> declared characterized EPS plant -> proposed USD whole-CUBICS numerical mappings.";
            attribute :>> fPrimeInterfaceTranslationPathAndVersions = "Capella/Valispace interface definitions -> new translations of all interface/ground meanings -> required versioned F Prime profile.";
            attribute :>> numericalEntityUnitSampleReceiptScenarioTimeChecks = "Check same scenario, entity/channel identity, quantities/units, sample/receipt times, synchronization rules/limits/delays, raw missing/invalid/inactive values and masks.";
            attribute :>> disciplineSolverEffectsAndUnsupportedTransfers = "Required electrical/thermal and applicable EMC/geometry/RAM profiles with supported effects, validity, omissions and independent evidence. Authored failure data to fault trees is a proposed adaptation with unresolved missing rates.";
        }
        part :>> replayDependencies {
            attribute :>> requiredDependencyClasses = "Both tool exports, Valispace parameter revisions, synchronization scripts, characterized EPS plant, solver/host dependencies and raw outputs.";
        }
        perform action :>> planAnalysis : PhysicalPlanAnalysis {
            bind profile = C03::mapping;
        }
        perform action :>> planMIL;
        perform action :>> coordinateCoding;
        perform action :>> compareMILSil;
        perform action :>> replay;
        perform action :>> planRepeat;
        perform action :>> mapFPrime : PhysicalMapFPrime {
            bind profile = C03::mapping;
        }
    }
    @ComponentSpecification about C03 { tools = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; logical = "L03"; sourceMethods = ("L03.IN1", "L03.IN5"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C03 { identifier = "VS-C03"; sourceText = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; sourceLocator = "OOSEM L03 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "review-0853, review-0573"; status = "proposed/unexecuted"; }
    part def <'VS-C04'> C04 :> ModelCredibilitySoftware {
        doc /* Casado waveform assessment plus Zhu calibration/physical-consistency checks. Calibration fit remains separate from independent validity and EPS conformity. */
        part assessmentMethods : CredibilityMethodProfile {
            attribute :>> waveformHistorySeparateModelAndCSRMMethods = "Casado reference waveforms plus Zhu calibration and physical-consistency checks.";
            attribute :>> applicabilityTimingRawMasksAndIndependentDataRules = "Keep calibration and independent reference use distinct. Check current intended use, units/timing/raw masks and uncertainty. Critical evidence gaps block unqualified claims.";
        }
        perform action :>> assessModel : PhysicalAssessModel {
            bind profile = C04::assessmentMethods;
        }
        perform action :>> proposeCalibration;
        perform action :>> checkReferenceData;
    }
    @ComponentSpecification about C04 { tools = "Casado waveform assessment plus Zhu calibration/physical-consistency checks. Calibration fit remains separate from independent validity and EPS conformity."; logical = "L04"; sourceMethods = ("L04.CR1", "L04.CR2"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C04 { identifier = "VS-C04"; sourceText = "Casado waveform assessment plus Zhu calibration/physical-consistency checks. Calibration fit remains separate from independent validity and EPS conformity."; sourceLocator = "OOSEM L04 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "review-0573, handpicked-0001"; status = "proposed/unexecuted"; }
    part def <'VS-C05'> C05 :> EvidenceReviewSoftware {
        doc /* Capella review/AIV traces plus requirement/procedure/verdict feedback. Exact current gate packages and designated authority control are proposed. */
        part evidenceMethods : EvidenceMethodProfile {
            attribute :>> requirementProcedureVerdictAndPublishedReviewTraces = "Capella review/AIV trace plus requirement/procedure/verdict feedback.";
            attribute :>> exactBaselineAuthorityAndCoverageAssembly = "Exact current baseline and scoped criteria, source-linked evidence and gaps. Preparation is not acceptance. Designated authority retains decisions and renewed closure control.";
        }
        perform action :>> planAssessment;
        perform action :>> assessProduct;
        perform action :>> prepareReview : PhysicalPrepareReviewPackage {
            bind profile = C05::evidenceMethods;
        }
        perform action :>> checkReviewDecision;
        perform action :>> recordReview;
        perform action :>> makeViews;
        perform action :>> presentAssessment;
    }
    @ComponentSpecification about C05 { tools = "Capella review/AIV traces plus requirement/procedure/verdict feedback. Exact current gate packages and designated authority control are proposed."; logical = "L05"; sourceMethods = ("L05.EC5", "L05.EC2"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C05 { identifier = "VS-C05"; sourceText = "Capella review/AIV traces plus requirement/procedure/verdict feedback. Exact current gate packages and designated authority control are proposed."; sourceLocator = "OOSEM L05 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "citation-1573, citation-0569"; status = "proposed/unexecuted"; }
    part def <'VS-C06'> C06 :> ConfigurationExchangeSoftware {
        doc /* Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use. */
        part currency : CurrencyProfile {
            attribute :>> affectedRevisionKeysAndInvalidationPolicy = "Asynchronous Capella and Valispace transfers invalidate advice and recheck both tool/context revisions.";
        }
        ref part replayProfile : ReplayProfile;
        ref part numericalMapping : IntegrationMethodProfile;
        ref port numericalEndpoint : AnalysisPort;
        perform action :>> captureContext;
        perform action :>> checkCurrency : PhysicalCheckCurrency {
            bind profile = C06::currency;
        }
        perform action :>> invalidate : PhysicalInvalidateAndReassess {
            bind profile = C06::currency;
        }
        perform action :>> checkChange;
        perform action :>> successor;
        perform action :>> preserveRun : PhysicalPreserveRun {
            bind mapping = C06::numericalMapping;
            bind currency = C06::currency;
            bind numericalEndpoint = C06::numericalEndpoint;
        }
        perform action :>> checkDesignAuthorization;
        perform action :>> retrieveBaseline;
        perform action :>> retainReview;
        perform action :>> prepareReplay : PhysicalPrepareReplay {
            bind profile = C06::replayProfile;
        }
        perform action :>> preserveRecord;
        perform action :>> checkSelection;
        perform action :>> checkResultContext;
        perform action :>> prepareCalibrationChange;
        perform action :>> checkTransfer;
        perform action :>> checkEngineeringTransfer;
        perform action :>> checkSourceTransfer;
    }
    @ComponentSpecification about C06 { tools = "Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use."; logical = "L06"; sourceMethods = ("L06.EC5", "L06.EC1"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C06 { identifier = "VS-C06"; sourceText = "Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use."; sourceLocator = "OOSEM L06 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "citation-1573, chiu2023sealion"; status = "proposed/unexecuted"; }
    part def Configuration :> LogicalFramework {
        part :>> L01 : C01 {
            perform action acknowledge : FrameworkLogical::AcknowledgeAssistance :>> C01::acknowledge, FrameworkLogical::RequirementsAssistance::acknowledge;
            perform action checkDraft : PhysicalCheckDraft :>> C01::checkDraft, FrameworkLogical::RequirementsAssistance::checkDraft;
            perform action recommend : PhysicalRecommendMethods :>> C01::recommend, FrameworkLogical::RequirementsAssistance::recommend;
            perform action dispose : FrameworkLogical::DisposeSuggestion :>> C01::dispose, FrameworkLogical::RequirementsAssistance::dispose;
            perform action reassess : PhysicalReassessAssistance :>> C01::reassess, FrameworkLogical::RequirementsAssistance::reassess;
            perform action retainRequirements : FrameworkLogical::RetainRequirements :>> C01::retainRequirements, FrameworkLogical::RequirementsAssistance::retainRequirements;
            perform action deriveAllocate : FrameworkLogical::DeriveAllocate :>> C01::deriveAllocate, FrameworkLogical::RequirementsAssistance::deriveAllocate;
            perform action traceLinks : FrameworkLogical::TraceLinks :>> C01::traceLinks, FrameworkLogical::RequirementsAssistance::traceLinks;
            perform action presentAdvice : FrameworkLogical::PresentAdvice :>> C01::presentAdvice, FrameworkLogical::RequirementsAssistance::presentAdvice;
            perform action sourceQuery : FrameworkLogical::RequestApplicableSource :>> C01::sourceQuery, FrameworkLogical::RequirementsAssistance::sourceQuery;
        }
        part :>> L02 : C02 {
            perform action defineDesign : FrameworkLogical::DefineDesign :>> C02::defineDesign, FrameworkLogical::MissionDesign::defineDesign;
            perform action budgetSize : PhysicalBudgetSize :>> C02::budgetSize, FrameworkLogical::MissionDesign::budgetSize;
            perform action compareDesigns : FrameworkLogical::CompareDesigns :>> C02::compareDesigns, FrameworkLogical::MissionDesign::compareDesigns;
            perform action defineInterfaces : FrameworkLogical::DefineInterfaces :>> C02::defineInterfaces, FrameworkLogical::MissionDesign::defineInterfaces;
            perform action configureConcept : FrameworkLogical::ConfigureConcept :>> C02::configureConcept, FrameworkLogical::MissionDesign::configureConcept;
        }
        part :>> L03 : C03 {
            perform action planAnalysis : PhysicalPlanAnalysis :>> C03::planAnalysis, FrameworkLogical::SimulationIntegration::planAnalysis;
            perform action planMIL : FrameworkLogical::PlanMIL :>> C03::planMIL, FrameworkLogical::SimulationIntegration::planMIL;
            perform action coordinateCoding : FrameworkLogical::CoordinateCoding :>> C03::coordinateCoding, FrameworkLogical::SimulationIntegration::coordinateCoding;
            perform action compareMILSil : FrameworkLogical::CompareMILSil :>> C03::compareMILSil, FrameworkLogical::SimulationIntegration::compareMILSil;
            perform action replay : FrameworkLogical::ReplayRun :>> C03::replay, FrameworkLogical::SimulationIntegration::replay;
            perform action planRepeat : FrameworkLogical::PlanRepeatedAssessment :>> C03::planRepeat, FrameworkLogical::SimulationIntegration::planRepeat;
            perform action mapFPrime : PhysicalMapFPrime :>> C03::mapFPrime, FrameworkLogical::SimulationIntegration::mapFPrime;
        }
        part :>> L04 : C04 {
            perform action assessModel : PhysicalAssessModel :>> C04::assessModel, FrameworkLogical::ModelCredibility::assessModel;
            perform action proposeCalibration : FrameworkLogical::ProposeCalibration :>> C04::proposeCalibration, FrameworkLogical::ModelCredibility::proposeCalibration;
            perform action checkReferenceData : FrameworkLogical::CheckReferenceData :>> C04::checkReferenceData, FrameworkLogical::ModelCredibility::checkReferenceData;
        }
        part :>> L05 : C05 {
            perform action planAssessment : FrameworkLogical::PlanAssessment :>> C05::planAssessment, FrameworkLogical::EvidenceReview::planAssessment;
            perform action assessProduct : FrameworkLogical::AssessProduct :>> C05::assessProduct, FrameworkLogical::EvidenceReview::assessProduct;
            perform action prepareReview : PhysicalPrepareReviewPackage :>> C05::prepareReview, FrameworkLogical::EvidenceReview::prepareReview;
            perform action checkReviewDecision : FrameworkLogical::CheckReviewDecision :>> C05::checkReviewDecision, FrameworkLogical::EvidenceReview::checkReviewDecision;
            perform action recordReview : FrameworkLogical::RecordReviewDecision :>> C05::recordReview, FrameworkLogical::EvidenceReview::recordReview;
            perform action makeViews : FrameworkLogical::MakeViews :>> C05::makeViews, FrameworkLogical::EvidenceReview::makeViews;
            perform action presentAssessment : FrameworkLogical::PresentAssessment :>> C05::presentAssessment, FrameworkLogical::EvidenceReview::presentAssessment;
        }
        part :>> L06 : C06 {
            perform action captureContext : FrameworkLogical::CaptureContext :>> C06::captureContext, FrameworkLogical::ConfigurationExchange::captureContext;
            perform action checkCurrency : PhysicalCheckCurrency :>> C06::checkCurrency, FrameworkLogical::ConfigurationExchange::checkCurrency;
            perform action invalidate : PhysicalInvalidateAndReassess :>> C06::invalidate, FrameworkLogical::ConfigurationExchange::invalidate;
            perform action checkChange : FrameworkLogical::CheckEngineeringChange :>> C06::checkChange, FrameworkLogical::ConfigurationExchange::checkChange;
            perform action successor : FrameworkLogical::RetainSuccessor :>> C06::successor, FrameworkLogical::ConfigurationExchange::successor;
            perform action preserveRun : PhysicalPreserveRun :>> C06::preserveRun, FrameworkLogical::ConfigurationExchange::preserveRun;
            perform action checkDesignAuthorization : FrameworkLogical::CheckDetailedDesignAuthorization :>> C06::checkDesignAuthorization, FrameworkLogical::ConfigurationExchange::checkDesignAuthorization;
            perform action retrieveBaseline : FrameworkLogical::RetrieveBaseline :>> C06::retrieveBaseline, FrameworkLogical::ConfigurationExchange::retrieveBaseline;
            perform action retainReview : FrameworkLogical::RetainReviewedBaseline :>> C06::retainReview, FrameworkLogical::ConfigurationExchange::retainReview;
            perform action prepareReplay : PhysicalPrepareReplay :>> C06::prepareReplay, FrameworkLogical::ConfigurationExchange::prepareReplay;
            perform action preserveRecord : FrameworkLogical::PreserveRecord :>> C06::preserveRecord, FrameworkLogical::ConfigurationExchange::preserveRecord;
            perform action checkSelection : FrameworkLogical::CheckEngineerSelection :>> C06::checkSelection, FrameworkLogical::ConfigurationExchange::checkSelection;
            perform action checkResultContext : FrameworkLogical::CheckResultContext :>> C06::checkResultContext, FrameworkLogical::ConfigurationExchange::checkResultContext;
            perform action prepareCalibrationChange : FrameworkLogical::PrepareCalibrationChange :>> C06::prepareCalibrationChange, FrameworkLogical::ConfigurationExchange::prepareCalibrationChange;
            perform action checkTransfer : FrameworkLogical::CheckTransfer :>> C06::checkTransfer, FrameworkLogical::ConfigurationExchange::checkTransfer;
            perform action checkEngineeringTransfer : FrameworkLogical::CheckTransfer :>> C06::checkEngineeringTransfer, FrameworkLogical::ConfigurationExchange::checkEngineeringTransfer;
            perform action checkSourceTransfer : FrameworkLogical::CheckTransfer :>> C06::checkSourceTransfer, FrameworkLogical::ConfigurationExchange::checkSourceTransfer;
        }
        part N1 : EngineeringHost;
        part N2 : AssistanceHost;
        part N3 : ArchiveHost;
        part engineeringNode : ResponsibilityNode;
        part assistanceNode : ResponsibilityNode;
        part evidenceNode : ResponsibilityNode;
        part models : ModelEnvironment;
        part hostCode : HostToolchain;
        ref item modelRecords : ModelData [0..*];
        ref item sourceAndAdviceRecords : AdviceData [0..*];
        ref item rawResultsAndReleases : ReleaseData [0..*];
        perform action engineeringProcedure : EngineeringProcedure;
        perform action reviewProcedure : ReviewProcedure;
        bind N1.requirements = L01;
        bind N1.design = L02;
        bind N1.analyses = L03;
        bind N1.credibility = L04;
        bind N1.review = L05;
        bind N2.advice = L01;
        bind N3.configuration = L06;
        bind N1.models = L03.p03;
        bind N1.hostCode = L03.p04;
        bind L03.mapping.sourceRecords = L01.authoring.currentRecords;
        bind L06.replayProfile = L03.replayDependencies;
        bind L06.numericalMapping = L03.mapping;
        bind L06.numericalEndpoint = L03.p03;
        bind L06.currency.latest.context = L01.authoring.currentRecords.context;
        bind L02.designMethods.sourceRecords = L01.authoring.currentRecords;
        interface adviceLink connect N1.assistance to N2.assistance;
        interface releasedData connect N1.revisions to N3.engineering;
        interface sourceAdvice connect N2.revisions to N3.assistance;
        interface modelLink connect N1.models to models.requests;
        interface codeLink connect N1.hostCode to hostCode.requests;
        perform action assistance : PhysicalAssistanceRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action capture :>> capture references L06.captureContext;
            perform action invalidateOnEdit :>> invalidateOnEdit references L06.invalidate;
            perform action acknowledge :>> acknowledge references L01.acknowledge;
            perform action retainDraft :>> retainDraft references L01.retainRequirements;
            perform action checkDraft :>> checkDraft references L01.checkDraft;
            perform action recommend :>> recommend references L01.recommend;
            perform action checkReply :>> checkReply references L06.checkCurrency;
            perform action present :>> present references L01.presentAdvice;
            perform action dispose :>> dispose references L01.dispose;
            perform action checkApplication :>> checkApplication references L06.checkCurrency;
            perform action derive :>> derive references L01.deriveAllocate;
            perform action trace :>> trace references L01.traceLinks;
            perform action retainValidation :>> retainValidation references L06.preserveRecord;
            perform action retainDisposition :>> retainDisposition references L06.preserveRecord;
            perform action invalidate :>> invalidate references L06.invalidate;
            perform action reassess :>> reassess references L01.reassess;
            perform action rejectTransfer :>> rejectTransfer references L06.preserveRecord;
            perform action rejectDisposition :>> rejectDisposition references L06.preserveRecord;
        }
        perform action concept : PhysicalConceptRealization {
            perform action makeConfiguration :>> makeConfiguration references L02.configureConcept;
            perform action receive :>> receive references L06.checkTransfer;
            perform action configure :>> configure references L02.defineDesign;
            perform action budget :>> budget references L02.budgetSize;
            perform action planCriteria :>> planCriteria references L05.planAssessment;
            perform action plan :>> plan references L03.planAnalysis;
            perform action :>> execute {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveResult :>> receiveResult references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action checkCurrent :>> checkCurrent references L06.checkResultContext;
            perform action credibility :>> credibility references L04.assessModel;
            perform action assess :>> assess references L05.assessProduct;
            perform action compare :>> compare references L02.compareDesigns;
            perform action checkSelection :>> checkSelection references L06.checkSelection;
            perform action retainSelection :>> retainSelection references L06.preserveRecord;
            perform action retainGaps :>> retainGaps references L06.preserveRecord;
            perform action retainRaw_receiveResult :>> retainRaw_receiveResult references L06.preserveRecord;
        }
        perform action designRun : PhysicalDesignRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action configure :>> configure references L02.defineDesign;
            perform action budget :>> budget references L02.budgetSize;
            perform action planCriteria :>> planCriteria references L05.planAssessment;
            perform action plan :>> plan references L03.planAnalysis;
            perform action :>> execute {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveResult :>> receiveResult references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action checkCurrent :>> checkCurrent references L06.checkResultContext;
            perform action credibility :>> credibility references L04.assessModel;
            perform action assess :>> assess references L05.assessProduct;
            perform action compare :>> compare references L02.compareDesigns;
            perform action checkSelection :>> checkSelection references L06.checkSelection;
            perform action retainSelection :>> retainSelection references L06.preserveRecord;
            perform action retainGaps :>> retainGaps references L06.preserveRecord;
            perform action retainRaw_receiveResult :>> retainRaw_receiveResult references L06.preserveRecord;
        }
        perform action software : PhysicalSoftwareRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action interfaces :>> interfaces references L02.defineInterfaces;
            perform action mapping :>> mapping references L03.mapFPrime;
            perform action planCriteria :>> planCriteria references L05.planAssessment;
            perform action planMIL :>> planMIL references L03.planMIL;
            perform action :>> executeMIL {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveMIL :>> receiveMIL references L06.checkTransfer;
            perform action preserveMIL :>> preserveMIL references L06.preserveRun;
            perform action assessMIL :>> assessMIL references L04.assessModel;
            perform action checkRelease :>> checkRelease references L06.checkDesignAuthorization;
            perform action coordinate :>> coordinate references L03.coordinateCoding;
            perform action :>> codeBuildSil {
                perform action :>> profiles references L03.verifyHostProfiles;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveSIL :>> receiveSIL references L06.checkTransfer;
            perform action preserveSIL :>> preserveSIL references L06.preserveRun;
            perform action checkCurrent :>> checkCurrent references L06.checkResultContext;
            perform action compare :>> compare references L03.compareMILSil;
            perform action credibility :>> credibility references L04.assessModel;
            perform action assess :>> assess references L05.assessProduct;
            perform action present :>> present references L05.presentAssessment;
            perform action checkProducts :>> checkProducts references L06.checkSelection;
            perform action retainProducts :>> retainProducts references L06.preserveRecord;
            perform action block :>> block references L06.preserveRecord;
            perform action retainRaw_receiveMIL :>> retainRaw_receiveMIL references L06.preserveRecord;
            perform action retainRaw_receiveSIL :>> retainRaw_receiveSIL references L06.preserveRecord;
            perform action rejectRelease :>> rejectRelease references L06.preserveRecord;
        }
        perform action changeReview : PhysicalChangeReviewRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action invalidate :>> invalidate references L06.invalidate;
            perform action checkChange :>> checkChange references L06.checkChange;
            perform action successor :>> successor references L06.successor;
            perform action reassessAdvice :>> reassessAdvice references L01.reassess;
            perform action planRepeat :>> planRepeat references L03.planRepeat;
            perform action :>> repeat {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveResult :>> receiveResult references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action credibility :>> credibility references L04.assessModel;
            perform action retrieve :>> retrieve references L06.retrieveBaseline;
            perform action assess :>> assess references L05.assessProduct;
            perform action views :>> views references L05.makeViews;
            perform action prepare :>> prepare references L05.prepareReview;
            perform action checkBaseline :>> checkBaseline references L06.checkResultContext;
            perform action checkDecision :>> checkDecision references L05.checkReviewDecision;
            perform action record :>> record references L05.recordReview;
            perform action retain :>> retain references L06.retainReview;
            perform action holdChange :>> holdChange references L06.preserveRecord;
            perform action holdReview :>> holdReview references L06.preserveRecord;
            perform action rejectReview :>> rejectReview references L06.preserveRecord;
            perform action retainRaw_receiveResult :>> retainRaw_receiveResult references L06.preserveRecord;
        }
        perform action replayRun : PhysicalReplayRealization {
            perform action prepare :>> prepare references L06.prepareReplay;
            perform action :>> execute {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receive :>> receive references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action compare :>> compare references L03.replay;
            perform action retain :>> retain references L06.preserveRecord;
            perform action missing :>> missing references L06.preserveRecord;
            perform action retainRaw_receive :>> retainRaw_receive references L06.preserveRecord;
        }
        perform action calibration : PhysicalCalibrationRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action checkData :>> checkData references L04.checkReferenceData;
            perform action propose :>> propose references L04.proposeCalibration;
            perform action prepareChange :>> prepareChange references L06.prepareCalibrationChange;
            perform action invalidate :>> invalidate references L06.invalidate;
            perform action checkChange :>> checkChange references L06.checkChange;
            perform action successor :>> successor references L06.successor;
            perform action reassess :>> reassess references L01.reassess;
            perform action planRepeat :>> planRepeat references L03.planRepeat;
            perform action :>> repeat {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveResult :>> receiveResult references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action credibility :>> credibility references L04.assessModel;
            perform action assess :>> assess references L05.assessProduct;
            perform action retainEvidence :>> retainEvidence references L06.preserveRecord;
            perform action retain :>> retain references L06.preserveRecord;
            perform action unusable :>> unusable references L06.preserveRecord;
            perform action retainRaw_receiveResult :>> retainRaw_receiveResult references L06.preserveRecord;
        }
    }
    @SourceRecord about Configuration { identifier = "PA-VS"; sourceText = "Capella/Valispace composite with exact six-component proposed composition and mandatory F Prime/numerical whole-CUBICS Omniverse connections."; sourceLocator = "OOSEM physical synthesis and neutral MOP comparison"; citationRecord = "citation-4690, review-0573, review-0853, handpicked-0001, citation-1573, citation-0569, chiu2023sealion"; status = "proposed/unexecuted"; }
    part candidate : Configuration;
    #logicalRealization allocation logical_L01 allocate logical.L01 to candidate.L01;
    #logicalRealization allocation logical_L02 allocate logical.L02 to candidate.L02;
    #logicalRealization allocation logical_L03 allocate logical.L03 to candidate.L03;
    #logicalRealization allocation logical_L04 allocate logical.L04 to candidate.L04;
    #logicalRealization allocation logical_L05 allocate logical.L05 to candidate.L05;
    #logicalRealization allocation logical_L06 allocate logical.L06 to candidate.L06;
    #physicalDetail allocation guidanceState allocate logical.L06.assistanceCurrency to candidate.L06.assistanceCurrency;
    #physicalDetail allocation reviewState allocate logical.L05.reviewState to candidate.L05.reviewState;
    #physicalPrimary allocation primary_FR_01 allocate FrameworkRequirements::FR_01 to candidate.L01 { @PhysicalAllocation { rationale = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; plannedCheck = "I,T: Round-trip quantitative and qualitative records, including unresolved criteria."; operation = CandidateVS::C01::retainRequirements meta SysML::ActionUsage; } }
    dependency operation_FR_01 from FrameworkLogical::RequirementsAssistance::retainRequirements to CandidateVS::C01::retainRequirements;
    dependency contract_FR_01 from FrameworkLogical::ContractFR01 to CandidateVS::C01::contractFR01;
    #physicalPrimary allocation primary_FR_02 allocate FrameworkRequirements::FR_02 to candidate.L01 { @PhysicalAllocation { rationale = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; plannedCheck = "A,T: Compare clean and seeded drafts with an independent expert reference, including valid similar requirements and missed defects."; operation = CandidateVS::C01::checkDraft meta SysML::ActionUsage; } }
    dependency operation_FR_02 from FrameworkLogical::RequirementsAssistance::checkDraft to CandidateVS::C01::checkDraft;
    dependency contract_FR_02 from FrameworkLogical::ContractFR02 to CandidateVS::C01::contractFR02;
    #physicalPrimary allocation primary_FR_03 allocate FrameworkRequirements::FR_03 to candidate.L01 { @PhysicalAllocation { rationale = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; plannedCheck = "A,T: Use contextual queries whose eligible methods change with inputs, maturity or intended use."; operation = CandidateVS::C01::recommend meta SysML::ActionUsage; } }
    dependency operation_FR_03 from FrameworkLogical::RequirementsAssistance::recommend to CandidateVS::C01::recommend;
    dependency contract_FR_03 from FrameworkLogical::ContractFR03 to CandidateVS::C01::contractFR03;
    #physicalPrimary allocation primary_FR_04 allocate FrameworkRequirements::FR_04 to candidate.L01 { @PhysicalAllocation { rationale = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; plannedCheck = "T: Compare both query directions and coverage with a known relationship set."; operation = CandidateVS::C01::traceLinks meta SysML::ActionUsage; } }
    dependency operation_FR_04 from FrameworkLogical::RequirementsAssistance::traceLinks to CandidateVS::C01::traceLinks;
    dependency contract_FR_04 from FrameworkLogical::ContractFR04 to CandidateVS::C01::contractFR04;
    #physicalPrimary allocation primary_FR_05 allocate FrameworkRequirements::FR_05 to candidate.L06 { @PhysicalAllocation { rationale = "Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use."; plannedCheck = "A,T: Compare the impact set of coupled load, pointing and interface changes with an expert reference."; operation = CandidateVS::C06::invalidate meta SysML::ActionUsage; } }
    dependency operation_FR_05 from FrameworkLogical::ConfigurationExchange::invalidate to CandidateVS::C06::invalidate;
    dependency contract_FR_05 from FrameworkLogical::ContractFR05 to CandidateVS::C06::contractFR05;
    #physicalPrimary allocation primary_FR_06 allocate FrameworkRequirements::FR_06 to candidate.L06 { @PhysicalAllocation { rationale = "Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use."; plannedCheck = "T: Accept, decline and interrupt changes without erasing the predecessor."; operation = CandidateVS::C06::successor meta SysML::ActionUsage; } }
    dependency operation_FR_06 from FrameworkLogical::ConfigurationExchange::successor to CandidateVS::C06::successor;
    dependency contract_FR_06 from FrameworkLogical::ContractFR06 to CandidateVS::C06::contractFR06;
    #physicalPrimary allocation primary_FR_07 allocate FrameworkRequirements::FR_07 to candidate.L06 { @PhysicalAllocation { rationale = "Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use."; plannedCheck = "I,T: Reconstruct predecessor and successor manifests and all applicable products."; operation = CandidateVS::C06::retrieveBaseline meta SysML::ActionUsage; } }
    dependency operation_FR_07 from FrameworkLogical::ConfigurationExchange::retrieveBaseline to CandidateVS::C06::retrieveBaseline;
    dependency contract_FR_07 from FrameworkLogical::ContractFR07 to CandidateVS::C06::contractFR07;
    #physicalPrimary allocation primary_FR_08 allocate FrameworkRequirements::FR_08 to candidate.L06 { @PhysicalAllocation { rationale = "Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use."; plannedCheck = "T: Inject identity, unit, sign and revision mismatches at each active interface."; operation = CandidateVS::C06::checkTransfer meta SysML::ActionUsage; } }
    dependency operation_FR_08 from FrameworkLogical::ConfigurationExchange::checkTransfer to CandidateVS::C06::checkTransfer;
    dependency contract_FR_08 from FrameworkLogical::ContractFR08 to CandidateVS::C06::contractFR08;
    #physicalPrimary allocation primary_FR_09 allocate FrameworkRequirements::FR_09 to candidate.L06 { @PhysicalAllocation { rationale = "Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use."; plannedCheck = "I,T: Trace successful, failed, cancelled and partial outputs to their configurations."; operation = CandidateVS::C06::preserveRun meta SysML::ActionUsage; } }
    dependency operation_FR_09 from FrameworkLogical::ConfigurationExchange::preserveRun to CandidateVS::C06::preserveRun;
    dependency contract_FR_09 from FrameworkLogical::ContractFR09 to CandidateVS::C06::contractFR09;
    #physicalPrimary allocation primary_FR_10 allocate FrameworkRequirements::FR_10 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "D,T: Independently replay in the declared host environment and compare under fixed tolerances."; operation = CandidateVS::C03::replay meta SysML::ActionUsage; } }
    dependency operation_FR_10 from FrameworkLogical::SimulationIntegration::replay to CandidateVS::C03::replay;
    dependency contract_FR_10 from FrameworkLogical::ContractFR10 to CandidateVS::C03::contractFR10;
    #physicalPrimary allocation primary_FR_11 allocate FrameworkRequirements::FR_11 to candidate.L05 { @PhysicalAllocation { rationale = "Capella review/AIV traces plus requirement/procedure/verdict feedback. Exact current gate packages and designated authority control are proposed."; plannedCheck = "T: Seed every evidence status and attempt a current claim with a blocking gap."; operation = CandidateVS::C05::assessProduct meta SysML::ActionUsage; } }
    dependency operation_FR_11 from FrameworkLogical::EvidenceReview::assessProduct to CandidateVS::C05::assessProduct;
    dependency contract_FR_11 from FrameworkLogical::ContractFR11 to CandidateVS::C05::contractFR11;
    #physicalPrimary allocation primary_FR_13 allocate FrameworkRequirements::FR_13 to candidate.L02 { @PhysicalAllocation { rationale = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; plannedCheck = "A,T: Recalculate mass and volume after a component substitution and preserve unknown properties and aggregation assumptions."; operation = CandidateVS::C02::budgetSize meta SysML::ActionUsage; } }
    dependency operation_FR_13 from FrameworkLogical::MissionDesign::budgetSize to CandidateVS::C02::budgetSize;
    dependency contract_FR_13 from FrameworkLogical::ContractFR13 to CandidateVS::C02::contractFR13;
    #physicalPrimary allocation primary_FR_14 allocate FrameworkRequirements::FR_14 to candidate.L02 { @PhysicalAllocation { rationale = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; plannedCheck = "A,T: Use infeasible and closely ranked alternatives with uncertain inputs."; operation = CandidateVS::C02::compareDesigns meta SysML::ActionUsage; } }
    dependency operation_FR_14 from FrameworkLogical::MissionDesign::compareDesigns to CandidateVS::C02::compareDesigns;
    dependency contract_FR_14 from FrameworkLogical::ContractFR14 to CandidateVS::C02::contractFR14;
    #physicalPrimary allocation primary_FR_15 allocate FrameworkRequirements::FR_15 to candidate.L02 { @PhysicalAllocation { rationale = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; plannedCheck = "I,D: Configure alternate EPS topologies and retain the distinct allocation and extension revisions."; operation = CandidateVS::C02::defineDesign meta SysML::ActionUsage; } }
    dependency operation_FR_15 from FrameworkLogical::MissionDesign::defineDesign to CandidateVS::C02::defineDesign;
    dependency contract_FR_15 from FrameworkLogical::ContractFR15 to CandidateVS::C02::contractFR15;
    #physicalPrimary allocation primary_FR_16 allocate FrameworkRequirements::FR_16 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "A,T: Use whole-CUBICS histories with a temporal shortage hidden by an average budget. Perturb load, mode or illumination and compare the mapped EPS numerical response with an independent reference within model scope."; operation = CandidateVS::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_16 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateVS::C03::planAnalysis;
    dependency contract_FR_16 from FrameworkLogical::ContractFR16 to CandidateVS::C03::contractFR16;
    #physicalPrimary allocation primary_FR_17 allocate FrameworkRequirements::FR_17 to candidate.L01 { @PhysicalAllocation { rationale = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; plannedCheck = "A,T: Recalculate an allocation and follow it to the parent and source quantities."; operation = CandidateVS::C01::deriveAllocate meta SysML::ActionUsage; } }
    dependency operation_FR_17 from FrameworkLogical::RequirementsAssistance::deriveAllocate to CandidateVS::C01::deriveAllocate;
    dependency contract_FR_17 from FrameworkLogical::ContractFR17 to CandidateVS::C01::contractFR17;
    #physicalPrimary allocation primary_FR_18 allocate FrameworkRequirements::FR_18 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "D,T: Exercise each discipline profile and incompatible mappings. Perturb an incoming whole-CUBICS history, compare the EPS numerical effect independently and return its identified response to the same scenario. Scene-only updates or missing numerical exchange cannot pass. Retain failed/partial status and transfer limits."; operation = CandidateVS::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_18 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateVS::C03::planAnalysis;
    dependency contract_FR_18 from FrameworkLogical::ContractFR18 to CandidateVS::C03::contractFR18;
    #physicalPrimary allocation primary_FR_19 allocate FrameworkRequirements::FR_19 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "D,T: Run declared nominal and fault sequences with a simulated plant and retain stimuli, expected/actual state/event responses and failed criteria for matched SIL comparison."; operation = CandidateVS::C03::planMIL meta SysML::ActionUsage; } }
    dependency operation_FR_19 from FrameworkLogical::SimulationIntegration::planMIL to CandidateVS::C03::planMIL;
    dependency contract_FR_19 from FrameworkLogical::ContractFR19 to CandidateVS::C03::contractFR19;
    #physicalPrimary allocation primary_FR_20 allocate FrameworkRequirements::FR_20 to candidate.L02 { @PhysicalAllocation { rationale = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; plannedCheck = "A,T: Compare sizing and energy balance with independent calculations, including an infeasible eclipse case."; operation = CandidateVS::C02::budgetSize meta SysML::ActionUsage; } }
    dependency operation_FR_20 from FrameworkLogical::MissionDesign::budgetSize to CandidateVS::C02::budgetSize;
    dependency contract_FR_20 from FrameworkLogical::ContractFR20 to CandidateVS::C02::contractFR20;
    #physicalPrimary allocation primary_FR_21 allocate FrameworkRequirements::FR_21 to candidate.L04 { @PhysicalAllocation { rationale = "Casado waveform assessment plus Zhu calibration/physical-consistency checks. Calibration fit remains separate from independent validity and EPS conformity."; plannedCheck = "I,T: Attempt conclusions outside validity and with missing independent evidence."; operation = CandidateVS::C04::assessModel meta SysML::ActionUsage; } }
    dependency operation_FR_21 from FrameworkLogical::ModelCredibility::assessModel to CandidateVS::C04::assessModel;
    dependency contract_FR_21 from FrameworkLogical::ContractFR21 to CandidateVS::C04::contractFR21;
    #physicalPrimary allocation primary_FR_22 allocate FrameworkRequirements::FR_22 to candidate.L04 { @PhysicalAllocation { rationale = "Casado waveform assessment plus Zhu calibration/physical-consistency checks. Calibration fit remains separate from independent validity and EPS conformity."; plannedCheck = "A,T: Calibrate from supplied data, retain separate assessment data and decline an update."; operation = CandidateVS::C04::proposeCalibration meta SysML::ActionUsage; } }
    dependency operation_FR_22 from FrameworkLogical::ModelCredibility::proposeCalibration to CandidateVS::C04::proposeCalibration;
    dependency contract_FR_22 from FrameworkLogical::ContractFR22 to CandidateVS::C04::contractFR22;
    #physicalPrimary allocation primary_FR_23 allocate FrameworkRequirements::FR_23 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "I,T: Change the time step, solver and resource limits and inspect the run configuration and findings."; operation = CandidateVS::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_23 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateVS::C03::planAnalysis;
    dependency contract_FR_23 from FrameworkLogical::ContractFR23 to CandidateVS::C03::contractFR23;
    #physicalPrimary allocation primary_FR_24 allocate FrameworkRequirements::FR_24 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "A,T: Execute released F Prime host software with simulated EPS/subsystem products connected to the same whole-CUBICS scenario. Use matched MIL results and fixed comparison rules. Seed a code/interface discrepancy and failed/partial runs. Retain raw host responses, requirement/ConOps outcomes, differences, status and limits. Builds and scene updates supply no SIL evidence."; operation = CandidateVS::C03::compareMILSil meta SysML::ActionUsage; } }
    dependency operation_FR_24 from FrameworkLogical::SimulationIntegration::compareMILSil to CandidateVS::C03::compareMILSil;
    dependency contract_FR_24 from FrameworkLogical::ContractFR24 to CandidateVS::C03::contractFR24;
    #physicalPrimary allocation primary_FR_25 allocate FrameworkRequirements::FR_25 to candidate.L02 { @PhysicalAllocation { rationale = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; plannedCheck = "I,T: Revise a degraded mode and trace its requirement and analysis inputs."; operation = CandidateVS::C02::defineDesign meta SysML::ActionUsage; } }
    dependency operation_FR_25 from FrameworkLogical::MissionDesign::defineDesign to CandidateVS::C02::defineDesign;
    dependency contract_FR_25 from FrameworkLogical::ContractFR25 to CandidateVS::C02::contractFR25;
    #physicalPrimary allocation primary_FR_26 allocate FrameworkRequirements::FR_26 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "I,T: Assess applicability with and without repair or redundancy assumptions."; operation = CandidateVS::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_26 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateVS::C03::planAnalysis;
    dependency contract_FR_26 from FrameworkLogical::ContractFR26 to CandidateVS::C03::contractFR26;
    #physicalPrimary allocation primary_FR_27 allocate FrameworkRequirements::FR_27 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "A,T: Compare transformations and results with a reference and leave missing rates unresolved."; operation = CandidateVS::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_27 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateVS::C03::planAnalysis;
    dependency contract_FR_27 from FrameworkLogical::ContractFR27 to CandidateVS::C03::contractFR27;
    #physicalPrimary allocation primary_FR_28 allocate FrameworkRequirements::FR_28 to candidate.L05 { @PhysicalAllocation { rationale = "Capella review/AIV traces plus requirement/procedure/verdict feedback. Exact current gate packages and designated authority control are proposed."; plannedCheck = "I,T: Distinguish planned activities from results and verification criteria from validation expectations."; operation = CandidateVS::C05::planAssessment meta SysML::ActionUsage; } }
    dependency operation_FR_28 from FrameworkLogical::EvidenceReview::planAssessment to CandidateVS::C05::planAssessment;
    dependency contract_FR_28 from FrameworkLogical::ContractFR28 to CandidateVS::C05::contractFR28;
    #physicalPrimary allocation primary_FR_29 allocate FrameworkRequirements::FR_29 to candidate.L01 { @PhysicalAllocation { rationale = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; plannedCheck = "I,T: Exercise all dispositions and an unauthorized attempt to apply a suggestion."; operation = CandidateVS::C01::dispose meta SysML::ActionUsage; } }
    dependency operation_FR_29 from FrameworkLogical::RequirementsAssistance::dispose to CandidateVS::C01::dispose;
    dependency contract_FR_29 from FrameworkLogical::ContractFR29 to CandidateVS::C01::contractFR29;
    #physicalPrimary allocation primary_FR_30 allocate FrameworkRequirements::FR_30 to candidate.L06 { @PhysicalAllocation { rationale = "Capella design/procedure change trace plus Git history. Asynchronous two-tool transfers retain owners and revisions before current advice or replay use."; plannedCheck = "T: Edit during a delayed response and check that the old response cannot replace current guidance."; operation = CandidateVS::C06::invalidate meta SysML::ActionUsage; } }
    dependency operation_FR_30 from FrameworkLogical::ConfigurationExchange::invalidate to CandidateVS::C06::invalidate;
    dependency contract_FR_30 from FrameworkLogical::ContractFR30 to CandidateVS::C06::contractFR30;
    #physicalPrimary allocation primary_FR_31 allocate FrameworkRequirements::FR_31 to candidate.L04 { @PhysicalAllocation { rationale = "Casado waveform assessment plus Zhu calibration/physical-consistency checks. Calibration fit remains separate from independent validity and EPS conformity."; plannedCheck = "A,T: Seed clock offset, delayed/out-of-order samples and missing timing. Compare checked alignments, delays and exceeded/unknown limits with fixed timing references. Distinguish scenario/sample/receipt times, scene update rate and numerical time step."; operation = CandidateVS::C04::assessModel meta SysML::ActionUsage; } }
    dependency operation_FR_31 from FrameworkLogical::ModelCredibility::assessModel to CandidateVS::C04::assessModel;
    dependency contract_FR_31 from FrameworkLogical::ContractFR31 to CandidateVS::C04::contractFR31;
    #physicalPrimary allocation primary_FR_32 allocate FrameworkRequirements::FR_32 to candidate.L04 { @PhysicalAllocation { rationale = "Casado waveform assessment plus Zhu calibration/physical-consistency checks. Calibration fit remains separate from independent validity and EPS conformity."; plannedCheck = "T: Seed wrong entity/channel/revision, unit/sign/frame mismatch and missing, inactive or invalid samples. Compare admission findings and masks with a fixed reference before numerical use. Preserve raw histories and unchanged controlled content for rejected transfers."; operation = CandidateVS::C04::assessModel meta SysML::ActionUsage; } }
    dependency operation_FR_32 from FrameworkLogical::ModelCredibility::assessModel to CandidateVS::C04::assessModel;
    dependency contract_FR_32 from FrameworkLogical::ContractFR32 to CandidateVS::C04::contractFR32;
    #physicalPrimary allocation primary_FR_33 allocate FrameworkRequirements::FR_33 to candidate.L02 { @PhysicalAllocation { rationale = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; plannedCheck = "I,T: Round-trip endpoint ownership/directions and all interface and ground-definition fields. Reject inconsistent identifiers, types, units, ranges, polarity and temporal meanings against an independent reference. Structural checks supply no behavior verdict."; operation = CandidateVS::C02::defineInterfaces meta SysML::ActionUsage; } }
    dependency operation_FR_33 from FrameworkLogical::MissionDesign::defineInterfaces to CandidateVS::C02::defineInterfaces;
    dependency contract_FR_33 from FrameworkLogical::ContractFR33 to CandidateVS::C02::contractFR33;
    #physicalPrimary allocation primary_FR_34 allocate FrameworkRequirements::FR_34 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "D,T: Compare required F Prime component/instance/port/topology and command/telemetry/event/parameter mappings with an independent reference at declared actual profile/tool/representation versions. Seed conflicts, wrong directions/types, missing meanings and incompatible versions. Retain unsupported behavior and lossy translations."; operation = CandidateVS::C03::mapFPrime meta SysML::ActionUsage; } }
    dependency operation_FR_34 from FrameworkLogical::SimulationIntegration::mapFPrime to CandidateVS::C03::mapFPrime;
    dependency contract_FR_34 from FrameworkLogical::ContractFR34 to CandidateVS::C03::contractFR34;
    #physicalPrimary allocation primary_FR_35 allocate FrameworkRequirements::FR_35 to candidate.L02 { @PhysicalAllocation { rationale = "Casado characterized EPS plant models mapped to declared architecture/mode quantities. Native tool access, broader effects and engineer design studies require verification."; plannedCheck = "A,T: Exercise nominal, rejected, protection and recovery sequences in simulated conditions."; operation = CandidateVS::C02::defineInterfaces meta SysML::ActionUsage; } }
    dependency operation_FR_35 from FrameworkLogical::MissionDesign::defineInterfaces to CandidateVS::C02::defineInterfaces;
    dependency contract_FR_35 from FrameworkLogical::ContractFR35 to CandidateVS::C02::contractFR35;
    #physicalPrimary allocation primary_FR_36 allocate FrameworkRequirements::FR_36 to candidate.L03 { @PhysicalAllocation { rationale = "F Prime architecture pattern plus Casado progressive EPS software/plant substitution. Whole-CUBICS USD mappings and matched released host SIL are proposed additions."; plannedCheck = "D,T: Reject stale, unreleased and unauthorized design requests. Coordinate an authorized current-release F Prime host build, retaining exact source/build, toolchain/dependency/host revisions, logs and generation/compilation failures. Review acceptance cannot replace exact authorization. Build success supplies no SIL verdict."; operation = CandidateVS::C03::coordinateCoding meta SysML::ActionUsage; } }
    dependency operation_FR_36 from FrameworkLogical::SimulationIntegration::coordinateCoding to CandidateVS::C03::coordinateCoding;
    dependency contract_FR_36 from FrameworkLogical::ContractFR36 to CandidateVS::C03::contractFR36;
    #physicalPrimary allocation primary_FR_37 allocate FrameworkRequirements::FR_37 to candidate.L05 { @PhysicalAllocation { rationale = "Capella review/AIV traces plus requirement/procedure/verdict feedback. Exact current gate packages and designated authority control are proposed."; plannedCheck = "I,D: Compare views with their source baseline and follow represented record links."; operation = CandidateVS::C05::makeViews meta SysML::ActionUsage; } }
    dependency operation_FR_37 from FrameworkLogical::EvidenceReview::makeViews to CandidateVS::C05::makeViews;
    dependency contract_FR_37 from FrameworkLogical::ContractFR37 to CandidateVS::C05::contractFR37;
    #physicalPrimary allocation primary_FR_38 allocate FrameworkRequirements::FR_38 to candidate.L05 { @PhysicalAllocation { rationale = "Capella review/AIV traces plus requirement/procedure/verdict feedback. Exact current gate packages and designated authority control are proposed."; plannedCheck = "I,D: Prepare phase-specific packages, including CDR design release and SIR released-product evidence."; operation = CandidateVS::C05::prepareReview meta SysML::ActionUsage; } }
    dependency operation_FR_38 from FrameworkLogical::EvidenceReview::prepareReview to CandidateVS::C05::prepareReview;
    dependency contract_FR_38 from FrameworkLogical::ContractFR38 to CandidateVS::C05::contractFR38;
    #physicalPrimary allocation primary_FR_39 allocate FrameworkRequirements::FR_39 to candidate.L01 { @PhysicalAllocation { rationale = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; plannedCheck = "A,D: Change maturity and blocking findings and inspect the revised activity proposals."; operation = CandidateVS::C01::recommend meta SysML::ActionUsage; } }
    dependency operation_FR_39 from FrameworkLogical::RequirementsAssistance::recommend to CandidateVS::C01::recommend;
    dependency contract_FR_39 from FrameworkLogical::ContractFR39 to CandidateVS::C01::contractFR39;
    #physicalPrimary allocation primary_FR_41 allocate FrameworkRequirements::FR_41 to candidate.L01 { @PhysicalAllocation { rationale = "Imported requirements and Capella architecture/tree/mode context bridged to Valispace. General drafting/semantic checks and method selection are proposed."; plannedCheck = "T: Measure response delay under the declared workload, including outage and superseded edits."; operation = CandidateVS::C01::acknowledge meta SysML::ActionUsage; } }
    dependency operation_FR_41 from FrameworkLogical::RequirementsAssistance::acknowledge to CandidateVS::C01::acknowledge;
    dependency contract_FR_41 from FrameworkLogical::ContractFR41 to CandidateVS::C01::contractFR41;
    #physicalPrimary allocation primary_FR_42 allocate FrameworkRequirements::FR_42 to candidate.L05 { @PhysicalAllocation { rationale = "Capella review/AIV traces plus requirement/procedure/verdict feedback. Exact current gate packages and designated authority control are proposed."; plannedCheck = "I,T: Reject unauthorized or stale-baseline decisions and exercise blocking and conditional findings."; operation = CandidateVS::C05::recordReview meta SysML::ActionUsage; } }
    dependency operation_FR_42 from FrameworkLogical::EvidenceReview::recordReview to CandidateVS::C05::recordReview;
    dependency contract_FR_42 from FrameworkLogical::ContractFR42 to CandidateVS::C05::contractFR42;
    #physicalDetail allocation step_AssistanceRealization_edit allocate LogicalRealization::AssistanceRealization::edit to candidate.assistance.edit;
    #physicalDetail allocation step_AssistanceRealization_receive allocate LogicalRealization::AssistanceRealization::receive to candidate.assistance.receive;
    #physicalDetail allocation step_AssistanceRealization_capture allocate LogicalRealization::AssistanceRealization::capture to candidate.assistance.capture;
    #physicalDetail allocation step_AssistanceRealization_invalidateOnEdit allocate LogicalRealization::AssistanceRealization::invalidateOnEdit to candidate.assistance.invalidateOnEdit;
    #physicalDetail allocation step_AssistanceRealization_acknowledge allocate LogicalRealization::AssistanceRealization::acknowledge to candidate.assistance.acknowledge;
    #physicalDetail allocation step_AssistanceRealization_retainDraft allocate LogicalRealization::AssistanceRealization::retainDraft to candidate.assistance.retainDraft;
    #physicalDetail allocation step_AssistanceRealization_checkDraft allocate LogicalRealization::AssistanceRealization::checkDraft to candidate.assistance.checkDraft;
    #physicalDetail allocation step_AssistanceRealization_recommend allocate LogicalRealization::AssistanceRealization::recommend to candidate.assistance.recommend;
    #physicalDetail allocation step_AssistanceRealization_checkReply allocate LogicalRealization::AssistanceRealization::checkReply to candidate.assistance.checkReply;
    #physicalDetail allocation step_AssistanceRealization_present allocate LogicalRealization::AssistanceRealization::present to candidate.assistance.present;
    #physicalDetail allocation step_AssistanceRealization_engineerDisposition allocate LogicalRealization::AssistanceRealization::engineerDisposition to candidate.assistance.engineerDisposition;
    #physicalDetail allocation step_AssistanceRealization_dispose allocate LogicalRealization::AssistanceRealization::dispose to candidate.assistance.dispose;
    #physicalDetail allocation step_AssistanceRealization_checkApplication allocate LogicalRealization::AssistanceRealization::checkApplication to candidate.assistance.checkApplication;
    #physicalDetail allocation step_AssistanceRealization_derive allocate LogicalRealization::AssistanceRealization::derive to candidate.assistance.derive;
    #physicalDetail allocation step_AssistanceRealization_trace allocate LogicalRealization::AssistanceRealization::trace to candidate.assistance.trace;
    #physicalDetail allocation step_AssistanceRealization_validate allocate LogicalRealization::AssistanceRealization::validate to candidate.assistance.validate;
    #physicalDetail allocation step_AssistanceRealization_retainValidation allocate LogicalRealization::AssistanceRealization::retainValidation to candidate.assistance.retainValidation;
    #physicalDetail allocation step_AssistanceRealization_retainDisposition allocate LogicalRealization::AssistanceRealization::retainDisposition to candidate.assistance.retainDisposition;
    #physicalDetail allocation step_AssistanceRealization_invalidate allocate LogicalRealization::AssistanceRealization::invalidate to candidate.assistance.invalidate;
    #physicalDetail allocation step_AssistanceRealization_reassess allocate LogicalRealization::AssistanceRealization::reassess to candidate.assistance.reassess;
    #physicalDetail allocation step_AssistanceRealization_rejectTransfer allocate LogicalRealization::AssistanceRealization::rejectTransfer to candidate.assistance.rejectTransfer;
    #physicalDetail allocation step_AssistanceRealization_rejectDisposition allocate LogicalRealization::AssistanceRealization::rejectDisposition to candidate.assistance.rejectDisposition;
    #physicalDetail allocation step_DesignRealization_submit allocate LogicalRealization::DesignRealization::submit to candidate.designRun.submit;
    #physicalDetail allocation step_DesignRealization_receive allocate LogicalRealization::DesignRealization::receive to candidate.designRun.receive;
    #physicalDetail allocation step_DesignRealization_configure allocate LogicalRealization::DesignRealization::configure to candidate.designRun.configure;
    #physicalDetail allocation step_DesignRealization_budget allocate LogicalRealization::DesignRealization::budget to candidate.designRun.budget;
    #physicalDetail allocation step_DesignRealization_planCriteria allocate LogicalRealization::DesignRealization::planCriteria to candidate.designRun.planCriteria;
    #physicalDetail allocation step_DesignRealization_plan allocate LogicalRealization::DesignRealization::plan to candidate.designRun.plan;
    #physicalDetail allocation step_DesignRealization_execute allocate LogicalRealization::DesignRealization::execute to candidate.designRun.execute;
    #executionHost allocation external_DesignRealization_execute allocate candidate.designRun.execute to candidate.models;
    #physicalDetail allocation step_DesignRealization_receiveResult allocate LogicalRealization::DesignRealization::receiveResult to candidate.designRun.receiveResult;
    #physicalDetail allocation step_DesignRealization_preserve allocate LogicalRealization::DesignRealization::preserve to candidate.designRun.preserve;
    #physicalDetail allocation step_DesignRealization_checkCurrent allocate LogicalRealization::DesignRealization::checkCurrent to candidate.designRun.checkCurrent;
    #physicalDetail allocation step_DesignRealization_credibility allocate LogicalRealization::DesignRealization::credibility to candidate.designRun.credibility;
    #physicalDetail allocation step_DesignRealization_assess allocate LogicalRealization::DesignRealization::assess to candidate.designRun.assess;
    #physicalDetail allocation step_DesignRealization_compare allocate LogicalRealization::DesignRealization::compare to candidate.designRun.compare;
    #physicalDetail allocation step_DesignRealization_select allocate LogicalRealization::DesignRealization::select to candidate.designRun.select;
    #physicalDetail allocation step_DesignRealization_checkSelection allocate LogicalRealization::DesignRealization::checkSelection to candidate.designRun.checkSelection;
    #physicalDetail allocation step_DesignRealization_retainSelection allocate LogicalRealization::DesignRealization::retainSelection to candidate.designRun.retainSelection;
    #physicalDetail allocation step_DesignRealization_retainGaps allocate LogicalRealization::DesignRealization::retainGaps to candidate.designRun.retainGaps;
    #physicalDetail allocation step_DesignRealization_retainRaw_receiveResult allocate LogicalRealization::DesignRealization::retainRaw_receiveResult to candidate.designRun.retainRaw_receiveResult;
    #physicalDetail allocation step_ConceptRealization_makeConfiguration allocate LogicalRealization::ConceptRealization::makeConfiguration to candidate.concept.makeConfiguration;
    #physicalDetail allocation step_ConceptRealization_submit allocate LogicalRealization::ConceptRealization::submit to candidate.concept.submit;
    #physicalDetail allocation step_ConceptRealization_receive allocate LogicalRealization::ConceptRealization::receive to candidate.concept.receive;
    #physicalDetail allocation step_ConceptRealization_configure allocate LogicalRealization::ConceptRealization::configure to candidate.concept.configure;
    #physicalDetail allocation step_ConceptRealization_budget allocate LogicalRealization::ConceptRealization::budget to candidate.concept.budget;
    #physicalDetail allocation step_ConceptRealization_planCriteria allocate LogicalRealization::ConceptRealization::planCriteria to candidate.concept.planCriteria;
    #physicalDetail allocation step_ConceptRealization_plan allocate LogicalRealization::ConceptRealization::plan to candidate.concept.plan;
    #physicalDetail allocation step_ConceptRealization_execute allocate LogicalRealization::ConceptRealization::execute to candidate.concept.execute;
    #executionHost allocation external_ConceptRealization_execute allocate candidate.concept.execute to candidate.models;
    #physicalDetail allocation step_ConceptRealization_receiveResult allocate LogicalRealization::ConceptRealization::receiveResult to candidate.concept.receiveResult;
    #physicalDetail allocation step_ConceptRealization_preserve allocate LogicalRealization::ConceptRealization::preserve to candidate.concept.preserve;
    #physicalDetail allocation step_ConceptRealization_checkCurrent allocate LogicalRealization::ConceptRealization::checkCurrent to candidate.concept.checkCurrent;
    #physicalDetail allocation step_ConceptRealization_credibility allocate LogicalRealization::ConceptRealization::credibility to candidate.concept.credibility;
    #physicalDetail allocation step_ConceptRealization_assess allocate LogicalRealization::ConceptRealization::assess to candidate.concept.assess;
    #physicalDetail allocation step_ConceptRealization_compare allocate LogicalRealization::ConceptRealization::compare to candidate.concept.compare;
    #physicalDetail allocation step_ConceptRealization_select allocate LogicalRealization::ConceptRealization::select to candidate.concept.select;
    #physicalDetail allocation step_ConceptRealization_checkSelection allocate LogicalRealization::ConceptRealization::checkSelection to candidate.concept.checkSelection;
    #physicalDetail allocation step_ConceptRealization_retainSelection allocate LogicalRealization::ConceptRealization::retainSelection to candidate.concept.retainSelection;
    #physicalDetail allocation step_ConceptRealization_retainGaps allocate LogicalRealization::ConceptRealization::retainGaps to candidate.concept.retainGaps;
    #physicalDetail allocation step_ConceptRealization_retainRaw_receiveResult allocate LogicalRealization::ConceptRealization::retainRaw_receiveResult to candidate.concept.retainRaw_receiveResult;
    #physicalDetail allocation step_SoftwareRealization_submit allocate LogicalRealization::SoftwareRealization::submit to candidate.software.submit;
    #physicalDetail allocation step_SoftwareRealization_receive allocate LogicalRealization::SoftwareRealization::receive to candidate.software.receive;
    #physicalDetail allocation step_SoftwareRealization_interfaces allocate LogicalRealization::SoftwareRealization::interfaces to candidate.software.interfaces;
    #physicalDetail allocation step_SoftwareRealization_mapping allocate LogicalRealization::SoftwareRealization::mapping to candidate.software.mapping;
    #physicalDetail allocation step_SoftwareRealization_planCriteria allocate LogicalRealization::SoftwareRealization::planCriteria to candidate.software.planCriteria;
    #physicalDetail allocation step_SoftwareRealization_planMIL allocate LogicalRealization::SoftwareRealization::planMIL to candidate.software.planMIL;
    #physicalDetail allocation step_SoftwareRealization_executeMIL allocate LogicalRealization::SoftwareRealization::executeMIL to candidate.software.executeMIL;
    #executionHost allocation external_SoftwareRealization_executeMIL allocate candidate.software.executeMIL to candidate.models;
    #physicalDetail allocation step_SoftwareRealization_receiveMIL allocate LogicalRealization::SoftwareRealization::receiveMIL to candidate.software.receiveMIL;
    #physicalDetail allocation step_SoftwareRealization_preserveMIL allocate LogicalRealization::SoftwareRealization::preserveMIL to candidate.software.preserveMIL;
    #physicalDetail allocation step_SoftwareRealization_assessMIL allocate LogicalRealization::SoftwareRealization::assessMIL to candidate.software.assessMIL;
    #physicalDetail allocation step_SoftwareRealization_release allocate LogicalRealization::SoftwareRealization::release to candidate.software.release;
    #physicalDetail allocation step_SoftwareRealization_checkRelease allocate LogicalRealization::SoftwareRealization::checkRelease to candidate.software.checkRelease;
    #physicalDetail allocation step_SoftwareRealization_coordinate allocate LogicalRealization::SoftwareRealization::coordinate to candidate.software.coordinate;
    #physicalDetail allocation step_SoftwareRealization_codeBuildSil allocate LogicalRealization::SoftwareRealization::codeBuildSil to candidate.software.codeBuildSil;
    #executionHost allocation external_SoftwareRealization_codeBuildSil allocate candidate.software.codeBuildSil to candidate.hostCode;
    #physicalDetail allocation step_SoftwareRealization_receiveSIL allocate LogicalRealization::SoftwareRealization::receiveSIL to candidate.software.receiveSIL;
    #physicalDetail allocation step_SoftwareRealization_preserveSIL allocate LogicalRealization::SoftwareRealization::preserveSIL to candidate.software.preserveSIL;
    #physicalDetail allocation step_SoftwareRealization_checkCurrent allocate LogicalRealization::SoftwareRealization::checkCurrent to candidate.software.checkCurrent;
    #physicalDetail allocation step_SoftwareRealization_compare allocate LogicalRealization::SoftwareRealization::compare to candidate.software.compare;
    #physicalDetail allocation step_SoftwareRealization_credibility allocate LogicalRealization::SoftwareRealization::credibility to candidate.software.credibility;
    #physicalDetail allocation step_SoftwareRealization_assess allocate LogicalRealization::SoftwareRealization::assess to candidate.software.assess;
    #physicalDetail allocation step_SoftwareRealization_present allocate LogicalRealization::SoftwareRealization::present to candidate.software.present;
    #physicalDetail allocation step_SoftwareRealization_approve allocate LogicalRealization::SoftwareRealization::approve to candidate.software.approve;
    #physicalDetail allocation step_SoftwareRealization_checkProducts allocate LogicalRealization::SoftwareRealization::checkProducts to candidate.software.checkProducts;
    #physicalDetail allocation step_SoftwareRealization_retainProducts allocate LogicalRealization::SoftwareRealization::retainProducts to candidate.software.retainProducts;
    #physicalDetail allocation step_SoftwareRealization_block allocate LogicalRealization::SoftwareRealization::block to candidate.software.block;
    #physicalDetail allocation step_SoftwareRealization_retainRaw_receiveMIL allocate LogicalRealization::SoftwareRealization::retainRaw_receiveMIL to candidate.software.retainRaw_receiveMIL;
    #physicalDetail allocation step_SoftwareRealization_retainRaw_receiveSIL allocate LogicalRealization::SoftwareRealization::retainRaw_receiveSIL to candidate.software.retainRaw_receiveSIL;
    #physicalDetail allocation step_SoftwareRealization_rejectRelease allocate LogicalRealization::SoftwareRealization::rejectRelease to candidate.software.rejectRelease;
    #physicalDetail allocation step_ChangeReviewRealization_request allocate LogicalRealization::ChangeReviewRealization::request to candidate.changeReview.request;
    #physicalDetail allocation step_ChangeReviewRealization_receive allocate LogicalRealization::ChangeReviewRealization::receive to candidate.changeReview.receive;
    #physicalDetail allocation step_ChangeReviewRealization_invalidate allocate LogicalRealization::ChangeReviewRealization::invalidate to candidate.changeReview.invalidate;
    #physicalDetail allocation step_ChangeReviewRealization_changeDecision allocate LogicalRealization::ChangeReviewRealization::changeDecision to candidate.changeReview.changeDecision;
    #physicalDetail allocation step_ChangeReviewRealization_checkChange allocate LogicalRealization::ChangeReviewRealization::checkChange to candidate.changeReview.checkChange;
    #physicalDetail allocation step_ChangeReviewRealization_successor allocate LogicalRealization::ChangeReviewRealization::successor to candidate.changeReview.successor;
    #physicalDetail allocation step_ChangeReviewRealization_reassessAdvice allocate LogicalRealization::ChangeReviewRealization::reassessAdvice to candidate.changeReview.reassessAdvice;
    #physicalDetail allocation step_ChangeReviewRealization_planRepeat allocate LogicalRealization::ChangeReviewRealization::planRepeat to candidate.changeReview.planRepeat;
    #physicalDetail allocation step_ChangeReviewRealization_repeat allocate LogicalRealization::ChangeReviewRealization::repeat to candidate.changeReview.repeat;
    #executionHost allocation external_ChangeReviewRealization_repeat allocate candidate.changeReview.repeat to candidate.models;
    #physicalDetail allocation step_ChangeReviewRealization_receiveResult allocate LogicalRealization::ChangeReviewRealization::receiveResult to candidate.changeReview.receiveResult;
    #physicalDetail allocation step_ChangeReviewRealization_preserve allocate LogicalRealization::ChangeReviewRealization::preserve to candidate.changeReview.preserve;
    #physicalDetail allocation step_ChangeReviewRealization_credibility allocate LogicalRealization::ChangeReviewRealization::credibility to candidate.changeReview.credibility;
    #physicalDetail allocation step_ChangeReviewRealization_retrieve allocate LogicalRealization::ChangeReviewRealization::retrieve to candidate.changeReview.retrieve;
    #physicalDetail allocation step_ChangeReviewRealization_assess allocate LogicalRealization::ChangeReviewRealization::assess to candidate.changeReview.assess;
    #physicalDetail allocation step_ChangeReviewRealization_views allocate LogicalRealization::ChangeReviewRealization::views to candidate.changeReview.views;
    #physicalDetail allocation step_ChangeReviewRealization_prepare allocate LogicalRealization::ChangeReviewRealization::prepare to candidate.changeReview.prepare;
    #physicalDetail allocation step_ChangeReviewRealization_reviewers allocate LogicalRealization::ChangeReviewRealization::reviewers to candidate.changeReview.reviewers;
    #physicalDetail allocation step_ChangeReviewRealization_authority allocate LogicalRealization::ChangeReviewRealization::authority to candidate.changeReview.authority;
    #physicalDetail allocation step_ChangeReviewRealization_checkBaseline allocate LogicalRealization::ChangeReviewRealization::checkBaseline to candidate.changeReview.checkBaseline;
    #physicalDetail allocation step_ChangeReviewRealization_checkDecision allocate LogicalRealization::ChangeReviewRealization::checkDecision to candidate.changeReview.checkDecision;
    #physicalDetail allocation step_ChangeReviewRealization_record allocate LogicalRealization::ChangeReviewRealization::record to candidate.changeReview.record;
    #physicalDetail allocation step_ChangeReviewRealization_retain allocate LogicalRealization::ChangeReviewRealization::retain to candidate.changeReview.retain;
    #physicalDetail allocation step_ChangeReviewRealization_holdChange allocate LogicalRealization::ChangeReviewRealization::holdChange to candidate.changeReview.holdChange;
    #physicalDetail allocation step_ChangeReviewRealization_holdReview allocate LogicalRealization::ChangeReviewRealization::holdReview to candidate.changeReview.holdReview;
    #physicalDetail allocation step_ChangeReviewRealization_rejectReview allocate LogicalRealization::ChangeReviewRealization::rejectReview to candidate.changeReview.rejectReview;
    #physicalDetail allocation step_ChangeReviewRealization_retainRaw_receiveResult allocate LogicalRealization::ChangeReviewRealization::retainRaw_receiveResult to candidate.changeReview.retainRaw_receiveResult;
    #physicalDetail allocation step_ReplayRealization_request allocate LogicalRealization::ReplayRealization::request to candidate.replayRun.request;
    #physicalDetail allocation step_ReplayRealization_prepare allocate LogicalRealization::ReplayRealization::prepare to candidate.replayRun.prepare;
    #physicalDetail allocation step_ReplayRealization_execute allocate LogicalRealization::ReplayRealization::execute to candidate.replayRun.execute;
    #executionHost allocation external_ReplayRealization_execute allocate candidate.replayRun.execute to candidate.models;
    #physicalDetail allocation step_ReplayRealization_receive allocate LogicalRealization::ReplayRealization::receive to candidate.replayRun.receive;
    #physicalDetail allocation step_ReplayRealization_preserve allocate LogicalRealization::ReplayRealization::preserve to candidate.replayRun.preserve;
    #physicalDetail allocation step_ReplayRealization_compare allocate LogicalRealization::ReplayRealization::compare to candidate.replayRun.compare;
    #physicalDetail allocation step_ReplayRealization_retain allocate LogicalRealization::ReplayRealization::retain to candidate.replayRun.retain;
    #physicalDetail allocation step_ReplayRealization_missing allocate LogicalRealization::ReplayRealization::missing to candidate.replayRun.missing;
    #physicalDetail allocation step_ReplayRealization_retainRaw_receive allocate LogicalRealization::ReplayRealization::retainRaw_receive to candidate.replayRun.retainRaw_receive;
    #physicalDetail allocation step_CalibrationRealization_supply allocate LogicalRealization::CalibrationRealization::supply to candidate.calibration.supply;
    #physicalDetail allocation step_CalibrationRealization_receive allocate LogicalRealization::CalibrationRealization::receive to candidate.calibration.receive;
    #physicalDetail allocation step_CalibrationRealization_checkData allocate LogicalRealization::CalibrationRealization::checkData to candidate.calibration.checkData;
    #physicalDetail allocation step_CalibrationRealization_propose allocate LogicalRealization::CalibrationRealization::propose to candidate.calibration.propose;
    #physicalDetail allocation step_CalibrationRealization_choose allocate LogicalRealization::CalibrationRealization::choose to candidate.calibration.choose;
    #physicalDetail allocation step_CalibrationRealization_prepareChange allocate LogicalRealization::CalibrationRealization::prepareChange to candidate.calibration.prepareChange;
    #physicalDetail allocation step_CalibrationRealization_invalidate allocate LogicalRealization::CalibrationRealization::invalidate to candidate.calibration.invalidate;
    #physicalDetail allocation step_CalibrationRealization_checkChange allocate LogicalRealization::CalibrationRealization::checkChange to candidate.calibration.checkChange;
    #physicalDetail allocation step_CalibrationRealization_successor allocate LogicalRealization::CalibrationRealization::successor to candidate.calibration.successor;
    #physicalDetail allocation step_CalibrationRealization_reassess allocate LogicalRealization::CalibrationRealization::reassess to candidate.calibration.reassess;
    #physicalDetail allocation step_CalibrationRealization_planRepeat allocate LogicalRealization::CalibrationRealization::planRepeat to candidate.calibration.planRepeat;
    #physicalDetail allocation step_CalibrationRealization_repeat allocate LogicalRealization::CalibrationRealization::repeat to candidate.calibration.repeat;
    #executionHost allocation external_CalibrationRealization_repeat allocate candidate.calibration.repeat to candidate.models;
    #physicalDetail allocation step_CalibrationRealization_receiveResult allocate LogicalRealization::CalibrationRealization::receiveResult to candidate.calibration.receiveResult;
    #physicalDetail allocation step_CalibrationRealization_preserve allocate LogicalRealization::CalibrationRealization::preserve to candidate.calibration.preserve;
    #physicalDetail allocation step_CalibrationRealization_credibility allocate LogicalRealization::CalibrationRealization::credibility to candidate.calibration.credibility;
    #physicalDetail allocation step_CalibrationRealization_assess allocate LogicalRealization::CalibrationRealization::assess to candidate.calibration.assess;
    #physicalDetail allocation step_CalibrationRealization_retainEvidence allocate LogicalRealization::CalibrationRealization::retainEvidence to candidate.calibration.retainEvidence;
    #physicalDetail allocation step_CalibrationRealization_retain allocate LogicalRealization::CalibrationRealization::retain to candidate.calibration.retain;
    #physicalDetail allocation step_CalibrationRealization_unusable allocate LogicalRealization::CalibrationRealization::unusable to candidate.calibration.unusable;
    #physicalDetail allocation step_CalibrationRealization_retainRaw_receiveResult allocate LogicalRealization::CalibrationRealization::retainRaw_receiveResult to candidate.calibration.retainRaw_receiveResult;
    @ComparisonMechanism about C01::checkDraft { mop = "MOP-FR02"; mechanism = "Imported requirement text and Capella architecture context feed proposed quality checks."; operation = CandidateVS::C01::checkDraft meta SysML::ActionUsage; }
    dependency comparison_MOP_FR02 from FrameworkRequirements::MOP_FR02 to CandidateVS::C01::checkDraft;
    @ComparisonMechanism about C01::recommend { mop = "MOP-FR03"; mechanism = "Architecture, modes and requirements feed a sourced method service with eligibility checks."; operation = CandidateVS::C01::recommend meta SysML::ActionUsage; }
    dependency comparison_MOP_FR03 from FrameworkRequirements::MOP_FR03 to CandidateVS::C01::recommend;
    @ComparisonMechanism about C03::planAnalysis { mop = "MOP-FR18"; mechanism = "Capella/Valispace definitions -> declared characterized EPS plant -> proposed USD whole-CUBICS numerical mappings."; operation = CandidateVS::C03::planAnalysis meta SysML::ActionUsage; }
    dependency comparison_MOP_FR18 from FrameworkRequirements::MOP_FR18 to CandidateVS::C03::planAnalysis;
    @ComparisonMechanism about C03::mapFPrime { mop = "MOP-FR34"; mechanism = "Capella/Valispace interface definitions -> new translations of all interface/ground meanings -> required versioned F Prime profile."; operation = CandidateVS::C03::mapFPrime meta SysML::ActionUsage; }
    dependency comparison_MOP_FR34 from FrameworkRequirements::MOP_FR34 to CandidateVS::C03::mapFPrime;
    @ComparisonMechanism about C06::invalidate { mop = "MOP-FR30"; mechanism = "Asynchronous Capella and Valispace transfers invalidate advice and recheck both tool/context revisions."; operation = CandidateVS::C06::invalidate meta SysML::ActionUsage; }
    dependency comparison_MOP_FR30 from FrameworkRequirements::MOP_FR30 to CandidateVS::C06::invalidate;
    @ComparisonMechanism about C06::prepareReplay { mop = "MOP-FR10"; mechanism = "Both tool exports, Valispace parameter revisions, synchronization scripts, characterized EPS plant, solver/host dependencies and raw outputs."; operation = CandidateVS::C06::prepareReplay meta SysML::ActionUsage; }
    dependency comparison_MOP_FR10 from FrameworkRequirements::MOP_FR10 to CandidateVS::C06::prepareReplay;
}
