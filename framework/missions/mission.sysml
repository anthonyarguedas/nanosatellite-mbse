// <requirements-ui>
// Mission data managed by requirements-ui. Generic definitions are imported.
// The JSON preserves UI data. The SysML elements below are generated from it.
/* requirements-ui:data
{
  "version": 8,
  "variables": [
    {
      "name": "x",
      "type": "float"
    },
    {
      "name": "y",
      "type": "float"
    },
    {
      "name": "z",
      "type": "float"
    },
    {
      "name": "a",
      "type": "float"
    },
    {
      "name": "altitude_km",
      "type": "float",
      "unit": "km"
    },
    {
      "name": "earthRadius_km",
      "type": "float",
      "unit": "km"
    },
    {
      "name": "gravitationalParameter_km3_s2",
      "type": "float",
      "unit": "km^3/s^2"
    },
    {
      "name": "orbit_period_s",
      "type": "float",
      "unit": "s"
    },
    {
      "name": "horizon_angle_rad",
      "type": "float",
      "unit": "rad"
    },
    {
      "name": "sunlight_s",
      "type": "float",
      "unit": "s"
    },
    {
      "name": "eclipse_s",
      "type": "float",
      "unit": "s"
    },
    {
      "name": "sunlight_power_W",
      "type": "float",
      "unit": "W"
    },
    {
      "name": "eclipse_power_W",
      "type": "float",
      "unit": "W"
    },
    {
      "name": "sunlight_duty",
      "type": "float"
    },
    {
      "name": "eclipse_duty",
      "type": "float"
    },
    {
      "name": "sunlight_energy_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "eclipse_energy_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "sunlight_efficiency",
      "type": "float"
    },
    {
      "name": "eclipse_efficiency",
      "type": "float"
    },
    {
      "name": "panel_min_W",
      "type": "float",
      "unit": "W"
    },
    {
      "name": "cell_eol_V",
      "type": "float",
      "unit": "V"
    },
    {
      "name": "cell_eol_A",
      "type": "float",
      "unit": "A"
    },
    {
      "name": "cell_eol_W",
      "type": "float",
      "unit": "W"
    },
    {
      "name": "required_cells",
      "type": "float",
      "unit": "cells"
    },
    {
      "name": "minimum_cells",
      "type": "integer",
      "unit": "cells"
    },
    {
      "name": "installed_cells",
      "type": "integer",
      "unit": "cells"
    },
    {
      "name": "orbits_per_day",
      "type": "float",
      "unit": "orbits/day"
    },
    {
      "name": "lifetime_years",
      "type": "float",
      "unit": "years"
    },
    {
      "name": "days_per_year",
      "type": "float",
      "unit": "days/year"
    },
    {
      "name": "required_cycles",
      "type": "float",
      "unit": "cycles"
    },
    {
      "name": "cycle_a",
      "type": "float",
      "unit": "cycles"
    },
    {
      "name": "cycle_b",
      "type": "float"
    },
    {
      "name": "dod_max",
      "type": "float"
    },
    {
      "name": "fit_dod_min",
      "type": "float"
    },
    {
      "name": "fit_dod_max",
      "type": "float"
    },
    {
      "name": "dod_cycle_limit",
      "type": "float"
    },
    {
      "name": "supported_cycles",
      "type": "float",
      "unit": "cycles"
    },
    {
      "name": "degradation_margin",
      "type": "float"
    },
    {
      "name": "battery_min_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "pack_bol_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "retained_energy_factor",
      "type": "float"
    },
    {
      "name": "pack_eol_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "sunlight_generation_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "nominal_dod",
      "type": "float"
    },
    {
      "name": "energy_start_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "energy_end_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "closure_tolerance_J",
      "type": "float",
      "unit": "J"
    },
    {
      "name": "soc_start",
      "type": "float"
    },
    {
      "name": "soc_end",
      "type": "float"
    },
    {
      "name": "mass_kg",
      "type": "float",
      "unit": "kg"
    },
    {
      "name": "mass_allocation_kg",
      "type": "float",
      "unit": "kg"
    },
    {
      "name": "volume_m3",
      "type": "float",
      "unit": "m^3"
    },
    {
      "name": "volume_allocation_m3",
      "type": "float",
      "unit": "m^3"
    },
    {
      "name": "required_data_bytes",
      "type": "integer",
      "unit": "bytes"
    },
    {
      "name": "available_data_bytes",
      "type": "integer",
      "unit": "bytes"
    },
    {
      "name": "required_program_bytes",
      "type": "integer",
      "unit": "bytes"
    },
    {
      "name": "available_program_bytes",
      "type": "integer",
      "unit": "bytes"
    },
    {
      "name": "required_utilization",
      "type": "float"
    },
    {
      "name": "allocated_utilization",
      "type": "float"
    }
  ],
  "stakeholders": [],
  "elements": [
    {
      "key": "domain-orbit",
      "id": "ORB",
      "name": "Orbit",
      "owner": "mission",
      "definition": "Orbit"
    },
    {
      "key": "domain-bus",
      "id": "BUS",
      "name": "CubeSat Bus",
      "owner": "mission",
      "definition": "SpaceSegment::CubeSat"
    },
    {
      "key": "domain-bus-CommandAndDataHandlingSubsystem",
      "id": "CDH",
      "name": "Command and Data Handling",
      "owner": "domain-bus",
      "definition": "SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem"
    },
    {
      "key": "domain-bus-CommunicationSubsystem",
      "id": "COM",
      "name": "Communication",
      "owner": "domain-bus",
      "definition": "SpaceSegment::CubeSat::CommunicationSubsystem"
    },
    {
      "key": "domain-bus-AttitudeDeterminationAndControlSubsystem",
      "id": "ADC",
      "name": "Attitude Determination and Control",
      "owner": "domain-bus",
      "definition": "SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem"
    },
    {
      "key": "domain-bus-GuidanceNavigationAndControlSubsystem",
      "id": "GNC",
      "name": "Guidance Navigation and Control",
      "owner": "domain-bus",
      "definition": "SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem"
    },
    {
      "key": "domain-bus-StructuresAndMechanismsSubsystem",
      "id": "STR",
      "name": "Structures and Mechanisms",
      "owner": "domain-bus",
      "definition": "SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem"
    },
    {
      "key": "domain-bus-ThermalSubsystem",
      "id": "THE",
      "name": "Thermal",
      "owner": "domain-bus",
      "definition": "SpaceSegment::CubeSat::ThermalSubsystem"
    },
    {
      "key": "domain-bus-PropulsionSubsystem",
      "id": "PRO",
      "name": "Propulsion",
      "owner": "domain-bus",
      "definition": "SpaceSegment::CubeSat::PropulsionSubsystem"
    },
    {
      "key": "domain-bus-PowerSubsystem",
      "id": "EPS",
      "name": "Power",
      "owner": "domain-bus",
      "definition": "SpaceSegment::CubeSat::PowerSubsystem"
    },
    {
      "key": "domain-bus-PowerSubsystem-Batteries",
      "id": "BAT",
      "name": "Batteries",
      "owner": "domain-bus-PowerSubsystem",
      "definition": "SpaceSegment::CubeSat::PowerSubsystem::Batteries"
    },
    {
      "key": "domain-bus-PowerSubsystem-SolarArrays",
      "id": "SOL",
      "name": "Solar Arrays",
      "owner": "domain-bus-PowerSubsystem",
      "definition": "SpaceSegment::CubeSat::PowerSubsystem::SolarArrays"
    },
    {
      "key": "domain-bus-PowerSubsystem-ProcessorAndMemory",
      "id": "PCM",
      "name": "Processor and Memory",
      "owner": "domain-bus-PowerSubsystem",
      "definition": "SpaceSegment::CubeSat::PowerSubsystem::ProcessorAndMemory"
    },
    {
      "key": "domain-bus-PowerSubsystem-RegulatorsAndConverters",
      "id": "REG",
      "name": "Regulators and Converters",
      "owner": "domain-bus-PowerSubsystem",
      "definition": "SpaceSegment::CubeSat::PowerSubsystem::RegulatorsAndConverters"
    },
    {
      "key": "domain-bus-PowerSubsystem-PowerCircuitsAndSwitches",
      "id": "PCS",
      "name": "Power Circuits and Switches",
      "owner": "domain-bus-PowerSubsystem",
      "definition": "SpaceSegment::CubeSat::PowerSubsystem::PowerCircuitsAndSwitches"
    },
    {
      "key": "domain-bus-PowerSubsystem-Software",
      "id": "SFW",
      "name": "Software",
      "owner": "domain-bus-PowerSubsystem",
      "definition": "SpaceSegment::CubeSat::PowerSubsystem::Software"
    },
    {
      "key": "domain-payload",
      "id": "PAY",
      "name": "Payload",
      "owner": "mission",
      "definition": "SpaceSegment::CubeSat::PayloadSubsystem"
    },
    {
      "key": "domain-payload-Instrument",
      "id": "INS",
      "name": "Instrument",
      "owner": "domain-payload",
      "definition": "SpaceSegment::CubeSat::PayloadSubsystem::Instrument"
    },
    {
      "key": "domain-payload-ProcessorAndMemory",
      "id": "AAA",
      "name": "Processor and Memory",
      "owner": "domain-payload",
      "definition": "SpaceSegment::CubeSat::PayloadSubsystem::ProcessorAndMemory"
    },
    {
      "key": "domain-ground",
      "id": "GND",
      "name": "Ground Station",
      "owner": "mission",
      "definition": "GroundSegment::GroundStation"
    },
    {
      "key": "domain-ground-PlanAndScheduleSubsystem",
      "id": "PLS",
      "name": "Plan and Schedule",
      "owner": "domain-ground",
      "definition": "GroundSegment::PlanAndScheduleSubsystem"
    },
    {
      "key": "domain-ground-SpacecraftCommandSubsystem",
      "id": "SCC",
      "name": "Spacecraft Command",
      "owner": "domain-ground",
      "definition": "GroundSegment::SpacecraftCommandSubsystem"
    },
    {
      "key": "domain-ground-GroundEquipmentControlSubsystem",
      "id": "GEC",
      "name": "Ground Equipment Control",
      "owner": "domain-ground",
      "definition": "GroundSegment::GroundEquipmentControlSubsystem"
    },
    {
      "key": "domain-ground-SpaceGroundCommunicationSubsystem",
      "id": "SGC",
      "name": "Space Ground Communication",
      "owner": "domain-ground",
      "definition": "GroundSegment::SpaceGroundCommunicationSubsystem"
    },
    {
      "key": "domain-ground-MissionDataProcessingSubsystem",
      "id": "MDP",
      "name": "Mission Data Processing",
      "owner": "domain-ground",
      "definition": "GroundSegment::MissionDataProcessingSubsystem"
    },
    {
      "key": "domain-ground-MissionDataDisseminationSubsystem",
      "id": "MDD",
      "name": "Mission Data Dissemination",
      "owner": "domain-ground",
      "definition": "GroundSegment::MissionDataDisseminationSubsystem"
    },
    {
      "key": "domain-ground-NetworkSubsystem",
      "id": "NET",
      "name": "Network",
      "owner": "domain-ground",
      "definition": "GroundSegment::NetworkSubsystem"
    },
    {
      "key": "domain-ground-TelemetryProcessingSubsystem",
      "id": "TLM",
      "name": "Telemetry Processing",
      "owner": "domain-ground",
      "definition": "GroundSegment::TelemetryProcessingSubsystem"
    }
  ],
  "statements": [
    {
      "key": "generic-ORB-OrbitPeriod",
      "id": "ORB001",
      "context": "mission",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::OrbitPeriod",
      "origin": "final_report/design-proposal.tex#eq:orbit-period (handpicked-0003, Eqs. 1-4)",
      "rationale": "final_report/design-proposal.tex#eq:orbit-period (handpicked-0003, Eqs. 1-4)",
      "text": "The preliminary circular orbit shall have period $$orbit_period_s$$ at altitude $$altitude_km$$, using Earth radius $$earthRadius_km$$ and gravitational parameter $$gravitationalParameter_km3_s2$$.",
      "condition": "altitude_km > 0 and earthRadius_km > 0 and gravitationalParameter_km3_s2 > 0 and orbit_period_s > 0 and orbit_period_s == 2 * pi * sqrt((earthRadius_km + altitude_km) ^ 3 / gravitationalParameter_km3_s2)",
      "sources": [],
      "affected": [
        "domain-orbit"
      ],
      "parameters": {
        "altitude_km": null,
        "earthRadius_km": "6378",
        "gravitationalParameter_km3_s2": "398601",
        "orbit_period_s": "2 * pi * sqrt((earthRadius_km + altitude_km) ^ 3 / gravitationalParameter_km3_s2)",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-ORB-IlluminationPeriods",
      "id": "ORB002",
      "context": "mission",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::IlluminationPeriods",
      "origin": "final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period, eq:eclipse-geometry",
      "rationale": "final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period, eq:eclipse-geometry",
      "text": "The preliminary circular orbit at altitude $$altitude_km$$ shall provide $$sunlight_s$$ of sunlight and $$eclipse_s$$ of eclipse per $$orbit_period_s$$ orbit, using Earth radius $$earthRadius_km$$ and horizon angle $$horizon_angle_rad$$.",
      "condition": "altitude_km > 0 and earthRadius_km > 0 and orbit_period_s > 0 and sunlight_s > 0 and eclipse_s > 0 and horizon_angle_rad == arccos(earthRadius_km / (earthRadius_km + altitude_km)) and sunlight_s == (0.5 + horizon_angle_rad / pi) * orbit_period_s and eclipse_s == (0.5 - horizon_angle_rad / pi) * orbit_period_s and abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s",
      "sources": [
        "generic-ORB-OrbitPeriod"
      ],
      "affected": [
        "domain-orbit"
      ],
      "parameters": {
        "altitude_km": "ORB001.altitude_km",
        "earthRadius_km": "ORB001.earthRadius_km",
        "orbit_period_s": "ORB001.orbit_period_s",
        "horizon_angle_rad": "arccos(earthRadius_km / (earthRadius_km + altitude_km))",
        "sunlight_s": "(0.5 + horizon_angle_rad / pi) * orbit_period_s",
        "eclipse_s": "(0.5 - horizon_angle_rad / pi) * orbit_period_s",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "gravitationalParameter_km3_s2": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-ORB-OrbitPeriodClosure",
      "id": "ORB003",
      "context": "mission",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::OrbitPeriodClosure",
      "origin": "final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period",
      "rationale": "final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period",
      "text": "The positive sunlight and eclipse periods shall sum to $$orbit_period_s$$ within numerical tolerance.",
      "condition": "orbit_period_s > 0 and sunlight_s > 0 and eclipse_s > 0 and abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s",
      "sources": [
        "generic-ORB-IlluminationPeriods"
      ],
      "affected": [
        "domain-orbit"
      ],
      "parameters": {
        "orbit_period_s": "ORB002.orbit_period_s",
        "sunlight_s": "ORB002.sunlight_s",
        "eclipse_s": "ORB002.eclipse_s",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "horizon_angle_rad": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-LoadEnergy",
      "id": "SIZ001",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::LoadEnergy",
      "origin": "final_report/design-proposal.tex#eq:minimum-panel-power; EPSModel::ModeLoadProfile and AccountingPlan",
      "rationale": "final_report/design-proposal.tex#eq:minimum-panel-power; EPSModel::ModeLoadProfile and AccountingPlan",
      "text": "The preliminary load budget shall allocate $$sunlight_energy_J$$ during $$sunlight_s$$ of sunlight and $$eclipse_energy_J$$ during $$eclipse_s$$ of eclipse.",
      "condition": "sunlight_power_W >= 0 and eclipse_power_W >= 0 and sunlight_duty >= 0 and sunlight_duty <= 1 and eclipse_duty >= 0 and eclipse_duty <= 1 and sunlight_s > 0 and eclipse_s > 0 and sunlight_energy_J == sunlight_power_W * sunlight_duty * sunlight_s and eclipse_energy_J == eclipse_power_W * eclipse_duty * eclipse_s",
      "sources": [
        "generic-ORB-IlluminationPeriods"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries",
        "domain-bus-PowerSubsystem-SolarArrays"
      ],
      "parameters": {
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_s": "ORB002.sunlight_s",
        "eclipse_s": "ORB002.eclipse_s",
        "sunlight_energy_J": "sunlight_power_W * sunlight_duty * sunlight_s",
        "eclipse_energy_J": "eclipse_power_W * eclipse_duty * eclipse_s",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-MinimumPanelPower",
      "id": "SIZ002",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::MinimumPanelPower",
      "origin": "final_report/design-proposal.tex#eq:minimum-panel-power (handpicked-0003)",
      "rationale": "final_report/design-proposal.tex#eq:minimum-panel-power (handpicked-0003)",
      "text": "The solar panels shall provide at least $$panel_min_W$$ at the declared source boundary.",
      "condition": "sunlight_energy_J >= 0 and eclipse_energy_J >= 0 and sunlight_s > 0 and sunlight_efficiency > 0 and sunlight_efficiency <= 1 and eclipse_efficiency > 0 and eclipse_efficiency <= 1 and panel_min_W == (sunlight_energy_J / sunlight_efficiency + eclipse_energy_J / eclipse_efficiency) / sunlight_s",
      "sources": [
        "generic-EPS-LoadEnergy",
        "generic-ORB-IlluminationPeriods"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-SolarArrays",
        "domain-bus-PowerSubsystem-RegulatorsAndConverters"
      ],
      "parameters": {
        "sunlight_energy_J": "SIZ001.sunlight_energy_J",
        "eclipse_energy_J": "SIZ001.eclipse_energy_J",
        "sunlight_s": "ORB002.sunlight_s",
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": "(sunlight_energy_J / sunlight_efficiency + eclipse_energy_J / eclipse_efficiency) / sunlight_s",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-SolarCellPower",
      "id": "SIZ003",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::SolarCellPower",
      "origin": "final_report/design-proposal.tex#eq:solar-cell-eol-power",
      "rationale": "final_report/design-proposal.tex#eq:solar-cell-eol-power",
      "text": "The selected solar cell shall provide EOL maximum power $$cell_eol_W$$ from maximum power point voltage $$cell_eol_V$$ and current $$cell_eol_A$$.",
      "condition": "cell_eol_V > 0 and cell_eol_A > 0 and cell_eol_W == cell_eol_V * cell_eol_A",
      "sources": [],
      "affected": [
        "domain-bus-PowerSubsystem-SolarArrays"
      ],
      "parameters": {
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": "cell_eol_V * cell_eol_A",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-SolarCellCount",
      "id": "SIZ004",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::SolarCellCount",
      "origin": "final_report/design-proposal.tex#eq:solar-cell-count, eq:pv-integer-configuration",
      "rationale": "final_report/design-proposal.tex#eq:solar-cell-count, eq:pv-integer-configuration",
      "text": "The array shall install $$installed_cells$$, at least the minimum $$minimum_cells$$ obtained by rounding calculated count $$required_cells$$ upward.",
      "condition": "panel_min_W >= 0 and cell_eol_W > 0 and required_cells == panel_min_W / cell_eol_W and minimum_cells == -floor(-required_cells) and installed_cells > 0 and installed_cells >= minimum_cells",
      "sources": [
        "generic-EPS-MinimumPanelPower",
        "generic-EPS-SolarCellPower"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-SolarArrays"
      ],
      "parameters": {
        "panel_min_W": "SIZ002.panel_min_W",
        "cell_eol_W": "SIZ003.cell_eol_W",
        "required_cells": "panel_min_W / cell_eol_W",
        "minimum_cells": "-floor(-required_cells)",
        "installed_cells": null,
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-MissionCycles",
      "id": "SIZ005",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::MissionCycles",
      "origin": "final_report/design-proposal.tex#eq:battery-mission-cycles",
      "rationale": "final_report/design-proposal.tex#eq:battery-mission-cycles",
      "text": "For one nominal cycle per orbit, the battery shall support at least $$required_cycles$$ over $$lifetime_years$$, using $$days_per_year$$ and $$orbits_per_day$$ derived from period $$orbit_period_s$$.",
      "condition": "orbit_period_s > 0 and lifetime_years > 0 and days_per_year > 0 and orbits_per_day == 86400 / orbit_period_s and required_cycles == lifetime_years * days_per_year * orbits_per_day",
      "sources": [
        "generic-ORB-OrbitPeriod"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "orbit_period_s": "ORB001.orbit_period_s",
        "orbits_per_day": "86400 / orbit_period_s",
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": "lifetime_years * days_per_year * orbits_per_day",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-CycleLife",
      "id": "SIZ006",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::CycleLife",
      "origin": "final_report/design-proposal.tex#eq:battery-cycle-life; EPS-09",
      "rationale": "final_report/design-proposal.tex#eq:battery-cycle-life; EPS-09",
      "text": "The selected maximum depth of discharge $$dod_max$$ shall support $$supported_cycles$$, at least the required $$required_cycles$$.",
      "condition": "required_cycles > 0 and cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max and dod_cycle_limit == (required_cycles / cycle_a) ^ (1 / cycle_b) and supported_cycles == cycle_a * dod_max ^ cycle_b and supported_cycles >= required_cycles",
      "sources": [
        "generic-EPS-MissionCycles"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "required_cycles": "SIZ005.required_cycles",
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": "(required_cycles / cycle_a) ^ (1 / cycle_b)",
        "supported_cycles": "cycle_a * dod_max ^ cycle_b",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-MinimumBatteryEnergy",
      "id": "SIZ007",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::MinimumBatteryEnergy",
      "origin": "final_report/design-proposal.tex#eq:battery-energy; EPS-08",
      "rationale": "final_report/design-proposal.tex#eq:battery-energy; EPS-08",
      "text": "The battery shall provide at least $$battery_min_J$$ of BOL energy for eclipse demand $$eclipse_energy_J$$ at maximum DoD $$dod_max$$ and degradation margin $$degradation_margin$$.",
      "condition": "eclipse_energy_J >= 0 and dod_max > 0 and dod_max <= 1 and degradation_margin >= 0 and battery_min_J == eclipse_energy_J / dod_max * (1 + degradation_margin) and required_cycles > 0 and cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max and supported_cycles == cycle_a * dod_max ^ cycle_b and supported_cycles >= required_cycles",
      "sources": [
        "generic-EPS-LoadEnergy",
        "generic-EPS-CycleLife",
        "generic-EPS-MissionCycles"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "eclipse_energy_J": "SIZ001.eclipse_energy_J",
        "dod_max": "SIZ006.dod_max",
        "degradation_margin": null,
        "battery_min_J": "eclipse_energy_J / dod_max * (1 + degradation_margin)",
        "required_cycles": "SIZ005.required_cycles",
        "supported_cycles": "SIZ006.supported_cycles",
        "fit_dod_min": "SIZ006.fit_dod_min",
        "fit_dod_max": "SIZ006.fit_dod_max",
        "cycle_a": "SIZ006.cycle_a",
        "cycle_b": "SIZ006.cycle_b",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "dod_cycle_limit": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-BatteryCapacityScreen",
      "id": "SIZ008",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::BatteryCapacityScreen",
      "origin": "final_report/design-proposal.tex#eq:battery-assembly-capacity; EPS-08",
      "rationale": "final_report/design-proposal.tex#eq:battery-assembly-capacity; EPS-08",
      "text": "The selected battery shall have BOL energy $$pack_bol_J$$, at least the preliminary minimum $$battery_min_J$$.",
      "condition": "battery_min_J >= 0 and pack_bol_J > 0 and pack_bol_J >= battery_min_J and retained_energy_factor > 0 and retained_energy_factor <= 1 and pack_eol_J == retained_energy_factor * pack_bol_J",
      "sources": [
        "generic-EPS-MinimumBatteryEnergy"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "battery_min_J": "SIZ007.battery_min_J",
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": "retained_energy_factor * pack_bol_J",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS02",
      "id": "EPS002",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS02",
      "origin": "final_report/eps-requirements.tex#EPS-02; eq:array-generation-screen, eq:pv-integer-configuration",
      "rationale": "final_report/eps-requirements.tex#EPS-02; eq:array-generation-screen, eq:pv-integer-configuration",
      "text": "EPS-02. The solar arrays shall provide at least $$panel_min_W$$ of average source power from $$sunlight_generation_J$$ over $$sunlight_s$$ of sunlight at each section's attainable DET or MPPT operating point under applicable illumination and EOL conditions.",
      "condition": "",
      "sources": [
        "generic-ORB-IlluminationPeriods",
        "generic-EPS-MinimumPanelPower"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-SolarArrays"
      ],
      "parameters": {
        "sunlight_generation_J": null,
        "sunlight_s": "ORB002.sunlight_s",
        "panel_min_W": "SIZ002.panel_min_W",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS08",
      "id": "EPS008",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS08",
      "origin": "final_report/eps-requirements.tex#EPS-08; eq:battery-energy, eq:battery-assembly-capacity, eq:battery-assembly-ratings",
      "rationale": "final_report/eps-requirements.tex#EPS-08; eq:battery-energy, eq:battery-assembly-capacity, eq:battery-assembly-ratings",
      "text": "EPS-08. The battery pack BOL energy $$pack_bol_J$$ shall meet minimum energy $$battery_min_J$$ from preliminary battery sizing.",
      "condition": "",
      "sources": [
        "generic-EPS-BatteryCapacityScreen",
        "generic-EPS-MinimumBatteryEnergy"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "pack_bol_J": "SIZ008.pack_bol_J",
        "battery_min_J": "SIZ007.battery_min_J",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS09",
      "id": "EPS009",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS09",
      "origin": "final_report/eps-requirements.tex#EPS-09; eq:battery-mission-cycles, eq:battery-cycle-life",
      "rationale": "final_report/eps-requirements.tex#EPS-09; eq:battery-mission-cycles, eq:battery-cycle-life",
      "text": "EPS-09. For nominal operation, the battery pack shall support $$supported_cycles$$, at least the required $$required_cycles$$ at the selected DoD and applicable conditions.",
      "condition": "",
      "sources": [
        "generic-EPS-MissionCycles",
        "generic-EPS-CycleLife"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "required_cycles": "SIZ005.required_cycles",
        "supported_cycles": "SIZ006.supported_cycles",
        "dod_max": "SIZ006.dod_max",
        "nominal_dod": null,
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "cycle_a": null,
        "cycle_b": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS11",
      "id": "EPS011",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS11",
      "origin": "final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility",
      "rationale": "final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility",
      "text": "EPS-11. The EPS shall replenish the battery from starting energy $$energy_start_J$$ and charge based SOC $$soc_start$$ over every specified nominal repeating interval.",
      "condition": "",
      "sources": [],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries",
        "domain-bus-PowerSubsystem-SolarArrays"
      ],
      "parameters": {
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS19",
      "id": "EPS019",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS19",
      "origin": "final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets",
      "rationale": "final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets",
      "text": "EPS-19. Total EPS mass $$mass_kg$$ shall remain within allocation $$mass_allocation_kg$$.",
      "condition": "",
      "sources": [],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries",
        "domain-bus-PowerSubsystem-SolarArrays",
        "domain-bus-PowerSubsystem-ProcessorAndMemory",
        "domain-bus-PowerSubsystem-RegulatorsAndConverters",
        "domain-bus-PowerSubsystem-PowerCircuitsAndSwitches"
      ],
      "parameters": {
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS21",
      "id": "EPS021",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS21",
      "origin": "final_report/design-proposal.tex#eq:software-resource-screen; Software-host checks",
      "rationale": "final_report/design-proposal.tex#eq:software-resource-screen; Software-host checks",
      "text": "EPS-21. Each software execution host shall provide $$required_data_bytes$$ of data memory within an allocation of $$available_data_bytes$$.",
      "condition": "",
      "sources": [],
      "affected": [
        "domain-bus-PowerSubsystem-ProcessorAndMemory",
        "domain-bus-PowerSubsystem-Software"
      ],
      "parameters": {
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null,
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null
      }
    },
    {
      "key": "generic-EPS-EnergyPathEfficiencyBounds",
      "id": "SIZ011",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EnergyPathEfficiencyBounds",
      "origin": "final_report/design-proposal.tex#eq:minimum-panel-power",
      "rationale": "final_report/design-proposal.tex#eq:minimum-panel-power",
      "text": "Sunlight path efficiency $$sunlight_efficiency$$ and eclipse path efficiency $$eclipse_efficiency$$ shall lie in (0,1].",
      "condition": "sunlight_efficiency > 0 and sunlight_efficiency <= 1 and eclipse_efficiency > 0 and eclipse_efficiency <= 1",
      "sources": [
        "generic-EPS-MinimumPanelPower"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-SolarArrays",
        "domain-bus-PowerSubsystem-RegulatorsAndConverters"
      ],
      "parameters": {
        "sunlight_efficiency": "SIZ002.sunlight_efficiency",
        "eclipse_efficiency": "SIZ002.eclipse_efficiency",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-CycleFitDomain",
      "id": "SIZ013",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::CycleFitDomain",
      "origin": "final_report/design-proposal.tex#eq:battery-cycle-life",
      "rationale": "final_report/design-proposal.tex#eq:battery-cycle-life",
      "text": "Maximum DoD $$dod_max$$ shall lie in (0,1] and the sourced fit interval [$$fit_dod_min$$,$$fit_dod_max$$] for power law coefficients $$cycle_a$$ and $$cycle_b$$.",
      "condition": "cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max",
      "sources": [
        "generic-EPS-CycleLife"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "dod_max": "SIZ006.dod_max",
        "fit_dod_min": "SIZ006.fit_dod_min",
        "fit_dod_max": "SIZ006.fit_dod_max",
        "cycle_a": "SIZ006.cycle_a",
        "cycle_b": "SIZ006.cycle_b",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-CycleLimitedDoD",
      "id": "SIZ014",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::CycleLimitedDoD",
      "origin": "final_report/design-proposal.tex#eq:battery-cycle-life",
      "rationale": "final_report/design-proposal.tex#eq:battery-cycle-life",
      "text": "Maximum DoD $$dod_max$$ shall not exceed fitted cycle limit $$dod_cycle_limit$$.",
      "condition": "dod_max > 0 and dod_max <= 1 and dod_cycle_limit > 0 and dod_max <= dod_cycle_limit",
      "sources": [
        "generic-EPS-CycleLife"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "dod_max": "SIZ006.dod_max",
        "dod_cycle_limit": "SIZ006.dod_cycle_limit",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-BatteryRetainedEnergy",
      "id": "SIZ016",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::BatteryRetainedEnergy",
      "origin": "final_report/design-proposal.tex#eq:battery-assembly-capacity",
      "rationale": "final_report/design-proposal.tex#eq:battery-assembly-capacity",
      "text": "Battery EOL energy $$pack_eol_J$$ shall equal BOL energy $$pack_bol_J$$ multiplied by retained energy factor $$retained_energy_factor$$ in (0,1].",
      "condition": "pack_bol_J > 0 and retained_energy_factor > 0 and retained_energy_factor <= 1 and pack_eol_J == retained_energy_factor * pack_bol_J",
      "sources": [
        "generic-EPS-BatteryCapacityScreen"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "pack_bol_J": "SIZ008.pack_bol_J",
        "pack_eol_J": "SIZ008.pack_eol_J",
        "retained_energy_factor": "SIZ008.retained_energy_factor",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS47",
      "id": "EPS047",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS47",
      "origin": "final_report/eps-requirements.tex#EPS-09",
      "rationale": "final_report/eps-requirements.tex#EPS-09",
      "text": "EPS-47. Nominal cycle DoD $$nominal_dod$$ shall not exceed maximum DoD $$dod_max$$.",
      "condition": "",
      "sources": [
        "generic-EPS-EPS09"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries"
      ],
      "parameters": {
        "nominal_dod": "EPS009.nominal_dod",
        "dod_max": "EPS009.dod_max",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS52",
      "id": "EPS052",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS52",
      "origin": "final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility",
      "rationale": "final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility",
      "text": "EPS-52. Ending energy $$energy_end_J$$ shall be at least starting energy $$energy_start_J$$ minus nonnegative numerical closure tolerance $$closure_tolerance_J$$ over each nominal repeating interval.",
      "condition": "",
      "sources": [
        "generic-EPS-EPS11"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries",
        "domain-bus-PowerSubsystem-SolarArrays"
      ],
      "parameters": {
        "energy_start_J": "EPS011.energy_start_J",
        "energy_end_J": "EPS011.energy_end_J",
        "closure_tolerance_J": "EPS011.closure_tolerance_J",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS53",
      "id": "EPS053",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS53",
      "origin": "final_report/eps-requirements.tex#EPS-11",
      "rationale": "final_report/eps-requirements.tex#EPS-11",
      "text": "EPS-53. Ending charge based SOC $$soc_end$$ shall be at least starting SOC $$soc_start$$ over each nominal repeating interval.",
      "condition": "",
      "sources": [
        "generic-EPS-EPS11"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries",
        "domain-bus-PowerSubsystem-SolarArrays"
      ],
      "parameters": {
        "soc_start": "EPS011.soc_start",
        "soc_end": "EPS011.soc_end",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS78",
      "id": "EPS078",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS78",
      "origin": "final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets",
      "rationale": "final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets",
      "text": "EPS-78. Occupied EPS volume $$volume_m3$$ shall remain within allocation $$volume_allocation_m3$$.",
      "condition": "",
      "sources": [
        "generic-EPS-EPS19"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-Batteries",
        "domain-bus-PowerSubsystem-SolarArrays",
        "domain-bus-PowerSubsystem-ProcessorAndMemory",
        "domain-bus-PowerSubsystem-RegulatorsAndConverters",
        "domain-bus-PowerSubsystem-PowerCircuitsAndSwitches"
      ],
      "parameters": {
        "volume_m3": "EPS019.volume_m3",
        "volume_allocation_m3": "EPS019.volume_allocation_m3",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS88",
      "id": "EPS088",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS88",
      "origin": "final_report/design-proposal.tex#eq:software-resource-screen",
      "rationale": "final_report/design-proposal.tex#eq:software-resource-screen",
      "text": "EPS-88. Each software execution host shall provide $$required_program_bytes$$ of program storage within an allocation of $$available_program_bytes$$.",
      "condition": "",
      "sources": [
        "generic-EPS-EPS21"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-ProcessorAndMemory",
        "domain-bus-PowerSubsystem-Software"
      ],
      "parameters": {
        "required_program_bytes": "EPS021.required_program_bytes",
        "available_program_bytes": "EPS021.available_program_bytes",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_utilization": null,
        "allocated_utilization": null
      }
    },
    {
      "key": "generic-EPS-EPS89",
      "id": "EPS089",
      "context": "domain-bus-PowerSubsystem",
      "kind": "Requirement",
      "definition": "FrameworkRequirements::EPS89",
      "origin": "final_report/design-proposal.tex#eq:software-resource-screen",
      "rationale": "final_report/design-proposal.tex#eq:software-resource-screen",
      "text": "EPS-89. The sum of each allocated task's execution time divided by its period shall give required utilization $$required_utilization$$, at most allocation $$allocated_utilization$$.",
      "condition": "",
      "sources": [
        "generic-EPS-EPS21"
      ],
      "affected": [
        "domain-bus-PowerSubsystem-ProcessorAndMemory",
        "domain-bus-PowerSubsystem-Software"
      ],
      "parameters": {
        "required_utilization": "EPS021.required_utilization",
        "allocated_utilization": "EPS021.allocated_utilization",
        "x": null,
        "y": null,
        "z": null,
        "a": null,
        "altitude_km": null,
        "earthRadius_km": null,
        "gravitationalParameter_km3_s2": null,
        "orbit_period_s": null,
        "horizon_angle_rad": null,
        "sunlight_s": null,
        "eclipse_s": null,
        "sunlight_power_W": null,
        "eclipse_power_W": null,
        "sunlight_duty": null,
        "eclipse_duty": null,
        "sunlight_energy_J": null,
        "eclipse_energy_J": null,
        "sunlight_efficiency": null,
        "eclipse_efficiency": null,
        "panel_min_W": null,
        "cell_eol_V": null,
        "cell_eol_A": null,
        "cell_eol_W": null,
        "required_cells": null,
        "minimum_cells": null,
        "installed_cells": null,
        "orbits_per_day": null,
        "lifetime_years": null,
        "days_per_year": null,
        "required_cycles": null,
        "cycle_a": null,
        "cycle_b": null,
        "dod_max": null,
        "fit_dod_min": null,
        "fit_dod_max": null,
        "dod_cycle_limit": null,
        "supported_cycles": null,
        "degradation_margin": null,
        "battery_min_J": null,
        "pack_bol_J": null,
        "retained_energy_factor": null,
        "pack_eol_J": null,
        "sunlight_generation_J": null,
        "nominal_dod": null,
        "energy_start_J": null,
        "energy_end_J": null,
        "closure_tolerance_J": null,
        "soc_start": null,
        "soc_end": null,
        "mass_kg": null,
        "mass_allocation_kg": null,
        "volume_m3": null,
        "volume_allocation_m3": null,
        "required_data_bytes": null,
        "available_data_bytes": null,
        "required_program_bytes": null,
        "available_program_bytes": null
      }
    }
  ],
  "components": []
}
requirements-ui:end-data */
package MissionRequirements {
    private import External::*;
    private import Orbit;
    private import SpaceSegment::*;
    private import GroundSegment::*;
    private import ScalarValues::*;
    part element_domain_horbit : Orbit {
        attribute externalId : String = "ORB";
        attribute displayName : String = "Orbit";
        attribute :>> altitude_km = statement_generic_hORB_hOrbitPeriod.'altitude_km';
        attribute :>> earthRadius_km = statement_generic_hORB_hOrbitPeriod.'earthRadius_km';
        attribute :>> gravitationalParameter_km3_s2 = statement_generic_hORB_hOrbitPeriod.'gravitationalParameter_km3_s2';
    }
    part element_domain_hbus : SpaceSegment::CubeSat {
        attribute externalId : String = "BUS";
        attribute displayName : String = "CubeSat Bus";
        part element_domain_hbus_hCommandAndDataHandlingSubsystem : SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem {
            attribute externalId : String = "CDH";
            attribute displayName : String = "Command and Data Handling";
        }
        part element_domain_hbus_hCommunicationSubsystem : SpaceSegment::CubeSat::CommunicationSubsystem {
            attribute externalId : String = "COM";
            attribute displayName : String = "Communication";
        }
        part element_domain_hbus_hAttitudeDeterminationAndControlSubsystem : SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem {
            attribute externalId : String = "ADC";
            attribute displayName : String = "Attitude Determination and Control";
        }
        part element_domain_hbus_hGuidanceNavigationAndControlSubsystem : SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem {
            attribute externalId : String = "GNC";
            attribute displayName : String = "Guidance Navigation and Control";
        }
        part element_domain_hbus_hStructuresAndMechanismsSubsystem : SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem {
            attribute externalId : String = "STR";
            attribute displayName : String = "Structures and Mechanisms";
        }
        part element_domain_hbus_hThermalSubsystem : SpaceSegment::CubeSat::ThermalSubsystem {
            attribute externalId : String = "THE";
            attribute displayName : String = "Thermal";
        }
        part element_domain_hbus_hPropulsionSubsystem : SpaceSegment::CubeSat::PropulsionSubsystem {
            attribute externalId : String = "PRO";
            attribute displayName : String = "Propulsion";
        }
        part element_domain_hbus_hPowerSubsystem : SpaceSegment::CubeSat::PowerSubsystem {
            attribute externalId : String = "EPS";
            attribute displayName : String = "Power";
            part element_domain_hbus_hPowerSubsystem_hBatteries : SpaceSegment::CubeSat::PowerSubsystem::Batteries {
                attribute externalId : String = "BAT";
                attribute displayName : String = "Batteries";
            }
            part element_domain_hbus_hPowerSubsystem_hSolarArrays : SpaceSegment::CubeSat::PowerSubsystem::SolarArrays {
                attribute externalId : String = "SOL";
                attribute displayName : String = "Solar Arrays";
            }
            part element_domain_hbus_hPowerSubsystem_hProcessorAndMemory : SpaceSegment::CubeSat::PowerSubsystem::ProcessorAndMemory {
                attribute externalId : String = "PCM";
                attribute displayName : String = "Processor and Memory";
            }
            part element_domain_hbus_hPowerSubsystem_hRegulatorsAndConverters : SpaceSegment::CubeSat::PowerSubsystem::RegulatorsAndConverters {
                attribute externalId : String = "REG";
                attribute displayName : String = "Regulators and Converters";
            }
            part element_domain_hbus_hPowerSubsystem_hPowerCircuitsAndSwitches : SpaceSegment::CubeSat::PowerSubsystem::PowerCircuitsAndSwitches {
                attribute externalId : String = "PCS";
                attribute displayName : String = "Power Circuits and Switches";
            }
            part element_domain_hbus_hPowerSubsystem_hSoftware : SpaceSegment::CubeSat::PowerSubsystem::Software {
                attribute externalId : String = "SFW";
                attribute displayName : String = "Software";
            }
        }
    }
    part element_domain_hpayload : SpaceSegment::CubeSat::PayloadSubsystem {
        attribute externalId : String = "PAY";
        attribute displayName : String = "Payload";
        part element_domain_hpayload_hInstrument : SpaceSegment::CubeSat::PayloadSubsystem::Instrument {
            attribute externalId : String = "INS";
            attribute displayName : String = "Instrument";
        }
        part element_domain_hpayload_hProcessorAndMemory : SpaceSegment::CubeSat::PayloadSubsystem::ProcessorAndMemory {
            attribute externalId : String = "AAA";
            attribute displayName : String = "Processor and Memory";
        }
    }
    part element_domain_hground : GroundSegment::GroundStation {
        attribute externalId : String = "GND";
        attribute displayName : String = "Ground Station";
        part element_domain_hground_hPlanAndScheduleSubsystem : GroundSegment::PlanAndScheduleSubsystem {
            attribute externalId : String = "PLS";
            attribute displayName : String = "Plan and Schedule";
        }
        part element_domain_hground_hSpacecraftCommandSubsystem : GroundSegment::SpacecraftCommandSubsystem {
            attribute externalId : String = "SCC";
            attribute displayName : String = "Spacecraft Command";
        }
        part element_domain_hground_hGroundEquipmentControlSubsystem : GroundSegment::GroundEquipmentControlSubsystem {
            attribute externalId : String = "GEC";
            attribute displayName : String = "Ground Equipment Control";
        }
        part element_domain_hground_hSpaceGroundCommunicationSubsystem : GroundSegment::SpaceGroundCommunicationSubsystem {
            attribute externalId : String = "SGC";
            attribute displayName : String = "Space Ground Communication";
        }
        part element_domain_hground_hMissionDataProcessingSubsystem : GroundSegment::MissionDataProcessingSubsystem {
            attribute externalId : String = "MDP";
            attribute displayName : String = "Mission Data Processing";
        }
        part element_domain_hground_hMissionDataDisseminationSubsystem : GroundSegment::MissionDataDisseminationSubsystem {
            attribute externalId : String = "MDD";
            attribute displayName : String = "Mission Data Dissemination";
        }
        part element_domain_hground_hNetworkSubsystem : GroundSegment::NetworkSubsystem {
            attribute externalId : String = "NET";
            attribute displayName : String = "Network";
        }
        part element_domain_hground_hTelemetryProcessingSubsystem : GroundSegment::TelemetryProcessingSubsystem {
            attribute externalId : String = "TLM";
            attribute displayName : String = "Telemetry Processing";
        }
    }
    requirement statement_generic_hORB_hOrbitPeriod : FrameworkRequirements::OrbitPeriod {
        attribute externalId : String = "ORB001";
        attribute tableName : String = "Mission";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The preliminary circular orbit shall have period $$orbit_period_s$$ at altitude $$altitude_km$$, using Earth radius $$earthRadius_km$$ and gravitational parameter $$gravitationalParameter_km3_s2$$.";
        attribute verificationExpression : String[0..1] = "altitude_km > 0 and earthRadius_km > 0 and gravitationalParameter_km3_s2 > 0 and orbit_period_s > 0 and orbit_period_s == 2 * pi * sqrt((earthRadius_km + altitude_km) ^ 3 / gravitationalParameter_km3_s2)";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:orbit-period (handpicked-0003, Eqs. 1-4)";
        attribute rationale : String = "final_report/design-proposal.tex#eq:orbit-period (handpicked-0003, Eqs. 1-4)";
        attribute :>> 'earthRadius_km' = 6378;
        attribute :>> 'gravitationalParameter_km3_s2' = 398601;
        attribute :>> 'orbit_period_s' = ((2 * TrigFunctions::pi) * RealFunctions::sqrt(((('earthRadius_km' + 'altitude_km') ^ 3) / 'gravitationalParameter_km3_s2')));
        ref part affectedElements[0..*] = (element_domain_horbit);
        require constraint verificationCondition { ((((('altitude_km' > 0) and ('earthRadius_km' > 0)) and ('gravitationalParameter_km3_s2' > 0)) and ('orbit_period_s' > 0)) and ('orbit_period_s' == ((2 * TrigFunctions::pi) * RealFunctions::sqrt(((('earthRadius_km' + 'altitude_km') ^ 3) / 'gravitationalParameter_km3_s2'))))) }
    }
    requirement statement_generic_hORB_hIlluminationPeriods : FrameworkRequirements::IlluminationPeriods {
        attribute externalId : String = "ORB002";
        attribute tableName : String = "Mission";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The preliminary circular orbit at altitude $$altitude_km$$ shall provide $$sunlight_s$$ of sunlight and $$eclipse_s$$ of eclipse per $$orbit_period_s$$ orbit, using Earth radius $$earthRadius_km$$ and horizon angle $$horizon_angle_rad$$.";
        attribute verificationExpression : String[0..1] = "altitude_km > 0 and earthRadius_km > 0 and orbit_period_s > 0 and sunlight_s > 0 and eclipse_s > 0 and horizon_angle_rad == arccos(earthRadius_km / (earthRadius_km + altitude_km)) and sunlight_s == (0.5 + horizon_angle_rad / pi) * orbit_period_s and eclipse_s == (0.5 - horizon_angle_rad / pi) * orbit_period_s and abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period, eq:eclipse-geometry";
        attribute rationale : String = "final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period, eq:eclipse-geometry";
        attribute :>> 'altitude_km' = statement_generic_hORB_hOrbitPeriod.'altitude_km';
        attribute :>> 'earthRadius_km' = statement_generic_hORB_hOrbitPeriod.'earthRadius_km';
        attribute :>> 'orbit_period_s' = statement_generic_hORB_hOrbitPeriod.'orbit_period_s';
        attribute :>> 'horizon_angle_rad' = TrigFunctions::arccos((('earthRadius_km' / ('earthRadius_km' + 'altitude_km')) as TrigFunctions::UnitBoundedReal));
        attribute :>> 'sunlight_s' = ((0.5 + ('horizon_angle_rad' / TrigFunctions::pi)) * 'orbit_period_s');
        attribute :>> 'eclipse_s' = ((0.5 - ('horizon_angle_rad' / TrigFunctions::pi)) * 'orbit_period_s');
        ref part affectedElements[0..*] = (element_domain_horbit);
        require constraint verificationCondition { ((((((((('altitude_km' > 0) and ('earthRadius_km' > 0)) and ('orbit_period_s' > 0)) and ('sunlight_s' > 0)) and ('eclipse_s' > 0)) and ('horizon_angle_rad' == TrigFunctions::arccos((('earthRadius_km' / ('earthRadius_km' + 'altitude_km')) as TrigFunctions::UnitBoundedReal)))) and ('sunlight_s' == ((0.5 + ('horizon_angle_rad' / TrigFunctions::pi)) * 'orbit_period_s'))) and ('eclipse_s' == ((0.5 - ('horizon_angle_rad' / TrigFunctions::pi)) * 'orbit_period_s'))) and (RealFunctions::abs((('sunlight_s' + 'eclipse_s') - 'orbit_period_s')) <= (1e-9 * 'orbit_period_s'))) }
    }
    requirement statement_generic_hORB_hOrbitPeriodClosure : FrameworkRequirements::OrbitPeriodClosure {
        attribute externalId : String = "ORB003";
        attribute tableName : String = "Mission";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The positive sunlight and eclipse periods shall sum to $$orbit_period_s$$ within numerical tolerance.";
        attribute verificationExpression : String[0..1] = "orbit_period_s > 0 and sunlight_s > 0 and eclipse_s > 0 and abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period";
        attribute rationale : String = "final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period";
        attribute :>> 'orbit_period_s' = statement_generic_hORB_hIlluminationPeriods.'orbit_period_s';
        attribute :>> 'sunlight_s' = statement_generic_hORB_hIlluminationPeriods.'sunlight_s';
        attribute :>> 'eclipse_s' = statement_generic_hORB_hIlluminationPeriods.'eclipse_s';
        ref part affectedElements[0..*] = (element_domain_horbit);
        require constraint verificationCondition { (((('orbit_period_s' > 0) and ('sunlight_s' > 0)) and ('eclipse_s' > 0)) and (RealFunctions::abs((('sunlight_s' + 'eclipse_s') - 'orbit_period_s')) <= (1e-9 * 'orbit_period_s'))) }
    }
    requirement statement_generic_hEPS_hLoadEnergy : FrameworkRequirements::LoadEnergy {
        attribute externalId : String = "SIZ001";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The preliminary load budget shall allocate $$sunlight_energy_J$$ during $$sunlight_s$$ of sunlight and $$eclipse_energy_J$$ during $$eclipse_s$$ of eclipse.";
        attribute verificationExpression : String[0..1] = "sunlight_power_W >= 0 and eclipse_power_W >= 0 and sunlight_duty >= 0 and sunlight_duty <= 1 and eclipse_duty >= 0 and eclipse_duty <= 1 and sunlight_s > 0 and eclipse_s > 0 and sunlight_energy_J == sunlight_power_W * sunlight_duty * sunlight_s and eclipse_energy_J == eclipse_power_W * eclipse_duty * eclipse_s";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:minimum-panel-power; EPSModel::ModeLoadProfile and AccountingPlan";
        attribute rationale : String = "final_report/design-proposal.tex#eq:minimum-panel-power; EPSModel::ModeLoadProfile and AccountingPlan";
        attribute :>> 'sunlight_s' = statement_generic_hORB_hIlluminationPeriods.'sunlight_s';
        attribute :>> 'eclipse_s' = statement_generic_hORB_hIlluminationPeriods.'eclipse_s';
        attribute :>> 'sunlight_energy_J' = (('sunlight_power_W' * 'sunlight_duty') * 'sunlight_s');
        attribute :>> 'eclipse_energy_J' = (('eclipse_power_W' * 'eclipse_duty') * 'eclipse_s');
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays);
        require constraint verificationCondition { (((((((((('sunlight_power_W' >= 0) and ('eclipse_power_W' >= 0)) and ('sunlight_duty' >= 0)) and ('sunlight_duty' <= 1)) and ('eclipse_duty' >= 0)) and ('eclipse_duty' <= 1)) and ('sunlight_s' > 0)) and ('eclipse_s' > 0)) and ('sunlight_energy_J' == (('sunlight_power_W' * 'sunlight_duty') * 'sunlight_s'))) and ('eclipse_energy_J' == (('eclipse_power_W' * 'eclipse_duty') * 'eclipse_s'))) }
    }
    requirement statement_generic_hEPS_hMinimumPanelPower : FrameworkRequirements::MinimumPanelPower {
        attribute externalId : String = "SIZ002";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The solar panels shall provide at least $$panel_min_W$$ at the declared source boundary.";
        attribute verificationExpression : String[0..1] = "sunlight_energy_J >= 0 and eclipse_energy_J >= 0 and sunlight_s > 0 and sunlight_efficiency > 0 and sunlight_efficiency <= 1 and eclipse_efficiency > 0 and eclipse_efficiency <= 1 and panel_min_W == (sunlight_energy_J / sunlight_efficiency + eclipse_energy_J / eclipse_efficiency) / sunlight_s";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:minimum-panel-power (handpicked-0003)";
        attribute rationale : String = "final_report/design-proposal.tex#eq:minimum-panel-power (handpicked-0003)";
        attribute :>> 'sunlight_s' = statement_generic_hORB_hIlluminationPeriods.'sunlight_s';
        attribute :>> 'sunlight_energy_J' = statement_generic_hEPS_hLoadEnergy.'sunlight_energy_J';
        attribute :>> 'eclipse_energy_J' = statement_generic_hEPS_hLoadEnergy.'eclipse_energy_J';
        attribute :>> 'panel_min_W' = ((('sunlight_energy_J' / 'sunlight_efficiency') + ('eclipse_energy_J' / 'eclipse_efficiency')) / 'sunlight_s');
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hRegulatorsAndConverters);
        require constraint verificationCondition { (((((((('sunlight_energy_J' >= 0) and ('eclipse_energy_J' >= 0)) and ('sunlight_s' > 0)) and ('sunlight_efficiency' > 0)) and ('sunlight_efficiency' <= 1)) and ('eclipse_efficiency' > 0)) and ('eclipse_efficiency' <= 1)) and ('panel_min_W' == ((('sunlight_energy_J' / 'sunlight_efficiency') + ('eclipse_energy_J' / 'eclipse_efficiency')) / 'sunlight_s'))) }
    }
    requirement statement_generic_hEPS_hSolarCellPower : FrameworkRequirements::SolarCellPower {
        attribute externalId : String = "SIZ003";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The selected solar cell shall provide EOL maximum power $$cell_eol_W$$ from maximum power point voltage $$cell_eol_V$$ and current $$cell_eol_A$$.";
        attribute verificationExpression : String[0..1] = "cell_eol_V > 0 and cell_eol_A > 0 and cell_eol_W == cell_eol_V * cell_eol_A";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:solar-cell-eol-power";
        attribute rationale : String = "final_report/design-proposal.tex#eq:solar-cell-eol-power";
        attribute :>> 'cell_eol_W' = ('cell_eol_V' * 'cell_eol_A');
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays);
        require constraint verificationCondition { ((('cell_eol_V' > 0) and ('cell_eol_A' > 0)) and ('cell_eol_W' == ('cell_eol_V' * 'cell_eol_A'))) }
    }
    requirement statement_generic_hEPS_hSolarCellCount : FrameworkRequirements::SolarCellCount {
        attribute externalId : String = "SIZ004";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The array shall install $$installed_cells$$, at least the minimum $$minimum_cells$$ obtained by rounding calculated count $$required_cells$$ upward.";
        attribute verificationExpression : String[0..1] = "panel_min_W >= 0 and cell_eol_W > 0 and required_cells == panel_min_W / cell_eol_W and minimum_cells == -floor(-required_cells) and installed_cells > 0 and installed_cells >= minimum_cells";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:solar-cell-count, eq:pv-integer-configuration";
        attribute rationale : String = "final_report/design-proposal.tex#eq:solar-cell-count, eq:pv-integer-configuration";
        attribute :>> 'panel_min_W' = statement_generic_hEPS_hMinimumPanelPower.'panel_min_W';
        attribute :>> 'cell_eol_W' = statement_generic_hEPS_hSolarCellPower.'cell_eol_W';
        attribute :>> 'required_cells' = ('panel_min_W' / 'cell_eol_W');
        assert constraint { (- RealFunctions::floor((- 'required_cells'))) == RealFunctions::ToInteger((- RealFunctions::floor((- 'required_cells')))) }
        attribute :>> 'minimum_cells' = RealFunctions::ToInteger((- RealFunctions::floor((- 'required_cells'))));
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays);
        require constraint verificationCondition { (((((('panel_min_W' >= 0) and ('cell_eol_W' > 0)) and ('required_cells' == ('panel_min_W' / 'cell_eol_W'))) and ('minimum_cells' == (- RealFunctions::floor((- 'required_cells'))))) and ('installed_cells' > 0)) and ('installed_cells' >= 'minimum_cells')) }
    }
    requirement statement_generic_hEPS_hMissionCycles : FrameworkRequirements::MissionCycles {
        attribute externalId : String = "SIZ005";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "For one nominal cycle per orbit, the battery shall support at least $$required_cycles$$ over $$lifetime_years$$, using $$days_per_year$$ and $$orbits_per_day$$ derived from period $$orbit_period_s$$.";
        attribute verificationExpression : String[0..1] = "orbit_period_s > 0 and lifetime_years > 0 and days_per_year > 0 and orbits_per_day == 86400 / orbit_period_s and required_cycles == lifetime_years * days_per_year * orbits_per_day";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:battery-mission-cycles";
        attribute rationale : String = "final_report/design-proposal.tex#eq:battery-mission-cycles";
        attribute :>> 'orbit_period_s' = statement_generic_hORB_hOrbitPeriod.'orbit_period_s';
        attribute :>> 'orbits_per_day' = (86400 / 'orbit_period_s');
        attribute :>> 'required_cycles' = (('lifetime_years' * 'days_per_year') * 'orbits_per_day');
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
        require constraint verificationCondition { ((((('orbit_period_s' > 0) and ('lifetime_years' > 0)) and ('days_per_year' > 0)) and ('orbits_per_day' == (86400 / 'orbit_period_s'))) and ('required_cycles' == (('lifetime_years' * 'days_per_year') * 'orbits_per_day'))) }
    }
    requirement statement_generic_hEPS_hCycleLife : FrameworkRequirements::CycleLife {
        attribute externalId : String = "SIZ006";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The selected maximum depth of discharge $$dod_max$$ shall support $$supported_cycles$$, at least the required $$required_cycles$$.";
        attribute verificationExpression : String[0..1] = "required_cycles > 0 and cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max and dod_cycle_limit == (required_cycles / cycle_a) ^ (1 / cycle_b) and supported_cycles == cycle_a * dod_max ^ cycle_b and supported_cycles >= required_cycles";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:battery-cycle-life; EPS-09";
        attribute rationale : String = "final_report/design-proposal.tex#eq:battery-cycle-life; EPS-09";
        attribute :>> 'required_cycles' = statement_generic_hEPS_hMissionCycles.'required_cycles';
        attribute :>> 'dod_cycle_limit' = (('required_cycles' / 'cycle_a') ^ (1 / 'cycle_b'));
        attribute :>> 'supported_cycles' = ('cycle_a' * ('dod_max' ^ 'cycle_b'));
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
        require constraint verificationCondition { ((((((((((('required_cycles' > 0) and ('cycle_a' > 0)) and ('cycle_b' < 0)) and ('fit_dod_min' > 0)) and ('fit_dod_min' <= 'fit_dod_max')) and ('fit_dod_max' <= 1)) and ('dod_max' >= 'fit_dod_min')) and ('dod_max' <= 'fit_dod_max')) and ('dod_cycle_limit' == (('required_cycles' / 'cycle_a') ^ (1 / 'cycle_b')))) and ('supported_cycles' == ('cycle_a' * ('dod_max' ^ 'cycle_b')))) and ('supported_cycles' >= 'required_cycles')) }
    }
    requirement statement_generic_hEPS_hMinimumBatteryEnergy : FrameworkRequirements::MinimumBatteryEnergy {
        attribute externalId : String = "SIZ007";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The battery shall provide at least $$battery_min_J$$ of BOL energy for eclipse demand $$eclipse_energy_J$$ at maximum DoD $$dod_max$$ and degradation margin $$degradation_margin$$.";
        attribute verificationExpression : String[0..1] = "eclipse_energy_J >= 0 and dod_max > 0 and dod_max <= 1 and degradation_margin >= 0 and battery_min_J == eclipse_energy_J / dod_max * (1 + degradation_margin) and required_cycles > 0 and cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max and supported_cycles == cycle_a * dod_max ^ cycle_b and supported_cycles >= required_cycles";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:battery-energy; EPS-08";
        attribute rationale : String = "final_report/design-proposal.tex#eq:battery-energy; EPS-08";
        attribute :>> 'eclipse_energy_J' = statement_generic_hEPS_hLoadEnergy.'eclipse_energy_J';
        attribute :>> 'required_cycles' = statement_generic_hEPS_hMissionCycles.'required_cycles';
        attribute :>> 'cycle_a' = statement_generic_hEPS_hCycleLife.'cycle_a';
        attribute :>> 'cycle_b' = statement_generic_hEPS_hCycleLife.'cycle_b';
        attribute :>> 'dod_max' = statement_generic_hEPS_hCycleLife.'dod_max';
        attribute :>> 'fit_dod_min' = statement_generic_hEPS_hCycleLife.'fit_dod_min';
        attribute :>> 'fit_dod_max' = statement_generic_hEPS_hCycleLife.'fit_dod_max';
        attribute :>> 'supported_cycles' = statement_generic_hEPS_hCycleLife.'supported_cycles';
        attribute :>> 'battery_min_J' = (('eclipse_energy_J' / 'dod_max') * (1 + 'degradation_margin'));
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
        require constraint verificationCondition { ((((((((((((((('eclipse_energy_J' >= 0) and ('dod_max' > 0)) and ('dod_max' <= 1)) and ('degradation_margin' >= 0)) and ('battery_min_J' == (('eclipse_energy_J' / 'dod_max') * (1 + 'degradation_margin')))) and ('required_cycles' > 0)) and ('cycle_a' > 0)) and ('cycle_b' < 0)) and ('fit_dod_min' > 0)) and ('fit_dod_min' <= 'fit_dod_max')) and ('fit_dod_max' <= 1)) and ('dod_max' >= 'fit_dod_min')) and ('dod_max' <= 'fit_dod_max')) and ('supported_cycles' == ('cycle_a' * ('dod_max' ^ 'cycle_b')))) and ('supported_cycles' >= 'required_cycles')) }
    }
    requirement statement_generic_hEPS_hBatteryCapacityScreen : FrameworkRequirements::BatteryCapacityScreen {
        attribute externalId : String = "SIZ008";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "The selected battery shall have BOL energy $$pack_bol_J$$, at least the preliminary minimum $$battery_min_J$$.";
        attribute verificationExpression : String[0..1] = "battery_min_J >= 0 and pack_bol_J > 0 and pack_bol_J >= battery_min_J and retained_energy_factor > 0 and retained_energy_factor <= 1 and pack_eol_J == retained_energy_factor * pack_bol_J";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:battery-assembly-capacity; EPS-08";
        attribute rationale : String = "final_report/design-proposal.tex#eq:battery-assembly-capacity; EPS-08";
        attribute :>> 'battery_min_J' = statement_generic_hEPS_hMinimumBatteryEnergy.'battery_min_J';
        attribute :>> 'pack_eol_J' = ('retained_energy_factor' * 'pack_bol_J');
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
        require constraint verificationCondition { (((((('battery_min_J' >= 0) and ('pack_bol_J' > 0)) and ('pack_bol_J' >= 'battery_min_J')) and ('retained_energy_factor' > 0)) and ('retained_energy_factor' <= 1)) and ('pack_eol_J' == ('retained_energy_factor' * 'pack_bol_J'))) }
    }
    requirement statement_generic_hEPS_hEPS02 : FrameworkRequirements::EPS02 {
        attribute externalId : String = "EPS002";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-02. The solar arrays shall provide at least $$panel_min_W$$ of average source power from $$sunlight_generation_J$$ over $$sunlight_s$$ of sunlight at each section's attainable DET or MPPT operating point under applicable illumination and EOL conditions.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-02; eq:array-generation-screen, eq:pv-integer-configuration";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-02; eq:array-generation-screen, eq:pv-integer-configuration";
        attribute :>> 'sunlight_s' = statement_generic_hORB_hIlluminationPeriods.'sunlight_s';
        attribute :>> 'panel_min_W' = statement_generic_hEPS_hMinimumPanelPower.'panel_min_W';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays);
    }
    requirement statement_generic_hEPS_hEPS08 : FrameworkRequirements::EPS08 {
        attribute externalId : String = "EPS008";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-08. The battery pack BOL energy $$pack_bol_J$$ shall meet minimum energy $$battery_min_J$$ from preliminary battery sizing.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-08; eq:battery-energy, eq:battery-assembly-capacity, eq:battery-assembly-ratings";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-08; eq:battery-energy, eq:battery-assembly-capacity, eq:battery-assembly-ratings";
        attribute :>> 'battery_min_J' = statement_generic_hEPS_hMinimumBatteryEnergy.'battery_min_J';
        attribute :>> 'pack_bol_J' = statement_generic_hEPS_hBatteryCapacityScreen.'pack_bol_J';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
    }
    requirement statement_generic_hEPS_hEPS09 : FrameworkRequirements::EPS09 {
        attribute externalId : String = "EPS009";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-09. For nominal operation, the battery pack shall support $$supported_cycles$$, at least the required $$required_cycles$$ at the selected DoD and applicable conditions.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-09; eq:battery-mission-cycles, eq:battery-cycle-life";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-09; eq:battery-mission-cycles, eq:battery-cycle-life";
        attribute :>> 'required_cycles' = statement_generic_hEPS_hMissionCycles.'required_cycles';
        attribute :>> 'dod_max' = statement_generic_hEPS_hCycleLife.'dod_max';
        attribute :>> 'supported_cycles' = statement_generic_hEPS_hCycleLife.'supported_cycles';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
    }
    requirement statement_generic_hEPS_hEPS11 : FrameworkRequirements::EPS11 {
        attribute externalId : String = "EPS011";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-11. The EPS shall replenish the battery from starting energy $$energy_start_J$$ and charge based SOC $$soc_start$$ over every specified nominal repeating interval.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility";
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays);
    }
    requirement statement_generic_hEPS_hEPS19 : FrameworkRequirements::EPS19 {
        attribute externalId : String = "EPS019";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-19. Total EPS mass $$mass_kg$$ shall remain within allocation $$mass_allocation_kg$$.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets";
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hProcessorAndMemory, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hRegulatorsAndConverters, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hPowerCircuitsAndSwitches);
    }
    requirement statement_generic_hEPS_hEPS21 : FrameworkRequirements::EPS21 {
        attribute externalId : String = "EPS021";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-21. Each software execution host shall provide $$required_data_bytes$$ of data memory within an allocation of $$available_data_bytes$$.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:software-resource-screen; Software-host checks";
        attribute rationale : String = "final_report/design-proposal.tex#eq:software-resource-screen; Software-host checks";
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hProcessorAndMemory, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSoftware);
    }
    requirement statement_generic_hEPS_hEnergyPathEfficiencyBounds : FrameworkRequirements::EnergyPathEfficiencyBounds {
        attribute externalId : String = "SIZ011";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "Sunlight path efficiency $$sunlight_efficiency$$ and eclipse path efficiency $$eclipse_efficiency$$ shall lie in (0,1].";
        attribute verificationExpression : String[0..1] = "sunlight_efficiency > 0 and sunlight_efficiency <= 1 and eclipse_efficiency > 0 and eclipse_efficiency <= 1";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:minimum-panel-power";
        attribute rationale : String = "final_report/design-proposal.tex#eq:minimum-panel-power";
        attribute :>> 'sunlight_efficiency' = statement_generic_hEPS_hMinimumPanelPower.'sunlight_efficiency';
        attribute :>> 'eclipse_efficiency' = statement_generic_hEPS_hMinimumPanelPower.'eclipse_efficiency';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hRegulatorsAndConverters);
        require constraint verificationCondition { (((('sunlight_efficiency' > 0) and ('sunlight_efficiency' <= 1)) and ('eclipse_efficiency' > 0)) and ('eclipse_efficiency' <= 1)) }
    }
    requirement statement_generic_hEPS_hCycleFitDomain : FrameworkRequirements::CycleFitDomain {
        attribute externalId : String = "SIZ013";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "Maximum DoD $$dod_max$$ shall lie in (0,1] and the sourced fit interval [$$fit_dod_min$$,$$fit_dod_max$$] for power law coefficients $$cycle_a$$ and $$cycle_b$$.";
        attribute verificationExpression : String[0..1] = "cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:battery-cycle-life";
        attribute rationale : String = "final_report/design-proposal.tex#eq:battery-cycle-life";
        attribute :>> 'cycle_a' = statement_generic_hEPS_hCycleLife.'cycle_a';
        attribute :>> 'cycle_b' = statement_generic_hEPS_hCycleLife.'cycle_b';
        attribute :>> 'dod_max' = statement_generic_hEPS_hCycleLife.'dod_max';
        attribute :>> 'fit_dod_min' = statement_generic_hEPS_hCycleLife.'fit_dod_min';
        attribute :>> 'fit_dod_max' = statement_generic_hEPS_hCycleLife.'fit_dod_max';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
        require constraint verificationCondition { ((((((('cycle_a' > 0) and ('cycle_b' < 0)) and ('fit_dod_min' > 0)) and ('fit_dod_min' <= 'fit_dod_max')) and ('fit_dod_max' <= 1)) and ('dod_max' >= 'fit_dod_min')) and ('dod_max' <= 'fit_dod_max')) }
    }
    requirement statement_generic_hEPS_hCycleLimitedDoD : FrameworkRequirements::CycleLimitedDoD {
        attribute externalId : String = "SIZ014";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "Maximum DoD $$dod_max$$ shall not exceed fitted cycle limit $$dod_cycle_limit$$.";
        attribute verificationExpression : String[0..1] = "dod_max > 0 and dod_max <= 1 and dod_cycle_limit > 0 and dod_max <= dod_cycle_limit";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:battery-cycle-life";
        attribute rationale : String = "final_report/design-proposal.tex#eq:battery-cycle-life";
        attribute :>> 'dod_max' = statement_generic_hEPS_hCycleLife.'dod_max';
        attribute :>> 'dod_cycle_limit' = statement_generic_hEPS_hCycleLife.'dod_cycle_limit';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
        require constraint verificationCondition { (((('dod_max' > 0) and ('dod_max' <= 1)) and ('dod_cycle_limit' > 0)) and ('dod_max' <= 'dod_cycle_limit')) }
    }
    requirement statement_generic_hEPS_hBatteryRetainedEnergy : FrameworkRequirements::BatteryRetainedEnergy {
        attribute externalId : String = "SIZ016";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "Battery EOL energy $$pack_eol_J$$ shall equal BOL energy $$pack_bol_J$$ multiplied by retained energy factor $$retained_energy_factor$$ in (0,1].";
        attribute verificationExpression : String[0..1] = "pack_bol_J > 0 and retained_energy_factor > 0 and retained_energy_factor <= 1 and pack_eol_J == retained_energy_factor * pack_bol_J";
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:battery-assembly-capacity";
        attribute rationale : String = "final_report/design-proposal.tex#eq:battery-assembly-capacity";
        attribute :>> 'pack_bol_J' = statement_generic_hEPS_hBatteryCapacityScreen.'pack_bol_J';
        attribute :>> 'retained_energy_factor' = statement_generic_hEPS_hBatteryCapacityScreen.'retained_energy_factor';
        attribute :>> 'pack_eol_J' = statement_generic_hEPS_hBatteryCapacityScreen.'pack_eol_J';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
        require constraint verificationCondition { (((('pack_bol_J' > 0) and ('retained_energy_factor' > 0)) and ('retained_energy_factor' <= 1)) and ('pack_eol_J' == ('retained_energy_factor' * 'pack_bol_J'))) }
    }
    requirement statement_generic_hEPS_hEPS47 : FrameworkRequirements::EPS47 {
        attribute externalId : String = "EPS047";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-47. Nominal cycle DoD $$nominal_dod$$ shall not exceed maximum DoD $$dod_max$$.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-09";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-09";
        attribute :>> 'dod_max' = statement_generic_hEPS_hEPS09.'dod_max';
        attribute :>> 'nominal_dod' = statement_generic_hEPS_hEPS09.'nominal_dod';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries);
    }
    requirement statement_generic_hEPS_hEPS52 : FrameworkRequirements::EPS52 {
        attribute externalId : String = "EPS052";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-52. Ending energy $$energy_end_J$$ shall be at least starting energy $$energy_start_J$$ minus nonnegative numerical closure tolerance $$closure_tolerance_J$$ over each nominal repeating interval.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility";
        attribute :>> 'energy_start_J' = statement_generic_hEPS_hEPS11.'energy_start_J';
        attribute :>> 'energy_end_J' = statement_generic_hEPS_hEPS11.'energy_end_J';
        attribute :>> 'closure_tolerance_J' = statement_generic_hEPS_hEPS11.'closure_tolerance_J';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays);
    }
    requirement statement_generic_hEPS_hEPS53 : FrameworkRequirements::EPS53 {
        attribute externalId : String = "EPS053";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-53. Ending charge based SOC $$soc_end$$ shall be at least starting SOC $$soc_start$$ over each nominal repeating interval.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-11";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-11";
        attribute :>> 'soc_start' = statement_generic_hEPS_hEPS11.'soc_start';
        attribute :>> 'soc_end' = statement_generic_hEPS_hEPS11.'soc_end';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays);
    }
    requirement statement_generic_hEPS_hEPS78 : FrameworkRequirements::EPS78 {
        attribute externalId : String = "EPS078";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-78. Occupied EPS volume $$volume_m3$$ shall remain within allocation $$volume_allocation_m3$$.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets";
        attribute rationale : String = "final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets";
        attribute :>> 'volume_m3' = statement_generic_hEPS_hEPS19.'volume_m3';
        attribute :>> 'volume_allocation_m3' = statement_generic_hEPS_hEPS19.'volume_allocation_m3';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hBatteries, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSolarArrays, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hProcessorAndMemory, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hRegulatorsAndConverters, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hPowerCircuitsAndSwitches);
    }
    requirement statement_generic_hEPS_hEPS88 : FrameworkRequirements::EPS88 {
        attribute externalId : String = "EPS088";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-88. Each software execution host shall provide $$required_program_bytes$$ of program storage within an allocation of $$available_program_bytes$$.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:software-resource-screen";
        attribute rationale : String = "final_report/design-proposal.tex#eq:software-resource-screen";
        assert constraint { statement_generic_hEPS_hEPS21.'required_program_bytes' == RealFunctions::ToInteger(statement_generic_hEPS_hEPS21.'required_program_bytes') }
        attribute :>> 'required_program_bytes' = RealFunctions::ToInteger(statement_generic_hEPS_hEPS21.'required_program_bytes');
        assert constraint { statement_generic_hEPS_hEPS21.'available_program_bytes' == RealFunctions::ToInteger(statement_generic_hEPS_hEPS21.'available_program_bytes') }
        attribute :>> 'available_program_bytes' = RealFunctions::ToInteger(statement_generic_hEPS_hEPS21.'available_program_bytes');
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hProcessorAndMemory, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSoftware);
    }
    requirement statement_generic_hEPS_hEPS89 : FrameworkRequirements::EPS89 {
        attribute externalId : String = "EPS089";
        attribute tableName : String = "EPS";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "EPS-89. The sum of each allocated task's execution time divided by its period shall give required utilization $$required_utilization$$, at most allocation $$allocated_utilization$$.";
        attribute verificationExpression : String[0..1];
        attribute sourceReference : String = "final_report/design-proposal.tex#eq:software-resource-screen";
        attribute rationale : String = "final_report/design-proposal.tex#eq:software-resource-screen";
        attribute :>> 'required_utilization' = statement_generic_hEPS_hEPS21.'required_utilization';
        attribute :>> 'allocated_utilization' = statement_generic_hEPS_hEPS21.'allocated_utilization';
        ref part affectedElements[0..*] = (element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hProcessorAndMemory, element_domain_hbus.element_domain_hbus_hPowerSubsystem.element_domain_hbus_hPowerSubsystem_hSoftware);
    }
    dependency from statement_generic_hORB_hIlluminationPeriods to statement_generic_hORB_hOrbitPeriod;
    dependency from statement_generic_hORB_hOrbitPeriodClosure to statement_generic_hORB_hIlluminationPeriods;
    dependency from statement_generic_hEPS_hLoadEnergy to statement_generic_hORB_hIlluminationPeriods;
    dependency from statement_generic_hEPS_hMinimumPanelPower to statement_generic_hEPS_hLoadEnergy;
    dependency from statement_generic_hEPS_hMinimumPanelPower to statement_generic_hORB_hIlluminationPeriods;
    dependency from statement_generic_hEPS_hSolarCellCount to statement_generic_hEPS_hMinimumPanelPower;
    dependency from statement_generic_hEPS_hSolarCellCount to statement_generic_hEPS_hSolarCellPower;
    dependency from statement_generic_hEPS_hMissionCycles to statement_generic_hORB_hOrbitPeriod;
    dependency from statement_generic_hEPS_hCycleLife to statement_generic_hEPS_hMissionCycles;
    dependency from statement_generic_hEPS_hMinimumBatteryEnergy to statement_generic_hEPS_hLoadEnergy;
    dependency from statement_generic_hEPS_hMinimumBatteryEnergy to statement_generic_hEPS_hCycleLife;
    dependency from statement_generic_hEPS_hMinimumBatteryEnergy to statement_generic_hEPS_hMissionCycles;
    dependency from statement_generic_hEPS_hBatteryCapacityScreen to statement_generic_hEPS_hMinimumBatteryEnergy;
    dependency from statement_generic_hEPS_hEPS02 to statement_generic_hORB_hIlluminationPeriods;
    dependency from statement_generic_hEPS_hEPS02 to statement_generic_hEPS_hMinimumPanelPower;
    dependency from statement_generic_hEPS_hEPS08 to statement_generic_hEPS_hBatteryCapacityScreen;
    dependency from statement_generic_hEPS_hEPS08 to statement_generic_hEPS_hMinimumBatteryEnergy;
    dependency from statement_generic_hEPS_hEPS09 to statement_generic_hEPS_hMissionCycles;
    dependency from statement_generic_hEPS_hEPS09 to statement_generic_hEPS_hCycleLife;
    dependency from statement_generic_hEPS_hEnergyPathEfficiencyBounds to statement_generic_hEPS_hMinimumPanelPower;
    dependency from statement_generic_hEPS_hCycleFitDomain to statement_generic_hEPS_hCycleLife;
    dependency from statement_generic_hEPS_hCycleLimitedDoD to statement_generic_hEPS_hCycleLife;
    dependency from statement_generic_hEPS_hBatteryRetainedEnergy to statement_generic_hEPS_hBatteryCapacityScreen;
    dependency from statement_generic_hEPS_hEPS47 to statement_generic_hEPS_hEPS09;
    dependency from statement_generic_hEPS_hEPS52 to statement_generic_hEPS_hEPS11;
    dependency from statement_generic_hEPS_hEPS53 to statement_generic_hEPS_hEPS11;
    dependency from statement_generic_hEPS_hEPS78 to statement_generic_hEPS_hEPS19;
    dependency from statement_generic_hEPS_hEPS88 to statement_generic_hEPS_hEPS21;
    dependency from statement_generic_hEPS_hEPS89 to statement_generic_hEPS_hEPS21;
}
// </requirements-ui>
