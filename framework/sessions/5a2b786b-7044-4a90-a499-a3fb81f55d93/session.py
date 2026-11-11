"""Native nanosat_mbse session configuration.

This is trusted local Python code. Loading builds configuration only.
Run this file explicitly to execute its imported verification classes.
"""

from nanosat_mbse.core.configuration import Variable
from nanosat_mbse.core.predicates import VerificationMethod
from nanosat_mbse.core.requirements import Parameter
from nanosat_mbse.core.session import SeedRule
from nanosat_mbse.core.session import Session
from nanosat_mbse.domains.budgets import ComponentMassLimit
from nanosat_mbse.domains.budgets import ComponentVolumeLimit
from nanosat_mbse.domains.budgets import MassLimit
from nanosat_mbse.domains.budgets import VolumeLimit
from nanosat_mbse.domains.components import Accelerometer
from nanosat_mbse.domains.components import ActuatedMount
from nanosat_mbse.domains.components import Actuator
from nanosat_mbse.domains.components import CommandTelemetryAndDataBus
from nanosat_mbse.domains.components import DeployableMount
from nanosat_mbse.domains.components import GNSSReceiver
from nanosat_mbse.domains.components import Instrument
from nanosat_mbse.domains.components import ProcessorAndMemory
from nanosat_mbse.domains.components import PropellantControl
from nanosat_mbse.domains.components import PropellantStorage
from nanosat_mbse.domains.components import ReceiveAntennaAndEquipment
from nanosat_mbse.domains.components import Sensor
from nanosat_mbse.domains.components import Software
from nanosat_mbse.domains.components import StaticMount
from nanosat_mbse.domains.components import ThermalSensor
from nanosat_mbse.domains.components import ThermalSink
from nanosat_mbse.domains.components import ThermalSource
from nanosat_mbse.domains.components import Thrusters
from nanosat_mbse.domains.components import TransmitAntennaAndEquipment
from nanosat_mbse.domains.eps.components import Battery
from nanosat_mbse.domains.eps.components import PowerCircuit
from nanosat_mbse.domains.eps.components import RegulatorAndConverter
from nanosat_mbse.domains.eps.components import SolarArray
from nanosat_mbse.domains.eps.requirements import GenericRequirement
from nanosat_mbse.domains.eps.subsystem import EPS
from nanosat_mbse.domains.mission import AttitudeDeterminationAndControl
from nanosat_mbse.domains.mission import CommandAndDataHandling
from nanosat_mbse.domains.mission import Communication
from nanosat_mbse.domains.mission import CubeSat
from nanosat_mbse.domains.mission import External
from nanosat_mbse.domains.mission import GroundEquipmentControl
from nanosat_mbse.domains.mission import GroundStation
from nanosat_mbse.domains.mission import GuidanceNavigationAndControl
from nanosat_mbse.domains.mission import Mission
from nanosat_mbse.domains.mission import MissionDataDissemination
from nanosat_mbse.domains.mission import MissionDataProcessing
from nanosat_mbse.domains.mission import Network
from nanosat_mbse.domains.mission import Orbit
from nanosat_mbse.domains.mission import Payload
from nanosat_mbse.domains.mission import PlanAndSchedule
from nanosat_mbse.domains.mission import Propulsion
from nanosat_mbse.domains.mission import SpaceGroundCommunication
from nanosat_mbse.domains.mission import SpacecraftCommand
from nanosat_mbse.domains.mission import StructuresAndMechanisms
from nanosat_mbse.domains.mission import TelemetryProcessing
from nanosat_mbse.domains.mission import Thermal

SESSION_FORMAT = 1


