part def Orbit {
    private import ScalarValues::*;
    attribute orbitType : String;
    doc /* Circular preliminary orbit. Legacy orbitHeight retains km meaning.
     * Runtime uses altitude_km. An instance using both must keep them aligned.
     * Positive is not a ScalarValues type in the installed standard library.
     * FrameworkRequirements::OrbitPeriod and IlluminationPeriods define the
     * reusable preliminary equations. Mission usages bind their inputs here.
     */
    attribute orbitHeight : Real = altitude_km;
    attribute altitude_km : Real;
    attribute earthRadius_km : Real;
    attribute gravitationalParameter_km3_s2 : Real;
    attribute altitude : ISQ::LengthValue = altitude_km * 1000[SI::m];
    assert constraint positiveOrbitHeight { orbitHeight > 0 }
    assert constraint validCentralBody {
        earthRadius_km > 0 and gravitationalParameter_km3_s2 > 0
    }
}
package SpaceSegment {
    part def CubeSat {
        attribute modeSchedule : EPSModel::ModeSchedule[0..1];
        attribute powerAccounting : EPSModel::AccountingPlan[0..1];
        part sharedProcessorAndMemory : SharedProcessorAndMemory[0..1];
        doc /* Shared processing is optional. Bind any present subsystem shared
         * reference to this one canonical resource. Designs may use dedicated
         * processors instead. Power accounting uses disjoint covered sets.
         */
        part def SharedProcessorAndMemory :> EPSModel::ProcessorMemory;
        part def PayloadSubsystem :> EPSModel::Subsystem {
            part def Instrument :> EPSModel::Load;
            part def ProcessorAndMemory :> EPSModel::ProcessorMemory;
        }
        part def CommandAndDataHandlingSubsystem :> EPSModel::Subsystem {
            part def CommandTelemetryAndDataBus :> EPSModel::Load;
            part def ProcessorAndMemory :> EPSModel::ProcessorMemory;
        }
        part def CommunicationSubsystem :> EPSModel::Subsystem {
            part def ProcessorAndMemory :> EPSModel::ProcessorMemory;
            part def ReceiveAntennaAndEquipment :> EPSModel::Load;
            part def TransmitAntennaAndEquipment :> EPSModel::Load;
        }
        part def AttitudeDeterminationAndControlSubsystem :> EPSModel::Subsystem {
            part def Software :> EPSModel::Software;
            part def Actuator :> EPSModel::Load;
            part def Sensor :> EPSModel::Load;
            ref part sharedProcessorAndMemory : SharedProcessorAndMemory[0..1];
        }
        part def GuidanceNavigationAndControlSubsystem :> EPSModel::Subsystem {
            part def Accelerometer :> EPSModel::Load;
            part def GNSSReceiver :> EPSModel::Load;
            part def Software :> EPSModel::Software;
            ref part sharedProcessorAndMemory : SharedProcessorAndMemory[0..1];
        }
        part def StructuresAndMechanismsSubsystem :> EPSModel::Subsystem {
            part def ActuatedMount :> EPSModel::Load;
            part def DeployableMount :> EPSModel::DeploymentActuator;
            part def StaticMount :> EPSModel::HardwareComponent;
        }
        part def ThermalSubsystem :> EPSModel::Subsystem {
            part def ThermalSensor :> EPSModel::Load;
            part def ThermalSource :> EPSModel::Load;
            part def ThermalSink :> EPSModel::HardwareComponent;
            part def ProcessorAndMemory :> EPSModel::ProcessorMemory;
            part def Software :> EPSModel::Software;
        }
        part def PropulsionSubsystem :> EPSModel::Subsystem {
            part def PropellantStorage :> EPSModel::HardwareComponent;
            part def PropellantControl :> EPSModel::Load;
            part def Thrusters :> EPSModel::Load;
            part def Software :> EPSModel::Software;
            part def ProcessorAndMemory :> EPSModel::ProcessorMemory;
        }
        part def PowerSubsystem :> EPSModel::Subsystem {
            part def Batteries :> EPSModel::Battery;
            part def SolarArrays :> EPSModel::SolarArray;
            part def ProcessorAndMemory :> EPSModel::ProcessorMemory;
            part def RegulatorsAndConverters :> EPSModel::RegulatorConverter;
            part def PowerCircuitsAndSwitches :> EPSModel::PowerCircuitSwitch;
            part def Software :> EPSModel::Software;
        }
    }
}
package GroundSegment {
    part def GroundStation;
    part def PlanAndScheduleSubsystem;
    part def SpacecraftCommandSubsystem;
    part def GroundEquipmentControlSubsystem;
    part def SpaceGroundCommunicationSubsystem;
    part def MissionDataProcessingSubsystem;
    part def MissionDataDisseminationSubsystem;
    part def NetworkSubsystem;
    part def TelemetryProcessingSubsystem;
}
