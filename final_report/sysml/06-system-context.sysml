// System context: framework, external actors, interfaces and typed input/output flows.
package FrameworkContext {
    private import FrameworkDomain::*;
    private import BoundaryViews::*;

    part def Users :> Engineers { port p : ~P01; }
    part def Sources { port p : ~P02; }
    part def Engines { port p : ~P03; }
    part def Software {
        port p : ~P04;
        ref part flightArtifact : FlightSoftware [0..*];
        ref part groundArtifact : GroundSoftware [0..*];
    }
    part def Facility {
        port p : ~P05;
        ref part technician : TestingFacilityTechnician [0..*];
        ref part dut : EPSHardware [0..*];
        doc /* Technician and physical DUT remain external. References identify
             * possible roles, not asserted staffing or available hardware. */
    }
    part def Reviewers { port p : ~P06; }

    part def Context {
        doc /* Every transfer retains identifier/source revision, case/baseline,
             * producer, dependency revisions, quantity/unit/polarity meanings,
             * time/mode interpretation, provenance and status under a declared
             * versioned profile. Reject or quarantine incompatible transfers
             * before registration; retain raw submissions, findings and the
             * previously accepted baseline. Registration checks do not confer
             * engineering decision, supplier qualification, facility safety
             * authorization or project-assessment authority. */
        part framework : Framework;
        part engineers : Users;
        part sources : Sources;
        part tools : Engines;
        alias engines for tools;
        part software : Software;
        part facility : Facility;
        part reviewers : Reviewers;

        interface IF01 : I01 connect engineers.p to framework.p01 {
            flow needs of Submission01 from client.submission to framework.submission;
            flow guidance of Response01 from framework.response to client.response;
        }
        interface IF02 : I02 connect sources.p to framework.p02 {
            flow facts of Submission02 from client.submission to framework.submission;
            flow registration of Response02 from framework.response to client.response;
        }
        interface IF03 : I03 connect engines.p to framework.p03 {
            flow inputs of Submission03 from framework.submission to client.submission;
            flow plan of ScenarioAnalysisPlan from framework.executionPlan to client.executionPlan;
            flow runContext of Response03 from client.response to framework.response;
            flow results of RunPackage from client.rawResult to framework.rawResult;
        }
        interface IF04 : I04 connect software.p to framework.p04 {
            flow definitions of Submission04 from client.submission to framework.submission;
            flow findings of Response04 from framework.response to client.response;
            flow sharedContract of ArchitectureServiceContract from framework.sharedContract to client.sharedContract;
            flow build of SoftwareArtifact from client.implementationArtifact to framework.implementationArtifact;
            flow resources of RunPackage from client.resourceEvidence to framework.resourceEvidence;
        }
        interface IF05 : I05 connect facility.p to framework.p05 {
            flow profiles of Submission05 from client.submission to framework.submission;
            flow feedback of Response05 from framework.response to client.response;
            flow procedure of VerificationSpecification from framework.plannedProcedure to client.plannedProcedure;
            flow observations of ObservationPackage from client.suppliedObservations to framework.suppliedObservations;
        }
        interface IF06 : I06 connect reviewers.p to framework.p06 {
            flow requests of Submission06 from client.submission to framework.submission;
            flow reviewPackage of Response06 from framework.response to client.response;
        }

        // High-level bundles use the same source/receiving ports. The report
        // exposes these summaries; each exact typed flow remains in its IF.
        flow 'IF-01' of 'Needs/criteria' from engineers.p to framework.p01;
        flow of 'Models/justification' from framework.p01 to engineers.p;
        flow 'IF-02' of 'Facts/methods' from sources.p to framework.p02;
        flow of 'Catalogue/assumptions' from framework.p02 to sources.p;
        flow of 'Plans/inputs' from framework.p03 to engines.p;
        flow 'IF-03' of 'Results/limits' from engines.p to framework.p03;
        flow 'IF-04' of 'Definitions/builds/resources' from software.p to framework.p04;
        flow of 'Contract/mappings' from framework.p04 to software.p;
        flow 'IF-05' of 'Profiles/observations' from facility.p to framework.p05;
        flow of 'Procedure/feedback' from framework.p05 to facility.p;
        flow 'IF-06' of 'Requests/findings' from reviewers.p to framework.p06;
        flow of 'Packages/replay' from framework.p06 to reviewers.p;
    }
    part context : Context;
}
