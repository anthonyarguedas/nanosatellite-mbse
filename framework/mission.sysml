part def Orbit {
    private import ScalarValues::*;
    attribute orbitType : String;
    attribute orbitHeight : Positive;
}
package SpaceSegment {
    part def CubeSat {
        part def SharedProcessorAndMemory;
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
            part def Actuator;
            part def Sensor;
            part sharedProcessorAndMemory : SharedProcessorAndMemory;
        }
        part def GuidanceNavigationAndControlSubsystem {
            part def Accelerometer;
            part def GNSSReceiver;
            part def Software;
            part sharedProcessorAndMemory : SharedProcessorAndMemory;
        }
        part def StructuresAndMechanismsSubsystem {
            part def ActuatedMount;
            part def DeployableMount;
            part def StaticMount;
        }
        part def ThermalSubsystem {
            part def ThermalSensor;
            part def ThermalSource;
            part def ThermalSink;
            part def ProcessorAndMemory;
            part def Software;
        }
        part def PropulsionSubsystem {
            part def PropellantStorage;
            part def PropellantControl;
            part def Thrusters;
            part def Software;
            part def ProcessorAndMemory;
        }
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