// Publicly documented institutional snapshot. Sources and caveats: README.md.
// Positions are published roles. Potential concerns and contacts are suggestions,
// not CUBICS assignments. Concern strings list topics, not confirmed commitments.
package ETSAITDomain {
    part def 'René Jr Landry' {
        attribute position : ScalarValues::String = "Professor and LASSENA director";
        attribute potentialConcerns : ScalarValues::String = "navigation receivers, space electronics";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Jean-Marc Gagné' {
        attribute position : ScalarValues::String = "LASSENA project manager";
        attribute potentialConcerns : ScalarValues::String = "project coordination, AIT scheduling";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Ahmad Esmailkhah' {
        attribute position : ScalarValues::String = "Postdoctoral fellow";
        attribute potentialConcerns : ScalarValues::String = "telecommunications integration, RF tests";
    }
    part def 'Ricardo Izquierdo' {
        attribute position : ScalarValues::String = "LaCIME director";
        attribute potentialConcerns : ScalarValues::String = "lab coordination, microelectronics";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Mathieu Gratuze' {
        attribute position : ScalarValues::String = "Research associate";
        attribute potentialConcerns : ScalarValues::String = "equipment access, component tests";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Mohsen Ketabi' {
        attribute position : ScalarValues::String = "Research assistant";
        attribute potentialConcerns : ScalarValues::String = "LaCIME research, component tests";
    }
    part def 'Ammar B. Kouki' {
        attribute position : ScalarValues::String = "LTCC laboratory director";
        attribute potentialConcerns : ScalarValues::String = "LTCC circuits, RF components";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Normand Gravel' {
        attribute position : ScalarValues::String = "LTCC MEMS laboratory manager";
        attribute potentialConcerns : ScalarValues::String = "LTCC fabrication, process equipment";
        attribute potentialContact : ScalarValues::Boolean = true;
    }

    // ÉTS identifies Professor Gonzalez Llorente with aerospace engineering,
    // CubeSat electrical power research, onboard AI, and space qualification.
    part def 'Jesus David Gonzalez Llorente' {
        attribute position : ScalarValues::String = "Professor, Department of Aerospace Engineering";
        attribute potentialConcerns : ScalarValues::String = "CubeSat power systems, onboard AI, space component tests";
        attribute potentialContact : ScalarValues::Boolean = true;
    }

    // RockÉTS publishes these names and positions on its board roster.
    part def 'Mélanie Fressard' {
        attribute position : ScalarValues::String = "Capitaine";
        attribute potentialConcerns : ScalarValues::String = "club coordination, student continuity";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Maëlle Marinier' {
        attribute position : ScalarValues::String = "Directrice du département de payload";
        attribute potentialConcerns : ScalarValues::String = "payload prototypes, instrument tests";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Audrey Provencher' {
        attribute position : ScalarValues::String = "Directrice du département des communications et de la logistique";
        attribute potentialConcerns : ScalarValues::String = "test logistics, club communications";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Olivier Nolin' {
        attribute position : ScalarValues::String = "Directeur du département propulsion";
        attribute potentialConcerns : ScalarValues::String = "propulsion prototypes, safety tests";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Samuel Laplante' {
        attribute position : ScalarValues::String = "Directeur du département d'avionique";
        attribute potentialConcerns : ScalarValues::String = "avionics boards, telemetry tests";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Paul Arnautovich' {
        attribute position : ScalarValues::String = "Directeur du département d'aérostructure";
        attribute potentialConcerns : ScalarValues::String = "structure fabrication, fit checks";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Raphaël Tremblay' {
        attribute position : ScalarValues::String = "Trésorier";
        attribute potentialConcerns : ScalarValues::String = "club procurement, cost tracking";
        attribute potentialContact : ScalarValues::Boolean = true;
    }

    // CSSR's public team page gives these LASSENA titles under "Our Team".
    part def 'CSSR Space Research Center' {
        ref part 'LASSENA director' : 'René Jr Landry';
        ref part 'LASSENA project manager' : 'Jean-Marc Gagné';
        ref part 'postdoctoral fellow' : 'Ahmad Esmailkhah';
        part reportedEquipment : 'CSSR Reported Equipment';
    }
    part def 'CSSR Reported Equipment' {
        part vacuumChambers : 'Vacuum Chambers';
        part spaceSimulators : 'Space Environment Simulators';
        part radiationDevices : 'Radiation Test Devices';
    }
    part def 'Vacuum Chambers';
    part def 'Space Environment Simulators';
    part def 'Radiation Test Devices';

    // LaCIME's contact page and equipment list identify these staff and tools.
    part def 'LaCIME' {
        ref part director : 'Ricardo Izquierdo';
        ref part 'research associate' : 'Mathieu Gratuze';
        ref part 'research assistant' : 'Mohsen Ketabi';
        part listedEquipment : 'LaCIME Listed Equipment';
    }
    part def 'LaCIME Listed Equipment' {
        part networkAnalyzers : 'Vector Network Analyzers';
        part shaker : 'Pot Vibrant Shaker';
        part environment : 'TPS T10RC Environmental Chamber';
        part vacuum : 'Vacuum Test Chamber';
    }
    part def 'Vector Network Analyzers';
    part def 'Pot Vibrant Shaker';
    part def 'TPS T10RC Environmental Chamber';
    part def 'Vacuum Test Chamber';

    // The LTCC@ÉTS site names its director, manager, and fabrication equipment.
    // It appears separately because the public pages do not state a legal reporting line.
    part def 'LTCC at ÉTS Laboratory' {
        ref part director : 'Ammar B. Kouki';
        ref part manager : 'Normand Gravel';
        part listedEquipment : 'LTCC Listed Equipment';
    }
    part def 'LTCC Listed Equipment' {
        part printer : 'P200S LTCC Printer';
        part laser : 'Protolaser U3';
        part furnace : 'PEO603 Firing Furnace';
        part maskAligner : '800MBA MEMS Mask Aligner';
    }
    part def 'P200S LTCC Printer';
    part def 'Protolaser U3';
    part def 'PEO603 Firing Furnace';
    part def '800MBA MEMS Mask Aligner';

    // RockÉTS board departments and its documented rocket avionics system.
    // Anirniq is rocket hardware. This model makes no satellite flight claim.
    part def 'RockÉTS Club' {
        ref part captain : 'Mélanie Fressard';
        ref part treasurer : 'Raphaël Tremblay';
        part payload : 'RockÉTS Payload Department';
        part avionics : 'RockÉTS Avionics Department';
        part aerostructure : 'RockÉTS Aerostructure Department';
        part propulsion : 'RockÉTS Propulsion Department';
        part communications : 'RockÉTS Communications and Logistics';
    }
    part def 'RockÉTS Payload Department' {
        ref part director : 'Maëlle Marinier';
    }
    part def 'RockÉTS Avionics Department' {
        ref part director : 'Samuel Laplante';
        part anirniq : 'Anirniq Rocket Avionics';
    }
    part def 'RockÉTS Aerostructure Department' {
        ref part director : 'Paul Arnautovich';
    }
    part def 'RockÉTS Propulsion Department' {
        ref part director : 'Olivier Nolin';
    }
    part def 'RockÉTS Communications and Logistics' {
        ref part director : 'Audrey Provencher';
    }
    part def 'Anirniq Rocket Avionics' {
        part cots : 'Commercial GPS and Altimeter';
        part modularBoards : 'Student Built Avionics Boards';
    }
    part def 'Commercial GPS and Altimeter';
    part def 'Student Built Avionics Boards';

    part def 'ÉTS Aerospace Engineering Faculty' {
        ref part 'small satellite research' : 'Jesus David Gonzalez Llorente';
    }

    part def 'ÉTS AIT Faculty Domain' {
        part cssr : 'CSSR Space Research Center';
        part lacime : 'LaCIME';
        part ltcc : 'LTCC at ÉTS Laboratory';
        part aerospace : 'ÉTS Aerospace Engineering Faculty';
    }
}