def build_session(*, catalog=None, database=None, verification_registry=None):
    session = Session(
        key='5a2b786b-7044-4a90-a499-a3fb81f55d93',
        name='Generic EPS Example',
        catalog=catalog,
        database=database,
        verification_registry=verification_registry,
    )

    mission = Mission.restore(
        id='MISSION',
        key='mission',
        name='Mission',
        definition='Mission',
        selection=False,
    )

    external = External.restore(
        id='EXTERNAL',
        key='external',
        name='External',
        definition='External',
        selection=False,
    )

    session.restore_roots(
        mission=mission,
        external=external,
        mission_fields=(),
        external_fields=(),
    )

    orb = session.restore(
        Orbit.restore(
            id='ORB',
            key='f23034d2-224c-4126-bf4c-6d7bf828a263',
            name='Orbit',
            definition='Orbit',
            selection=False,
        ),
        projection_fields=(),
    )

    orb001 = session.restore(
        GenericRequirement.restore(
            id='ORB001',
            key='generic-ORB-OrbitPeriod',
            name='',
            definition='FrameworkRequirements::OrbitPeriod',
            text='The preliminary circular orbit shall have period $$orbit_period_s$$ at altitude $$altitude_km$$, using Earth radius $$earthRadius_km$$ and gravitational parameter $$gravitationalParameter_km3_s2$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:orbit-period (handpicked-0003, Eqs. 1-4)',
            origin='final_report/design-proposal.tex#eq:orbit-period (handpicked-0003, Eqs. 1-4)',
            parameters=(
                Parameter('altitude_km', unit='km'),
                Parameter('earthRadius_km', unit='km', expression='6378'),
                Parameter('gravitationalParameter_km3_s2', unit='km^3/s^2', expression='398601'),
                Parameter('orbit_period_s', unit='s', expression='((2 * math.pi) * math.sqrt((((earthRadius_km + altitude_km) ** 3) / gravitationalParameter_km3_s2)))'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::OrbitPeriod'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    orb002 = session.restore(
        GenericRequirement.restore(
            id='ORB002',
            key='generic-ORB-IlluminationPeriods',
            name='',
            definition='FrameworkRequirements::IlluminationPeriods',
            text='The preliminary circular orbit at altitude $$altitude_km$$ shall provide $$sunlight_s$$ of sunlight and $$eclipse_s$$ of eclipse per $$orbit_period_s$$ orbit, using Earth radius $$earthRadius_km$$ and horizon angle $$horizon_angle_rad$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period, eq:eclipse-geometry',
            origin='final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period, eq:eclipse-geometry',
            parameters=(
                Parameter('altitude_km', unit='km', expression='ORB001.altitude_km'),
                Parameter('earthRadius_km', unit='km', expression='ORB001.earthRadius_km'),
                Parameter('orbit_period_s', unit='s', expression='ORB001.orbit_period_s'),
                Parameter('horizon_angle_rad', unit='rad', expression='math.acos((earthRadius_km / (earthRadius_km + altitude_km)))'),
                Parameter('sunlight_s', unit='s', expression='((0.5 + (horizon_angle_rad / math.pi)) * orbit_period_s)'),
                Parameter('eclipse_s', unit='s', expression='((0.5 - (horizon_angle_rad / math.pi)) * orbit_period_s)'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::IlluminationPeriods'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    orb003 = session.restore(
        GenericRequirement.restore(
            id='ORB003',
            key='generic-ORB-OrbitPeriodClosure',
            name='',
            definition='FrameworkRequirements::OrbitPeriodClosure',
            text='The positive sunlight and eclipse periods shall sum to $$orbit_period_s$$ within numerical tolerance.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period',
            origin='final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period',
            parameters=(
                Parameter('orbit_period_s', unit='s', expression='ORB002.orbit_period_s'),
                Parameter('sunlight_s', unit='s', expression='ORB002.sunlight_s'),
                Parameter('eclipse_s', unit='s', expression='ORB002.eclipse_s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::OrbitPeriodClosure'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    bus = session.restore(
        CubeSat.restore(
            id='BUS',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3',
            name='CubeSat Bus',
            definition='SpaceSegment::CubeSat',
            selection=False,
        ),
        projection_fields=(),
    )

    cdh = session.restore(
        CommandAndDataHandling.restore(
            id='CDH',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem',
            name='Command and Data Handling',
            definition='SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    com = session.restore(
        Communication.restore(
            id='COM',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem',
            name='Communication',
            definition='SpaceSegment::CubeSat::CommunicationSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    adc = session.restore(
        AttitudeDeterminationAndControl.restore(
            id='ADC',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu',
            name='Attitude Determination and Control',
            definition='SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    gnc = session.restore(
        GuidanceNavigationAndControl.restore(
            id='GNC',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy',
            name='Guidance Navigation and Control',
            definition='SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    str = session.restore(
        StructuresAndMechanisms.restore(
            id='STR',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem',
            name='Structures and Mechanisms',
            definition='SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    the = session.restore(
        Thermal.restore(
            id='THE',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem',
            name='Thermal',
            definition='SpaceSegment::CubeSat::ThermalSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    pro = session.restore(
        Propulsion.restore(
            id='PRO',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem',
            name='Propulsion',
            definition='SpaceSegment::CubeSat::PropulsionSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    eps = session.restore(
        EPS.restore(
            id='EPS',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem',
            name='Power',
            definition='SpaceSegment::CubeSat::PowerSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    aaa = session.restore(
        CommandTelemetryAndDataBus.restore(
            id='AAA',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem-C',
            name='Command Telemetry and Data Bus',
            definition='SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem::CommandTelemetryAndDataBus',
            selection=False,
        ),
        projection_fields=(),
    )

    pcm = session.restore(
        ProcessorAndMemory.restore(
            id='PCM',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem-P',
            name='Processor and Memory',
            definition='SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem::ProcessorAndMemory',
            selection=False,
        ),
        projection_fields=(),
    )

    aab = session.restore(
        ProcessorAndMemory.restore(
            id='AAB',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-ProcessorA',
            name='Processor and Memory',
            definition='SpaceSegment::CubeSat::CommunicationSubsystem::ProcessorAndMemory',
            selection=False,
        ),
        projection_fields=(),
    )

    rec = session.restore(
        ReceiveAntennaAndEquipment.restore(
            id='REC',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-ReceiveAnt',
            name='Receive Antenna and Equipment',
            definition='SpaceSegment::CubeSat::CommunicationSubsystem::ReceiveAntennaAndEquipment',
            selection=False,
        ),
        projection_fields=(),
    )

    tra = session.restore(
        TransmitAntennaAndEquipment.restore(
            id='TRA',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-TransmitAn',
            name='Transmit Antenna and Equipment',
            definition='SpaceSegment::CubeSat::CommunicationSubsystem::TransmitAntennaAndEquipment',
            selection=False,
        ),
        projection_fields=(),
    )

    sfw = session.restore(
        Software.restore(
            id='SFW',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_1',
            name='Software',
            definition='SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem::Software',
            selection=False,
        ),
        projection_fields=(),
    )

    act = session.restore(
        Actuator.restore(
            id='ACT',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_2',
            name='Actuator',
            definition='SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem::Actuator',
            selection=False,
        ),
        projection_fields=(),
    )

    sen = session.restore(
        Sensor.restore(
            id='SEN',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_3',
            name='Sensor',
            definition='SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem::Sensor',
            selection=False,
        ),
        projection_fields=(),
    )

    acc = session.restore(
        Accelerometer.restore(
            id='ACC',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_1',
            name='Accelerometer',
            definition='SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem::Accelerometer',
            selection=False,
        ),
        projection_fields=(),
    )

    gns = session.restore(
        GNSSReceiver.restore(
            id='GNS',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_2',
            name='GNSS Receiver',
            definition='SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem::GNSSReceiver',
            selection=False,
        ),
        projection_fields=(),
    )

    aac = session.restore(
        Software.restore(
            id='AAC',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_3',
            name='Software',
            definition='SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem::Software',
            selection=False,
        ),
        projection_fields=(),
    )

    aad = session.restore(
        ActuatedMount.restore(
            id='AAD',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-',
            name='Actuated Mount',
            definition='SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::ActuatedMount',
            selection=False,
        ),
        projection_fields=(),
    )

    dep = session.restore(
        DeployableMount.restore(
            id='DEP',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-_1',
            name='Deployable Mount',
            definition='SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::DeployableMount',
            selection=False,
        ),
        projection_fields=(),
    )

    sta = session.restore(
        StaticMount.restore(
            id='STA',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-_2',
            name='Static Mount',
            definition='SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::StaticMount',
            selection=False,
        ),
        projection_fields=(),
    )

    aae = session.restore(
        ThermalSensor.restore(
            id='AAE',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSensor',
            name='Thermal Sensor',
            definition='SpaceSegment::CubeSat::ThermalSubsystem::ThermalSensor',
            selection=False,
        ),
        projection_fields=(),
    )

    aaf = session.restore(
        ThermalSource.restore(
            id='AAF',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSource',
            name='Thermal Source',
            definition='SpaceSegment::CubeSat::ThermalSubsystem::ThermalSource',
            selection=False,
        ),
        projection_fields=(),
    )

    aag = session.restore(
        ThermalSink.restore(
            id='AAG',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSink',
            name='Thermal Sink',
            definition='SpaceSegment::CubeSat::ThermalSubsystem::ThermalSink',
            selection=False,
        ),
        projection_fields=(),
    )

    aah = session.restore(
        ProcessorAndMemory.restore(
            id='AAH',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ProcessorAndMemo',
            name='Processor and Memory',
            definition='SpaceSegment::CubeSat::ThermalSubsystem::ProcessorAndMemory',
            selection=False,
        ),
        projection_fields=(),
    )

    aai = session.restore(
        Software.restore(
            id='AAI',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-Software',
            name='Software',
            definition='SpaceSegment::CubeSat::ThermalSubsystem::Software',
            selection=False,
        ),
        projection_fields=(),
    )

    aaj = session.restore(
        PropellantStorage.restore(
            id='AAJ',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-PropellantSto',
            name='Propellant Storage',
            definition='SpaceSegment::CubeSat::PropulsionSubsystem::PropellantStorage',
            selection=False,
        ),
        projection_fields=(),
    )

    aak = session.restore(
        PropellantControl.restore(
            id='AAK',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-PropellantCon',
            name='Propellant Control',
            definition='SpaceSegment::CubeSat::PropulsionSubsystem::PropellantControl',
            selection=False,
        ),
        projection_fields=(),
    )

    thr = session.restore(
        Thrusters.restore(
            id='THR',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Thrusters',
            name='Thrusters',
            definition='SpaceSegment::CubeSat::PropulsionSubsystem::Thrusters',
            selection=False,
        ),
        projection_fields=(),
    )

    aal = session.restore(
        Software.restore(
            id='AAL',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Software',
            name='Software',
            definition='SpaceSegment::CubeSat::PropulsionSubsystem::Software',
            selection=False,
        ),
        projection_fields=(),
    )

    aam = session.restore(
        ProcessorAndMemory.restore(
            id='AAM',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-ProcessorAndM',
            name='Processor and Memory',
            definition='SpaceSegment::CubeSat::PropulsionSubsystem::ProcessorAndMemory',
            selection=False,
        ),
        projection_fields=(),
    )

    bat = session.restore(
        Battery.restore(
            id='BAT',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries',
            name='Batteries',
            definition='SpaceSegment::CubeSat::PowerSubsystem::Batteries',
            selection=False,
        ),
        projection_fields=(),
    )

    sol = session.restore(
        SolarArray.restore(
            id='SOL',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays',
            name='Solar Arrays',
            definition='SpaceSegment::CubeSat::PowerSubsystem::SolarArrays',
            selection=False,
        ),
        projection_fields=(),
    )

    aan = session.restore(
        ProcessorAndMemory.restore(
            id='AAN',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-ProcessorAndMemory',
            name='Processor and Memory',
            definition='SpaceSegment::CubeSat::PowerSubsystem::ProcessorAndMemory',
            selection=False,
        ),
        projection_fields=(),
    )

    reg = session.restore(
        RegulatorAndConverter.restore(
            id='REG',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-RegulatorsAndConve',
            name='Regulators and Converters',
            definition='SpaceSegment::CubeSat::PowerSubsystem::RegulatorsAndConverters',
            selection=False,
        ),
        projection_fields=(),
    )

    pcs = session.restore(
        PowerCircuit.restore(
            id='PCS',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircuitsAndSw',
            name='Power Circuits and Switches',
            definition='SpaceSegment::CubeSat::PowerSubsystem::PowerCircuitsAndSwitches',
            selection=False,
        ),
        projection_fields=(),
    )

    aao = session.restore(
        Software.restore(
            id='AAO',
            key='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Software',
            name='Software',
            definition='SpaceSegment::CubeSat::PowerSubsystem::Software',
            selection=False,
        ),
        projection_fields=(),
    )

    siz001 = session.restore(
        GenericRequirement.restore(
            id='SIZ001',
            key='generic-EPS-LoadEnergy',
            name='',
            definition='FrameworkRequirements::LoadEnergy',
            text='The preliminary load budget shall allocate $$sunlight_energy_J$$ during $$sunlight_s$$ of sunlight and $$eclipse_energy_J$$ during $$eclipse_s$$ of eclipse.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:minimum-panel-power; EPSModel::ModeLoadProfile and AccountingPlan',
            origin='final_report/design-proposal.tex#eq:minimum-panel-power; EPSModel::ModeLoadProfile and AccountingPlan',
            parameters=(
                Parameter('sunlight_power_W', unit='W'),
                Parameter('eclipse_power_W', unit='W'),
                Parameter('sunlight_duty'),
                Parameter('eclipse_duty'),
                Parameter('sunlight_s', unit='s', expression='ORB002.sunlight_s'),
                Parameter('eclipse_s', unit='s', expression='ORB002.eclipse_s'),
                Parameter('sunlight_energy_J', unit='J', expression='((sunlight_power_W * sunlight_duty) * sunlight_s)'),
                Parameter('eclipse_energy_J', unit='J', expression='((eclipse_power_W * eclipse_duty) * eclipse_s)'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::LoadEnergy'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz002 = session.restore(
        GenericRequirement.restore(
            id='SIZ002',
            key='generic-EPS-MinimumPanelPower',
            name='',
            definition='FrameworkRequirements::MinimumPanelPower',
            text='The solar panels shall provide at least $$panel_min_W$$ at the declared source boundary.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:minimum-panel-power (handpicked-0003)',
            origin='final_report/design-proposal.tex#eq:minimum-panel-power (handpicked-0003)',
            parameters=(
                Parameter('sunlight_energy_J', unit='J', expression='SIZ001.sunlight_energy_J'),
                Parameter('eclipse_energy_J', unit='J', expression='SIZ001.eclipse_energy_J'),
                Parameter('sunlight_s', unit='s', expression='ORB002.sunlight_s'),
                Parameter('sunlight_efficiency'),
                Parameter('eclipse_efficiency'),
                Parameter('panel_min_W', unit='W', expression='(((sunlight_energy_J / sunlight_efficiency) + (eclipse_energy_J / eclipse_efficiency)) / sunlight_s)'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::MinimumPanelPower'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz003 = session.restore(
        GenericRequirement.restore(
            id='SIZ003',
            key='generic-EPS-SolarCellPower',
            name='',
            definition='FrameworkRequirements::SolarCellPower',
            text='The selected solar cell shall provide EOL maximum power $$cell_eol_W$$ from maximum power point voltage $$cell_eol_V$$ and current $$cell_eol_A$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:solar-cell-eol-power',
            origin='final_report/design-proposal.tex#eq:solar-cell-eol-power',
            parameters=(
                Parameter('cell_eol_V', unit='V'),
                Parameter('cell_eol_A', unit='A'),
                Parameter('cell_eol_W', unit='W', expression='(cell_eol_V * cell_eol_A)'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::SolarCellPower'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz004 = session.restore(
        GenericRequirement.restore(
            id='SIZ004',
            key='generic-EPS-SolarCellCount',
            name='',
            definition='FrameworkRequirements::SolarCellCount',
            text='The array shall install $$installed_cells$$, at least the minimum $$minimum_cells$$ obtained by rounding calculated count $$required_cells$$ upward.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:solar-cell-count, eq:pv-integer-configuration',
            origin='final_report/design-proposal.tex#eq:solar-cell-count, eq:pv-integer-configuration',
            parameters=(
                Parameter('panel_min_W', unit='W', expression='SIZ002.panel_min_W'),
                Parameter('cell_eol_W', unit='W', expression='SIZ003.cell_eol_W'),
                Parameter('required_cells', unit='cells', expression='(panel_min_W / cell_eol_W)'),
                Parameter('minimum_cells', value_type=int, unit='cells', expression='(- math.floor((- required_cells)))'),
                Parameter('installed_cells', value_type=int, unit='cells'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::SolarCellCount'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz005 = session.restore(
        GenericRequirement.restore(
            id='SIZ005',
            key='generic-EPS-MissionCycles',
            name='',
            definition='FrameworkRequirements::MissionCycles',
            text='For one nominal cycle per orbit, the battery shall support at least $$required_cycles$$ over $$lifetime_years$$, using $$days_per_year$$ and $$orbits_per_day$$ derived from period $$orbit_period_s$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:battery-mission-cycles',
            origin='final_report/design-proposal.tex#eq:battery-mission-cycles',
            parameters=(
                Parameter('orbit_period_s', unit='s', expression='ORB001.orbit_period_s'),
                Parameter('orbits_per_day', unit='orbits/day', expression='(86400 / orbit_period_s)'),
                Parameter('lifetime_years', unit='years'),
                Parameter('days_per_year', unit='days/year'),
                Parameter('required_cycles', unit='cycles', expression='((lifetime_years * days_per_year) * orbits_per_day)'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::MissionCycles'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz006 = session.restore(
        GenericRequirement.restore(
            id='SIZ006',
            key='generic-EPS-CycleLife',
            name='',
            definition='FrameworkRequirements::CycleLife',
            text='The selected maximum depth of discharge $$dod_max$$ shall support $$supported_cycles$$, at least the required $$required_cycles$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:battery-cycle-life; EPS-09',
            origin='final_report/design-proposal.tex#eq:battery-cycle-life; EPS-09',
            parameters=(
                Parameter('required_cycles', unit='cycles', expression='SIZ005.required_cycles'),
                Parameter('cycle_a', unit='cycles'),
                Parameter('cycle_b'),
                Parameter('dod_max'),
                Parameter('fit_dod_min'),
                Parameter('fit_dod_max'),
                Parameter('dod_cycle_limit', expression='((required_cycles / cycle_a) ** (1 / cycle_b))'),
                Parameter('supported_cycles', unit='cycles', expression='(cycle_a * (dod_max ** cycle_b))'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::CycleLife'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz007 = session.restore(
        GenericRequirement.restore(
            id='SIZ007',
            key='generic-EPS-MinimumBatteryEnergy',
            name='',
            definition='FrameworkRequirements::MinimumBatteryEnergy',
            text='The battery shall provide at least $$battery_min_J$$ of BOL energy for eclipse demand $$eclipse_energy_J$$ at maximum DoD $$dod_max$$ and degradation margin $$degradation_margin$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:battery-energy; EPS-08',
            origin='final_report/design-proposal.tex#eq:battery-energy; EPS-08',
            parameters=(
                Parameter('eclipse_energy_J', unit='J', expression='SIZ001.eclipse_energy_J'),
                Parameter('dod_max', expression='SIZ006.dod_max'),
                Parameter('degradation_margin'),
                Parameter('battery_min_J', unit='J', expression='((eclipse_energy_J / dod_max) * (1 + degradation_margin))'),
                Parameter('required_cycles', unit='cycles', expression='SIZ005.required_cycles'),
                Parameter('supported_cycles', unit='cycles', expression='SIZ006.supported_cycles'),
                Parameter('fit_dod_min', expression='SIZ006.fit_dod_min'),
                Parameter('fit_dod_max', expression='SIZ006.fit_dod_max'),
                Parameter('cycle_a', unit='cycles', expression='SIZ006.cycle_a'),
                Parameter('cycle_b', expression='SIZ006.cycle_b'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::MinimumBatteryEnergy'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz008 = session.restore(
        GenericRequirement.restore(
            id='SIZ008',
            key='generic-EPS-BatteryCapacityScreen',
            name='',
            definition='FrameworkRequirements::BatteryCapacityScreen',
            text='The selected battery shall have BOL energy $$pack_bol_J$$, at least the preliminary minimum $$battery_min_J$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:battery-assembly-capacity; EPS-08',
            origin='final_report/design-proposal.tex#eq:battery-assembly-capacity; EPS-08',
            parameters=(
                Parameter('battery_min_J', unit='J', expression='SIZ007.battery_min_J'),
                Parameter('pack_bol_J', unit='J'),
                Parameter('retained_energy_factor'),
                Parameter('pack_eol_J', unit='J', expression='(retained_energy_factor * pack_bol_J)'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::BatteryCapacityScreen'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps002 = session.restore(
        GenericRequirement.restore(
            id='EPS002',
            key='generic-EPS-EPS02',
            name='',
            definition='FrameworkRequirements::EPS02',
            text="EPS-02. The solar arrays shall provide at least $$panel_min_W$$ of average source power from $$sunlight_generation_J$$ over $$sunlight_s$$ of sunlight at each section's attainable DET or MPPT operating point under applicable illumination and EOL conditions.",
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-02; eq:array-generation-screen, eq:pv-integer-configuration',
            origin='final_report/eps-requirements.tex#EPS-02; eq:array-generation-screen, eq:pv-integer-configuration',
            parameters=(
                Parameter('sunlight_generation_J', unit='J'),
                Parameter('sunlight_s', unit='s', expression='ORB002.sunlight_s'),
                Parameter('panel_min_W', unit='W', expression='SIZ002.panel_min_W'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS02'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps008 = session.restore(
        GenericRequirement.restore(
            id='EPS008',
            key='generic-EPS-EPS08',
            name='',
            definition='FrameworkRequirements::EPS08',
            text='EPS-08. The battery pack BOL energy $$pack_bol_J$$ shall meet minimum energy $$battery_min_J$$ from preliminary battery sizing.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-08; eq:battery-energy, eq:battery-assembly-capacity, eq:battery-assembly-ratings',
            origin='final_report/eps-requirements.tex#EPS-08; eq:battery-energy, eq:battery-assembly-capacity, eq:battery-assembly-ratings',
            parameters=(
                Parameter('pack_bol_J', unit='J', expression='SIZ008.pack_bol_J'),
                Parameter('battery_min_J', unit='J', expression='SIZ007.battery_min_J'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS08'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps009 = session.restore(
        GenericRequirement.restore(
            id='EPS009',
            key='generic-EPS-EPS09',
            name='',
            definition='FrameworkRequirements::EPS09',
            text='EPS-09. For nominal operation, the battery pack shall support $$supported_cycles$$, at least the required $$required_cycles$$ at the selected DoD and applicable conditions.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-09; eq:battery-mission-cycles, eq:battery-cycle-life',
            origin='final_report/eps-requirements.tex#EPS-09; eq:battery-mission-cycles, eq:battery-cycle-life',
            parameters=(
                Parameter('required_cycles', unit='cycles', expression='SIZ005.required_cycles'),
                Parameter('supported_cycles', unit='cycles', expression='SIZ006.supported_cycles'),
                Parameter('nominal_dod'),
                Parameter('dod_max', expression='SIZ006.dod_max'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS09'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps011 = session.restore(
        GenericRequirement.restore(
            id='EPS011',
            key='generic-EPS-EPS11',
            name='',
            definition='FrameworkRequirements::EPS11',
            text='EPS-11. The EPS shall replenish the battery from starting energy $$energy_start_J$$ and charge based SOC $$soc_start$$ over every specified nominal repeating interval.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility',
            origin='final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility',
            parameters=(
                Parameter('energy_start_J', unit='J'),
                Parameter('energy_end_J', unit='J'),
                Parameter('closure_tolerance_J', unit='J'),
                Parameter('soc_start'),
                Parameter('soc_end'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS11'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps019 = session.restore(
        GenericRequirement.restore(
            id='EPS019',
            key='generic-EPS-EPS19',
            name='',
            definition='FrameworkRequirements::EPS19',
            text='EPS-19. Total EPS mass $$mass_kg$$ shall remain within allocation $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets',
            origin='final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets',
            parameters=(
                Parameter('mass_kg', unit='kg'),
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('volume_m3', unit='m^3'),
                Parameter('volume_allocation_m3', unit='m^3'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS19'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps021 = session.restore(
        GenericRequirement.restore(
            id='EPS021',
            key='generic-EPS-EPS21',
            name='',
            definition='FrameworkRequirements::EPS21',
            text='EPS-21. Each software execution host shall provide $$required_data_bytes$$ of data memory within an allocation of $$available_data_bytes$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:software-resource-screen; Software-host checks',
            origin='final_report/design-proposal.tex#eq:software-resource-screen; Software-host checks',
            parameters=(
                Parameter('required_data_bytes', value_type=int, unit='bytes'),
                Parameter('available_data_bytes', value_type=int, unit='bytes'),
                Parameter('required_program_bytes', value_type=int, unit='bytes'),
                Parameter('available_program_bytes', value_type=int, unit='bytes'),
                Parameter('required_utilization'),
                Parameter('allocated_utilization'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS21'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz011 = session.restore(
        GenericRequirement.restore(
            id='SIZ011',
            key='generic-EPS-EnergyPathEfficiencyBounds',
            name='',
            definition='FrameworkRequirements::EnergyPathEfficiencyBounds',
            text='Sunlight path efficiency $$sunlight_efficiency$$ and eclipse path efficiency $$eclipse_efficiency$$ shall lie in (0,1].',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:minimum-panel-power',
            origin='final_report/design-proposal.tex#eq:minimum-panel-power',
            parameters=(
                Parameter('sunlight_efficiency', expression='SIZ002.sunlight_efficiency'),
                Parameter('eclipse_efficiency', expression='SIZ002.eclipse_efficiency'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EnergyPathEfficiencyBounds'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz013 = session.restore(
        GenericRequirement.restore(
            id='SIZ013',
            key='generic-EPS-CycleFitDomain',
            name='',
            definition='FrameworkRequirements::CycleFitDomain',
            text='Maximum DoD $$dod_max$$ shall lie in (0,1] and the sourced fit interval [$$fit_dod_min$$,$$fit_dod_max$$] for power law coefficients $$cycle_a$$ and $$cycle_b$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:battery-cycle-life',
            origin='final_report/design-proposal.tex#eq:battery-cycle-life',
            parameters=(
                Parameter('dod_max', expression='SIZ006.dod_max'),
                Parameter('fit_dod_min', expression='SIZ006.fit_dod_min'),
                Parameter('fit_dod_max', expression='SIZ006.fit_dod_max'),
                Parameter('cycle_a', unit='cycles', expression='SIZ006.cycle_a'),
                Parameter('cycle_b', expression='SIZ006.cycle_b'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::CycleFitDomain'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz014 = session.restore(
        GenericRequirement.restore(
            id='SIZ014',
            key='generic-EPS-CycleLimitedDoD',
            name='',
            definition='FrameworkRequirements::CycleLimitedDoD',
            text='Maximum DoD $$dod_max$$ shall not exceed fitted cycle limit $$dod_cycle_limit$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:battery-cycle-life',
            origin='final_report/design-proposal.tex#eq:battery-cycle-life',
            parameters=(
                Parameter('dod_max', expression='SIZ006.dod_max'),
                Parameter('dod_cycle_limit', expression='SIZ006.dod_cycle_limit'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::CycleLimitedDoD'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    siz016 = session.restore(
        GenericRequirement.restore(
            id='SIZ016',
            key='generic-EPS-BatteryRetainedEnergy',
            name='',
            definition='FrameworkRequirements::BatteryRetainedEnergy',
            text='Battery EOL energy $$pack_eol_J$$ shall equal BOL energy $$pack_bol_J$$ multiplied by retained energy factor $$retained_energy_factor$$ in (0,1].',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:battery-assembly-capacity',
            origin='final_report/design-proposal.tex#eq:battery-assembly-capacity',
            parameters=(
                Parameter('pack_bol_J', unit='J', expression='SIZ008.pack_bol_J'),
                Parameter('pack_eol_J', unit='J', expression='SIZ008.pack_eol_J'),
                Parameter('retained_energy_factor', expression='SIZ008.retained_energy_factor'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::BatteryRetainedEnergy'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps047 = session.restore(
        GenericRequirement.restore(
            id='EPS047',
            key='generic-EPS-EPS47',
            name='',
            definition='FrameworkRequirements::EPS47',
            text='EPS-47. Nominal cycle DoD $$nominal_dod$$ shall not exceed maximum DoD $$dod_max$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-09',
            origin='final_report/eps-requirements.tex#EPS-09',
            parameters=(
                Parameter('nominal_dod', expression='EPS009.nominal_dod'),
                Parameter('dod_max', expression='EPS009.dod_max'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS47'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps052 = session.restore(
        GenericRequirement.restore(
            id='EPS052',
            key='generic-EPS-EPS52',
            name='',
            definition='FrameworkRequirements::EPS52',
            text='EPS-52. Ending energy $$energy_end_J$$ shall be at least starting energy $$energy_start_J$$ minus nonnegative numerical closure tolerance $$closure_tolerance_J$$ over each nominal repeating interval.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility',
            origin='final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility',
            parameters=(
                Parameter('energy_start_J', unit='J', expression='EPS011.energy_start_J'),
                Parameter('energy_end_J', unit='J', expression='EPS011.energy_end_J'),
                Parameter('closure_tolerance_J', unit='J', expression='EPS011.closure_tolerance_J'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS52'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps053 = session.restore(
        GenericRequirement.restore(
            id='EPS053',
            key='generic-EPS-EPS53',
            name='',
            definition='FrameworkRequirements::EPS53',
            text='EPS-53. Ending charge based SOC $$soc_end$$ shall be at least starting SOC $$soc_start$$ over each nominal repeating interval.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-11',
            origin='final_report/eps-requirements.tex#EPS-11',
            parameters=(
                Parameter('soc_start', expression='EPS011.soc_start'),
                Parameter('soc_end', expression='EPS011.soc_end'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS53'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps078 = session.restore(
        GenericRequirement.restore(
            id='EPS078',
            key='generic-EPS-EPS78',
            name='',
            definition='FrameworkRequirements::EPS78',
            text='EPS-78. Occupied EPS volume $$volume_m3$$ shall remain within allocation $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets',
            origin='final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets',
            parameters=(
                Parameter('volume_m3', unit='m^3', expression='EPS019.volume_m3'),
                Parameter('volume_allocation_m3', unit='m^3', expression='EPS019.volume_allocation_m3'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS78'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps088 = session.restore(
        GenericRequirement.restore(
            id='EPS088',
            key='generic-EPS-EPS88',
            name='',
            definition='FrameworkRequirements::EPS88',
            text='EPS-88. Each software execution host shall provide $$required_program_bytes$$ of program storage within an allocation of $$available_program_bytes$$.',
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:software-resource-screen',
            origin='final_report/design-proposal.tex#eq:software-resource-screen',
            parameters=(
                Parameter('required_program_bytes', value_type=int, unit='bytes', expression='EPS021.required_program_bytes'),
                Parameter('available_program_bytes', value_type=int, unit='bytes', expression='EPS021.available_program_bytes'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS88'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps089 = session.restore(
        GenericRequirement.restore(
            id='EPS089',
            key='generic-EPS-EPS89',
            name='',
            definition='FrameworkRequirements::EPS89',
            text="EPS-89. The sum of each allocated task's execution time divided by its period shall give required utilization $$required_utilization$$, at most allocation $$allocated_utilization$$.",
            kind='Requirement',
            rationale='final_report/design-proposal.tex#eq:software-resource-screen',
            origin='final_report/design-proposal.tex#eq:software-resource-screen',
            parameters=(
                Parameter('required_utilization', expression='EPS021.required_utilization'),
                Parameter('allocated_utilization', expression='EPS021.allocated_utilization'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS89'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps001 = session.restore(
        GenericRequirement.restore(
            id='EPS001',
            key='generic-EPS-EPS01',
            name='',
            definition='FrameworkRequirements::EPS01',
            text='EPS-01. The EPS shall use supported array arrangements of $$array_series_cells$$ series cells and $$array_parallel_strings$$ parallel strings and battery arrangements of $$battery_series_cells$$ series cells and $$battery_parallel_strings$$ parallel strings.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-01 | Study: Supported product configurations and eps_sizing, preserving fixed purchased assemblies | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-01 | Study: Supported product configurations and eps_sizing, preserving fixed purchased assemblies | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('array_series_cells', value_type=int),
                Parameter('array_parallel_strings', value_type=int),
                Parameter('battery_series_cells', value_type=int),
                Parameter('battery_parallel_strings', value_type=int),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS01'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps003 = session.restore(
        GenericRequirement.restore(
            id='EPS003',
            key='generic-EPS-EPS03',
            name='',
            definition='FrameworkRequirements::EPS03',
            text='EPS-03. The assessed solar input interval from $$source_operating_min_V$$ to $$source_operating_max_V$$ shall remain within receiver limits $$receiver_min_V$$ and $$receiver_max_V$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-03 | Study: mppt_po and eps_power_path with applicable startup, tracking and shared-input conditions | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-03 | Study: mppt_po and eps_power_path with applicable startup, tracking and shared-input conditions | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('source_operating_min_V', unit='V'),
                Parameter('source_operating_max_V', unit='V'),
                Parameter('receiver_min_V', unit='V'),
                Parameter('receiver_max_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS03'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr001 = session.restore(
        GenericRequirement.restore(
            id='EPR001',
            key='generic-EPS-EPS03OpenCircuit',
            name='',
            definition='FrameworkRequirements::EPS03OpenCircuit',
            text='The solar source open circuit voltage $$source_voc_max_V$$ shall remain within absolute input limit $$input_absolute_max_V$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-03 | Study: mppt_po maximum open circuit voltage at the applicable temperature and arrangement | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-03 | Study: mppt_po maximum open circuit voltage at the applicable temperature and arrangement | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('source_voc_max_V', unit='V'),
                Parameter('input_absolute_max_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS03OpenCircuit'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr002 = session.restore(
        GenericRequirement.restore(
            id='EPR002',
            key='generic-EPS-EPS03SourceCurrent',
            name='',
            definition='FrameworkRequirements::EPS03SourceCurrent',
            text='The solar source short circuit current $$source_isc_max_A$$ shall remain within permissible source current $$source_current_limit_A$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-03 | Study: mppt_po maximum short circuit current and receiver source ratings | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-03 | Study: mppt_po maximum short circuit current and receiver source ratings | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('source_isc_max_A', unit='A'),
                Parameter('source_current_limit_A', unit='A'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS03SourceCurrent'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps004 = session.restore(
        GenericRequirement.restore(
            id='EPS004',
            key='generic-EPS-EPS04',
            name='',
            definition='FrameworkRequirements::EPS04',
            text='EPS-04. Each converter shall support input voltage $$converter_input_V$$ and output voltage $$converter_output_V$$ within its declared conversion envelope.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-04 | Study: eps_power_path topology, duty, dropout and startup-source checks | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-04 | Study: eps_power_path topology, duty, dropout and startup-source checks | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('converter_input_V', unit='V'),
                Parameter('converter_output_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS04'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    mil001 = session.restore(
        GenericRequirement.restore(
            id='MIL001',
            key='generic-EPS-RegulatorSettling',
            name='',
            definition='FrameworkRequirements::RegulatorSettling',
            text='The regulator response shall settle within $$settling_limit_s$$ after the declared command or load change.',
            kind='Requirement',
            rationale='final_report/requirements.tex#FR-16 | Study: eps_converter_step or mppt_po with a declared error band and hold interval | Supply applicable bounds and independently assigned limits.',
            origin='final_report/requirements.tex#FR-16 | Study: eps_converter_step or mppt_po with a declared error band and hold interval | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('settling_time_s', unit='s'),
                Parameter('settling_limit_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::RegulatorSettling'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps005 = session.restore(
        GenericRequirement.restore(
            id='EPS005',
            key='generic-EPS-EPS05',
            name='',
            definition='FrameworkRequirements::EPS05',
            text='EPS-05. The charger shall support $$battery_series_cells$$ series cells with the selected chemistry and charge policy.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-05 | Study: Battery and charger configuration facts and charge-policy compatibility | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-05 | Study: Battery and charger configuration facts and charge-policy compatibility | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('battery_series_cells', value_type=int),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS05'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr003 = session.restore(
        GenericRequirement.restore(
            id='EPR003',
            key='generic-EPS-EPS05ChargeVoltage',
            name='',
            definition='FrameworkRequirements::EPS05ChargeVoltage',
            text='The charge voltage $$charge_voltage_V$$ shall remain in the common battery and charger interval from $$charge_voltage_min_V$$ to $$charge_voltage_max_V$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-05 | Study: Battery and charger operating limits | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-05 | Study: Battery and charger operating limits | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('charge_voltage_V', unit='V'),
                Parameter('charge_voltage_min_V', unit='V'),
                Parameter('charge_voltage_max_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS05ChargeVoltage'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr004 = session.restore(
        GenericRequirement.restore(
            id='EPR004',
            key='generic-EPS-EPS05ChargeCurrent',
            name='',
            definition='FrameworkRequirements::EPS05ChargeCurrent',
            text='The charging current $$charge_current_A$$ shall remain within common battery and charger limit $$charge_current_limit_A$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-05 | Study: eps_energy_segment charge acceptance and sourced charging ratings | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-05 | Study: eps_energy_segment charge acceptance and sourced charging ratings | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('charge_current_A', unit='A'),
                Parameter('charge_current_limit_A', unit='A'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS05ChargeCurrent'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr005 = session.restore(
        GenericRequirement.restore(
            id='EPR005',
            key='generic-EPS-EPS05Termination',
            name='',
            definition='FrameworkRequirements::EPS05Termination',
            text='The charge termination current $$termination_current_A$$ shall remain within battery policy limit $$termination_limit_A$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-05 | Study: Selected battery termination policy and charger behavior | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-05 | Study: Selected battery termination policy and charger behavior | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('termination_current_A', unit='A'),
                Parameter('termination_limit_A', unit='A'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS05Termination'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps006 = session.restore(
        GenericRequirement.restore(
            id='EPS006',
            key='generic-EPS-EPS06',
            name='',
            definition='FrameworkRequirements::EPS06',
            text='EPS-06. The assessed load terminal interval from $$load_voltage_min_V$$ to $$load_voltage_max_V$$ shall remain within required supply limits $$load_supply_min_V$$ and $$load_supply_max_V$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-06 | Study: eps_power_path and eps_battery_step across required service and pulse cases | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-06 | Study: eps_power_path and eps_battery_step across required service and pulse cases | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('load_voltage_min_V', unit='V'),
                Parameter('load_voltage_max_V', unit='V'),
                Parameter('load_supply_min_V', unit='V'),
                Parameter('load_supply_max_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS06'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr006 = session.restore(
        GenericRequirement.restore(
            id='EPR006',
            key='generic-EPS-EPS06Startup',
            name='',
            definition='FrameworkRequirements::EPS06Startup',
            text='The load service shall satisfy allowance $$startup_limit_s$$ with assessed startup time $$startup_time_s$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-06 | Study: eps_converter_step startup and applicable source conditions | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-06 | Study: eps_converter_step startup and applicable source conditions | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('startup_time_s', unit='s'),
                Parameter('startup_limit_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS06Startup'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps007 = session.restore(
        GenericRequirement.restore(
            id='EPS007',
            key='generic-EPS-EPS07',
            name='',
            definition='FrameworkRequirements::EPS07',
            text='EPS-07. Each shared power path continuous current $$continuous_current_A$$ shall remain within its applicable rating $$continuous_rating_A$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-07 | Study: eps_power_path with simultaneous loads, upstream conversion losses and disjoint consumer accounting | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-07 | Study: eps_power_path with simultaneous loads, upstream conversion losses and disjoint consumer accounting | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('continuous_current_A', unit='A'),
                Parameter('continuous_rating_A', unit='A'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS07'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr007 = session.restore(
        GenericRequirement.restore(
            id='EPR007',
            key='generic-EPS-EPS07Pulse',
            name='',
            definition='FrameworkRequirements::EPS07Pulse',
            text='Each power path pulse current $$pulse_current_A$$ shall remain within rating $$pulse_rating_A$$ for duration $$pulse_duration_s$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-07 | Study: eps_power_path with explicit additive or replacing pulses and temperature-dependent ratings | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-07 | Study: eps_power_path with explicit additive or replacing pulses and temperature-dependent ratings | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('pulse_current_A', unit='A'),
                Parameter('pulse_rating_A', unit='A'),
                Parameter('pulse_duration_s', unit='s'),
                Parameter('pulse_rating_duration_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS07Pulse'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr008 = session.restore(
        GenericRequirement.restore(
            id='EPR008',
            key='generic-EPS-EPS08RetainedCharge',
            name='',
            definition='FrameworkRequirements::EPS08RetainedCharge',
            text='The retained battery charge capacity $$pack_eol_C$$ shall meet required capacity $$required_charge_C$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-08 | Study: eps_sizing charge capacity in Ah converted explicitly to C, with separate energy and charge retention | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-08 | Study: eps_sizing charge capacity in Ah converted explicitly to C, with separate energy and charge retention | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('pack_bol_C', unit='C'),
                Parameter('retained_charge_factor'),
                Parameter('pack_eol_C', unit='C', expression='pack_bol_C * retained_charge_factor'),
                Parameter('required_charge_C', unit='C'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS08RetainedCharge'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps010 = session.restore(
        GenericRequirement.restore(
            id='EPS010',
            key='generic-EPS-EPS10',
            name='',
            definition='FrameworkRequirements::EPS10',
            text='EPS-10. The EPS shall provide at least $$required_service_s$$ of scheduled nominal load service without energy shortages.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-10 | Study: Chained eps_energy_segment intervals with chronological source and load schedules | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-10 | Study: Chained eps_energy_segment intervals with chronological source and load schedules | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('required_service_s', unit='s'),
                Parameter('assessed_service_s', unit='s'),
                Parameter('unserved_energy_J', unit='J'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS10'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr009 = session.restore(
        GenericRequirement.restore(
            id='EPR009',
            key='generic-EPS-EPS10EnergyReserve',
            name='',
            definition='FrameworkRequirements::EPS10EnergyReserve',
            text='The nominal stored energy shall remain between reserve $$energy_reserve_J$$ and retained capacity $$pack_eol_J$$ throughout required service.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-10 | Study: eps_energy_segment energy minima and maxima across the complete nominal schedule | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-10 | Study: eps_energy_segment energy minima and maxima across the complete nominal schedule | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('energy_min_J', unit='J'),
                Parameter('energy_max_J', unit='J'),
                Parameter('energy_reserve_J', unit='J'),
                Parameter('pack_eol_J', unit='J'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS10EnergyReserve'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr010 = session.restore(
        GenericRequirement.restore(
            id='EPR010',
            key='generic-EPS-EPS10ChargeReserve',
            name='',
            definition='FrameworkRequirements::EPS10ChargeReserve',
            text='The nominal charge state shall retain reserve $$soc_reserve_min$$ within maximum depth of discharge $$dod_max$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-10 | Study: eps_energy_segment or eps_battery_step charge state extrema with applicable cycle-life limits | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-10 | Study: eps_energy_segment or eps_battery_step charge state extrema with applicable cycle-life limits | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('soc_min'),
                Parameter('soc_max'),
                Parameter('soc_reserve_min'),
                Parameter('dod_max'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS10ChargeReserve'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps012 = session.restore(
        GenericRequirement.restore(
            id='EPS012',
            key='generic-EPS-EPS12',
            name='',
            definition='FrameworkRequirements::EPS12',
            text='EPS-12. The EPS shall provide at least $$required_service_s$$ of essential load service during the declared survival scenario.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-12 | Study: Chained eps_energy_segment survival intervals with approved shedding and initial state | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-12 | Study: Chained eps_energy_segment survival intervals with approved shedding and initial state | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('required_service_s', unit='s'),
                Parameter('assessed_service_s', unit='s'),
                Parameter('unserved_energy_J', unit='J'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS12'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr011 = session.restore(
        GenericRequirement.restore(
            id='EPR011',
            key='generic-EPS-EPS12EnergyReserve',
            name='',
            definition='FrameworkRequirements::EPS12EnergyReserve',
            text='The survival stored energy shall remain between exceptional reserve $$energy_reserve_J$$ and retained capacity $$pack_eol_J$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-12 | Study: eps_energy_segment survival energy bounds with separately approved exceptional limits | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-12 | Study: eps_energy_segment survival energy bounds with separately approved exceptional limits | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('energy_min_J', unit='J'),
                Parameter('energy_max_J', unit='J'),
                Parameter('energy_reserve_J', unit='J'),
                Parameter('pack_eol_J', unit='J'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS12EnergyReserve'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr012 = session.restore(
        GenericRequirement.restore(
            id='EPR012',
            key='generic-EPS-EPS12ChargeReserve',
            name='',
            definition='FrameworkRequirements::EPS12ChargeReserve',
            text='The survival charge state shall retain exceptional reserve $$soc_reserve_min$$ throughout essential load service.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-12 | Study: eps_energy_segment or eps_battery_step survival charge bounds | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-12 | Study: eps_energy_segment or eps_battery_step survival charge bounds | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('soc_min'),
                Parameter('soc_max'),
                Parameter('soc_reserve_min'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS12ChargeReserve'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr013 = session.restore(
        GenericRequirement.restore(
            id='EPR013',
            key='generic-EPS-EPS12Recovery',
            name='',
            definition='FrameworkRequirements::EPS12Recovery',
            text='The EPS shall reach its required survival recovery state within $$recovery_limit_s$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-12 | Study: Explicit recovery energy segments and electrical service checks | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-12 | Study: Explicit recovery energy segments and electrical service checks | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('recovery_time_s', unit='s'),
                Parameter('recovery_limit_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS12Recovery'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps013 = session.restore(
        GenericRequirement.restore(
            id='EPS013',
            key='generic-EPS-EPS13',
            name='',
            definition='FrameworkRequirements::EPS13',
            text='EPS-13. EPS component temperatures shall remain within their state-specific interval from $$temp_limit_min_K$$ to $$temp_limit_max_K$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-13 | Study: eps_thermal or electrothermal bounds using eps_battery_step resistor heat at the declared cell, case or junction node | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-13 | Study: eps_thermal or electrothermal bounds using eps_battery_step resistor heat at the declared cell, case or junction node | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('assessed_temp_min_K', unit='K'),
                Parameter('assessed_temp_max_K', unit='K'),
                Parameter('temp_limit_min_K', unit='K'),
                Parameter('temp_limit_max_K', unit='K'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS13'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr014 = session.restore(
        GenericRequirement.restore(
            id='EPR014',
            key='generic-EPS-EPS13Charging',
            name='',
            definition='FrameworkRequirements::EPS13Charging',
            text='Battery charging temperatures shall remain between $$temp_limit_min_K$$ and $$temp_limit_max_K$$ throughout charging.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-13 | Study: eps_thermal charging interval with compatible battery and charger temperature facts | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-13 | Study: eps_thermal charging interval with compatible battery and charger temperature facts | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('assessed_temp_min_K', unit='K'),
                Parameter('assessed_temp_max_K', unit='K'),
                Parameter('temp_limit_min_K', unit='K'),
                Parameter('temp_limit_max_K', unit='K'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS13Charging'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr015 = session.restore(
        GenericRequirement.restore(
            id='EPR015',
            key='generic-EPS-EPS13Discharging',
            name='',
            definition='FrameworkRequirements::EPS13Discharging',
            text='Battery discharging temperatures shall remain between $$temp_limit_min_K$$ and $$temp_limit_max_K$$ throughout discharge.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-13 | Study: eps_thermal with separate discharge limits and explicit heater electrical load accounting | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-13 | Study: eps_thermal with separate discharge limits and explicit heater electrical load accounting | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('assessed_temp_min_K', unit='K'),
                Parameter('assessed_temp_max_K', unit='K'),
                Parameter('temp_limit_min_K', unit='K'),
                Parameter('temp_limit_max_K', unit='K'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS13Discharging'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps014 = session.restore(
        GenericRequirement.restore(
            id='EPS014',
            key='generic-EPS-EPS14',
            name='',
            definition='FrameworkRequirements::EPS14',
            text='EPS-14. Available solar surplus $$surplus_peak_W$$ shall remain within supported handling capacity $$surplus_capacity_W$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-14 | Study: eps_energy_segment full-charge acceptance and surplus with supported curtailment or shunt policy | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-14 | Study: eps_energy_segment full-charge acceptance and surplus with supported curtailment or shunt policy | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('surplus_peak_W', unit='W'),
                Parameter('surplus_capacity_W', unit='W'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS14'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr016 = session.restore(
        GenericRequirement.restore(
            id='EPR016',
            key='generic-EPS-EPS14ShuntHeat',
            name='',
            definition='FrameworkRequirements::EPS14ShuntHeat',
            text='Shunt dissipation $$dissipation_W$$ shall remain within thermal allowance $$dissipation_limit_W$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-14 | Study: eps_energy_segment shunt heat coupled to eps_thermal, keeping curtailed harvest separate | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-14 | Study: eps_energy_segment shunt heat coupled to eps_thermal, keeping curtailed harvest separate | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('dissipation_W', unit='W'),
                Parameter('dissipation_limit_W', unit='W'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS14ShuntHeat'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr017 = session.restore(
        GenericRequirement.restore(
            id='EPR017',
            key='generic-EPS-EPS14EndOfCharge',
            name='',
            definition='FrameworkRequirements::EPS14EndOfCharge',
            text='Accepted charging current after full charge shall remain within $$eoc_current_limit_A$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-14 | Study: Full-state eps_energy_segment intervals and the selected charge termination policy | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-14 | Study: Full-state eps_energy_segment intervals and the selected charge termination policy | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('eoc_current_A', unit='A'),
                Parameter('eoc_current_limit_A', unit='A'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS14EndOfCharge'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps015 = session.restore(
        GenericRequirement.restore(
            id='EPS015',
            key='generic-EPS-EPS15',
            name='',
            definition='FrameworkRequirements::EPS15',
            text='EPS-15. The EPS shall interrupt declared fault current within $$interruption_limit_s$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-15 | Study: eps_protection fault scenarios with threshold tolerance corners and applicable interruption limits | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-15 | Study: eps_protection fault scenarios with threshold tolerance corners and applicable interruption limits | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('fault_interruption_s', unit='s'),
                Parameter('interruption_limit_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS15'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr018 = session.restore(
        GenericRequirement.restore(
            id='EPR018',
            key='generic-EPS-EPS15FaultStress',
            name='',
            definition='FrameworkRequirements::EPS15FaultStress',
            text='Protected path fault stress $$fault_i2t_A2s$$ shall remain within allowance $$i2t_limit_A2s$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-15 | Study: eps_protection switched rectangular-current stress and independent path ratings | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-15 | Study: eps_protection switched rectangular-current stress and independent path ratings | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('fault_i2t_A2s', unit='A**2*s'),
                Parameter('i2t_limit_A2s', unit='A**2*s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS15FaultStress'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr019 = session.restore(
        GenericRequirement.restore(
            id='EPR019',
            key='generic-EPS-EPS15NoNuisance',
            name='',
            definition='FrameworkRequirements::EPS15NoNuisance',
            text='The protected path shall supply legitimate current $$legitimate_current_A$$ for $$legitimate_duration_s$$ without nuisance trips.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-15 | Study: eps_protection nominal workload and no-trip pulse cases | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-15 | Study: eps_protection nominal workload and no-trip pulse cases | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('legitimate_current_A', unit='A'),
                Parameter('legitimate_duration_s', unit='s'),
                Parameter('nuisance_trip_count', value_type=int),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS15NoNuisance'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr020 = session.restore(
        GenericRequirement.restore(
            id='EPR020',
            key='generic-EPS-EPS15SafeOperatingArea',
            name='',
            definition='FrameworkRequirements::EPS15SafeOperatingArea',
            text='Protection components shall support fault current $$pulse_current_A$$ at voltage $$fault_voltage_V$$ for duration $$pulse_duration_s$$ within their safe operating area.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-15 | Study: Sourced device safe operating area at the declared temperature, waveform and duration | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-15 | Study: Sourced device safe operating area at the declared temperature, waveform and duration | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('pulse_current_A', unit='A'),
                Parameter('fault_voltage_V', unit='V'),
                Parameter('pulse_duration_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS15SafeOperatingArea'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps016 = session.restore(
        GenericRequirement.restore(
            id='EPS016',
            key='generic-EPS-EPS16',
            name='',
            definition='FrameworkRequirements::EPS16',
            text='EPS-16. The EPS shall enter the specified battery protective state at undervoltage threshold $$uv_trip_V$$ or overvoltage threshold $$ov_trip_V$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-16 | Study: eps_protection battery UV and OV cases with sourced threshold bounds | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-16 | Study: eps_protection battery UV and OV cases with sourced threshold bounds | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('uv_trip_V', unit='V'),
                Parameter('ov_trip_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS16'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr021 = session.restore(
        GenericRequirement.restore(
            id='EPR021',
            key='generic-EPS-EPS16Reset',
            name='',
            definition='FrameworkRequirements::EPS16Reset',
            text='The EPS shall reset battery protection within its hysteresis interval from $$uv_reset_V$$ to $$ov_reset_V$$ according to the declared reset policy.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-16 | Study: eps_protection hysteresis, delays, reset policy and recharge-path cases | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-16 | Study: eps_protection hysteresis, delays, reset policy and recharge-path cases | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('uv_trip_V', unit='V'),
                Parameter('uv_reset_V', unit='V'),
                Parameter('ov_reset_V', unit='V'),
                Parameter('ov_trip_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS16Reset'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps017 = session.restore(
        GenericRequirement.restore(
            id='EPS017',
            key='generic-EPS-EPS17',
            name='',
            definition='FrameworkRequirements::EPS17',
            text='EPS-17. Inhibited output voltage $$inhibited_output_V$$ shall remain within permitted unpowered-state bound $$inhibited_voltage_limit_V$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-17 | Study: eps_protection inhibit truth-table cases and actual connected circuit voltage evidence | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-17 | Study: eps_protection inhibit truth-table cases and actual connected circuit voltage evidence | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('inhibited_output_V', unit='V'),
                Parameter('inhibited_voltage_limit_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS17'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr022 = session.restore(
        GenericRequirement.restore(
            id='EPR022',
            key='generic-EPS-EPS17PowerOn',
            name='',
            definition='FrameworkRequirements::EPS17PowerOn',
            text='The EPS shall realize its specified power-on state within $$startup_limit_s$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-17 | Study: Power-on truth table and eps_converter_step startup with sourced output defaults | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-17 | Study: Power-on truth table and eps_converter_step startup with sourced output defaults | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('startup_time_s', unit='s'),
                Parameter('startup_limit_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS17PowerOn'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr023 = session.restore(
        GenericRequirement.restore(
            id='EPR023',
            key='generic-EPS-EPS17AutonomousProtection',
            name='',
            definition='FrameworkRequirements::EPS17AutonomousProtection',
            text='The EPS shall interrupt the declared fault within $$interruption_limit_s$$ when its processor is unavailable.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-17 | Study: eps_protection processor-unavailable cases and sourced autonomous protection circuitry | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-17 | Study: eps_protection processor-unavailable cases and sourced autonomous protection circuitry | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('fault_interruption_s', unit='s'),
                Parameter('interruption_limit_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS17AutonomousProtection'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps018 = session.restore(
        GenericRequirement.restore(
            id='EPS018',
            key='generic-EPS-EPS18',
            name='',
            definition='FrameworkRequirements::EPS18',
            text='EPS-18. The EPS service ports shall support required exchange rate $$required_rate_Hz$$ through compatible connected endpoints.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-18 | Study: Connected pin, return, direction, protocol, version, address and quantity compatibility with sourced interface rates | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-18 | Study: Connected pin, return, direction, protocol, version, address and quantity compatibility with sourced interface rates | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('required_rate_Hz', unit='Hz'),
                Parameter('supported_rate_Hz', unit='Hz'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS18'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr024 = session.restore(
        GenericRequirement.restore(
            id='EPR024',
            key='generic-EPS-EPS18Response',
            name='',
            definition='FrameworkRequirements::EPS18Response',
            text='The EPS service shall satisfy response bound $$response_limit_s$$ with assessed response time $$response_time_s$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-18 | Study: Declared telemetry and command response bounds in every required mode | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-18 | Study: Declared telemetry and command response bounds in every required mode | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('response_time_s', unit='s'),
                Parameter('response_limit_s', unit='s'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS18Response'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr025 = session.restore(
        GenericRequirement.restore(
            id='EPR025',
            key='generic-EPS-EPS18LogicLevels',
            name='',
            definition='FrameworkRequirements::EPS18LogicLevels',
            text='Transmitted levels $$signal_low_max_V$$ and $$signal_high_min_V$$ shall satisfy receiver thresholds $$receiver_low_max_V$$ and $$receiver_high_min_V$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-18 | Study: Sourced signal levels, operating limits and connected enable/inhibit polarity | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-18 | Study: Sourced signal levels, operating limits and connected enable/inhibit polarity | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('signal_low_max_V', unit='V'),
                Parameter('signal_high_min_V', unit='V'),
                Parameter('receiver_low_max_V', unit='V'),
                Parameter('receiver_high_min_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS18LogicLevels'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    eps020 = session.restore(
        GenericRequirement.restore(
            id='EPS020',
            key='generic-EPS-EPS20',
            name='',
            definition='FrameworkRequirements::EPS20',
            text='EPS-20. Installed EPS envelopes shall retain clearance of at least $$required_clearance_m$$ in every required installation and deployment state.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-20 | Study: eps_geometry containment and keep-out cases with conservative clearance bounds | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-20 | Study: eps_geometry containment and keep-out cases with conservative clearance bounds | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('clearance_bound_m', unit='m'),
                Parameter('required_clearance_m', unit='m'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS20'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr026 = session.restore(
        GenericRequirement.restore(
            id='EPR026',
            key='generic-EPS-EPS20StackHeight',
            name='',
            definition='FrameworkRequirements::EPS20StackHeight',
            text='The installed stack height $$stack_height_m$$ shall remain within allocation $$stack_allocation_m$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-20 | Study: Installation frame, mounting, harness and connector envelopes | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-20 | Study: Installation frame, mounting, harness and connector envelopes | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('stack_height_m', unit='m'),
                Parameter('stack_allocation_m', unit='m'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS20StackHeight'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    epr027 = session.restore(
        GenericRequirement.restore(
            id='EPR027',
            key='generic-EPS-EPS20ArrayPacking',
            name='',
            definition='FrameworkRequirements::EPS20ArrayPacking',
            text='Array active area $$array_active_area_m2$$ shall fit usable face area $$usable_face_area_m2$$ at packing fraction $$packing_fraction$$.',
            kind='Requirement',
            rationale='final_report/eps-requirements.tex#EPS-20 | Study: eps_sizing cell assembly packing, with fixed-panel envelopes assessed separately | Supply applicable bounds and independently assigned limits.',
            origin='final_report/eps-requirements.tex#EPS-20 | Study: eps_sizing cell assembly packing, with fixed-panel envelopes assessed separately | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('array_active_area_m2', unit='m**2'),
                Parameter('usable_face_area_m2', unit='m**2'),
                Parameter('packing_fraction'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::EPS20ArrayPacking'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    cal001 = session.restore(
        GenericRequirement.restore(
            id='CAL001',
            key='generic-EPS-PVModelFit',
            name='',
            definition='FrameworkRequirements::PVModelFit',
            text='The photovoltaic model shall reproduce supplied current samples within RMS error $$pv_fit_limit_A$$.',
            kind='Requirement',
            rationale='final_report/requirements.tex#FR-22 | Study: eps_fit local affine PV law with checked samples and independent model applicability | Supply applicable bounds and independently assigned limits.',
            origin='final_report/requirements.tex#FR-22 | Study: eps_fit local affine PV law with checked samples and independent model applicability | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('pv_fit_rmse_A', unit='A'),
                Parameter('pv_fit_limit_A', unit='A'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::PVModelFit'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    cal002 = session.restore(
        GenericRequirement.restore(
            id='CAL002',
            key='generic-EPS-BatteryModelFit',
            name='',
            definition='FrameworkRequirements::BatteryModelFit',
            text='The battery electrical model shall reproduce supplied voltage samples within RMS error $$battery_fit_limit_V$$.',
            kind='Requirement',
            rationale='final_report/requirements.tex#FR-22 | Study: eps_fit battery OCV and resistance with identified data conditions | Supply applicable bounds and independently assigned limits.',
            origin='final_report/requirements.tex#FR-22 | Study: eps_fit battery OCV and resistance with identified data conditions | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('battery_fit_rmse_V', unit='V'),
                Parameter('battery_fit_limit_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::BatteryModelFit'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    cal003 = session.restore(
        GenericRequirement.restore(
            id='CAL003',
            key='generic-EPS-ConverterModelFit',
            name='',
            definition='FrameworkRequirements::ConverterModelFit',
            text='The converter response model shall reproduce supplied voltage samples within RMS error $$converter_fit_limit_V$$.',
            kind='Requirement',
            rationale='final_report/requirements.tex#FR-22 | Study: eps_fit first-order response with a supplied asymptote and sufficient excitation | Supply applicable bounds and independently assigned limits.',
            origin='final_report/requirements.tex#FR-22 | Study: eps_fit first-order response with a supplied asymptote and sufficient excitation | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('converter_fit_rmse_V', unit='V'),
                Parameter('converter_fit_limit_V', unit='V'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::ConverterModelFit'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    cal004 = session.restore(
        GenericRequirement.restore(
            id='CAL004',
            key='generic-EPS-ThermalModelFit',
            name='',
            definition='FrameworkRequirements::ThermalModelFit',
            text='The thermal model shall reproduce supplied node temperatures within RMS error $$thermal_fit_limit_K$$.',
            kind='Requirement',
            rationale='final_report/requirements.tex#FR-22 | Study: eps_fit thermal response at a declared node, with separate prediction validation | Supply applicable bounds and independently assigned limits.',
            origin='final_report/requirements.tex#FR-22 | Study: eps_fit thermal response at a declared node, with separate prediction validation | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('thermal_fit_rmse_K', unit='K'),
                Parameter('thermal_fit_limit_K', unit='K'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::ThermalModelFit'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    ram001 = session.restore(
        GenericRequirement.restore(
            id='RAM001',
            key='generic-EPS-MissionReliability',
            name='',
            definition='FrameworkRequirements::MissionReliability',
            text='The EPS shall retain mission reliability of at least $$reliability_min$$ over exposure $$ram_exposure_h$$.',
            kind='Requirement',
            rationale='final_report/requirements.tex#FR-27 | Study: eps_ram authored fault tree with sourced probabilities or rates, explicit independence and common-cause treatment | Supply applicable bounds and independently assigned limits.',
            origin='final_report/requirements.tex#FR-27 | Study: eps_ram authored fault tree with sourced probabilities or rates, explicit independence and common-cause treatment | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('mission_reliability'),
                Parameter('reliability_min'),
                Parameter('ram_exposure_h', unit='h'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::MissionReliability'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    ram002 = session.restore(
        GenericRequirement.restore(
            id='RAM002',
            key='generic-EPS-ConditionalFailureProbability',
            name='',
            definition='FrameworkRequirements::ConditionalFailureProbability',
            text='The conditional EPS failure probability shall remain at most $$conditional_probability_limit$$ for the declared failure evidence.',
            kind='Requirement',
            rationale='final_report/requirements.tex#FR-27 | Study: eps_ram conditional failure calculation, preserving undefined zero-probability conditioning as pending | Supply applicable bounds and independently assigned limits.',
            origin='final_report/requirements.tex#FR-27 | Study: eps_ram conditional failure calculation, preserving undefined zero-probability conditioning as pending | Supply applicable bounds and independently assigned limits.',
            parameters=(
                Parameter('conditional_failure_probability'),
                Parameter('conditional_probability_limit'),
            ),
            template=session.catalog.by_requirement['FrameworkRequirements::ConditionalFailureProbability'],
        ),
        projection_fields=(),
        verification_style='condition',
    )

    mas001 = session.restore(
        MassLimit.restore(
            id='MAS001',
            key='mass-mission',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The spacecraft mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSS003.mass_kg, MSS001.mass_kg, MSS002.mass_kg, MSS004.mass_kg, MSS008.mass_kg, MSS007.mass_kg, MSS005.mass_kg, MSS006.mass_kg, MSS009.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSS003.mass_allocation_kg, MSS001.mass_allocation_kg, MSS002.mass_allocation_kg, MSS004.mass_allocation_kg, MSS008.mass_allocation_kg, MSS007.mass_allocation_kg, MSS005.mass_allocation_kg, MSS006.mass_allocation_kg, MSS009.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    mss001 = session.restore(
        MassLimit.restore(
            id='MSS001',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsys',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC001.mass_kg, MSC002.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC001.mass_allocation_kg, MSC002.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    mss002 = session.restore(
        MassLimit.restore(
            id='MSS002',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC003.mass_kg, MSC004.mass_kg, MSC005.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC003.mass_allocation_kg, MSC004.mass_allocation_kg, MSC005.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    mss003 = session.restore(
        MassLimit.restore(
            id='MSS003',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndCont',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC006.mass_kg, MSC007.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC006.mass_allocation_kg, MSC007.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    mss004 = session.restore(
        MassLimit.restore(
            id='MSS004',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControl',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC008.mass_kg, MSC009.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC008.mass_allocation_kg, MSC009.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    mss005 = session.restore(
        MassLimit.restore(
            id='MSS005',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsy',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC010.mass_kg, MSC011.mass_kg, MSC012.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC010.mass_allocation_kg, MSC011.mass_allocation_kg, MSC012.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    mss006 = session.restore(
        MassLimit.restore(
            id='MSS006',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC016.mass_kg, MSC013.mass_kg, MSC015.mass_kg, MSC014.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC016.mass_allocation_kg, MSC013.mass_allocation_kg, MSC015.mass_allocation_kg, MSC014.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    mss007 = session.restore(
        MassLimit.restore(
            id='MSS007',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC020.mass_kg, MSC018.mass_kg, MSC017.mass_kg, MSC019.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC020.mass_allocation_kg, MSC018.mass_allocation_kg, MSC017.mass_allocation_kg, MSC019.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    mss008 = session.restore(
        MassLimit.restore(
            id='MSS008',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC021.mass_kg, MSC025.mass_kg, MSC023.mass_kg, MSC024.mass_kg, MSC022.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC021.mass_allocation_kg, MSC025.mass_allocation_kg, MSC023.mass_allocation_kg, MSC024.mass_allocation_kg, MSC022.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc001 = session.restore(
        ComponentMassLimit.restore(
            id='MSC001',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsys_1',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc002 = session.restore(
        ComponentMassLimit.restore(
            id='MSC002',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsys_2',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc003 = session.restore(
        ComponentMassLimit.restore(
            id='MSC003',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-Proce',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc004 = session.restore(
        ComponentMassLimit.restore(
            id='MSC004',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-Recei',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc005 = session.restore(
        ComponentMassLimit.restore(
            id='MSC005',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-Trans',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc006 = session.restore(
        ComponentMassLimit.restore(
            id='MSC006',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndCont_1',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc007 = session.restore(
        ComponentMassLimit.restore(
            id='MSC007',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndCont_2',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc008 = session.restore(
        ComponentMassLimit.restore(
            id='MSC008',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControl_1',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc009 = session.restore(
        ComponentMassLimit.restore(
            id='MSC009',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControl_2',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc010 = session.restore(
        ComponentMassLimit.restore(
            id='MSC010',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsy_1',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc011 = session.restore(
        ComponentMassLimit.restore(
            id='MSC011',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsy_2',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc012 = session.restore(
        ComponentMassLimit.restore(
            id='MSC012',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsy_3',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc013 = session.restore(
        ComponentMassLimit.restore(
            id='MSC013',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSens',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc014 = session.restore(
        ComponentMassLimit.restore(
            id='MSC014',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSour',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc015 = session.restore(
        ComponentMassLimit.restore(
            id='MSC015',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSink',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc016 = session.restore(
        ComponentMassLimit.restore(
            id='MSC016',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ProcessorAn',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc017 = session.restore(
        ComponentMassLimit.restore(
            id='MSC017',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Propella',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc018 = session.restore(
        ComponentMassLimit.restore(
            id='MSC018',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Propella_1',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc019 = session.restore(
        ComponentMassLimit.restore(
            id='MSC019',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Thruster',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc020 = session.restore(
        ComponentMassLimit.restore(
            id='MSC020',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Processo',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc021 = session.restore(
        ComponentMassLimit.restore(
            id='MSC021',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc022 = session.restore(
        ComponentMassLimit.restore(
            id='MSC022',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc023 = session.restore(
        ComponentMassLimit.restore(
            id='MSC023',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-ProcessorAndM',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc024 = session.restore(
        ComponentMassLimit.restore(
            id='MSC024',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-RegulatorsAnd',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc025 = session.restore(
        ComponentMassLimit.restore(
            id='MSC025',
            key='mass-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircuits',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vol001 = session.restore(
        VolumeLimit.restore(
            id='VOL001',
            key='volume-mission',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The spacecraft volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLS003.volume_m3, VLS001.volume_m3, VLS002.volume_m3, VLS004.volume_m3, VLS008.volume_m3, VLS007.volume_m3, VLS005.volume_m3, VLS006.volume_m3, VLS009.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLS003.volume_allocation_m3, VLS001.volume_allocation_m3, VLS002.volume_allocation_m3, VLS004.volume_allocation_m3, VLS008.volume_allocation_m3, VLS007.volume_allocation_m3, VLS005.volume_allocation_m3, VLS006.volume_allocation_m3, VLS009.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls001 = session.restore(
        VolumeLimit.restore(
            id='VLS001',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubs',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC001.volume_m3, VLC002.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC001.volume_allocation_m3, VLC002.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls002 = session.restore(
        VolumeLimit.restore(
            id='VLS002',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC003.volume_m3, VLC004.volume_m3, VLC005.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC003.volume_allocation_m3, VLC004.volume_allocation_m3, VLC005.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls003 = session.restore(
        VolumeLimit.restore(
            id='VLS003',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndCo',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC006.volume_m3, VLC007.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC006.volume_allocation_m3, VLC007.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls004 = session.restore(
        VolumeLimit.restore(
            id='VLS004',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndContr',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC008.volume_m3, VLC009.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC008.volume_allocation_m3, VLC009.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls005 = session.restore(
        VolumeLimit.restore(
            id='VLS005',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSub',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC010.volume_m3, VLC011.volume_m3, VLC012.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC010.volume_allocation_m3, VLC011.volume_allocation_m3, VLC012.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls006 = session.restore(
        VolumeLimit.restore(
            id='VLS006',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC016.volume_m3, VLC013.volume_m3, VLC015.volume_m3, VLC014.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC016.volume_allocation_m3, VLC013.volume_allocation_m3, VLC015.volume_allocation_m3, VLC014.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls007 = session.restore(
        VolumeLimit.restore(
            id='VLS007',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC020.volume_m3, VLC018.volume_m3, VLC017.volume_m3, VLC019.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC020.volume_allocation_m3, VLC018.volume_allocation_m3, VLC017.volume_allocation_m3, VLC019.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls008 = session.restore(
        VolumeLimit.restore(
            id='VLS008',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC021.volume_m3, VLC025.volume_m3, VLC023.volume_m3, VLC024.volume_m3, VLC022.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC021.volume_allocation_m3, VLC025.volume_allocation_m3, VLC023.volume_allocation_m3, VLC024.volume_allocation_m3, VLC022.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc001 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC001',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubs_1',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc002 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC002',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubs_2',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc003 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC003',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-Pro',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc004 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC004',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-Rec',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc005 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC005',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-Tra',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc006 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC006',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndCo_1',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc007 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC007',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndCo_2',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc008 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC008',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndContr_1',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc009 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC009',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndContr_2',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc010 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC010',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSub_1',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc011 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC011',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSub_2',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc012 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC012',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSub_3',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc013 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC013',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSe',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc014 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC014',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSo',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc015 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC015',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSi',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc016 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC016',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-Processor',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc017 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC017',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Propel',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc018 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC018',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Propel_1',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc019 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC019',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Thrust',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc020 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC020',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Proces',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc021 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC021',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc022 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC022',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc023 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC023',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-ProcessorAn',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc024 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC024',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-RegulatorsA',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc025 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC025',
            key='volume-2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircui',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    pay = session.restore(
        Payload.restore(
            id='PAY',
            key='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2',
            name='Payload',
            definition='SpaceSegment::CubeSat::PayloadSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    ins = session.restore(
        Instrument.restore(
            id='INS',
            key='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-Instrument',
            name='Instrument',
            definition='SpaceSegment::CubeSat::PayloadSubsystem::Instrument',
            selection=False,
        ),
        projection_fields=(),
    )

    aap = session.restore(
        ProcessorAndMemory.restore(
            id='AAP',
            key='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-ProcessorAndMemory',
            name='Processor and Memory',
            definition='SpaceSegment::CubeSat::PayloadSubsystem::ProcessorAndMemory',
            selection=False,
        ),
        projection_fields=(),
    )

    mss009 = session.restore(
        MassLimit.restore(
            id='MSS009',
            key='mass-8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2',
            name='',
            definition='ResourceBudgetModel::MassLimit',
            text='The subsystem mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg', expression='sum([MSC026.mass_kg, MSC027.mass_kg])'),
                Parameter('allocated_mass_kg', unit='kg', expression='sum([MSC026.mass_allocation_kg, MSC027.mass_allocation_kg])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc026 = session.restore(
        ComponentMassLimit.restore(
            id='MSC026',
            key='mass-8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-Instrument',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    msc027 = session.restore(
        ComponentMassLimit.restore(
            id='MSC027',
            key='mass-8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-ProcessorAndMemory',
            name='',
            definition='ResourceBudgetModel::ComponentMassLimit',
            text='The installed component mass shall not exceed $$mass_allocation_kg$$.',
            kind='Requirement',
            rationale='Enter total installed mass, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('mass_allocation_kg', unit='kg'),
                Parameter('mass_kg', unit='kg'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vls009 = session.restore(
        VolumeLimit.restore(
            id='VLS009',
            key='volume-8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2',
            name='',
            definition='ResourceBudgetModel::VolumeLimit',
            text='The subsystem volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3', expression='sum([VLC026.volume_m3, VLC027.volume_m3])'),
                Parameter('allocated_volume_m3', unit='m^3', expression='sum([VLC026.volume_allocation_m3, VLC027.volume_allocation_m3])'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc026 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC026',
            key='volume-8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-Instrument',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    vlc027 = session.restore(
        ComponentVolumeLimit.restore(
            id='VLC027',
            key='volume-8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-ProcessorAndMemory',
            name='',
            definition='ResourceBudgetModel::ComponentVolumeLimit',
            text='The installed component volume shall not exceed $$volume_allocation_m3$$.',
            kind='Requirement',
            rationale='Enter total installed volume, including quantity and auxiliaries, using disjoint hardware accounting boundaries.',
            origin='',
            parameters=(
                Parameter('volume_allocation_m3', unit='m^3'),
                Parameter('volume_m3', unit='m^3'),
            ),
        ),
        projection_fields=(),
        verification_style='auto',
    )

    gnd = session.restore(
        GroundStation.restore(
            id='GND',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50',
            name='Ground Station',
            definition='GroundSegment::GroundStation',
            selection=False,
        ),
        projection_fields=(),
    )

    pls = session.restore(
        PlanAndSchedule.restore(
            id='PLS',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50-PlanAndScheduleSubsystem',
            name='Plan and Schedule',
            definition='GroundSegment::PlanAndScheduleSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    scc = session.restore(
        SpacecraftCommand.restore(
            id='SCC',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50-SpacecraftCommandSubsystem',
            name='Spacecraft Command',
            definition='GroundSegment::SpacecraftCommandSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    gec = session.restore(
        GroundEquipmentControl.restore(
            id='GEC',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50-GroundEquipmentControlSubsystem',
            name='Ground Equipment Control',
            definition='GroundSegment::GroundEquipmentControlSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    sgc = session.restore(
        SpaceGroundCommunication.restore(
            id='SGC',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50-SpaceGroundCommunicationSubsystem',
            name='Space Ground Communication',
            definition='GroundSegment::SpaceGroundCommunicationSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    mdp = session.restore(
        MissionDataProcessing.restore(
            id='MDP',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50-MissionDataProcessingSubsystem',
            name='Mission Data Processing',
            definition='GroundSegment::MissionDataProcessingSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    mdd = session.restore(
        MissionDataDissemination.restore(
            id='MDD',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50-MissionDataDisseminationSubsystem',
            name='Mission Data Dissemination',
            definition='GroundSegment::MissionDataDisseminationSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    net = session.restore(
        Network.restore(
            id='NET',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50-NetworkSubsystem',
            name='Network',
            definition='GroundSegment::NetworkSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    tlm = session.restore(
        TelemetryProcessing.restore(
            id='TLM',
            key='2b51eaed-8d07-4609-bb98-3bffc86bae50-TelemetryProcessingSubsystem',
            name='Telemetry Processing',
            definition='GroundSegment::TelemetryProcessingSubsystem',
            selection=False,
        ),
        projection_fields=(),
    )

    # Connect the populated objects after every identity is registered.
    orb.owner = mission
    orb001.owner = mission
    orb001.sources = ()
    orb001.affected = (orb,)
    orb001.verifications = (
        VerificationMethod('condition', '(((((altitude_km > 0) and (earthRadius_km > 0)) and (gravitationalParameter_km3_s2 > 0)) and (orbit_period_s > 0)) and (orbit_period_s == ((2 * math.pi) * math.sqrt((((earthRadius_km + altitude_km) ** 3) / gravitationalParameter_km3_s2)))))', key='condition'),
    )
    orb002.owner = mission
    orb002.sources = (orb001,)
    orb002.affected = (orb,)
    orb002.verifications = (
        VerificationMethod('condition', '(((((((((altitude_km > 0) and (earthRadius_km > 0)) and (orbit_period_s > 0)) and (sunlight_s > 0)) and (eclipse_s > 0)) and (horizon_angle_rad == math.acos((earthRadius_km / (earthRadius_km + altitude_km))))) and (sunlight_s == ((0.5 + (horizon_angle_rad / math.pi)) * orbit_period_s))) and (eclipse_s == ((0.5 - (horizon_angle_rad / math.pi)) * orbit_period_s))) and (abs(((sunlight_s + eclipse_s) - orbit_period_s)) <= (1e-9 * orbit_period_s)))', key='condition'),
    )
    orb003.owner = mission
    orb003.sources = (orb002,)
    orb003.affected = (orb,)
    orb003.verifications = (
        VerificationMethod('condition', '((((orbit_period_s > 0) and (sunlight_s > 0)) and (eclipse_s > 0)) and (abs(((sunlight_s + eclipse_s) - orbit_period_s)) <= (1e-9 * orbit_period_s)))', key='condition'),
    )
    bus.owner = mission
    cdh.owner = bus
    com.owner = bus
    adc.owner = bus
    gnc.owner = bus
    str.owner = bus
    the.owner = bus
    pro.owner = bus
    eps.owner = bus
    aaa.owner = cdh
    pcm.owner = cdh
    aab.owner = com
    rec.owner = com
    tra.owner = com
    sfw.owner = adc
    act.owner = adc
    sen.owner = adc
    acc.owner = gnc
    gns.owner = gnc
    aac.owner = gnc
    aad.owner = str
    dep.owner = str
    sta.owner = str
    aae.owner = the
    aaf.owner = the
    aag.owner = the
    aah.owner = the
    aai.owner = the
    aaj.owner = pro
    aak.owner = pro
    thr.owner = pro
    aal.owner = pro
    aam.owner = pro
    bat.owner = eps
    sol.owner = eps
    aan.owner = eps
    reg.owner = eps
    pcs.owner = eps
    aao.owner = eps
    siz001.owner = eps
    siz001.sources = (orb002,)
    siz001.affected = (bat, sol)
    siz001.verifications = (
        VerificationMethod('condition', '((((((((((sunlight_power_W >= 0) and (eclipse_power_W >= 0)) and (sunlight_duty >= 0)) and (sunlight_duty <= 1)) and (eclipse_duty >= 0)) and (eclipse_duty <= 1)) and (sunlight_s > 0)) and (eclipse_s > 0)) and (sunlight_energy_J == ((sunlight_power_W * sunlight_duty) * sunlight_s))) and (eclipse_energy_J == ((eclipse_power_W * eclipse_duty) * eclipse_s)))', key='condition'),
    )
    siz002.owner = eps
    siz002.sources = (siz001, orb002)
    siz002.affected = (sol, reg)
    siz002.verifications = (
        VerificationMethod('condition', '((((((((sunlight_energy_J >= 0) and (eclipse_energy_J >= 0)) and (sunlight_s > 0)) and (sunlight_efficiency > 0)) and (sunlight_efficiency <= 1)) and (eclipse_efficiency > 0)) and (eclipse_efficiency <= 1)) and (panel_min_W == (((sunlight_energy_J / sunlight_efficiency) + (eclipse_energy_J / eclipse_efficiency)) / sunlight_s)))', key='condition'),
    )
    siz003.owner = eps
    siz003.sources = ()
    siz003.affected = (sol,)
    siz003.verifications = (
        VerificationMethod('condition', '(((cell_eol_V > 0) and (cell_eol_A > 0)) and (cell_eol_W == (cell_eol_V * cell_eol_A)))', key='condition'),
    )
    siz004.owner = eps
    siz004.sources = (siz002, siz003)
    siz004.affected = (sol,)
    siz004.verifications = (
        VerificationMethod('condition', '((((((panel_min_W >= 0) and (cell_eol_W > 0)) and (required_cells == (panel_min_W / cell_eol_W))) and (minimum_cells == (- math.floor((- required_cells))))) and (installed_cells > 0)) and (installed_cells >= minimum_cells))', key='condition'),
    )
    siz005.owner = eps
    siz005.sources = (orb001,)
    siz005.affected = (bat,)
    siz005.verifications = (
        VerificationMethod('condition', '(((((orbit_period_s > 0) and (lifetime_years > 0)) and (days_per_year > 0)) and (orbits_per_day == (86400 / orbit_period_s))) and (required_cycles == ((lifetime_years * days_per_year) * orbits_per_day)))', key='condition'),
    )
    siz006.owner = eps
    siz006.sources = (siz005,)
    siz006.affected = (bat,)
    siz006.verifications = (
        VerificationMethod('condition', '(((((((((((required_cycles > 0) and (cycle_a > 0)) and (cycle_b < 0)) and (fit_dod_min > 0)) and (fit_dod_min <= fit_dod_max)) and (fit_dod_max <= 1)) and (dod_max >= fit_dod_min)) and (dod_max <= fit_dod_max)) and (dod_cycle_limit == ((required_cycles / cycle_a) ** (1 / cycle_b)))) and (supported_cycles == (cycle_a * (dod_max ** cycle_b)))) and (supported_cycles >= required_cycles))', key='condition'),
    )
    siz007.owner = eps
    siz007.sources = (siz001, siz006, siz005)
    siz007.affected = (bat,)
    siz007.verifications = (
        VerificationMethod('condition', '(((((((((((((((eclipse_energy_J >= 0) and (dod_max > 0)) and (dod_max <= 1)) and (degradation_margin >= 0)) and (battery_min_J == ((eclipse_energy_J / dod_max) * (1 + degradation_margin)))) and (required_cycles > 0)) and (cycle_a > 0)) and (cycle_b < 0)) and (fit_dod_min > 0)) and (fit_dod_min <= fit_dod_max)) and (fit_dod_max <= 1)) and (dod_max >= fit_dod_min)) and (dod_max <= fit_dod_max)) and (supported_cycles == (cycle_a * (dod_max ** cycle_b)))) and (supported_cycles >= required_cycles))', key='condition'),
    )
    siz008.owner = eps
    siz008.sources = (siz007,)
    siz008.affected = (bat,)
    siz008.verifications = (
        VerificationMethod('condition', '((((((battery_min_J >= 0) and (pack_bol_J > 0)) and (pack_bol_J >= battery_min_J)) and (retained_energy_factor > 0)) and (retained_energy_factor <= 1)) and (pack_eol_J == (retained_energy_factor * pack_bol_J)))', key='condition'),
    )
    eps002.owner = eps
    eps002.sources = (orb002, siz002)
    eps002.affected = (sol,)
    eps008.owner = eps
    eps008.sources = (siz008, siz007)
    eps008.affected = (bat,)
    eps009.owner = eps
    eps009.sources = (siz005, siz006)
    eps009.affected = (bat,)
    eps011.owner = eps
    eps011.sources = ()
    eps011.affected = (bat, sol)
    eps019.owner = eps
    eps019.sources = ()
    eps019.affected = (bat, sol, aan, reg, pcs)
    eps021.owner = eps
    eps021.sources = ()
    eps021.affected = (aan, aao)
    siz011.owner = eps
    siz011.sources = (siz002,)
    siz011.affected = (sol, reg)
    siz011.verifications = (
        VerificationMethod('condition', '((((sunlight_efficiency > 0) and (sunlight_efficiency <= 1)) and (eclipse_efficiency > 0)) and (eclipse_efficiency <= 1))', key='condition'),
    )
    siz013.owner = eps
    siz013.sources = (siz006,)
    siz013.affected = (bat,)
    siz013.verifications = (
        VerificationMethod('condition', '(((((((cycle_a > 0) and (cycle_b < 0)) and (fit_dod_min > 0)) and (fit_dod_min <= fit_dod_max)) and (fit_dod_max <= 1)) and (dod_max >= fit_dod_min)) and (dod_max <= fit_dod_max))', key='condition'),
    )
    siz014.owner = eps
    siz014.sources = (siz006,)
    siz014.affected = (bat,)
    siz014.verifications = (
        VerificationMethod('condition', '((((dod_max > 0) and (dod_max <= 1)) and (dod_cycle_limit > 0)) and (dod_max <= dod_cycle_limit))', key='condition'),
    )
    siz016.owner = eps
    siz016.sources = (siz008,)
    siz016.affected = (bat,)
    siz016.verifications = (
        VerificationMethod('condition', '((((pack_bol_J > 0) and (retained_energy_factor > 0)) and (retained_energy_factor <= 1)) and (pack_eol_J == (retained_energy_factor * pack_bol_J)))', key='condition'),
    )
    eps047.owner = eps
    eps047.sources = (eps009,)
    eps047.affected = (bat,)
    eps052.owner = eps
    eps052.sources = (eps011,)
    eps052.affected = (bat, sol)
    eps053.owner = eps
    eps053.sources = (eps011,)
    eps053.affected = (bat, sol)
    eps078.owner = eps
    eps078.sources = (eps019,)
    eps078.affected = (bat, sol, aan, reg, pcs)
    eps088.owner = eps
    eps088.sources = (eps021,)
    eps088.affected = (aan, aao)
    eps089.owner = eps
    eps089.sources = (eps021,)
    eps089.affected = (aan, aao)
    eps001.owner = eps
    eps001.sources = ()
    eps001.affected = (bat, sol, aan, reg, pcs)
    eps003.owner = eps
    eps003.sources = ()
    eps003.affected = (sol, reg)
    epr001.owner = eps
    epr001.sources = (eps003,)
    epr001.affected = (sol, reg)
    epr002.owner = eps
    epr002.sources = (eps003,)
    epr002.affected = (sol, reg)
    eps004.owner = eps
    eps004.sources = ()
    eps004.affected = (reg,)
    mil001.owner = eps
    mil001.sources = ()
    mil001.affected = (reg, aao)
    eps005.owner = eps
    eps005.sources = ()
    eps005.affected = (bat, reg)
    epr003.owner = eps
    epr003.sources = (eps005,)
    epr003.affected = (bat, reg)
    epr004.owner = eps
    epr004.sources = (eps005,)
    epr004.affected = (bat, reg)
    epr005.owner = eps
    epr005.sources = (eps005,)
    epr005.affected = (bat, reg)
    eps006.owner = eps
    eps006.sources = ()
    eps006.affected = (bat, reg, pcs)
    epr006.owner = eps
    epr006.sources = (eps006,)
    epr006.affected = (bat, reg, pcs)
    eps007.owner = eps
    eps007.sources = ()
    eps007.affected = (bat, reg, pcs)
    epr007.owner = eps
    epr007.sources = (eps007,)
    epr007.affected = (bat, reg, pcs)
    epr008.owner = eps
    epr008.sources = (eps008,)
    epr008.affected = (bat,)
    eps010.owner = eps
    eps010.sources = ()
    eps010.affected = (bat, sol, reg, pcs)
    epr009.owner = eps
    epr009.sources = (eps010,)
    epr009.affected = (bat,)
    epr010.owner = eps
    epr010.sources = (eps010, eps009)
    epr010.affected = (bat,)
    eps012.owner = eps
    eps012.sources = ()
    eps012.affected = (bat, sol, reg, pcs)
    epr011.owner = eps
    epr011.sources = (eps012,)
    epr011.affected = (bat,)
    epr012.owner = eps
    epr012.sources = (eps012,)
    epr012.affected = (bat,)
    epr013.owner = eps
    epr013.sources = (eps012,)
    epr013.affected = (bat, sol, reg, pcs)
    eps013.owner = eps
    eps013.sources = ()
    eps013.affected = (bat, sol, aan, reg, pcs)
    epr014.owner = eps
    epr014.sources = (eps013, eps005)
    epr014.affected = (bat, reg)
    epr015.owner = eps
    epr015.sources = (eps013,)
    epr015.affected = (bat,)
    eps014.owner = eps
    eps014.sources = ()
    eps014.affected = (sol, reg, pcs)
    epr016.owner = eps
    epr016.sources = (eps014,)
    epr016.affected = (reg, pcs)
    epr017.owner = eps
    epr017.sources = (eps014, eps005)
    epr017.affected = (bat, reg)
    eps015.owner = eps
    eps015.sources = ()
    eps015.affected = (reg, pcs)
    epr018.owner = eps
    epr018.sources = (eps015,)
    epr018.affected = (pcs,)
    epr019.owner = eps
    epr019.sources = (eps015,)
    epr019.affected = (pcs,)
    epr020.owner = eps
    epr020.sources = (eps015,)
    epr020.affected = (pcs,)
    eps016.owner = eps
    eps016.sources = ()
    eps016.affected = (bat, reg, pcs, aao)
    epr021.owner = eps
    epr021.sources = (eps016,)
    epr021.affected = (bat, reg, pcs, aao)
    eps017.owner = eps
    eps017.sources = ()
    eps017.affected = (aan, pcs, aao)
    epr022.owner = eps
    epr022.sources = (eps017,)
    epr022.affected = (aan, pcs, aao)
    epr023.owner = eps
    epr023.sources = (eps017, eps015)
    epr023.affected = (aan, pcs, aao)
    eps018.owner = eps
    eps018.sources = ()
    eps018.affected = (aan, pcs, aao)
    epr024.owner = eps
    epr024.sources = (eps018,)
    epr024.affected = (aan, pcs, aao)
    epr025.owner = eps
    epr025.sources = (eps018,)
    epr025.affected = (aan, pcs, aao)
    eps020.owner = eps
    eps020.sources = ()
    eps020.affected = (bat, sol, aan, reg, pcs)
    epr026.owner = eps
    epr026.sources = (eps020,)
    epr026.affected = (bat, sol, aan, reg, pcs)
    epr027.owner = eps
    epr027.sources = (eps020, eps001)
    epr027.affected = (sol,)
    cal001.owner = eps
    cal001.sources = ()
    cal001.affected = (sol,)
    cal002.owner = eps
    cal002.sources = ()
    cal002.affected = (bat,)
    cal003.owner = eps
    cal003.sources = ()
    cal003.affected = (reg,)
    cal004.owner = eps
    cal004.sources = ()
    cal004.affected = (bat, sol, aan, reg, pcs)
    ram001.owner = eps
    ram001.sources = ()
    ram001.affected = (bat, sol, aan, reg, pcs)
    ram002.owner = eps
    ram002.sources = (ram001,)
    ram002.affected = (bat, sol, aan, reg, pcs)
    mas001.owner = mission
    mas001.sources = ()
    mas001.affected = (bus, pay)
    mas001.budget_scope = mission
    mas001.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    mss001.owner = cdh
    mss001.sources = (mas001,)
    mss001.affected = ()
    mss001.budget_scope = cdh
    mss001.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    mss002.owner = com
    mss002.sources = (mas001,)
    mss002.affected = ()
    mss002.budget_scope = com
    mss002.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    mss003.owner = adc
    mss003.sources = (mas001,)
    mss003.affected = ()
    mss003.budget_scope = adc
    mss003.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    mss004.owner = gnc
    mss004.sources = (mas001,)
    mss004.affected = ()
    mss004.budget_scope = gnc
    mss004.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    mss005.owner = str
    mss005.sources = (mas001,)
    mss005.affected = ()
    mss005.budget_scope = str
    mss005.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    mss006.owner = the
    mss006.sources = (mas001,)
    mss006.affected = ()
    mss006.budget_scope = the
    mss006.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    mss007.owner = pro
    mss007.sources = (mas001,)
    mss007.affected = ()
    mss007.budget_scope = pro
    mss007.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    mss008.owner = eps
    mss008.sources = (mas001,)
    mss008.affected = ()
    mss008.budget_scope = eps
    mss008.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc001.owner = cdh
    msc001.sources = (mss001,)
    msc001.affected = (aaa,)
    msc001.budget_scope = aaa
    msc001.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc002.owner = cdh
    msc002.sources = (mss001,)
    msc002.affected = (pcm,)
    msc002.budget_scope = pcm
    msc002.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc003.owner = com
    msc003.sources = (mss002,)
    msc003.affected = (aab,)
    msc003.budget_scope = aab
    msc003.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc004.owner = com
    msc004.sources = (mss002,)
    msc004.affected = (rec,)
    msc004.budget_scope = rec
    msc004.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc005.owner = com
    msc005.sources = (mss002,)
    msc005.affected = (tra,)
    msc005.budget_scope = tra
    msc005.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc006.owner = adc
    msc006.sources = (mss003,)
    msc006.affected = (act,)
    msc006.budget_scope = act
    msc006.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc007.owner = adc
    msc007.sources = (mss003,)
    msc007.affected = (sen,)
    msc007.budget_scope = sen
    msc007.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc008.owner = gnc
    msc008.sources = (mss004,)
    msc008.affected = (acc,)
    msc008.budget_scope = acc
    msc008.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc009.owner = gnc
    msc009.sources = (mss004,)
    msc009.affected = (gns,)
    msc009.budget_scope = gns
    msc009.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc010.owner = str
    msc010.sources = (mss005,)
    msc010.affected = (aad,)
    msc010.budget_scope = aad
    msc010.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc011.owner = str
    msc011.sources = (mss005,)
    msc011.affected = (dep,)
    msc011.budget_scope = dep
    msc011.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc012.owner = str
    msc012.sources = (mss005,)
    msc012.affected = (sta,)
    msc012.budget_scope = sta
    msc012.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc013.owner = the
    msc013.sources = (mss006,)
    msc013.affected = (aae,)
    msc013.budget_scope = aae
    msc013.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc014.owner = the
    msc014.sources = (mss006,)
    msc014.affected = (aaf,)
    msc014.budget_scope = aaf
    msc014.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc015.owner = the
    msc015.sources = (mss006,)
    msc015.affected = (aag,)
    msc015.budget_scope = aag
    msc015.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc016.owner = the
    msc016.sources = (mss006,)
    msc016.affected = (aah,)
    msc016.budget_scope = aah
    msc016.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc017.owner = pro
    msc017.sources = (mss007,)
    msc017.affected = (aaj,)
    msc017.budget_scope = aaj
    msc017.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc018.owner = pro
    msc018.sources = (mss007,)
    msc018.affected = (aak,)
    msc018.budget_scope = aak
    msc018.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc019.owner = pro
    msc019.sources = (mss007,)
    msc019.affected = (thr,)
    msc019.budget_scope = thr
    msc019.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc020.owner = pro
    msc020.sources = (mss007,)
    msc020.affected = (aam,)
    msc020.budget_scope = aam
    msc020.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc021.owner = eps
    msc021.sources = (mss008,)
    msc021.affected = (bat,)
    msc021.budget_scope = bat
    msc021.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc022.owner = eps
    msc022.sources = (mss008,)
    msc022.affected = (sol,)
    msc022.budget_scope = sol
    msc022.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc023.owner = eps
    msc023.sources = (mss008,)
    msc023.affected = (aan,)
    msc023.budget_scope = aan
    msc023.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc024.owner = eps
    msc024.sources = (mss008,)
    msc024.affected = (reg,)
    msc024.budget_scope = reg
    msc024.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc025.owner = eps
    msc025.sources = (mss008,)
    msc025.affected = (pcs,)
    msc025.budget_scope = pcs
    msc025.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    vol001.owner = mission
    vol001.sources = ()
    vol001.affected = (bus, pay)
    vol001.budget_scope = mission
    vol001.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vls001.owner = cdh
    vls001.sources = (vol001,)
    vls001.affected = ()
    vls001.budget_scope = cdh
    vls001.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vls002.owner = com
    vls002.sources = (vol001,)
    vls002.affected = ()
    vls002.budget_scope = com
    vls002.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vls003.owner = adc
    vls003.sources = (vol001,)
    vls003.affected = ()
    vls003.budget_scope = adc
    vls003.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vls004.owner = gnc
    vls004.sources = (vol001,)
    vls004.affected = ()
    vls004.budget_scope = gnc
    vls004.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vls005.owner = str
    vls005.sources = (vol001,)
    vls005.affected = ()
    vls005.budget_scope = str
    vls005.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vls006.owner = the
    vls006.sources = (vol001,)
    vls006.affected = ()
    vls006.budget_scope = the
    vls006.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vls007.owner = pro
    vls007.sources = (vol001,)
    vls007.affected = ()
    vls007.budget_scope = pro
    vls007.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vls008.owner = eps
    vls008.sources = (vol001,)
    vls008.affected = ()
    vls008.budget_scope = eps
    vls008.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc001.owner = cdh
    vlc001.sources = (vls001,)
    vlc001.affected = (aaa,)
    vlc001.budget_scope = aaa
    vlc001.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc002.owner = cdh
    vlc002.sources = (vls001,)
    vlc002.affected = (pcm,)
    vlc002.budget_scope = pcm
    vlc002.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc003.owner = com
    vlc003.sources = (vls002,)
    vlc003.affected = (aab,)
    vlc003.budget_scope = aab
    vlc003.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc004.owner = com
    vlc004.sources = (vls002,)
    vlc004.affected = (rec,)
    vlc004.budget_scope = rec
    vlc004.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc005.owner = com
    vlc005.sources = (vls002,)
    vlc005.affected = (tra,)
    vlc005.budget_scope = tra
    vlc005.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc006.owner = adc
    vlc006.sources = (vls003,)
    vlc006.affected = (act,)
    vlc006.budget_scope = act
    vlc006.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc007.owner = adc
    vlc007.sources = (vls003,)
    vlc007.affected = (sen,)
    vlc007.budget_scope = sen
    vlc007.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc008.owner = gnc
    vlc008.sources = (vls004,)
    vlc008.affected = (acc,)
    vlc008.budget_scope = acc
    vlc008.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc009.owner = gnc
    vlc009.sources = (vls004,)
    vlc009.affected = (gns,)
    vlc009.budget_scope = gns
    vlc009.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc010.owner = str
    vlc010.sources = (vls005,)
    vlc010.affected = (aad,)
    vlc010.budget_scope = aad
    vlc010.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc011.owner = str
    vlc011.sources = (vls005,)
    vlc011.affected = (dep,)
    vlc011.budget_scope = dep
    vlc011.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc012.owner = str
    vlc012.sources = (vls005,)
    vlc012.affected = (sta,)
    vlc012.budget_scope = sta
    vlc012.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc013.owner = the
    vlc013.sources = (vls006,)
    vlc013.affected = (aae,)
    vlc013.budget_scope = aae
    vlc013.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc014.owner = the
    vlc014.sources = (vls006,)
    vlc014.affected = (aaf,)
    vlc014.budget_scope = aaf
    vlc014.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc015.owner = the
    vlc015.sources = (vls006,)
    vlc015.affected = (aag,)
    vlc015.budget_scope = aag
    vlc015.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc016.owner = the
    vlc016.sources = (vls006,)
    vlc016.affected = (aah,)
    vlc016.budget_scope = aah
    vlc016.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc017.owner = pro
    vlc017.sources = (vls007,)
    vlc017.affected = (aaj,)
    vlc017.budget_scope = aaj
    vlc017.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc018.owner = pro
    vlc018.sources = (vls007,)
    vlc018.affected = (aak,)
    vlc018.budget_scope = aak
    vlc018.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc019.owner = pro
    vlc019.sources = (vls007,)
    vlc019.affected = (thr,)
    vlc019.budget_scope = thr
    vlc019.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc020.owner = pro
    vlc020.sources = (vls007,)
    vlc020.affected = (aam,)
    vlc020.budget_scope = aam
    vlc020.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc021.owner = eps
    vlc021.sources = (vls008,)
    vlc021.affected = (bat,)
    vlc021.budget_scope = bat
    vlc021.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc022.owner = eps
    vlc022.sources = (vls008,)
    vlc022.affected = (sol,)
    vlc022.budget_scope = sol
    vlc022.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc023.owner = eps
    vlc023.sources = (vls008,)
    vlc023.affected = (aan,)
    vlc023.budget_scope = aan
    vlc023.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc024.owner = eps
    vlc024.sources = (vls008,)
    vlc024.affected = (reg,)
    vlc024.budget_scope = reg
    vlc024.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc025.owner = eps
    vlc025.sources = (vls008,)
    vlc025.affected = (pcs,)
    vlc025.budget_scope = pcs
    vlc025.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    pay.owner = mission
    ins.owner = pay
    aap.owner = pay
    mss009.owner = pay
    mss009.sources = (mas001,)
    mss009.affected = ()
    mss009.budget_scope = pay
    mss009.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg and allocated_mass_kg >= 0 and allocated_mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc026.owner = pay
    msc026.sources = (mss009,)
    msc026.affected = (ins,)
    msc026.budget_scope = ins
    msc026.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    msc027.owner = pay
    msc027.sources = (mss009,)
    msc027.affected = (aap,)
    msc027.budget_scope = aap
    msc027.verifications = (
        VerificationMethod('condition', 'mass_allocation_kg >= 0 and mass_kg >= 0 and mass_kg <= mass_allocation_kg', key='condition'),
    )
    vls009.owner = pay
    vls009.sources = (vol001,)
    vls009.affected = ()
    vls009.budget_scope = pay
    vls009.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and allocated_volume_m3 >= 0 and allocated_volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc026.owner = pay
    vlc026.sources = (vls009,)
    vlc026.affected = (ins,)
    vlc026.budget_scope = ins
    vlc026.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    vlc027.owner = pay
    vlc027.sources = (vls009,)
    vlc027.affected = (aap,)
    vlc027.budget_scope = aap
    vlc027.verifications = (
        VerificationMethod('condition', 'volume_allocation_m3 >= 0 and volume_m3 >= 0 and volume_m3 <= volume_allocation_m3', key='condition'),
    )
    gnd.owner = mission
    pls.owner = gnd
    scc.owner = gnd
    gec.owner = gnd
    sgc.owner = gnd
    mdp.owner = gnd
    mdd.owner = gnd
    net.owner = gnd
    tlm.owner = gnd


    # Restore initialization history, including deliberately deleted defaults.
    session.restore_state(
        variables=(
            Variable(name='x', value_type=float, unit=None),
            Variable(name='y', value_type=float, unit=None),
            Variable(name='z', value_type=float, unit=None),
            Variable(name='a', value_type=float, unit=None),
            Variable(name='altitude_km', value_type=float, unit='km'),
            Variable(name='earthRadius_km', value_type=float, unit='km'),
            Variable(name='gravitationalParameter_km3_s2', value_type=float, unit='km^3/s^2'),
            Variable(name='orbit_period_s', value_type=float, unit='s'),
            Variable(name='horizon_angle_rad', value_type=float, unit='rad'),
            Variable(name='sunlight_s', value_type=float, unit='s'),
            Variable(name='eclipse_s', value_type=float, unit='s'),
            Variable(name='sunlight_power_W', value_type=float, unit='W'),
            Variable(name='eclipse_power_W', value_type=float, unit='W'),
            Variable(name='sunlight_duty', value_type=float, unit=None),
            Variable(name='eclipse_duty', value_type=float, unit=None),
            Variable(name='sunlight_energy_J', value_type=float, unit='J'),
            Variable(name='eclipse_energy_J', value_type=float, unit='J'),
            Variable(name='sunlight_efficiency', value_type=float, unit=None),
            Variable(name='eclipse_efficiency', value_type=float, unit=None),
            Variable(name='panel_min_W', value_type=float, unit='W'),
            Variable(name='cell_eol_V', value_type=float, unit='V'),
            Variable(name='cell_eol_A', value_type=float, unit='A'),
            Variable(name='cell_eol_W', value_type=float, unit='W'),
            Variable(name='required_cells', value_type=float, unit='cells'),
            Variable(name='minimum_cells', value_type=int, unit='cells'),
            Variable(name='installed_cells', value_type=int, unit='cells'),
            Variable(name='orbits_per_day', value_type=float, unit='orbits/day'),
            Variable(name='lifetime_years', value_type=float, unit='years'),
            Variable(name='days_per_year', value_type=float, unit='days/year'),
            Variable(name='required_cycles', value_type=float, unit='cycles'),
            Variable(name='cycle_a', value_type=float, unit='cycles'),
            Variable(name='cycle_b', value_type=float, unit=None),
            Variable(name='dod_max', value_type=float, unit=None),
            Variable(name='fit_dod_min', value_type=float, unit=None),
            Variable(name='fit_dod_max', value_type=float, unit=None),
            Variable(name='dod_cycle_limit', value_type=float, unit=None),
            Variable(name='supported_cycles', value_type=float, unit='cycles'),
            Variable(name='degradation_margin', value_type=float, unit=None),
            Variable(name='battery_min_J', value_type=float, unit='J'),
            Variable(name='pack_bol_J', value_type=float, unit='J'),
            Variable(name='retained_energy_factor', value_type=float, unit=None),
            Variable(name='pack_eol_J', value_type=float, unit='J'),
            Variable(name='sunlight_generation_J', value_type=float, unit='J'),
            Variable(name='nominal_dod', value_type=float, unit=None),
            Variable(name='energy_start_J', value_type=float, unit='J'),
            Variable(name='energy_end_J', value_type=float, unit='J'),
            Variable(name='closure_tolerance_J', value_type=float, unit='J'),
            Variable(name='soc_start', value_type=float, unit=None),
            Variable(name='soc_end', value_type=float, unit=None),
            Variable(name='mass_kg', value_type=float, unit='kg'),
            Variable(name='mass_allocation_kg', value_type=float, unit='kg'),
            Variable(name='volume_m3', value_type=float, unit='m^3'),
            Variable(name='volume_allocation_m3', value_type=float, unit='m^3'),
            Variable(name='required_data_bytes', value_type=int, unit='bytes'),
            Variable(name='available_data_bytes', value_type=int, unit='bytes'),
            Variable(name='required_program_bytes', value_type=int, unit='bytes'),
            Variable(name='available_program_bytes', value_type=int, unit='bytes'),
            Variable(name='required_utilization', value_type=float, unit=None),
            Variable(name='allocated_utilization', value_type=float, unit=None),
            Variable(name='array_series_cells', value_type=int, unit=None),
            Variable(name='array_parallel_strings', value_type=int, unit=None),
            Variable(name='battery_series_cells', value_type=int, unit=None),
            Variable(name='battery_parallel_strings', value_type=int, unit=None),
            Variable(name='source_operating_min_V', value_type=float, unit='V'),
            Variable(name='source_operating_max_V', value_type=float, unit='V'),
            Variable(name='receiver_min_V', value_type=float, unit='V'),
            Variable(name='receiver_max_V', value_type=float, unit='V'),
            Variable(name='source_voc_max_V', value_type=float, unit='V'),
            Variable(name='input_absolute_max_V', value_type=float, unit='V'),
            Variable(name='source_isc_max_A', value_type=float, unit='A'),
            Variable(name='source_current_limit_A', value_type=float, unit='A'),
            Variable(name='converter_input_V', value_type=float, unit='V'),
            Variable(name='converter_output_V', value_type=float, unit='V'),
            Variable(name='settling_time_s', value_type=float, unit='s'),
            Variable(name='settling_limit_s', value_type=float, unit='s'),
            Variable(name='charge_voltage_V', value_type=float, unit='V'),
            Variable(name='charge_voltage_min_V', value_type=float, unit='V'),
            Variable(name='charge_voltage_max_V', value_type=float, unit='V'),
            Variable(name='charge_current_A', value_type=float, unit='A'),
            Variable(name='charge_current_limit_A', value_type=float, unit='A'),
            Variable(name='termination_current_A', value_type=float, unit='A'),
            Variable(name='termination_limit_A', value_type=float, unit='A'),
            Variable(name='load_voltage_min_V', value_type=float, unit='V'),
            Variable(name='load_voltage_max_V', value_type=float, unit='V'),
            Variable(name='load_supply_min_V', value_type=float, unit='V'),
            Variable(name='load_supply_max_V', value_type=float, unit='V'),
            Variable(name='startup_time_s', value_type=float, unit='s'),
            Variable(name='startup_limit_s', value_type=float, unit='s'),
            Variable(name='continuous_current_A', value_type=float, unit='A'),
            Variable(name='continuous_rating_A', value_type=float, unit='A'),
            Variable(name='pulse_current_A', value_type=float, unit='A'),
            Variable(name='pulse_rating_A', value_type=float, unit='A'),
            Variable(name='pulse_duration_s', value_type=float, unit='s'),
            Variable(name='pulse_rating_duration_s', value_type=float, unit='s'),
            Variable(name='pack_bol_C', value_type=float, unit='C'),
            Variable(name='retained_charge_factor', value_type=float, unit=None),
            Variable(name='pack_eol_C', value_type=float, unit='C'),
            Variable(name='required_charge_C', value_type=float, unit='C'),
            Variable(name='required_service_s', value_type=float, unit='s'),
            Variable(name='assessed_service_s', value_type=float, unit='s'),
            Variable(name='unserved_energy_J', value_type=float, unit='J'),
            Variable(name='energy_min_J', value_type=float, unit='J'),
            Variable(name='energy_max_J', value_type=float, unit='J'),
            Variable(name='energy_reserve_J', value_type=float, unit='J'),
            Variable(name='soc_min', value_type=float, unit=None),
            Variable(name='soc_max', value_type=float, unit=None),
            Variable(name='soc_reserve_min', value_type=float, unit=None),
            Variable(name='recovery_time_s', value_type=float, unit='s'),
            Variable(name='recovery_limit_s', value_type=float, unit='s'),
            Variable(name='assessed_temp_min_K', value_type=float, unit='K'),
            Variable(name='assessed_temp_max_K', value_type=float, unit='K'),
            Variable(name='temp_limit_min_K', value_type=float, unit='K'),
            Variable(name='temp_limit_max_K', value_type=float, unit='K'),
            Variable(name='surplus_peak_W', value_type=float, unit='W'),
            Variable(name='surplus_capacity_W', value_type=float, unit='W'),
            Variable(name='dissipation_W', value_type=float, unit='W'),
            Variable(name='dissipation_limit_W', value_type=float, unit='W'),
            Variable(name='eoc_current_A', value_type=float, unit='A'),
            Variable(name='eoc_current_limit_A', value_type=float, unit='A'),
            Variable(name='fault_interruption_s', value_type=float, unit='s'),
            Variable(name='interruption_limit_s', value_type=float, unit='s'),
            Variable(name='fault_i2t_A2s', value_type=float, unit='A**2*s'),
            Variable(name='i2t_limit_A2s', value_type=float, unit='A**2*s'),
            Variable(name='legitimate_current_A', value_type=float, unit='A'),
            Variable(name='legitimate_duration_s', value_type=float, unit='s'),
            Variable(name='nuisance_trip_count', value_type=int, unit=None),
            Variable(name='fault_voltage_V', value_type=float, unit='V'),
            Variable(name='uv_trip_V', value_type=float, unit='V'),
            Variable(name='ov_trip_V', value_type=float, unit='V'),
            Variable(name='uv_reset_V', value_type=float, unit='V'),
            Variable(name='ov_reset_V', value_type=float, unit='V'),
            Variable(name='inhibited_output_V', value_type=float, unit='V'),
            Variable(name='inhibited_voltage_limit_V', value_type=float, unit='V'),
            Variable(name='required_rate_Hz', value_type=float, unit='Hz'),
            Variable(name='supported_rate_Hz', value_type=float, unit='Hz'),
            Variable(name='response_time_s', value_type=float, unit='s'),
            Variable(name='response_limit_s', value_type=float, unit='s'),
            Variable(name='signal_low_max_V', value_type=float, unit='V'),
            Variable(name='signal_high_min_V', value_type=float, unit='V'),
            Variable(name='receiver_low_max_V', value_type=float, unit='V'),
            Variable(name='receiver_high_min_V', value_type=float, unit='V'),
            Variable(name='clearance_bound_m', value_type=float, unit='m'),
            Variable(name='required_clearance_m', value_type=float, unit='m'),
            Variable(name='stack_height_m', value_type=float, unit='m'),
            Variable(name='stack_allocation_m', value_type=float, unit='m'),
            Variable(name='array_active_area_m2', value_type=float, unit='m**2'),
            Variable(name='usable_face_area_m2', value_type=float, unit='m**2'),
            Variable(name='packing_fraction', value_type=float, unit=None),
            Variable(name='pv_fit_rmse_A', value_type=float, unit='A'),
            Variable(name='pv_fit_limit_A', value_type=float, unit='A'),
            Variable(name='battery_fit_rmse_V', value_type=float, unit='V'),
            Variable(name='battery_fit_limit_V', value_type=float, unit='V'),
            Variable(name='converter_fit_rmse_V', value_type=float, unit='V'),
            Variable(name='converter_fit_limit_V', value_type=float, unit='V'),
            Variable(name='thermal_fit_rmse_K', value_type=float, unit='K'),
            Variable(name='thermal_fit_limit_K', value_type=float, unit='K'),
            Variable(name='mission_reliability', value_type=float, unit=None),
            Variable(name='reliability_min', value_type=float, unit=None),
            Variable(name='ram_exposure_h', value_type=float, unit='h'),
            Variable(name='conditional_failure_probability', value_type=float, unit=None),
            Variable(name='conditional_probability_limit', value_type=float, unit=None),
            Variable(name='allocated_mass_kg', value_type=float, unit='kg'),
            Variable(name='allocated_volume_m3', value_type=float, unit='m^3'),
        ),
        seed_history=(
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3', subject='2327953b-39ca-46e9-b08b-c23fa32deea3', rule='child:SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3', subject='2327953b-39ca-46e9-b08b-c23fa32deea3', rule='child:SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3', subject='2327953b-39ca-46e9-b08b-c23fa32deea3', rule='child:SpaceSegment::CubeSat::CommunicationSubsystem'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3', subject='2327953b-39ca-46e9-b08b-c23fa32deea3', rule='child:SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3', subject='2327953b-39ca-46e9-b08b-c23fa32deea3', rule='child:SpaceSegment::CubeSat::PowerSubsystem'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3', subject='2327953b-39ca-46e9-b08b-c23fa32deea3', rule='child:SpaceSegment::CubeSat::PropulsionSubsystem'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3', subject='2327953b-39ca-46e9-b08b-c23fa32deea3', rule='child:SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3', subject='2327953b-39ca-46e9-b08b-c23fa32deea3', rule='child:SpaceSegment::CubeSat::ThermalSubsystem'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', rule='child:SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem::Actuator'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', rule='child:SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem::Sensor'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', rule='child:SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem::Software'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_2', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_2', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_3', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_3', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', rule='child:SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem::CommandTelemetryAndDataBus'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', rule='child:SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem::ProcessorAndMemory'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem-C', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem-C', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem-P', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem-P', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', rule='child:SpaceSegment::CubeSat::CommunicationSubsystem::ProcessorAndMemory'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', rule='child:SpaceSegment::CubeSat::CommunicationSubsystem::ReceiveAntennaAndEquipment'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', rule='child:SpaceSegment::CubeSat::CommunicationSubsystem::TransmitAntennaAndEquipment'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-ProcessorA', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-ProcessorA', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-ReceiveAnt', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-ReceiveAnt', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-TransmitAn', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-TransmitAn', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', rule='child:SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem::Accelerometer'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', rule='child:SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem::GNSSReceiver'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', rule='child:SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem::Software'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_1', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_1', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_2', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_2', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::BatteryCapacityScreen'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::BatteryModelFit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::BatteryRetainedEnergy'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::ConditionalFailureProbability'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::ConverterModelFit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::CycleFitDomain'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::CycleLife'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::CycleLimitedDoD'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS01'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS02'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS03'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS03OpenCircuit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS03SourceCurrent'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS04'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS05'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS05ChargeCurrent'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS05ChargeVoltage'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS05Termination'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS06'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS06Startup'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS07'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS07Pulse'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS08'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS08RetainedCharge'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS09'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS10'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS10ChargeReserve'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS10EnergyReserve'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS11'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS12'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS12ChargeReserve'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS12EnergyReserve'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS12Recovery'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS13'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS13Charging'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS13Discharging'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS14'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS14EndOfCharge'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS14ShuntHeat'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS15'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS15FaultStress'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS15NoNuisance'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS15SafeOperatingArea'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS16'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS16Reset'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS17'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS17AutonomousProtection'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS17PowerOn'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS18'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS18LogicLevels'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS18Response'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS19'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS20'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS20ArrayPacking'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS20StackHeight'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS21'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS47'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS52'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS53'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS78'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS88'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EPS89'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::EnergyPathEfficiencyBounds'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::LoadEnergy'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::MinimumBatteryEnergy'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::MinimumPanelPower'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::MissionCycles'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::MissionReliability'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::PVModelFit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::RegulatorSettling'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::SolarCellCount'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::SolarCellPower'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='FrameworkRequirements::ThermalModelFit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='child:SpaceSegment::CubeSat::PowerSubsystem::Batteries'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='child:SpaceSegment::CubeSat::PowerSubsystem::PowerCircuitsAndSwitches'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='child:SpaceSegment::CubeSat::PowerSubsystem::ProcessorAndMemory'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='child:SpaceSegment::CubeSat::PowerSubsystem::RegulatorsAndConverters'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='child:SpaceSegment::CubeSat::PowerSubsystem::Software'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', rule='child:SpaceSegment::CubeSat::PowerSubsystem::SolarArrays'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::BatteryCapacityScreen'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::BatteryModelFit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::BatteryRetainedEnergy'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::CycleFitDomain'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::CycleLife'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::CycleLimitedDoD'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS08'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS08RetainedCharge'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS09'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS10ChargeReserve'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS10EnergyReserve'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS12ChargeReserve'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS12EnergyReserve'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS13Discharging'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::EPS47'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::MinimumBatteryEnergy'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='FrameworkRequirements::MissionCycles'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircuitsAndSw', rule='FrameworkRequirements::EPS15FaultStress'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircuitsAndSw', rule='FrameworkRequirements::EPS15NoNuisance'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircuitsAndSw', rule='FrameworkRequirements::EPS15SafeOperatingArea'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircuitsAndSw', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircuitsAndSw', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-ProcessorAndMemory', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-ProcessorAndMemory', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-RegulatorsAndConve', rule='FrameworkRequirements::ConverterModelFit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-RegulatorsAndConve', rule='FrameworkRequirements::EPS04'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-RegulatorsAndConve', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-RegulatorsAndConve', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays', rule='FrameworkRequirements::EPS02'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays', rule='FrameworkRequirements::EPS20ArrayPacking'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays', rule='FrameworkRequirements::PVModelFit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays', rule='FrameworkRequirements::SolarCellCount'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays', rule='FrameworkRequirements::SolarCellPower'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', rule='child:SpaceSegment::CubeSat::PropulsionSubsystem::ProcessorAndMemory'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', rule='child:SpaceSegment::CubeSat::PropulsionSubsystem::PropellantControl'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', rule='child:SpaceSegment::CubeSat::PropulsionSubsystem::PropellantStorage'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', rule='child:SpaceSegment::CubeSat::PropulsionSubsystem::Software'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', rule='child:SpaceSegment::CubeSat::PropulsionSubsystem::Thrusters'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-ProcessorAndM', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-ProcessorAndM', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-PropellantCon', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-PropellantCon', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-PropellantSto', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-PropellantSto', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Thrusters', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Thrusters', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', rule='child:SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::ActuatedMount'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', rule='child:SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::DeployableMount'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', rule='child:SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::StaticMount'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-_1', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-_1', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-_2', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-_2', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', rule='child:SpaceSegment::CubeSat::ThermalSubsystem::ProcessorAndMemory'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', rule='child:SpaceSegment::CubeSat::ThermalSubsystem::Software'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', rule='child:SpaceSegment::CubeSat::ThermalSubsystem::ThermalSensor'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', rule='child:SpaceSegment::CubeSat::ThermalSubsystem::ThermalSink'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', rule='child:SpaceSegment::CubeSat::ThermalSubsystem::ThermalSource'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ProcessorAndMemo', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ProcessorAndMemo', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSensor', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSensor', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSink', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSink', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSource', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', subject='2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSource', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='2b51eaed-8d07-4609-bb98-3bffc86bae50', subject='2b51eaed-8d07-4609-bb98-3bffc86bae50', rule='child:GroundSegment::GroundEquipmentControlSubsystem'),
            SeedRule(owner='2b51eaed-8d07-4609-bb98-3bffc86bae50', subject='2b51eaed-8d07-4609-bb98-3bffc86bae50', rule='child:GroundSegment::MissionDataDisseminationSubsystem'),
            SeedRule(owner='2b51eaed-8d07-4609-bb98-3bffc86bae50', subject='2b51eaed-8d07-4609-bb98-3bffc86bae50', rule='child:GroundSegment::MissionDataProcessingSubsystem'),
            SeedRule(owner='2b51eaed-8d07-4609-bb98-3bffc86bae50', subject='2b51eaed-8d07-4609-bb98-3bffc86bae50', rule='child:GroundSegment::NetworkSubsystem'),
            SeedRule(owner='2b51eaed-8d07-4609-bb98-3bffc86bae50', subject='2b51eaed-8d07-4609-bb98-3bffc86bae50', rule='child:GroundSegment::PlanAndScheduleSubsystem'),
            SeedRule(owner='2b51eaed-8d07-4609-bb98-3bffc86bae50', subject='2b51eaed-8d07-4609-bb98-3bffc86bae50', rule='child:GroundSegment::SpaceGroundCommunicationSubsystem'),
            SeedRule(owner='2b51eaed-8d07-4609-bb98-3bffc86bae50', subject='2b51eaed-8d07-4609-bb98-3bffc86bae50', rule='child:GroundSegment::SpacecraftCommandSubsystem'),
            SeedRule(owner='2b51eaed-8d07-4609-bb98-3bffc86bae50', subject='2b51eaed-8d07-4609-bb98-3bffc86bae50', rule='child:GroundSegment::TelemetryProcessingSubsystem'),
            SeedRule(owner='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', subject='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', subject='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', rule='ResourceBudgetModel::VolumeLimit'),
            SeedRule(owner='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', subject='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', rule='child:SpaceSegment::CubeSat::PayloadSubsystem::Instrument'),
            SeedRule(owner='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', subject='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', rule='child:SpaceSegment::CubeSat::PayloadSubsystem::ProcessorAndMemory'),
            SeedRule(owner='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', subject='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-Instrument', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', subject='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-Instrument', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', subject='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-ProcessorAndMemory', rule='ResourceBudgetModel::ComponentMassLimit'),
            SeedRule(owner='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', subject='8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-ProcessorAndMemory', rule='ResourceBudgetModel::ComponentVolumeLimit'),
            SeedRule(owner='mission', subject='f23034d2-224c-4126-bf4c-6d7bf828a263', rule='FrameworkRequirements::IlluminationPeriods'),
            SeedRule(owner='mission', subject='f23034d2-224c-4126-bf4c-6d7bf828a263', rule='FrameworkRequirements::OrbitPeriod'),
            SeedRule(owner='mission', subject='f23034d2-224c-4126-bf4c-6d7bf828a263', rule='FrameworkRequirements::OrbitPeriodClosure'),
            SeedRule(owner='mission', subject='mission', rule='ResourceBudgetModel::MassLimit'),
            SeedRule(owner='mission', subject='mission', rule='ResourceBudgetModel::VolumeLimit'),
        ),
        initialized=('2327953b-39ca-46e9-b08b-c23fa32deea3', '2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu', '2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_1', '2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_2', '2327953b-39ca-46e9-b08b-c23fa32deea3-AttitudeDeterminationAndControlSu_3', '2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem', '2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem-C', '2327953b-39ca-46e9-b08b-c23fa32deea3-CommandAndDataHandlingSubsystem-P', '2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem', '2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-ProcessorA', '2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-ReceiveAnt', '2327953b-39ca-46e9-b08b-c23fa32deea3-CommunicationSubsystem-TransmitAn', '2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy', '2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_1', '2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_2', '2327953b-39ca-46e9-b08b-c23fa32deea3-GuidanceNavigationAndControlSubsy_3', '2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem', '2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Batteries', '2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-PowerCircuitsAndSw', '2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-ProcessorAndMemory', '2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-RegulatorsAndConve', '2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-Software', '2327953b-39ca-46e9-b08b-c23fa32deea3-PowerSubsystem-SolarArrays', '2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem', '2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-ProcessorAndM', '2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-PropellantCon', '2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-PropellantSto', '2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Software', '2327953b-39ca-46e9-b08b-c23fa32deea3-PropulsionSubsystem-Thrusters', '2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem', '2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-', '2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-_1', '2327953b-39ca-46e9-b08b-c23fa32deea3-StructuresAndMechanismsSubsystem-_2', '2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem', '2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ProcessorAndMemo', '2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-Software', '2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSensor', '2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSink', '2327953b-39ca-46e9-b08b-c23fa32deea3-ThermalSubsystem-ThermalSource', '2b51eaed-8d07-4609-bb98-3bffc86bae50', '2b51eaed-8d07-4609-bb98-3bffc86bae50-GroundEquipmentControlSubsystem', '2b51eaed-8d07-4609-bb98-3bffc86bae50-MissionDataDisseminationSubsystem', '2b51eaed-8d07-4609-bb98-3bffc86bae50-MissionDataProcessingSubsystem', '2b51eaed-8d07-4609-bb98-3bffc86bae50-NetworkSubsystem', '2b51eaed-8d07-4609-bb98-3bffc86bae50-PlanAndScheduleSubsystem', '2b51eaed-8d07-4609-bb98-3bffc86bae50-SpaceGroundCommunicationSubsystem', '2b51eaed-8d07-4609-bb98-3bffc86bae50-SpacecraftCommandSubsystem', '2b51eaed-8d07-4609-bb98-3bffc86bae50-TelemetryProcessingSubsystem', '8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2', '8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-Instrument', '8131dfa6-27e1-4c9f-96c1-dbb3984ff8b2-ProcessorAndMemory', 'f23034d2-224c-4126-bf4c-6d7bf828a263'),
        requirement_seeds=(
            (eps, ('FrameworkRequirements::EPS01', 'FrameworkRequirements::EPS03', 'FrameworkRequirements::EPS03OpenCircuit', 'FrameworkRequirements::EPS03SourceCurrent', 'FrameworkRequirements::EPS04', 'FrameworkRequirements::RegulatorSettling', 'FrameworkRequirements::EPS05', 'FrameworkRequirements::EPS05ChargeVoltage', 'FrameworkRequirements::EPS05ChargeCurrent', 'FrameworkRequirements::EPS05Termination', 'FrameworkRequirements::EPS06', 'FrameworkRequirements::EPS06Startup', 'FrameworkRequirements::EPS07', 'FrameworkRequirements::EPS07Pulse', 'FrameworkRequirements::EPS08RetainedCharge', 'FrameworkRequirements::EPS10', 'FrameworkRequirements::EPS10EnergyReserve', 'FrameworkRequirements::EPS10ChargeReserve', 'FrameworkRequirements::EPS12', 'FrameworkRequirements::EPS12EnergyReserve', 'FrameworkRequirements::EPS12ChargeReserve', 'FrameworkRequirements::EPS12Recovery', 'FrameworkRequirements::EPS13', 'FrameworkRequirements::EPS13Charging', 'FrameworkRequirements::EPS13Discharging', 'FrameworkRequirements::EPS14', 'FrameworkRequirements::EPS14ShuntHeat', 'FrameworkRequirements::EPS14EndOfCharge', 'FrameworkRequirements::EPS15', 'FrameworkRequirements::EPS15FaultStress', 'FrameworkRequirements::EPS15NoNuisance', 'FrameworkRequirements::EPS15SafeOperatingArea', 'FrameworkRequirements::EPS16', 'FrameworkRequirements::EPS16Reset', 'FrameworkRequirements::EPS17', 'FrameworkRequirements::EPS17PowerOn', 'FrameworkRequirements::EPS17AutonomousProtection', 'FrameworkRequirements::EPS18', 'FrameworkRequirements::EPS18Response', 'FrameworkRequirements::EPS18LogicLevels', 'FrameworkRequirements::EPS20', 'FrameworkRequirements::EPS20StackHeight', 'FrameworkRequirements::EPS20ArrayPacking', 'FrameworkRequirements::PVModelFit', 'FrameworkRequirements::BatteryModelFit', 'FrameworkRequirements::ConverterModelFit', 'FrameworkRequirements::ThermalModelFit', 'FrameworkRequirements::MissionReliability', 'FrameworkRequirements::ConditionalFailureProbability')),
        ),
        resource_budgets=True,
        model_state_present=True,
        resource_budgets_present=True,
        requirement_seeds_present=True,
    )
    return session


def run_verifications(session, **execution_options):
    """Explicitly execute the configured imported analysis implementations."""
    return session.run((
    ), **execution_options)


if __name__ == "__main__":
    session = build_session()
    evidence = run_verifications(session)
    print(session.name or "Session", len(session.objects), "objects")
    for requirement, result in session.verify().assessments:
        print(requirement.id, result.state.value)
