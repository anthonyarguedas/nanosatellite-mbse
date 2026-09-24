// Publicly documented institutional snapshot. Sources and caveats: README.md.
// Positions are published roles. Potential concerns and contacts are suggestions,
// not CUBICS assignments. Concern strings list topics, not confirmed commitments.
package McGillAITDomain {
    part def 'Jamil Ahram' {
        attribute position : ScalarValues::String = "Faculty Workshop manager";
        attribute potentialConcerns : ScalarValues::String = "workshop scheduling, machining";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Meisam Aghajani' {
        attribute position : ScalarValues::String = "Chief shop technician";
        attribute potentialConcerns : ScalarValues::String = "prototype machining, part fit";
    }
    part def 'Sam Minter' {
        attribute position : ScalarValues::String = "Wong Machine Shop coordinator";
        attribute potentialConcerns : ScalarValues::String = "CNC fabrication, fixtures";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Zhao Lu' {
        attribute position : ScalarValues::String = "Nanotools manager";
        attribute potentialConcerns : ScalarValues::String = "cleanroom access, process scheduling";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'John Li' {
        attribute position : ScalarValues::String = "Equipment technologist";
        attribute potentialConcerns : ScalarValues::String = "Nanotools equipment, microfab tests";
        attribute potentialContact : ScalarValues::Boolean = true;
    }
    part def 'Peng Yang' {
        attribute position : ScalarValues::String = "Research assistant";
        attribute potentialConcerns : ScalarValues::String = "microfabrication research support";
    }

    // Faculty of Engineering Workshop site and staff page.
    part def 'Faculty Engineering Workshop' {
        ref part manager : 'Jamil Ahram';
        ref part 'chief shop technician' : 'Meisam Aghajani';
        part wongShop : 'Wong Machine Shop';
        part listedEquipment : 'Workshop Listed Equipment';
    }
    part def 'Wong Machine Shop' {
        ref part coordinator : 'Sam Minter';
    }
    part def 'Workshop Listed Equipment' {
        part cnc : 'CNC Mills and Lathes';
        part cmm : 'Coordinate Measuring Machine';
        part laser : 'Laser Cutter';
    }
    part def 'CNC Mills and Lathes';
    part def 'Coordinate Measuring Machine';
    part def 'Laser Cutter';

    // Nanotools' published staff, address, facility description and capabilities.
    part def 'Nanotools Microfab' {
        ref part manager : 'Zhao Lu';
        ref part 'equipment technologist' : 'John Li';
        ref part 'research assistant' : 'Peng Yang';
        ref part location : 'Rutherford Physics Building B1';
        part listedEquipment : 'Nanotools Listed Equipment';
    }
    part def 'Rutherford Physics Building B1';
    part def 'Nanotools Listed Equipment' {
        part cleanrooms : 'ISO 5 and ISO 6 Cleanrooms';
        part lithography : 'Lithography Tools';
        part deposition : 'Thin Film Deposition Tools';
        part etching : 'Etching Tools';
    }
    part def 'ISO 5 and ISO 6 Cleanrooms';
    part def 'Lithography Tools';
    part def 'Thin Film Deposition Tools';
    part def 'Etching Tools';

    part def 'McGill AIT Institutional Domain' {
        part workshop : 'Faculty Engineering Workshop';
        part nanotools : 'Nanotools Microfab';
    }
}
