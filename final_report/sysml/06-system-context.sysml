// Controlled report model. Trace records are published in final_report/traceability/.
package FrameworkContext {
private import FrameworkDomain::*;
part def Users :> Engineers { port p : ~P01; }
part def Sources { port p : ~P02;
}
part def Engines { port p : ~P03;
}
part def Software { port p : ~P04;
ref part flightArtifact : FlightSoftware [0..*]; ref part groundArtifact : GroundSoftware [0..*];
}
part def Facility { port p : ~P05;
ref part technician : TestingFacilityTechnician [0..*]; ref part dut : EPSHardware [0..*]; doc /* Technician and physical DUT remain external. References describe possible interaction roles and do not assert actual staffing or available hardware. */
}
part def Reviewers { port p : ~P06;
}
part def Context {
part framework : Framework;
part engineers : Users;
interface IF01 : I01 connect engineers.p to framework.p01;
part sources : Sources;
interface IF02 : I02 connect sources.p to framework.p02;
part engines : Engines;
interface IF03 : I03 connect engines.p to framework.p03;
part software : Software;
interface IF04 : I04 connect software.p to framework.p04;
part facility : Facility;
interface IF05 : I05 connect facility.p to framework.p05;
part reviewers : Reviewers;
interface IF06 : I06 connect reviewers.p to framework.p06;
}
part context : Context;

}
