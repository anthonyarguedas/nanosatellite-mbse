// Detailed external interface specifications and high-level typed exchange bundles.
package BoundaryViews {
    private import FrameworkDomain::*;
    private import ScalarValues::String;

    doc /* OOSEM 17.3.3: the system context specifies the framework as a black box
         * interacting with external actors through typed input/output flows.
         * Each bundle below groups existing directed P01..P06 features for the
         * report. It adds no transport, tool-specific schema or implementation
         * capability. The exact 19 flows remain inside Context::IF01..IF06.
         * FrameworkDomain retains the original payload and port definitions.
         */

    item def 'Needs/criteria' :> Submission01 {
        doc /* Needs, changes, requirements, mission assumptions, criteria and
             * decisions supplied by PM, SE, EPS and non-EPS engineers. */
    }
    item def 'Models/justification' :> Response01 {
        doc /* Guidance, templates, models, traces, impacts, BOM/cost and
             * justification returned to the engineering team. */
    }
    item def 'Facts/methods' :> Submission02 {
        doc /* Supplier datasheets, part identities, quotes/prices, evidence,
             * standards, literature methods and tailoring rules. */
    }
    item def 'Catalogue/assumptions' :> Response02 {
        doc /* Source-linked catalogue, registered assumptions and status.
             * This does not transfer supplier qualification authority. */
    }
    item def 'Plans/inputs' :> EngineeringArtifact {
        ref item inputs : Submission03;
        ref item plan : ScenarioAnalysisPlan;
        doc /* Framework outputs P03.submission and P03.executionPlan:
             * controlled inputs, run contract and analysis plan. */
    }
    item def 'Results/limits' :> EngineeringArtifact {
        ref item context : Response03;
        ref item rawResults : RunPackage;
        doc /* Framework inputs P03.response and P03.rawResult: raw results,
             * environment identity, runtime, applicability and limitations. */
    }
    item def 'Definitions/builds/resources' :> EngineeringArtifact {
        ref item definitions : Submission04;
        ref item implementation : SoftwareArtifact;
        ref item resourceEvidence : RunPackage;
        doc /* Framework inputs P04.submission, implementationArtifact and
             * resourceEvidence: dictionaries, commands/modes, target profiles,
             * builds and processor, memory, timing and power evidence. */
    }
    item def 'Contract/mappings' :> EngineeringArtifact {
        ref item findings : Response04;
        ref item contract : ArchitectureServiceContract;
        doc /* Framework outputs P04.response and sharedContract: checked
             * flight/ground mappings, integration findings and shared contract. */
    }
    item def 'Profiles/observations' :> EngineeringArtifact {
        ref item profiles : Submission05;
        ref item observations : ObservationPackage;
        doc /* Framework inputs P05.submission and suppliedObservations:
             * equipment/DUT profiles, safety dispositions, timestamped raw
             * observations, calibration data, invalid samples and masks. */
    }
    item def 'Procedure/feedback' :> EngineeringArtifact {
        ref item feedback : Response05;
        ref item procedure : VerificationSpecification;
        doc /* Framework outputs P05.response and plannedProcedure:
             * verification procedure/capture proposal, quality checks and
             * proposed update records, not facility authorization. */
    }
    item def 'Requests/findings' :> Submission06 {
        doc /* Named analyses, review/reproduction requests, reference answers
             * and findings supplied by reviewers, researchers or reproducers. */
    }
    item def 'Packages/replay' :> Response06 {
        doc /* Reconstructable packages, replay verdicts, views, measured
             * evaluation observations and retained dispositions. */
    }

    metadata def ExternalInterfaceSpecification {
        attribute identifier : String;
        attribute actors : String;
        attribute responsibleComponents : String;
        attribute receivingChecks : String;
        attribute failureBehavior : String;
        attribute externalAuthority : String;
    }

    @ExternalInterfaceSpecification about FrameworkContext::Context::IF01 {
        identifier = "IF-01";
        actors = "Project manager, systems engineer, EPS and non-EPS engineers; roles may share people";
        responsibleComponents = "L09 case workspace/technical review; L02 requirements/decision governance";
        receivingChecks = "Check case scope, identity and unresolved criteria";
        failureBehavior = "Incomplete submissions remain draft; reject/quarantine incompatible transfers and preserve the accepted baseline";
        externalAuthority = "Engineers authorize mission decisions, changes and EPS acceptance criteria";
    }
    @ExternalInterfaceSpecification about FrameworkContext::Context::IF02 {
        identifier = "IF-02";
        actors = "Suppliers, standards owners and literature sources";
        responsibleComponents = "L01 guidance/knowledge; L04 component/lifecycle characterization";
        receivingChecks = "Check source, revision, units and applicability";
        failureBehavior = "Unsupported facts stay unknown; rejected submissions and findings are retained";
        externalAuthority = "Supplier qualification and source truth remain external";
    }
    @ExternalInterfaceSpecification about FrameworkContext::Context::IF03 {
        identifier = "IF-03";
        actors = "Declared electrical, thermal, EMC, CAD, orbit/attitude, battery and RAM tools or their operators";
        responsibleComponents = "L05 analysis orchestration; L03 architecture/service contracts; L08 information/configuration authority";
        receivingChecks = "Check supported tool/version profiles, applicability and transfer integrity";
        failureBehavior = "Preserve failed runs and unsupported/lossy mappings; no unsupported claim receives unqualified support";
        externalAuthority = "External tools/operators execute declared analyses; execution success is not a verification verdict";
    }
    @ExternalInterfaceSpecification about FrameworkContext::Context::IF04 {
        identifier = "IF-04";
        actors = "Flight/ground contributors and declared cFS/F-Prime build/configuration environments";
        responsibleComponents = "L03 architecture/service contracts";
        receivingChecks = "Check versions, typed-connection/message semantics and target resource evidence";
        failureBehavior = "Missing implementation or target evidence remains unresolved; preserve rejected and unsupported mappings";
        externalAuthority = "Mission functionality remains an engineered artifact; contributors own implementation and flight qualification is not presumed";
    }
    @ExternalInterfaceSpecification about FrameworkContext::Context::IF05 {
        identifier = "IF-05";
        actors = "Testing facility technician, facility safety authority and later instruments/DUTs";
        responsibleComponents = "L07 verification specification/safety; L06 model credibility/observation reconciliation";
        receivingChecks = "L07 checks safety/procedure completeness; L06 checks clocks, channels, completeness and validity";
        failureBehavior = "Preserve raw/invalid samples and masks; incomplete readiness remains blocked";
        externalAuthority = "The facility alone authorizes physical work and owns feasibility, safety approval and execution";
    }
    @ExternalInterfaceSpecification about FrameworkContext::Context::IF06 {
        identifier = "IF-06";
        actors = "Reviewer, researcher or reproducer; these may be separate roles held by mission-team members";
        responsibleComponents = "L09 case workspace/technical review; L05 analysis orchestration";
        receivingChecks = "Identify the review subject, dependencies, comparison rule and replay tolerance";
        failureBehavior = "Missing dependencies and contested findings remain explicit; preserve findings and dispositions";
        externalAuthority = "Reviewer outcomes, study governance and project/research-deliverable assessment remain separate authorities";
    }
}
