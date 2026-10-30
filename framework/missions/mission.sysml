// <requirements-ui>
// Mission data managed by requirements-ui. Generic definitions are imported.
// The JSON preserves UI data. The SysML elements below are generated from it.
/* requirements-ui:data
{
  "version": 4,
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
      "id": "PCM",
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
      "key": "4ed97983-d1df-4d47-a607-74b3d37d599c",
      "id": "REQ001",
      "context": "external",
      "sources": [],
      "affected": [],
      "kind": "Requirement",
      "text": "",
      "condition": "",
      "parameters": {
        "x": null,
        "y": null,
        "z": null,
        "a": null
      }
    },
    {
      "key": "4903141e-d1b3-429e-9e99-da4c5b7f634f",
      "id": "PAY001",
      "context": "domain-payload",
      "sources": [],
      "affected": [],
      "kind": "Requirement",
      "text": "",
      "condition": "",
      "parameters": {
        "x": null,
        "y": null,
        "z": null,
        "a": null
      }
    }
  ]
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
            attribute externalId : String = "PCM";
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
    requirement statement_4ed97983_hd1df_h4d47_ha607_h74b3d37d599c {
        attribute externalId : String = "REQ001";
        attribute tableName : String = "External";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "";
        attribute verificationExpression : String[0..1];
        attribute 'x' : Real[0..1];
        attribute 'y' : Real[0..1];
        attribute 'z' : Real[0..1];
        attribute 'a' : Real[0..1];
    }
    requirement statement_4903141e_hd1b3_h429e_h9e99_hda4c5b7f634f {
        attribute externalId : String = "PAY001";
        attribute tableName : String = "Payload";
        attribute statementKind : String = "Requirement";
        attribute statementText : String = "";
        attribute verificationExpression : String[0..1];
        attribute 'x' : Real[0..1];
        attribute 'y' : Real[0..1];
        attribute 'z' : Real[0..1];
        attribute 'a' : Real[0..1];
    }
}
// </requirements-ui>
