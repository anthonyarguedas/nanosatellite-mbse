"""Resolve catalog definitions to importable, concrete engineering classes."""

from . import components, mission
from .eps import components as eps_components
from .eps.subsystem import EPS

_TYPES = (
    mission.Orbit,
    mission.CubeSat,
    mission.Payload,
    mission.GroundStation,
    mission.CommandAndDataHandling,
    mission.Communication,
    mission.AttitudeDeterminationAndControl,
    mission.GuidanceNavigationAndControl,
    mission.StructuresAndMechanisms,
    mission.Thermal,
    mission.Propulsion,
    EPS,
    mission.PlanAndSchedule,
    mission.SpacecraftCommand,
    mission.GroundEquipmentControl,
    mission.SpaceGroundCommunication,
    mission.MissionDataProcessing,
    mission.MissionDataDissemination,
    mission.Network,
    mission.TelemetryProcessing,
    eps_components.Battery,
    eps_components.SolarArray,
    eps_components.RegulatorAndConverter,
    eps_components.PowerCircuit,
    eps_components.PowerLoss,
    components.ProcessorAndMemory,
    components.Software,
    components.Instrument,
    components.CommandTelemetryAndDataBus,
    components.ReceiveAntennaAndEquipment,
    components.TransmitAntennaAndEquipment,
    components.Actuator,
    components.Sensor,
    components.Accelerometer,
    components.GNSSReceiver,
    components.ActuatedMount,
    components.DeployableMount,
    components.StaticMount,
    components.ThermalSensor,
    components.ThermalSource,
    components.ThermalSink,
    components.PropellantStorage,
    components.PropellantControl,
    components.Thrusters,
)
BY_MODEL = {cls.model: cls for cls in _TYPES}
BY_COMPONENT_NAME = {
    cls.model.rsplit("::", 1)[-1]: cls for cls in _TYPES if cls.role == "component"
}


def element_class(definition):
    cls = BY_MODEL.get(definition)
    if cls is None:
        cls = BY_COMPONENT_NAME.get(definition.rsplit("::", 1)[-1])
    if cls is None:
        raise ValueError(f"No native element class is registered for {definition!r}.")
    return cls
