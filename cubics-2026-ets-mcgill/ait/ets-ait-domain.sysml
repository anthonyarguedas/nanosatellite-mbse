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

    part def 'ÉTS AIT Institutional Domain' {
        part cssr : 'CSSR Space Research Center';
        part lacime : 'LaCIME';
        part ltcc : 'LTCC at ÉTS Laboratory';
    }
}
