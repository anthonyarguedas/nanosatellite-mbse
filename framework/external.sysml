package External {
    package RegulatoryAgencyStakeholders {
        part def RegulatoryAgencyStakeholder;
        package RegulatoryAgencyStakeholderConcerns {}
    }
    package LaunchProviders {
        part def LaunchProvider;
        package LaunchProviderConcerns {}
        package LaunchProviderRequirements {}
    }
    package Partners {
        part def Partner;
        package PartnerConcerns {}
        package PartnerRequirements {}
    }
    package MissionStakeholders {
        part def MissionStakeholder;

        package MissionStakeholderConcerns {}
        package MissionNeeds {}
        package MissionObjectives {}
        package MissionConstraints {}
        package MissionRequirements {}
    }
    package CubeSatDeployerSystems {
        part def CubeSatDeployer;
        package CubeSatDeployerInterfaceRequirements {
            package Environmental {}
            package Materials {}
            package Mechanical {}
            package Safety {}
            package Electrical {}
            package Deployment {}
        }
    }
    package ExternalGroundStationServices {
        part def ExternalGroundStationService;
        package ExternalGroundStationServicesRequirements {}
    }
}
package TechnicalMeasures {
    package MeasuresOfEffectiveness {}
    package MeasuresOfPerformance {}
    package TechnicalPerformanceMeasure {}
    package KeyPerformanceParameter {}
}
package Facilities {
    part def DesignFacility;
    part def ProductionFacility;
    part def CleanRoom;
    part def IntegrationFacility;
    part def TestFacility;
    part def ThermalVacuumChamber;
    part def HelmholtzCage;
}
