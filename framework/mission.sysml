part def Orbit {
    private import ScalarValues::*;
    attribute orbitType : String;
    attribute orbitHeight : Positive;
}
package SpaceSegment {
    part def CubeSat {
        part def PayloadSubsystem {
            part def Instrument;
            part def ProcessorAndMemory;
        }
        part def CommandAndDataHandlingSubsystem {
            part def CommandTelemetryAndDataBus;
            part def ProcessorAndMemory;
        }
        part def CommunicationSubsystem {
            part def ProcessorAndMemory;
            part def ReceiveAntennaAndEquipment;
            part def TransmitAntennaAndEquipment;
        }
        part def AttitudeDeterminationAndControlSubsystem {
            part def Software;
            }
        part def GuidanceNavigationAndControlSubsystem;
        part def StructuresAndMechanismsSubsystem;
        part def ThermalSubsystem;
        part def PropulsionSubsystem;
        part def PowerSubsystem {
            part def Batteries;
            part def SolarArrays;
            part def ProcessorAndMemory;
            part def RegulatorsAndConverters;
            part def PowerCircuitsAndSwitches;
            part def Software;
        }
    }
}
package GroundSegment {
    part def PlanAndScheduleSubsystem;
    part def SpacecraftCommandSubsystem;
    part def GroundEquipmentControlSubsystem;
    part def SpaceGroundCommunicationSubsystem;
    part def MissionDataProcessingSubsystem;
    part def MissionDataDisseminationSubsystem;
    part def NetworkSubsystem;
    part def TelemetryProcessingSubsystem;
}