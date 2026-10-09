// Mission/lifecycle stage. Six mission requirements define the scoped review gates.
// Preserve the established as-is basis, effectiveness measures and concern cuts.
package FrameworkNeeds {
    private import FrameworkDomain::*;
    private import ScalarValues::*;

    item asIsBasis : EngineeringArtifact {
        doc /* ASCEND-associated students wishing to participate in CUBICS follow no systems engineering method. They verify payload power requirements only after fabrication. They value simulating rocket requirements before fabrication and want the same capability for power. These observations concern those students. The retained concern hierarchy covers four engineering roles. */
    }
    item lifecycleBasis : EngineeringArtifact {
        doc /* NASA supplies reference phases, product maturity and review purposes. EPS mission analysis, empirical and analytical sizing, time-dependent power analysis, coupled subsystem trades, model credibility and shared engineering data enrich the work. This is a proposed lifecycle through adapted C, not NASA certification or approved waivers. Modeling hardware and comparing physical EPS architectures remain in scope. No physical prototyping, fabrication, procurement, operation, testing, PIL, HIL, target processor timing/power qualification, physical qualification or Phase D. */
    }
    @SourceRecord {
        identifier = "EPS lifecycle basis";
        sourceText = "Reference lifecycle from Pre-Phase A through adapted Phase C with scoped model/software integration readiness.";
        sourceLocator = "EPS lifecycle and scope, mission requirements and effectiveness";
        status = "proposed specification, stakeholder agreement and empirical evaluation pending";
        citationRecord = "nasa2016systems: 2.1--2.4, 3.3--3.6, 6.2--6.7; handpicked-0003: 2--4; review-0289: 2--4; review-0711: 2--3; review-0340: 3,5--6; campioli2025integration: 3--4; review-0573: 2--4; handpicked-0002: slides 4,13,18; handpicked-0001: p.3, pp.7--9";
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
        attribute :>> epsWork = "Refine array/battery sizing, conversion, bus regulation, protection, distribution and control. Compare mass, volume, availability, margins and risk using a common time-dependent mission basis. Resolve subsystem incompatibilities. Hardware maturity depends on applicable existing evidence, with gaps external.";
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

    item gateSuccessConditions : EngineeringArtifact {
        doc /* The following success conditions apply to all six mission requirements. The enterprise shall establish and maintain coherent phase baselines through authorized changes, repeated affected checks and applicable verification and validation evidence, retaining configuration-linked requirements, expectations, methods, results, limitations and finding dispositions. It shall obtain and retain acceptance decisions from the designated review authority against agreed success criteria, prevent progression with blocking findings, and record conditional limits, closure actions, owners and dates. A prepared package supports entrance to review. Acceptance requires an explicit authorized accepted decision. */
    }
    item continuedRefinement : EngineeringArtifact {
        doc /* The enterprise shall derive, refine and validate EPS and component requirements and interfaces as the design matures through Phase B and adapted C. Changes can reopen earlier work. */
    }

    requirement <'MR-01'> MR_01 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The EPS engineering enterprise shall obtain MCR acceptance at the end of Pre-Phase A for a mission concept whose EPS feasibility is justified against agreed stakeholder expectations and mission constraints, supported by initial ConOps, technical budgets, assumptions, risks and a preliminary verification and validation approach. */
    }
    @SourceRecord about MR_01 { identifier = "MR-01"; sourceText = "The EPS engineering enterprise shall obtain MCR acceptance at the end of Pre-Phase A for a mission concept whose EPS feasibility is justified against agreed stakeholder expectations and mission constraints, supported by initial ConOps, technical budgets, assumptions, risks and a preliminary verification and validation approach."; sourceLocator = "Mission requirements and effectiveness, Table tab:framework-mission-requirements"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.3"; }
    requirement <'MR-02'> MR_02 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall obtain SRR acceptance during Phase A for validated EPS requirements and interfaces traced to the mission concept and allocated spacecraft requirements, with measurable criteria consistent with stakeholder expectations. */
    }
    @SourceRecord about MR_02 { identifier = "MR-02"; sourceText = "The enterprise shall obtain SRR acceptance during Phase A for validated EPS requirements and interfaces traced to the mission concept and allocated spacecraft requirements, with measurable criteria consistent with stakeholder expectations."; sourceLocator = "Mission requirements and effectiveness, Table tab:framework-mission-requirements"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.4, 4.1--4.2"; }
    requirement <'MR-03'> MR_03 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall obtain MDR/SDR acceptance at the end of Phase A for a credible EPS architecture with requirement allocations and justified alternatives. */
    }
    @SourceRecord about MR_03 { identifier = "MR-03"; sourceText = "The enterprise shall obtain MDR/SDR acceptance at the end of Phase A for a credible EPS architecture with requirement allocations and justified alternatives."; sourceLocator = "Mission requirements and effectiveness, Table tab:framework-mission-requirements"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.4"; }
    requirement <'MR-04'> MR_04 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall obtain PDR acceptance at the end of Phase B for a sized, compatible preliminary EPS design supported by sizing and trades, margins, risk dispositions, controlled interfaces and verification and validation plans against applicable requirements and agreed technical resource and risk limits. */
    }
    @SourceRecord about MR_04 { identifier = "MR-04"; sourceText = "The enterprise shall obtain PDR acceptance at the end of Phase B for a sized, compatible preliminary EPS design supported by sizing and trades, margins, risk dispositions, controlled interfaces and verification and validation plans against applicable requirements and agreed technical resource and risk limits."; sourceLocator = "Mission requirements and effectiveness, Table tab:framework-mission-requirements"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.5"; }
    requirement <'MR-05'> MR_05 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall obtain scoped CDR acceptance during adapted Phase C, before deliverable coding, for complete detailed EPS model and software designs, interface specifications and implementation, integration and verification and validation plans. */
    }
    @SourceRecord about MR_05 { identifier = "MR-05"; sourceText = "The enterprise shall obtain scoped CDR acceptance during adapted Phase C, before deliverable coding, for complete detailed EPS model and software designs, interface specifications and implementation, integration and verification and validation plans."; sourceLocator = "Mission requirements and effectiveness, Table tab:framework-mission-requirements"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.6, 6.7 Table 6.7-1; review-0573: 2; handpicked-0002: slides 13,18"; }
    requirement <'MR-06'> MR_06 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        doc /* The enterprise shall obtain scoped SIR acceptance at the end of adapted Phase C for released EPS models and declared control and interface software for host execution, applicable MIL/SIL evidence, compatible interfaces and ready integration configurations and procedures. */
    }
    @SourceRecord about MR_06 { identifier = "MR-06"; sourceText = "The enterprise shall obtain scoped SIR acceptance at the end of adapted Phase C for released EPS models and declared control and interface software for host execution, applicable MIL/SIL evidence, compatible interfaces and ready integration configurations and procedures."; sourceLocator = "Mission requirements and effectiveness, Table tab:framework-mission-requirements"; status = "proposed specification, stakeholder agreement pending"; citationRecord = "nasa2016systems: 3.6, 6.7 Table 6.7-1; handpicked-0002: slide 4; handpicked-0001: p.3"; }
    #proposedDerivation dependency basis_MR01 from MR_01 to lifecycleBasis;
    #proposedDerivation dependency basis_MR02 from MR_02 to lifecycleBasis;
    #proposedDerivation dependency basis_MR03 from MR_03 to lifecycleBasis;
    #proposedDerivation dependency basis_MR04 from MR_04 to lifecycleBasis;
    #proposedDerivation dependency basis_MR05 from MR_05 to lifecycleBasis;
    #proposedDerivation dependency basis_MR06 from MR_06 to lifecycleBasis;
    #sourceTrace dependency gate_MR01_MCR from MR_01 to mcr;
    #sourceTrace dependency gate_MR02_SRR from MR_02 to srr;
    #sourceTrace dependency gate_MR03_MDRSDR from MR_03 to mdrSdr;
    #sourceTrace dependency gate_MR04_PDR from MR_04 to pdr;
    #sourceTrace dependency gate_MR05_CDR from MR_05 to cdr;
    #sourceTrace dependency gate_MR06_SIR from MR_06 to sir;
    #sourceTrace dependency gateConditions_MR01 from MR_01 to gateSuccessConditions;
    #sourceTrace dependency gateConditions_MR02 from MR_02 to gateSuccessConditions;
    #sourceTrace dependency gateConditions_MR03 from MR_03 to gateSuccessConditions;
    #sourceTrace dependency gateConditions_MR04 from MR_04 to gateSuccessConditions;
    #sourceTrace dependency gateConditions_MR05 from MR_05 to gateSuccessConditions;
    #sourceTrace dependency gateConditions_MR06 from MR_06 to gateSuccessConditions;

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
        doc /* Adoption burden: person-hours to learn and complete correct tasks and adapt to a mission. */
        attribute :>> observationBasis = "Correct learning and mission-adaptation tasks under declared participants, computing resources and task boundaries";
        attribute learningAndTaskEffort : ActiveEffort [0..1];
        attribute missionAdaptationEffort : ActiveEffort [0..1];
    }
    item <'MOE-05'> MOE_05 : EffectivenessMeasure {
        doc /* Resource and access burden: monetary cost of required software, data and host computing over a fixed period, and required task attempts blocked by cost or access restrictions. Declare currency, price date, resource quantities and access terms. Report person-hours separately. */
        attribute :>> observationBasis = "Fixed evaluation period, currency and price date, declared quantities of software, data and host computing, and access terms. Hardware procurement, savings from replica maintenance and avoided fabrication cost remain outside scope.";
        attribute monetaryCost : Real [0..1];
        attribute currency : String [0..1];
        attribute priceDate : String [0..1];
        attribute evaluationPeriod : String [0..1];
        attribute resourceQuantitiesAndAccessTerms : String [0..1];
        attribute blockedTaskAttempts : Integer [0..1];
    }
    item <'MOE-06'> MOE_06 : EffectivenessMeasure {
        doc /* Clarity of scope and evidence limits: reviewer accuracy in distinguishing supported model and host software conclusions from unresolved physical, operational or target claims. Also measure coverage of external evidence gaps with a recorded disposition and responsible authority. */
        attribute :>> observationBasis = "Independent questions on claim classification and an applicable checklist of external obligations. Retain exclusions, limits of supplied evidence, unresolved gaps and responsible authorities. Completion of excluded work remains outside this measure.";
        attribute boundaryInterpretationAccuracy : CoverageFraction [0..1];
        attribute externalGapDispositionCoverage : CoverageFraction [0..1];
    }
    // Each MOE observes enterprise accomplishment across MR-01--06.
    #sourceTrace dependency effectiveness_MOE01 from MOE_01 to ToBe::EPSEngineeringEnterprise;
    #sourceTrace dependency effectiveness_MOE02 from MOE_02 to ToBe::EPSEngineeringEnterprise;
    #sourceTrace dependency effectiveness_MOE03 from MOE_03 to ToBe::EPSEngineeringEnterprise;
    #sourceTrace dependency effectiveness_MOE04 from MOE_04 to ToBe::EPSEngineeringEnterprise;
    #sourceTrace dependency effectiveness_MOE05 from MOE_05 to ToBe::EPSEngineeringEnterprise;
    #sourceTrace dependency effectiveness_MOE06 from MOE_06 to ToBe::EPSEngineeringEnterprise;
    // Every concern occurrence contributes explicitly in FrameworkConcerns.
    // No duplicate primary-root-only contribution inventory is maintained here.

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
    // TODO: Extend the later research evaluation plan from MOE-01--04 to MOE-01--06.
    // MOE-05 needs fixed costs/access terms. MOE-06 needs independent scope/evidence references.
    item researchEvaluationProtocol : FrameworkEvaluation {
        doc /* Two contrasting EPS cases are an evaluation protocol only. Fix cases, tasks, reference answers, participants, configurations, permitted adaptations, comparison rules before execution. Include failed checks, missing data, misleading suggestions, stale evidence and clean controls. Compare burden only for correct outcomes under comparable conditions. All achieved values are unknown. Targets, acceptable errors and review thresholds remain pending stakeholder agreement and intended-use justification. */
    }

    use case <'UC01'> UC01 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers establish and compare EPS mission concepts against agreed stakeholder expectations and mission constraints. */ }
        doc /* Establish a feasible EPS mission concept. Enterprise participants develop concepts, initial ConOps and feasibility evidence for stakeholder and MCR assessment. */
    }
    use case <'UC02'> UC02 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor reviewers : IndependentReviewer;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers derive, allocate and validate EPS and component requirements and interfaces from the mission concept and spacecraft requirements. */ }
        doc /* Define and validate EPS requirements and interfaces. Enterprise participants prepare consistent requirements, criteria and interfaces for stakeholder and SRR assessment. UC02 is reused for requirement refinement through detailed design. */
    }
    use case <'UC03'> UC03 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor reviewers : IndependentReviewer;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers compare and size EPS architectures, justify the preliminary design against applicable requirements and resolve subsystem incompatibilities within agreed resources and risk. */ }
        doc /* Justify the EPS preliminary design. Enterprise participants mature trades, allocation and preliminary design evidence through MDR/SDR and PDR. No hardware qualification is claimed. */
    }
    use case <'UC04'> UC04 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor reviewers : IndependentReviewer;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers complete detailed EPS design models and declared host-executed control/interface software, assess them through MIL/SIL and prepare scoped integration readiness evidence. */ }
        doc /* Complete detailed EPS models and software. Enterprise participants prepare detailed design for scoped CDR, complete declared software and models, and prepare applicable MIL/SIL evidence and integration configurations/procedures for end-of-C SIR. */
    }
    use case <'UC05'> UC05 {
        subject enterprise : ToBe::EPSEngineeringEnterprise;
        actor stakeholders : MissionStakeholder;
        actor reviewers : IndependentReviewer;
        actor authority : TechnicalReviewAuthority;
        objective { doc /* Engineers control changes, repeat affected analyses and V&V, and submit coherent phase baselines for authorized review decisions. */ }
        doc /* Maintain and review coherent phase baselines. Crosscutting enterprise work preserves configuration, evidence currency, decision rationale and finding dispositions across phases and changes. Package preparation is distinct from accepted review decisions. */
    }
    #proposedDerivation dependency refine_UC01_MR01 from UC01 to MR_01;
    #proposedDerivation dependency refine_UC02_MR02 from UC02 to MR_02;
    #proposedDerivation dependency refine_UC02_MR03 from UC02 to MR_03;
    #proposedDerivation dependency refine_UC02_MR04 from UC02 to MR_04;
    #proposedDerivation dependency refine_UC02_MR05 from UC02 to MR_05;
    #proposedDerivation dependency refine_UC03_MR03 from UC03 to MR_03;
    #proposedDerivation dependency refine_UC03_MR04 from UC03 to MR_04;
    #proposedDerivation dependency refine_UC04_MR05 from UC04 to MR_05;
    #proposedDerivation dependency refine_UC04_MR06 from UC04 to MR_06;
    #proposedDerivation dependency refine_UC05_MR01 from UC05 to MR_01;
    #proposedDerivation dependency refine_UC05_MR02 from UC05 to MR_02;
    #proposedDerivation dependency refine_UC05_MR03 from UC05 to MR_03;
    #proposedDerivation dependency refine_UC05_MR04 from UC05 to MR_04;
    #proposedDerivation dependency refine_UC05_MR05 from UC05 to MR_05;
    #proposedDerivation dependency refine_UC05_MR06 from UC05 to MR_06;
}
