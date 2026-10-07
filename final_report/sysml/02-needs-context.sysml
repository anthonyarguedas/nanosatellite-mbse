// Mission/lifecycle stage. The report and this model agree on final MR/MOE/UC text.
// TODO: Re-derive 03-requirements and 09-scenarios. MR-06--11, all MN records and old SC01--03 are retired.
// TODO: Old links to MR-01--05 resolve by name but have obsolete meanings. Replace them in the next stage.
package FrameworkNeeds {
    private import FrameworkDomain::*;
    private import ScalarValues::*;

    item asIsBasis : EngineeringArtifact {
        doc /* The preserved observations show reuse, atomic tasks, club review names and useful simulation. They establish no shared formal EPS lifecycle or NASA review maturity. All existing stakeholder roles and concern statements remain available unchanged in FrameworkDomain and FrameworkConcerns. */
    }
    item lifecycleBasis : EngineeringArtifact {
        doc /* NASA supplies reference phases, product maturity and review purposes. EPS mission analysis, empirical and analytical sizing, time-dependent power analysis, coupled subsystem trades, model credibility and shared engineering data enrich the work. This is a proposed lifecycle through adapted C, not NASA certification or approved waivers. Modeling hardware and comparing physical EPS architectures remain in scope. No physical prototyping, fabrication, procurement, operation, testing, PIL, HIL, target processor timing/power qualification, physical qualification or Phase D. */
    }
    @SourceRecord {
        identifier = "EPS lifecycle basis";
        sourceText = "Reference lifecycle from Pre-Phase A through adapted Phase C with scoped model/software integration readiness.";
        sourceLocator = "EPS lifecycle and scope, mission requirements and effectiveness";
        status = "proposed specification, stakeholder agreement and empirical evaluation pending";
        citationRecord = "nasa2016systems: 2.1--2.4, 3.3--3.6, 6.2--6.7; handpicked-0003: 2--4; review-0289: 2--4; review-0711: 2--3; review-0340: 3,5--6; campioli2025integration: 3--4; review-0573: 2--4; handpicked-0001: pp.7--9";
    }
    #sourceTrace dependency observedContext from lifecycleBasis to asIsBasis;

    item def EPSLifecyclePhase :> EngineeringArtifact {
        attribute standardName : String;
        attribute epsWork : String;
        attribute importantProducts : String;
        attribute :>> status = "proposed scope, no accepted phase baseline asserted";
    }
    item prePhaseA : EPSLifecyclePhase {
        attribute :>> standardName = "Pre-Phase A: Concept Studies";
        attribute :>> epsWork = "Establish expectations, mission objectives and ConOps including degraded operation. Declare orbit, attitude, duration, environment and loads. Compare feasible concepts with initial budgets, sizing and uncertainty.";
        attribute :>> importantProducts = "Feasible EPS concepts, initial ConOps, draft requirements, budgets, assumptions, risks and preliminary verification and validation approach.";
    }
    item phaseA : EPSLifecyclePhase {
        attribute :>> standardName = "Phase A: Concept and Technology Development";
        attribute :>> epsWork = "Derive and validate EPS requirements and interfaces. Allocate functions and requirements while comparing credible architectures. Identify technology gaps and assessment methods.";
        attribute :>> importantProducts = "Mission concept baseline, EPS requirements and interface definitions, architecture alternatives and selection rationale, technical and verification and validation plans.";
    }
    item phaseB : EPSLifecyclePhase {
        attribute :>> standardName = "Phase B: Preliminary Design and Technology Completion";
        attribute :>> epsWork = "Refine array/battery sizing, conversion, bus regulation, protection, distribution and control. Compare mass, volume, cost, availability, margins and risk using a common time-dependent mission basis. Resolve subsystem incompatibilities. Hardware maturity depends on applicable existing evidence, with gaps external.";
        attribute :>> importantProducts = "Justified preliminary design, allocated specifications, agreed interfaces, trade and sizing results, updated budgets and risks, integration and verification and validation plans.";
    }
    item phaseC : EPSLifecyclePhase {
        attribute :>> standardName = "Phase C: Final Design and Fabrication (adapted)";
        attribute :>> epsWork = "Complete detailed EPS models and interface specifications. Define detailed software design before deliverable coding. Complete declared host-executed control/interface software. Assess modeled control through MIL and declared code through SIL, including transitions, protection and recovery.";
        attribute :>> importantProducts = "Controlled technical data package, released models and software, applicable analysis and MIL/SIL results, model/software integration configurations and procedures.";
        doc /* Scoped completion establishes model/software integration readiness only. Target processor timing, memory and power qualification, PIL, HIL, physical qualification and flight readiness are excluded. CDR during C precedes deliverable coding. End-of-C SIR assesses released-product readiness. */
    }
    item iterationAndRecursion : EngineeringArtifact {
        doc /* Requirements allocation and component refinement apply processes recursively across levels and maturity stages. Changed loads, orbit, components or software interfaces can reopen earlier work. Engineers assess impacts, authorize changes, repeat affected checks and issue coherent successor baselines. Stale evidence remains identifiable and supports no current claim. These behaviors implement the mission outcomes without a separate iteration/recursion requirement. */
    }

    item def ScopedReviewSpecification :> EngineeringArtifact {
        attribute timing : String;
        attribute successEvidence : String;
        attribute futureDecision : String;
        attribute :>> status = "proposed criteria, stakeholder agreement pending";
        doc /* Specification of a future review. A prepared package is an entrance product. Acceptance requires an authorized decision against agreed success criteria. Blocking findings prevent progression. Conditional decisions retain limits, actions, owners and dates. Hardware production readiness and physical qualification criteria are excluded. Missing hardware evidence is not treated as satisfied. */
    }
    item mcr : ScopedReviewSpecification {
        attribute :>> identifier = "MCR";
        attribute :>> timing = "end of Pre-Phase A";
        attribute :>> successEvidence = "Justified mission need, feasible EPS concepts, initial ConOps, budgets, assumptions, risks and preliminary V&V approach";
        attribute :>> futureDecision = "support further concept development";
    }
    item srr : ScopedReviewSpecification {
        attribute :>> identifier = "SRR";
        attribute :>> timing = "during Phase A";
        attribute :>> successEvidence = "Validated EPS requirements, measurable criteria, source traceability and defined interfaces consistent with mission expectations";
        attribute :>> futureDecision = "support architecture definition";
    }
    item mdrSdr : ScopedReviewSpecification {
        attribute :>> identifier = "MDR/SDR";
        attribute :>> timing = "end of Phase A";
        attribute :>> successEvidence = "Credible EPS architecture, requirement allocation and justified alternatives";
        attribute :>> futureDecision = "support preliminary design";
    }
    item pdr : ScopedReviewSpecification {
        attribute :>> identifier = "PDR";
        attribute :>> timing = "end of Phase B";
        attribute :>> successEvidence = "Compatible preliminary design, sizing and trade evidence, margins, risk dispositions, controlled interfaces and V&V plans";
        attribute :>> futureDecision = "justify detailed design against applicable requirements";
    }
    item cdr : ScopedReviewSpecification {
        attribute :>> identifier = "CDR";
        attribute :>> timing = "during adapted Phase C, before deliverable coding";
        attribute :>> successEvidence = "Complete detailed model/software design, interface specifications and scoped implementation, integration and V&V plans";
        attribute :>> futureDecision = "support design baseline release and deliverable coding";
    }
    item sir : ScopedReviewSpecification {
        attribute :>> identifier = "SIR";
        attribute :>> timing = "end of adapted Phase C";
        attribute :>> successEvidence = "Released model/software products, applicable MIL/SIL evidence, compatible interfaces and ready integration configurations and procedures";
        attribute :>> futureDecision = "justify scoped integration readiness";
    }
    #sourceTrace dependency phaseReview_preA from mcr to prePhaseA;
    #sourceTrace dependency phaseReview_A1 from srr to phaseA;
    #sourceTrace dependency phaseReview_A2 from mdrSdr to phaseA;
    #sourceTrace dependency phaseReview_B from pdr to phaseB;
    #sourceTrace dependency phaseReview_C1 from cdr to phaseC;
    #sourceTrace dependency phaseReview_C2 from sir to phaseC;

    requirement <'MR-01'> MR_01 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The EPS engineering enterprise shall establish a mission concept whose EPS feasibility is justified against agreed stakeholder expectations and mission constraints. */
    }
    @SourceRecord { identifier = "MR-01"; sourceText = "The EPS engineering enterprise shall establish a mission concept whose EPS feasibility is justified against agreed stakeholder expectations and mission constraints."; sourceLocator = "Enterprise mission requirements and measures"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.3--3.5"; }
    requirement <'MR-02'> MR_02 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall establish validated EPS and component requirements and interfaces consistent with the mission concept and allocated spacecraft requirements. */
    }
    @SourceRecord { identifier = "MR-02"; sourceText = "The enterprise shall establish validated EPS and component requirements and interfaces consistent with the mission concept and allocated spacecraft requirements."; sourceLocator = "Enterprise mission requirements and measures"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.4--3.6, 4.1--4.2"; }
    requirement <'MR-03'> MR_03 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall justify a sized EPS architecture and preliminary design against applicable requirements, agreed resource limits and acceptable risk within the declared model and analysis scope. */
    }
    @SourceRecord { identifier = "MR-03"; sourceText = "The enterprise shall justify a sized EPS architecture and preliminary design against applicable requirements, agreed resource limits and acceptable risk within the declared model and analysis scope."; sourceLocator = "Enterprise mission requirements and measures"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.4--3.5; review-0289: 2--4; handpicked-0003: 3--4; review-0711: 2--3"; }
    requirement <'MR-04'> MR_04 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall complete detailed EPS design models and declared host-executed control/interface software products sufficient for integration within the model and software scope. */
    }
    @SourceRecord { identifier = "MR-04"; sourceText = "The enterprise shall complete detailed EPS design models and declared host-executed control/interface software products sufficient for integration within the model and software scope."; sourceLocator = "Enterprise mission requirements and measures"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.6; review-0573: 2; handpicked-0001: pp.7--9"; }
    requirement <'MR-05'> MR_05 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall establish and maintain coherent phase baselines after controlled changes, supported by applicable verification and validation evidence and accepted against agreed technical review success criteria. */
    }
    @SourceRecord { identifier = "MR-05"; sourceText = "The enterprise shall establish and maintain coherent phase baselines after controlled changes, supported by applicable verification and validation evidence and accepted against agreed technical review success criteria."; sourceLocator = "Enterprise mission requirements and measures"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 2.4, 5.3--5.4, 6.2--6.7; review-0340: 3.2,5--6; campioli2025integration: 3--4"; }
    #proposedDerivation dependency basis_MR01 from MR_01 to lifecycleBasis;
    #proposedDerivation dependency basis_MR02 from MR_02 to lifecycleBasis;
    #proposedDerivation dependency basis_MR03 from MR_03 to lifecycleBasis;
    #proposedDerivation dependency basis_MR04 from MR_04 to lifecycleBasis;
    #proposedDerivation dependency basis_MR05 from MR_05 to lifecycleBasis;

    item <'MOE-01'> MOE_01 : EffectivenessMeasure {
        doc /* Engineering burden: active person-hours and elapsed hours for correct requirements, design, change and review tasks, with waiting and unattended execution reported separately. */
        attribute :>> observationBasis = "Correct task outcomes under comparable declared tasks, participants, resources and time boundaries";
        attribute activeEffort : ActiveEffort [0..1];
        attribute elapsed : ElapsedTime [0..1];
        attribute waiting : ElapsedTime [0..1];
        attribute unattendedExecution : ElapsedTime [0..1];
    }
    item <'MOE-02'> MOE_02 : EffectivenessMeasure {
        doc /* Early issue detection: expert-confirmed issues found before scoped final design, critical misses and unnecessary investigations against a declared reference issue set. */
        attribute :>> observationBasis = "Independent expert reference issues and clean controls, with critical misses and unnecessary investigations retained";
        attribute confirmedEarlyIssues : Integer [0..1];
        attribute criticalMisses : Integer [0..1];
        attribute unnecessaryInvestigations : Integer [0..1];
    }
    item <'MOE-03'> MOE_03 : EffectivenessMeasure {
        doc /* Evidence and review usefulness: applicable requirement and expectation coverage, critical review defects, reviewer interpretation accuracy and successful independent reconstruction. */
        attribute :>> observationBasis = "Declared applicable requirements and expectations, fixed reviewer tasks and result-specific reconstruction comparison rules";
        attribute requirementCoverage : CoverageFraction [0..1];
        attribute expectationCoverage : CoverageFraction [0..1];
        attribute criticalReviewDefects : Integer [0..1];
        attribute interpretationAccuracy : CoverageFraction [0..1];
        attribute successfulReconstruction : CoverageFraction [0..1];
    }
    item <'MOE-04'> MOE_04 : EffectivenessMeasure {
        doc /* Adoption and affordability: person-hours to learn and complete correct tasks and adapt to a mission, and direct framework usage cost in CAD over a declared period and price date. */
        attribute :>> observationBasis = "Correct adoption and mission-adaptation tasks, declared computing/licenses/services, period and price date";
        attribute learningAndTaskEffort : ActiveEffort [0..1];
        attribute missionAdaptationEffort : ActiveEffort [0..1];
        attribute directUsageCost : FrameworkUsageCost [0..1];
    }
    // Each MOE observes enterprise accomplishment across MR-01--05.
    #sourceTrace dependency effectiveness_MOE01 from MOE_01 to ToBe::EPSEngineeringEnterprise;
    #sourceTrace dependency effectiveness_MOE02 from MOE_02 to ToBe::EPSEngineeringEnterprise;
    #sourceTrace dependency effectiveness_MOE03 from MOE_03 to ToBe::EPSEngineeringEnterprise;
    #sourceTrace dependency effectiveness_MOE04 from MOE_04 to ToBe::EPSEngineeringEnterprise;
    // Concern contributions explain quality of accomplishment, not one MR per concern.
    #qualitativeContribution dependency burden_PM01 from FrameworkConcerns::C_PM_01 to MOE_01;
    #qualitativeContribution dependency burden_PM02 from FrameworkConcerns::C_PM_02 to MOE_01;
    #qualitativeContribution dependency burden_SE03 from FrameworkConcerns::C_SE_03 to MOE_01;
    #qualitativeContribution dependency detection_PM03 from FrameworkConcerns::C_PM_03 to MOE_02;
    #qualitativeContribution dependency detection_EPS01 from FrameworkConcerns::C_EPS_01 to MOE_02;
    #qualitativeContribution dependency review_SE02 from FrameworkConcerns::C_SE_02 to MOE_03;
    #qualitativeContribution dependency review_EPS11 from FrameworkConcerns::C_EPS_11 to MOE_03;
    #qualitativeContribution dependency adoption_PM011 from FrameworkConcerns::C_PM_01_1 to MOE_04;
    #qualitativeContribution dependency adoption_PM012 from FrameworkConcerns::C_PM_01_2 to MOE_04;
    #qualitativeContribution dependency adoption_PM05 from FrameworkConcerns::C_PM_05 to MOE_04;

    item modelCredibilityMeasures : ModelCredibility {
        attribute voltageResidual : VoltageResidual [0..1];
        attribute temperatureResidual : TemperatureResidual [0..1];
        attribute energyResidual : EnergyResidual [0..1];
        attribute batteryHealthResidual : BatteryHealthResidual [0..1];
        attribute uncertaintyAndValidityDomain : String [0..1];
        attribute runtime : ElapsedTime [0..1];
        doc /* Supporting measures retain engineering units: volts, kelvin difference, watt-hours and health percentage points. Calibration fit and reconstruction alone establish no predictive validity. Assistance precision/recall and response delay are framework performance measures. Supporting measures do not replace enterprise MOEs. Targets and achieved values remain unresolved. */
    }
    item distinctAssessmentSubjects : FrameworkEvaluation {
        doc /* Framework verification assesses framework requirements. Framework validation assesses engineer/reviewer suitability in representative use. EPS phase-product verification assesses applicable EPS requirements. EPS validation assesses stakeholder expectations and ConOps in representative, possibly simulated conditions, beginning early with phase products including models. Model credibility assesses intended use, numerical correctness, assumptions, calibration, independent validation data and uncertainty. Research evaluation assesses enterprise benefit and bounded transfer. Planned procedures remain specifications. Native syntax/semantic checks establish model quality within tool scope, not framework V&V or measured benefit. */
    }
    item researchEvaluationProtocol : FrameworkEvaluation {
        doc /* Two contrasting EPS cases are an evaluation protocol only. Fix cases, tasks, reference answers, participants, configurations, permitted adaptations, comparison rules and price date before execution. Include failed checks, missing data, misleading suggestions, stale evidence and clean controls. Compare burden only for correct outcomes under comparable conditions. All achieved values are unknown. Targets, acceptable errors and review thresholds remain pending stakeholder agreement and intended-use justification. */
    }

    use case <'UC01'> UC01 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers establish and compare EPS mission concepts against agreed stakeholder expectations and mission constraints. */ }
        doc /* Establish a feasible EPS mission concept. Enterprise participants develop concepts, initial ConOps and feasibility evidence for stakeholder and MCR assessment. Scenario elaboration is pending. */
    }
    use case <'UC02'> UC02 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor reviewers : IndependentReviewer;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers derive, allocate and validate EPS and component requirements and interfaces from the mission concept and spacecraft requirements. */ }
        doc /* Define and validate EPS requirements and interfaces. Enterprise participants prepare consistent requirements, criteria and interfaces for stakeholder and SRR assessment. Scenario elaboration is pending. */
    }
    use case <'UC03'> UC03 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor reviewers : IndependentReviewer;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers compare and size EPS architectures, justify the preliminary design against applicable requirements and resolve subsystem incompatibilities within agreed resources and risk. */ }
        doc /* Justify the EPS preliminary design. Enterprise participants mature trades, allocation and preliminary design evidence through MDR/SDR and PDR. No hardware qualification is claimed. Scenario elaboration is pending. */
    }
    use case <'UC04'> UC04 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor reviewers : IndependentReviewer;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers complete detailed EPS design models and declared host-executed control/interface software, assess them through MIL/SIL and prepare scoped integration readiness evidence. */ }
        doc /* Complete detailed EPS models and software. Enterprise participants prepare detailed design for scoped CDR, complete declared software and models, and prepare applicable MIL/SIL evidence and integration configurations/procedures for end-of-C SIR. Scenario elaboration is pending. */
    }
    use case <'UC05'> UC05 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor reviewers : IndependentReviewer;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers control changes, repeat affected analyses and V&V, and submit coherent phase baselines for authorized review decisions. */ }
        doc /* Maintain and review coherent phase baselines. Crosscutting enterprise work preserves configuration, evidence currency, decision rationale and finding dispositions across phases and changes. Package preparation is distinct from accepted review decisions. Scenario elaboration is pending. */
    }
    #proposedDerivation dependency refine_UC01_MR01 from UC01 to MR_01;
    #proposedDerivation dependency refine_UC01_MR05 from UC01 to MR_05;
    #proposedDerivation dependency refine_UC02_MR01 from UC02 to MR_01;
    #proposedDerivation dependency refine_UC02_MR02 from UC02 to MR_02;
    #proposedDerivation dependency refine_UC02_MR05 from UC02 to MR_05;
    #proposedDerivation dependency refine_UC03_MR02 from UC03 to MR_02;
    #proposedDerivation dependency refine_UC03_MR03 from UC03 to MR_03;
    #proposedDerivation dependency refine_UC03_MR05 from UC03 to MR_05;
    #proposedDerivation dependency refine_UC04_MR02 from UC04 to MR_02;
    #proposedDerivation dependency refine_UC04_MR03 from UC04 to MR_03;
    #proposedDerivation dependency refine_UC04_MR04 from UC04 to MR_04;
    #proposedDerivation dependency refine_UC04_MR05 from UC04 to MR_05;
    #proposedDerivation dependency refine_UC05_MR01 from UC05 to MR_01;
    #proposedDerivation dependency refine_UC05_MR02 from UC05 to MR_02;
    #proposedDerivation dependency refine_UC05_MR03 from UC05 to MR_03;
    #proposedDerivation dependency refine_UC05_MR04 from UC05 to MR_04;
    #proposedDerivation dependency refine_UC05_MR05 from UC05 to MR_05;
}
