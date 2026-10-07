// Shared vocabulary, preserved as-is roles and separate proposed to-be context.
// TODO: Re-derive downstream interfaces/functions and replace the old facility context.
package FrameworkDomain {
    private import ScalarValues::*;

    metadata def SourceRecord {
        attribute identifier : String;
        attribute sourceText : String;
        attribute sourceLocator : String;
        attribute status : String;
        attribute citationRecord : String;
    }
    metadata def sourceTrace;
    metadata def proposedDerivation;
    metadata def qualitativeContribution;
    metadata def aliasReference;
    metadata def primaryResponsibility;
    metadata def supportingResponsibility;
    metadata def InterfaceControl {
        attribute owner : String;
        attribute validation : String;
        attribute failureBehavior : String;
    }

    // Existing role definitions remain available for the unchanged concern model.
    part def Person;
    part def Role { ref part occupant : Person [0..1]; }
    part def ProjectManager :> Role;
    part def SystemsEngineer :> Role;
    part def EPSEngineer :> Role;
    part def NonEPSEngineer :> Role;
    part def TestingFacilityTechnician :> Role;
    part def EngineeringEnterprise;
    part def EPSHardware;
    part def FlightSoftware;
    part def GroundSoftware;
    part def ResearchDeliverables;
    part def Engineers {
        ref part people : Person [0..*];
        ref part projectManager : ProjectManager [0..*];
        ref part systemsEngineer : SystemsEngineer [0..*];
        ref part epsEngineer : EPSEngineer [0..*];
        ref part nonEpsEngineer : NonEPSEngineer [0..*];
        doc /* Roles remain distinct. Shared occupants are permitted. No staffing or named people are asserted. */
    }
    part def MissionStakeholder :> Role;
    part def IndependentReviewer :> Role;
    part def TechnicalReviewAuthority :> Role;

    item def EngineeringArtifact {
        attribute identifier : String;
        attribute revision : String;
        attribute subjectKind : String;
        attribute producer : String;
        attribute sourceLocator : String;
        attribute status : String;
    }
    item def EPSModelArtifact :> EngineeringArtifact;
    item def SoftwareArtifact :> EngineeringArtifact {
        doc /* Declared host-executed control/interface code is a scoped EPS product. Its presence establishes no target processor or flight qualification. */
    }
    item def VerificationSpecification :> EngineeringArtifact;
    item def BaselineManifest :> EngineeringArtifact;
    item def NeedRequirementDecision :> EngineeringArtifact;
    item def ArchitectureServiceContract :> EngineeringArtifact {
        doc /* Compatibility name for an interface specification. No physical execution or target deployment obligation is implied. */
    }
    item def ComponentCharacterization :> EngineeringArtifact;
    item def BOMCostRAM :> EngineeringArtifact;
    item def ScenarioAnalysisPlan :> EngineeringArtifact;
    item def RunPackage :> EngineeringArtifact;
    item def ModelCredibility :> EngineeringArtifact;
    item def ObservationPackage :> EngineeringArtifact {
        doc /* Identified supplied reference data or simulation observations. Acquisition from physical hardware is outside the proposed enterprise. */
    }
    item def KnowledgeCaseReview :> EngineeringArtifact;
    item def FrameworkEvaluation :> EngineeringArtifact;

    // Structured values use explicit fixed units. No measured or target value is assigned.
    // Effort, elapsed time, framework cost and EPS cost remain distinct data types.
    attribute def ActiveEffort { attribute personHours : Real; }
    attribute def ElapsedTime { attribute hours : Real; }
    attribute def FrameworkUsageCost {
        attribute canadianDollars : Real;
        attribute declaredPeriod : String;
        attribute priceDate : String;
    }
    attribute def EPSAcquisitionEstimate {
        attribute canadianDollars : Real;
        attribute estimateScope : String;
        attribute priceDate : String;
        doc /* Sourced estimate only. Hardware procurement is excluded. */
    }
    attribute def VoltageResidual { attribute volts : Real; }
    attribute def TemperatureResidual { attribute kelvinDifference : Real; }
    attribute def EnergyResidual { attribute wattHours : Real; }
    attribute def BatteryHealthResidual { attribute percentagePoints : Real; }
    attribute def CoverageFraction {
        attribute coveredCount : Integer;
        attribute applicableCount : Integer;
        doc /* Report numerator and denominator for a declared reference set. An empty set gives no coverage claim. */
    }
    item def EffectivenessMeasure :> FrameworkEvaluation {
        attribute targetStatus : String = "pending stakeholder agreement and intended-use justification";
        attribute achievedStatus : String = "unknown, empirical evaluation pending";
        attribute observationBasis : String;
    }

    enum def ReviewDisposition {
        enum accepted;
        enum conditional;
        enum progressionBlocked;
    }
    item def TechnicalReviewDecision :> EngineeringArtifact {
        attribute disposition : ReviewDisposition;
        attribute authority : String;
        attribute successCriteriaRevision : String;
        attribute rationale : String;
        attribute conditionsActionsOwnersDates : String [0..*];
        doc /* A future decision against agreed scoped criteria. Blocking findings prevent progression. Conditional decisions identify limits, closure actions, owners and dates. No decisions are instantiated by this specification. */
    }
    item def PhaseBaseline :> BaselineManifest {
        attribute phaseName : String;
        ref item products : EngineeringArtifact [0..*];
        ref item decisions : TechnicalReviewDecision [0..*];
        doc /* Requirements, interfaces, design, analysis and V&V evidence remain coherent after authorized changes and repeated affected checks. Current evidence identifies its configuration and limitations. Superseded evidence cannot support current compliance. A prepared package alone establishes no acceptance. */
    }
    item def TechnicalReviewPackage :> EngineeringArtifact {
        ref item baseline : PhaseBaseline;
        attribute preparationStatus : String;
        doc /* Review entrance product. Preparation status is separate from the authorized review decision and from the current specification status. */
    }

    // Temporary signatures preserve downstream imports while OOSEM derivation is revised.
    // They impose no tool choice. IF-05 has no port on the proposed framework.
    item def Submission01 :> EngineeringArtifact;
    item def Response01 :> EngineeringArtifact;
    port def P01 { in item submission : Submission01; out item response : Response01; }
    interface def <'IF-01'> I01 { end client : ~P01; end framework : P01; }
    item def Submission02 :> EngineeringArtifact;
    item def Response02 :> EngineeringArtifact;
    port def P02 { in item submission : Submission02; out item response : Response02; }
    interface def <'IF-02'> I02 { end client : ~P02; end framework : P02; }
    item def Submission03 :> EngineeringArtifact;
    item def Response03 :> EngineeringArtifact;
    port def P03 {
        out item submission : Submission03;
        in item response : Response03;
        out item executionPlan : ScenarioAnalysisPlan;
        in item rawResult : RunPackage;
    }
    interface def <'IF-03'> I03 { end client : ~P03; end framework : P03; }
    item def Submission04 :> EngineeringArtifact;
    item def Response04 :> EngineeringArtifact;
    port def P04 {
        in item submission : Submission04;
        out item response : Response04;
        out item sharedContract : ArchitectureServiceContract;
        in item implementationArtifact : SoftwareArtifact;
        in item resourceEvidence : RunPackage;
    }
    interface def <'IF-04'> I04 {
        end client : ~P04;
        end framework : P04;
        doc /* Model and declared host-software exchange only. No PIL, HIL or target processor timing/power qualification. */
    }
    item def Submission05 :> EngineeringArtifact;
    item def Response05 :> EngineeringArtifact;
    port def P05 {
        in item submission : Submission05;
        out item response : Response05;
        out item plannedProcedure : VerificationSpecification;
        in item suppliedObservations : ObservationPackage;
    }
    interface def <'IF-05'> I05 {
        end client : ~P05;
        end framework : P05;
        doc /* Obsolete facility-exchange signature retained solely for downstream imports. No instance or facility obligation belongs to the revised to-be domain. */
    }
    item def Submission06 :> EngineeringArtifact;
    item def Response06 :> EngineeringArtifact;
    port def P06 { in item submission : Submission06; out item response : Response06; }
    interface def <'IF-06'> I06 { end client : ~P06; end framework : P06; }

    // Temporary function signatures for existing allocations, pending scenario derivation.
    action def F01 { doc /* Guide engineers and reuse a controlled engineering baseline. */ }
    action def F02 { doc /* Specify and revise requirements, criteria, decisions and dependencies. */ }
    action def F03 { doc /* Compare modeled EPS designs with sourced component and resource evidence. */ }
    action def F04 {
        in item observations : ObservationPackage [0..*];
        doc /* Execute and reconstruct analyses within declared model applicability. */
    }
    action def F05 { doc /* Define and check EPS modeled interfaces and declared host-executed software. */ }
    action def F06 {
        in item analyticalResults : RunPackage [0..*];
        doc /* Specify scoped EPS phase-product V&V and assess applicable model/software results. */
    }
    action def F07 { doc /* Control changes, evidence and coherent successor baselines. */ }
    action def F08 { doc /* Communicate justified decisions and retain reviewed knowledge. */ }
    part def Framework {
        doc /* OOSEM system of interest: the proposed EPS engineering framework. EPS phase products follow the NASA reference lifecycle from Pre-Phase A through adapted C. Models of hardware alternatives and declared host-executed control/interface software remain in scope, with analysis, MIL and SIL. No EPS hardware is made or operated. Physical prototyping, fabrication, procurement, testing, PIL, HIL, target processor timing/power qualification and Phase D are excluded. Engineers retain engineering decisions. Review authority is distinct from package preparation. Implementation and empirical framework V&V are pending. */
        port p01 : P01;
        port p02 : P02;
        port p03 : P03;
        port p04 : P04;
        port p06 : P06;
        perform action f01 : F01;
        perform action f02 : F02;
        perform action f03 : F03;
        perform action f04 : F04;
        perform action f05 : F05;
        perform action f06 : F06;
        perform action f07 : F07;
        perform action f08 : F08;
        ref item controlledBaseline : BaselineManifest;
    }

    package AsIs {
        part def TestingFacility;
        part def OperationalDomain {
            ref part enterprise : EngineeringEnterprise [0..1];
            ref part engineers : Engineers [0..1];
            ref part technician : TestingFacilityTechnician [0..*];
            ref part facility : TestingFacility [0..*];
            ref part hardware : EPSHardware [0..*];
            ref part flightSoftware : FlightSoftware [0..*];
            ref part groundSoftware : GroundSoftware [0..*];
            doc /* Context vocabulary for the preserved observations and concerns. References assert no staffing, available equipment or accepted lifecycle. Technician and facility concerns remain solely as-is. */
        }
        part domain : OperationalDomain;
    }
    package ToBe {
        // Current black-box specification. Shared legacy types remain available
        // for downstream architecture migration without adding a physical port.
        part def FutureFramework :> FrameworkDomain::Framework {
            port :>> p01 : BoundaryViews::EngineeringUsePort;
            port :>> p02 : BoundaryViews::KnowledgePort;
            port :>> p03 : BoundaryViews::AnalysisPort;
            port :>> p04 : BoundaryViews::HostSoftwarePort;
            port :>> p06 : BoundaryViews::TechnicalReviewPort;
            perform action :>> f01 : BoundaryViews::F01;
            perform action :>> f02 : BoundaryViews::F02;
            perform action :>> f03 : BoundaryViews::F03;
            perform action :>> f04 : BoundaryViews::F04;
            perform action :>> f05 : BoundaryViews::F05;
            perform action :>> f06 : BoundaryViews::F06;
            perform action :>> f07 : BoundaryViews::F07;
            perform action :>> f08 : BoundaryViews::F08;
            ref item requirementRecords : BoundaryViews::RequirementRecord [0..*];
            ref item designModels : BoundaryViews::DesignConfiguration [0..*];
            ref item sourceRecords : BoundaryViews::SourceSubmission [0..*];
            ref item assistanceRecords : BoundaryViews::AssistanceReport [0..*];
            ref item runRecords : BoundaryViews::AnalysisResult [0..*];
            ref item reviewRecords : BoundaryViews::ReviewPackage [0..*];
            ref item authorizedDecisions : EngineeringArtifact [0..*];
            exhibit state baselineControl : ScenarioViews::BaselineControl;
            exhibit state guidanceControl : ScenarioViews::GuidanceControl;
        }
        part def ModelSoftwareAnalysisEnvironment {
            doc /* Software environments for model construction, analysis, MIL and SIL. Physical EPS components and target processors are not executing participants. */
        }
        part def HostSoftwareDevelopmentEnvironment;
        part def EPSEngineeringEnterprise :> EngineeringEnterprise {
            part engineers : Engineers;
            part framework : FutureFramework;
            ref part analysisEnvironments : ModelSoftwareAnalysisEnvironment [0..*];
            ref part codingEnvironments : HostSoftwareDevelopmentEnvironment [0..*];
            ref item phaseProducts : EngineeringArtifact [0..*];
            ref item baselines : PhaseBaseline [0..*];
            doc /* Engineers, framework and supporting model/software environments collaborate to achieve MR-01--05. Hardware alternatives are engineered representations. There is no technician, testing facility, physical safety authority or executing EPS hardware. */
        }
        part def OperationalDomain {
            part enterprise : EPSEngineeringEnterprise;
            ref part missionStakeholders : MissionStakeholder [0..*];
            ref part reviewers : IndependentReviewer [0..*];
            ref part reviewAuthority : TechnicalReviewAuthority [0..*];
            ref item sourceKnowledge : KnowledgeCaseReview [0..*];
            ref item suppliedReferenceData : ObservationPackage [0..*];
            doc /* Mission stakeholders provide expectations and constraints. Reviewers assess justification. The designated technical review authority decides progression. Role occupants may overlap while decision responsibilities remain distinct. Source knowledge and supplied reference data introduce no physical-execution obligation. */
        }
        part domain : OperationalDomain;
    }
}
