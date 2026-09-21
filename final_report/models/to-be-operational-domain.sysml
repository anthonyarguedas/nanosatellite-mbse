// SysML v2 representation of the intended to-be operational domain.
package ToBeOperationalDomain {
    private import FrameworkEffectivenessParametrics
            ::'Academic Nanosatellite EPS Development Enterprise';

    metadata def systemOfInterest;

    part def 'Academic Mission Team' {
        doc
        /* The team applies the enterprise capability to a nanosatellite EPS study. */

        port frameworkApplication
            : FrameworkBoundaryInterfaces::'Mission Application Port';
    }

    part def 'Academic Researcher' {
        doc
        /* The researcher evaluates, compares, and extends framework methods and analyses. */

        port frameworkResearch
            : FrameworkBoundaryInterfaces::'Research Governance Port';
    }

    part def Reviewer {
        doc
        /* An independent reviewer may inspect a justification or reproduce an analysis. */

        port frameworkReview
            : FrameworkBoundaryInterfaces::'Independent Review Port';
    }

    part def 'Versioned System Model' {
        doc
        /* Controlled models, requirements, architecture, interfaces, assumptions, and configurations. */

        port frameworkControl
            : FrameworkBoundaryInterfaces::'Model Control Port';
    }

    part def 'Analysis Tools' {
        doc
        /* Tools that execute or support EPS analyses. No specific implementation is selected here. */

        port frameworkExecution
            : FrameworkBoundaryInterfaces::'Analysis Execution Port';
    }

    part def 'Evidence Repository' {
        doc
        /* Retained analysis inputs, results, verification evidence, and reviewable evidence packages. */

        port frameworkCustody
            : FrameworkBoundaryInterfaces::'Evidence Custody Port';
    }

    part def 'Nanosatellite EPS Engineering Framework' {
        doc
        /* The system of interest coordinates these enterprise resources. This abstraction does not
         * select a deployment, toolchain, or internal architecture.
         */

        ref part systemModel : 'Versioned System Model';
        ref part analysisTools : 'Analysis Tools';
        ref part evidenceRepository : 'Evidence Repository';

        port missionApplication
            : FrameworkBoundaryInterfaces::'Mission Application Port';
        port researchGovernance
            : FrameworkBoundaryInterfaces::'Research Governance Port';
        port independentReview
            : FrameworkBoundaryInterfaces::'Independent Review Port';
        port modelControl
            : FrameworkBoundaryInterfaces::'Model Control Port';
        port analysisExecution
            : FrameworkBoundaryInterfaces::'Analysis Execution Port';
        port evidenceCustody
            : FrameworkBoundaryInterfaces::'Evidence Custody Port';

        perform action maintainEvidenceChain
            : FrameworkBlackBoxFunctions::'Maintain Evidence Chain';
        perform action configureFrameworkForCase
            : FrameworkBlackBoxFunctions::'Configure Framework for EPS Case';
        perform action reproduceDesignatedAnalysis
            : FrameworkBlackBoxFunctions::'Reproduce Designated Analysis';
        perform action assessControlledDesignChange
            : FrameworkBlackBoxFunctions::'Assess Controlled Design Change';
        perform action compareCandidateArchitectures
            : FrameworkBlackBoxFunctions::'Compare Candidate EPS Architectures';
        perform action supportEarlyDesignReview
            : FrameworkBlackBoxFunctions::'Support Early Design Review';

        exhibit state operationalControl
            : FrameworkOperationalState::'Framework Operational Control';
    }

    concern def 'Early EPS Design Justification' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        stakeholder missionTeam : 'Academic Mission Team';
        stakeholder researcher : 'Academic Researcher';
        stakeholder reviewer : Reviewer;
        doc
        /* Enable the academic nanosatellite community to justify early EPS design decisions by
         * maintaining a traceable, reproducible, consistent, and reusable evidence chain from
         * stakeholder needs and requirements through architecture, assumptions, analyses, and
         * verification results across contrasting mission contexts.
         */
    }

    concern earlyEPSDesignJustification : 'Early EPS Design Justification';

    use case def 'Maintain EPS Evidence Chain' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        objective {
            doc
            /* Maintain linked, versioned evidence from needs and requirements through architecture,
             * assumptions, analyses, and verification results.
             */
        }
    }

    use case def 'Configure Framework for an EPS Case' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        objective {
            doc
            /* Establish the declared environment, common information model, workflow, case parameters,
             * extensions, and mappings needed to apply the framework to a selected EPS context.
             */
        }
    }

    use case def 'Reproduce an Analysis' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        actor reviewer : Reviewer;
        objective {
            doc
            /* Re-execute a designated analysis from its recorded configuration and compare its output
             * against the reported result.
             */
        }
    }

    use case def 'Assess a Design Change' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        objective {
            doc
            /* Identify affected evidence, update the controlled configuration, and regenerate a
             * reviewable evidence package.
             */
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

    part 'To-be Operational Domain' {
        part enterprise : 'Academic Nanosatellite EPS Development Enterprise' {
            part missionTeam : 'Academic Mission Team';
            part researcher : 'Academic Researcher';
            #systemOfInterest part framework : 'Nanosatellite EPS Engineering Framework';
            part systemModel : 'Versioned System Model';
            part analysisTools : 'Analysis Tools';
            part evidenceRepository : 'Evidence Repository';
        }
        part reviewer : Reviewer [0..*];
    }
} // package ToBeOperationalDomain
