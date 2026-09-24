// Proposal concept, not an institutional commitment or a claim of facility access.
// The institution and its single PI retain mission and regulatory accountability.
// See README.md for evidence, decision gates, and the meaning of every open concern.
package ETSMcGillCUBICS2026 {
    metadata def SystemOfInterest;

    // External participants are referred to, not owned by the project.
    part def 'Canadian Space Agency';
    part def 'ISED Spectrum Authority';
    part def 'ÉTS Faculty PI';
    part def 'McGill Faculty Co-I';
    part def 'ÉTS CSSR Payload Research Lead';
    part def 'McGill Ground Site Sponsor';
    part def 'ÉTS CSSR Facility Coordinator';
    part def 'ÉTS Spectrum Licensing Lead';
    part def 'ÉTS Orbital Safety Lead';

    // Contact usages are singular. These are roles to fill, not appointed people.
    part def 'PI Appointment' {
        ref part pointOfContact : 'ÉTS Faculty PI' [1];
    }
    part def 'Co-I Appointment' {
        ref part pointOfContact : 'McGill Faculty Co-I' [1];
    }
    part def 'Payload and Priority Selection' {
        ref part pointOfContact : 'ÉTS CSSR Payload Research Lead' [1];
    }
    part def 'Ground Site Access' {
        ref part pointOfContact : 'McGill Ground Site Sponsor' [1];
    }
    part def 'Lab and AIT Access' {
        ref part pointOfContact : 'ÉTS CSSR Facility Coordinator' [1];
    }
    part def 'Spectrum Authorization' {
        ref part pointOfContact : 'ÉTS Spectrum Licensing Lead' [1];
    }
    part def 'Orbital Debris and Disposal' {
        ref part pointOfContact : 'ÉTS Orbital Safety Lead' [1];
    }
    part def 'Open Proposal Decisions' {
        part piAppointment : 'PI Appointment';
        part coIAppointment : 'Co-I Appointment';
        part payloadChoice : 'Payload and Priority Selection';
        part groundAccess : 'Ground Site Access';
        part labAccess : 'Lab and AIT Access';
        part radioLicensing : 'Spectrum Authorization';
        part debrisPlan : 'Orbital Debris and Disposal';
    }

    part def 'RockÉTS Student Team';
    part def 'CSSR Research Group';
    part def 'Orbital CubeSat Division' {
        part structures : 'OCS1 Structures and Mechanisms';
        part computer : 'OCS2 Command and Data Handling';
        part radio : 'OCS3 Space Ground Communications';
        part attitude : 'OCS4 Attitude Control';
        part power : 'OCS5 Power';
        part balloonTests : 'OCS6 High Altitude Balloon';
    }
    part def 'OCS1 Structures and Mechanisms';
    part def 'OCS2 Command and Data Handling';
    part def 'OCS3 Space Ground Communications';
    part def 'OCS4 Attitude Control';
    part def 'OCS5 Power';
    part def 'OCS6 High Altitude Balloon';
    part def 'ÉTS Applicant' {
        part studentTeam : 'RockÉTS Student Team';
        part researchGroup : 'CSSR Research Group';
    }
    part def 'McGill Collaborator' {
        part studentTeam : 'Orbital CubeSat Division';
    }

    // Functional scope adapted from csrm-diagrams. A payload is still to be selected.
    part def 'Science or Technology Payload';
    part def 'Structure and Thermal';
    part def 'Command and Data Handling';
    part def 'Communications';
    part def 'Attitude Determination and Control';
    part def 'Electrical Power';
    part def 'Propulsion Option';
    part def 'CubeSat Bus' {
        part structure : 'Structure and Thermal';
        part computer : 'Command and Data Handling';
        part radio : 'Communications';
        part attitude : 'Attitude Determination and Control';
        part power : 'Electrical Power';
        // Trade only: the launch orbit and ISED licence may require propulsion.
        part propulsion : 'Propulsion Option' [0..1];
    }
    part def 'Space Segment' {
        part spacecraft : 'CubeSat Bus';
        part payload : 'Science or Technology Payload';
    }
    part def 'Planned Ground Station';
    part def 'Mission Operations and Data' {
        part scheduleAndCommand : 'Ground Command and Scheduling';
        part telemetry : 'Telemetry and Data Processing';
    }
    part def 'Ground Command and Scheduling';
    part def 'Telemetry and Data Processing';
    part def 'Ground Segment' {
        // Planned work; this usage does not mean an operational, permitted site exists.
        part station : 'Planned Ground Station';
        part operations : 'Mission Operations and Data';
    }
    part def 'Student HQP Training';

    part def 'Stream 2 CubeSat Project' {
        @SystemOfInterest;
        part space : 'Space Segment';
        part ground : 'Ground Segment';
        part training : 'Student HQP Training';
        part openDecisions : 'Open Proposal Decisions';
        ref part applicant : 'ÉTS Applicant';
        ref part collaborator : 'McGill Collaborator';
    }
    part def 'Proposed Domain' {
        // The project references the applicant and collaborator as external parties.
        // Keeping one role usage for each avoids duplicating their teams in a native view.
        part project : 'Stream 2 CubeSat Project';
        ref part sponsor : 'Canadian Space Agency';
        ref part radioAuthority : 'ISED Spectrum Authority';
    }
}
