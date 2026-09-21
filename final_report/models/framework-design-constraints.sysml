// Project-imposed design constraints retained after constraint validation.
package FrameworkDesignConstraints {
    private import ModelingMetadata::refinement;
    private import ToBeOperationalDomain::'Nanosatellite EPS Engineering Framework';

    metadata def projectImposedDesignConstraint;

    requirement <'DC-00'> 'Project-Imposed Framework Design Constraints' {
        subject framework : 'Nanosatellite EPS Engineering Framework';
        doc
        /* The implemented framework conforms to the technology and configuration-control choices
         * imposed by the project technical baseline. DC-01 and DC-02 are design constraints rather
         * than stakeholder-derived performance requirements.
         */

        require constraint statement {
            doc
            /* The implementation satisfies every retained project-imposed design constraint. */
        }
    }

    #projectImposedDesignConstraint requirement <'DC-01'> 'Authoritative SysML v2 Model' {
        subject framework : 'Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall maintain its authoritative system model as conformant textual SysML v2
         * source. Verification is by inspection of the designated authoritative source and successful
         * parsing and semantic validation by a conformant SysML v2 implementation.
         * Source: project technical baseline recorded in Manage System Development.
         */

        require constraint statement {
            doc
            /* The authoritative system model is conformant textual SysML v2 source. */
        }
    }

    #projectImposedDesignConstraint requirement <'DC-02'> 'Version-Controlled Textual Baseline' {
        subject framework : 'Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall maintain the authoritative SysML v2 model and report source as text
         * files in one version-controlled project repository, and each evaluation baseline shall be
         * identified by an immutable repository revision. Verification is by repository inspection
         * and demonstration that a recorded revision reconstructs the designated model and report.
         * Source: project technical baseline. Supporting rationale: buruso2026modelbased Secs. 4.4
         * and 5.1; rostamnia2026digitaltwin Secs. 8.4-8.6 and Table 13.
         */

        require constraint statement {
            doc
            /* The authoritative model and report are controlled as text in one repository, and every
             * evaluation baseline resolves to an immutable repository revision.
             */
        }
    }

    #refinement dependency
        'Authoritative SysML v2 Model'
        to 'Project-Imposed Framework Design Constraints';
    #refinement dependency
        'Version-Controlled Textual Baseline'
        to 'Project-Imposed Framework Design Constraints';
} // package FrameworkDesignConstraints
