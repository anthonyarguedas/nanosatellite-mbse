// SysML v2 representation of the intended to-be operational domain.
package ToBeOperationalDomain {
    private import FrameworkEffectivenessParametrics::'Academic Nanosatellite EPS Development Enterprise';
    private import ModelingMetadata::refinement;

    metadata def systemOfInterest;

    part def 'Academic Mission Team' {
        doc
        /* The team applies the enterprise capability to a nanosatellite EPS study. */
    }

    part def Reviewer {
        doc
        /* An independent reviewer may inspect a justification or reproduce an analysis. */
    }

    part def 'Versioned System Model' {
        doc
        /* Controlled models, requirements, architecture, interfaces, assumptions, and configurations. */
    }

    part def 'Analysis Tools' {
        doc
        /* Tools that execute or support EPS analyses. No specific implementation is selected here. */
    }

    part def 'Evidence Repository' {
        doc
        /* Retained analysis inputs, results, verification evidence, and reviewable evidence packages. */
    }

    part def 'Nanosatellite EPS Engineering Framework' {
        doc
        /* The system of interest coordinates these enterprise resources. This abstraction does not
         * select a deployment, toolchain, or internal architecture. */

        ref part systemModel : 'Versioned System Model';
        ref part analysisTools : 'Analysis Tools';
        ref part evidenceRepository : 'Evidence Repository';
    }

    concern def 'Early EPS Design Justification' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        stakeholder missionTeam : 'Academic Mission Team';
        stakeholder reviewer : Reviewer;
        doc
        /* Enable the academic nanosatellite community to justify early EPS design decisions by
         * maintaining a traceable, reproducible, consistent, and reusable evidence chain from
         * stakeholder needs and requirements through architecture, assumptions, analyses, and
         * verification results across contrasting mission contexts. */
    }

    concern earlyEPSDesignJustification : 'Early EPS Design Justification';

    use case def 'Maintain EPS Evidence Chain' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        objective {
            doc
            /* Maintain linked, versioned evidence from needs and requirements through architecture,
             * assumptions, analyses, and verification results. */
        }
    }

    use case def 'Reproduce an Analysis' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        actor reviewer : Reviewer;
        objective {
            doc
            /* Re-execute a designated analysis from its recorded configuration and compare its output
             * against the reported result. */
        }
    }

    use case def 'Assess a Design Change' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        objective {
            doc
            /* Identify affected evidence, update the controlled configuration, and regenerate a
             * reviewable evidence package. */
        }
    }

    use case def 'Compare Candidate EPS Architectures' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        objective {
            doc
            /* Compare candidate EPS architectures on an explicit common basis. */
        }
    }

    use case def 'Review an Early Design Justification' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        actor reviewer : Reviewer;
        objective {
            doc
            /* Inspect a selected evidence package and record a review outcome. */
        }
    }

    #refinement dependency 'Maintain EPS Evidence Chain' to earlyEPSDesignJustification;
    #refinement dependency 'Reproduce an Analysis' to earlyEPSDesignJustification;
    #refinement dependency 'Assess a Design Change' to earlyEPSDesignJustification;
    #refinement dependency 'Compare Candidate EPS Architectures' to earlyEPSDesignJustification;
    #refinement dependency 'Review an Early Design Justification' to earlyEPSDesignJustification;

    part 'To-be Operational Domain' {
        part enterprise : 'Academic Nanosatellite EPS Development Enterprise' {
            part missionTeam : 'Academic Mission Team';
            #systemOfInterest part framework : 'Nanosatellite EPS Engineering Framework';
            part systemModel : 'Versioned System Model';
            part analysisTools : 'Analysis Tools';
            part evidenceRepository : 'Evidence Repository';
        }
        part reviewer : Reviewer[0..*];
    }
}
