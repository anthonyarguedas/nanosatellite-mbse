// Comparison vocabulary. Allocations express intended realization responsibility only.
package PhysicalVocabulary {
private import ScalarValues::String;
private import FrameworkDomain::*;
metadata def PhysicalRecord {
    attribute identifier : String;
    attribute recordJSON : String;
    attribute status : String;
}
metadata def intendedRealization;
metadata def executionHost;
metadata def storageCustody;
metadata def procedurePerformer;
metadata def plannedVerification;
metadata def fieldAuthority;
part def SoftwareResource;
part def CompositeResource { ref item controlledArtifacts : EngineeringArtifact [0..*]; }
part def HostResource;
part def ResponsibilityPartition;
item def DataResource :> EngineeringArtifact;
action def OperatingProcedure;
part def ExternalFacility { ref part dut : EPSHardware [0..*]; ref part technician : TestingFacilityTechnician [0..*]; }
port def SyncPort { inout item baseline : BaselineManifest; inout item change : NeedRequirementDecision; }
interface def Sync { end a : SyncPort; end b : SyncPort; }
port def ArchivePort { inout item baseline : BaselineManifest; inout item result : RunPackage; }
interface def Archive { end a : ArchivePort; end b : ArchivePort; }
part def CPU :> HostResource { port api : SyncPort; port files : ArchivePort; port IF03 : P03; }
part def SaaS :> HostResource { port api : SyncPort; }
part def Store :> HostResource { port files : ArchivePort; }
part def External :> HostResource { port IF03 : ~P03; }
interface def Discipline { end framework : P03; end provider : ~P03; }
}
