// Proposed framework specifications and trace relationships.
// Source locators retain historical provenance.
package FrameworkDomain {

private import ScalarValues::String;
private import Base::Anything;
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
item def EngineeringArtifact {
    attribute identifier : String;
    attribute revision : String;
    attribute subjectKind : String;
    attribute producer : String;
    attribute sourceLocator : String;
    attribute status : String;
}
item def EPSModelArtifact :> EngineeringArtifact;
item def SoftwareArtifact :> EngineeringArtifact;
item def VerificationSpecification :> EngineeringArtifact;
item def BaselineManifest :> EngineeringArtifact;
item def NeedRequirementDecision :> EngineeringArtifact;
item def ArchitectureServiceContract :> EngineeringArtifact;
item def ComponentCharacterization :> EngineeringArtifact;
item def BOMCostRAM :> EngineeringArtifact;
item def ScenarioAnalysisPlan :> EngineeringArtifact;
item def RunPackage :> EngineeringArtifact;
item def ModelCredibility :> EngineeringArtifact;
item def ObservationPackage :> EngineeringArtifact;
item def KnowledgeCaseReview :> EngineeringArtifact;
item def FrameworkEvaluation :> EngineeringArtifact;
part def Engineers {
    ref part people : Person [0..*];
    ref part projectManager : ProjectManager [0..*];
    ref part systemsEngineer : SystemsEngineer [0..*];
    ref part epsEngineer : EPSEngineer [0..*];
    ref part nonEpsEngineer : NonEPSEngineer [0..*];
    doc /* Roles remain distinct. Shared occupants are permitted. No staffing or named people are asserted. */
}
item def Submission01 :> EngineeringArtifact { doc /* Needs, requirements, design revisions, candidate requests, mission assumptions and decisions → templates, models, traces, impact, BOM/cost and justification packages */ }
item def Response01 :> EngineeringArtifact;
port def P01 { in item submission : Submission01; out item response : Response01; }
interface def <'IF-01'> I01 { end client : ~P01; end framework : P01; doc /* Engineering use. Engineers own the mission decisions and EPS acceptance criteria. The framework captures and checks their records. */ }
@InterfaceControl { owner = "L09,L02"; validation = "Check declared identity, schema, quantity, time, mapping and provenance profile. Applicability is a separate decision."; failureBehavior = "Reject or quarantine incompatible submissions, retain findings, preserve the accepted baseline, and report unsupported profiles."; }
@SourceRecord { identifier = "IF-01"; sourceText = "Engineering use | Project Manager, Systems Engineer, EPS Engineer, Non-EPS Engineer. Roles may overlap. | Needs, requirements, design revisions, candidate requests, mission assumptions and decisions → templates, models, traces, impact, BOM/cost and justification packages"; sourceLocator = "concerns/baseline-addendum.md:External actors and interface families"; status = "proposed contract"; citationRecord = ""; }
item def Submission02 :> EngineeringArtifact { doc /* Datasheets, part identities, prices, evidence, methods and tailoring rules → source-linked catalogue and registered assumptions */ }
item def Response02 :> EngineeringArtifact;
port def P02 { in item submission : Submission02; out item response : Response02; }
interface def <'IF-02'> I02 { end client : ~P02; end framework : P02; doc /* Source knowledge and components. Supplier qualification and source truth are external. Unsupported component characteristics remain visible. */ }
@InterfaceControl { owner = "L01,L04,L08"; validation = "Check declared identity, schema, quantity, time, mapping and provenance profile. Applicability is a separate decision."; failureBehavior = "Reject or quarantine incompatible submissions, retain findings, preserve the accepted baseline, and report unsupported profiles."; }
@SourceRecord { identifier = "IF-02"; sourceText = "Source knowledge and components | Suppliers, standards owners and literature sources | Datasheets, part identities, prices, evidence, methods and tailoring rules → source-linked catalogue and registered assumptions"; sourceLocator = "concerns/baseline-addendum.md:External actors and interface families"; status = "proposed contract"; citationRecord = ""; }
item def Submission03 :> EngineeringArtifact { doc /* Controlled inputs and run contract → raw results, environment identity, runtime and limitations */ }
item def Response03 :> EngineeringArtifact;
port def P03 { out item submission : Submission03; in item response : Response03; out item executionPlan : ScenarioAnalysisPlan; in item rawResult : RunPackage; }
interface def <'IF-03'> I03 { end client : ~P03; end framework : P03; doc /* Discipline execution. A candidate may include the tool as a physical component or use an external checked exchange. The logical contract is unchanged. */ }
@InterfaceControl { owner = "L05,L06,L08"; validation = "Check declared identity, schema, quantity, time, mapping and provenance profile. Applicability is a separate decision."; failureBehavior = "Reject or quarantine incompatible submissions, retain findings, preserve the accepted baseline, and report unsupported profiles."; }
@SourceRecord { identifier = "IF-03"; sourceText = "Discipline execution | Electrical, thermal, EMC, CAD, orbit/attitude, battery and RAM tools or their operators | Controlled inputs and run contract → raw results, environment identity, runtime and limitations"; sourceLocator = "concerns/baseline-addendum.md:External actors and interface families"; status = "proposed contract"; citationRecord = ""; }
item def Submission04 :> EngineeringArtifact { doc /* EPS dictionaries, hardware interfaces, command/mode behavior and target profile → checked mappings, integration findings and resource evidence */ }
item def Response04 :> EngineeringArtifact;
port def P04 { in item submission : Submission04; out item response : Response04; out item sharedContract : ArchitectureServiceContract; in item implementationArtifact : SoftwareArtifact; in item resourceEvidence : RunPackage; }
interface def <'IF-04'> I04 { end client : ~P04; end framework : P04; doc /* EPS software engineering. Flight/ground mission-specific implementation is an engineered artifact. No automatic full software implementation or flight qualification is presumed. */ }
@InterfaceControl { owner = "L03,L05,L08"; validation = "Check declared identity, schema, quantity, time, mapping and provenance profile. Applicability is a separate decision."; failureBehavior = "Reject or quarantine incompatible submissions, retain findings, preserve the accepted baseline, and report unsupported profiles."; }
@SourceRecord { identifier = "IF-04"; sourceText = "EPS software engineering | Flight and ground software engineers and cFS/F-Prime build/configuration environments | EPS dictionaries, hardware interfaces, command/mode behavior and target profile → checked mappings, integration findings and resource evidence"; sourceLocator = "concerns/baseline-addendum.md:External actors and interface families"; status = "proposed contract"; citationRecord = ""; }
item def Submission05 :> EngineeringArtifact { doc /* Proposal, equipment/DUT profile, safety review, timestamped observations and calibration data → procedure/evidence contract, quality checks and update records */ }
item def Response05 :> EngineeringArtifact;
port def P05 { in item submission : Submission05; out item response : Response05; out item plannedProcedure : VerificationSpecification; in item suppliedObservations : ObservationPackage; }
interface def <'IF-05'> I05 { end client : ~P05; end framework : P05; doc /* Facility planning and supplied evidence. The facility owns feasibility, safety approval and physical execution. This project covers planning, virtual fixtures and supplied data exchange. */ }
@InterfaceControl { owner = "L07,L06,L08"; validation = "Check declared identity, schema, quantity, time, mapping and provenance profile. Applicability is a separate decision."; failureBehavior = "Reject or quarantine incompatible submissions, retain findings, preserve the accepted baseline, and report unsupported profiles."; }
@SourceRecord { identifier = "IF-05"; sourceText = "Facility planning and supplied evidence | Testing Facility Technician, facility safety authority and future instruments/DUTs | Proposal, equipment/DUT profile, safety review, timestamped observations and calibration data → procedure/evidence contract, quality checks and update records"; sourceLocator = "concerns/baseline-addendum.md:External actors and interface families"; status = "proposed contract"; citationRecord = ""; }
item def Submission06 :> EngineeringArtifact { doc /* Named analysis, review request, reference answers and findings → reconstructable package, replay verdict, views, measured observations and dispositions */ }
item def Response06 :> EngineeringArtifact;
port def P06 { in item submission : Submission06; out item response : Response06; }
interface def <'IF-06'> I06 { end client : ~P06; end framework : P06; doc /* Independent review and evaluation. Reviewer outcome, study governance and research deliverable assessment are separate authorities. */ }
@InterfaceControl { owner = "L09,L02,L08"; validation = "Check declared identity, schema, quantity, time, mapping and provenance profile. Applicability is a separate decision."; failureBehavior = "Reject or quarantine incompatible submissions, retain findings, preserve the accepted baseline, and report unsupported profiles."; }
@SourceRecord { identifier = "IF-06"; sourceText = "Independent review and evaluation | Reviewer, researcher or reproducer. These may be people in the mission team serving a distinct role. | Named analysis, review request, reference answers and findings → reconstructable package, replay verdict, views, measured observations and dispositions"; sourceLocator = "concerns/baseline-addendum.md:External actors and interface families"; status = "proposed contract"; citationRecord = ""; }
action def F01 { doc /* Guide a user and tailor a case from a controlled reusable baseline. */ }
action def F02 { doc /* Specify and revise needs, requirements, criteria, architecture decisions, and their dependencies. */ }
action def F03 { doc /* Characterize and compare EPS component/design options with BOM, cost, RAM, and resource evidence. */ }
action def F04 {
    in item observations : ObservationPackage [0..*];
    doc /* Execute and reproduce scenario-based analyses with declared model applicability. Expected/observed comparisons consume the identified observation packages. */
}
action def F05 { doc /* Define, map, and check shared EPS hardware/flight/ground service contracts. */ }
action def F06 {
    in item analyticalResults : RunPackage [0..*];
    doc /* Specify verification and assess readiness for safe later execution. Analytical verdicts consume identified run packages and their applicable credibility records. */
}
action def F07 { doc /* Control evidence, assess change impact, and reconcile new observations. */ }
action def F08 { doc /* Communicate a justified decision and feed reviewed learning into reusable knowledge. */ }
part def Framework {
doc /* EPS engineering framework black box. Framework-owned responsibilities include authoring, models, analysis orchestration, evidence, contracts, verification planning, configuration and views. EPS hardware and flight/ground software are engineered artifacts. Facility authorization, physical execution and flight operation remain external. Baseline custody belongs to the framework. Specialist engines may be internal dependencies or external services in a later candidate. */
port p01 : P01;
port p02 : P02;
port p03 : P03;
port p04 : P04;
port p05 : P05;
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

}
