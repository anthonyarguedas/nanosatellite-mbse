// Literature-grounded stakeholder concerns, viewpoints, and conforming views.
package StakeholderViewpoints {
    private import StandardViewDefinitions::GeneralView;
    private import FrameworkEffectivenessParametrics
            ::'Academic Nanosatellite EPS Development Enterprise';
    private import ToBeOperationalDomain::'Academic Mission Team';
    private import ToBeOperationalDomain::'Academic Researcher';
    private import ToBeOperationalDomain::Reviewer;

    concern def 'Framework Application Concern' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        stakeholder missionTeam : 'Academic Mission Team';
        doc
        /* Apply the framework within university mission constraints while preserving a usable workflow,
         * declared adaptations, interoperable information, traceability, and acceptable adoption effort
         * and cost. Evidence basis: buruso2026modelbased; vizitiu2025optimizing;
         * rojasramirez2022comparative.
         */
    }

    concern def 'Framework Research Concern' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        stakeholder researcher : 'Academic Researcher';
        doc
        /* Evaluate and improve the framework through explicit methods, assumptions, case adaptations,
         * analyses, uncertainty, raw results, and measured evidence that can be compared and reused
         * across contexts. Evidence basis: buruso2026modelbased; rostamnia2026digitaltwin;
         * rojasramirez2022comparative; akundi2022textmining.
         */
    }

    concern def 'Independent Review Concern' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        stakeholder reviewer : Reviewer;
        doc
        /* Assess claims from controlled baselines using provenance, requirement and evidence traces,
         * declared assumptions, verification criteria and results, discrepancy status, uncertainty,
         * and reproduction instructions. Evidence basis: buruso2026modelbased;
         * rostamnia2026digitaltwin; rojasramirez2022comparative.
         */
    }

    viewpoint def 'Framework Application Viewpoint' {
        doc
        /* Select the operational domain, enterprise use cases, mission requirements, resources,
         * adaptation points, and adoption, effort, cost, and assurance measures needed by a mission
         * team to judge whether and how to apply the framework.
         */
        frame concern applicationConcern : 'Framework Application Concern';
    }

    viewpoint def 'Framework Research Viewpoint' {
        doc
        /* Select the rationale, mission requirements, case configuration and comparison information,
         * measures, analyses, assumptions, uncertainty, and limitations needed to evaluate and extend
         * the framework.
         */
        frame concern researchConcern : 'Framework Research Concern';
    }

    viewpoint def 'Framework Independent Review Viewpoint' {
        doc
        /* Select controlled configuration, traceability, provenance, verification, discrepancy, and
         * reproduction information needed to assess an early design justification independently.
         */
        frame concern independentReviewConcern : 'Independent Review Concern';
    }

    view 'Framework Application View' : GeneralView {
        satisfy requirement applicationViewpoint : 'Framework Application Viewpoint';
        expose ToBeOperationalDomain::'To-be Operational Domain';
        expose FrameworkSystemContext::'Framework System Context';
        expose ToBeOperationalDomain::'Maintain EPS Evidence Chain';
        expose ToBeOperationalDomain::'Configure Framework for an EPS Case';
        expose ToBeOperationalDomain::'Reproduce an Analysis';
        expose ToBeOperationalDomain::'Assess a Design Change';
        expose ToBeOperationalDomain::'Compare Candidate EPS Architectures';
        expose ToBeOperationalDomain::'Review an Early Design Justification';
        expose FrameworkMissionRequirements::'Candidate Framework Eligibility';
        expose FrameworkMissionRequirements::'Complete and Valid Evidence Chains';
        expose FrameworkMissionRequirements::'Reproduce Reference Analyses';
        expose FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies';
        expose FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        expose FrameworkEffectivenessParametrics
                ::'Academic Nanosatellite EPS Development Enterprise';
    }

    view 'Framework Research View' : GeneralView {
        satisfy requirement researchViewpoint : 'Framework Research Viewpoint';
        expose ToBeOperationalDomain::earlyEPSDesignJustification;
        expose FrameworkSystemContext::'Framework System Context';
        expose ToBeOperationalDomain::'Configure Framework for an EPS Case';
        expose ToBeOperationalDomain::'Compare Candidate EPS Architectures';
        expose FrameworkMissionRequirements::*;
        expose FrameworkEffectivenessParametrics::*;
    }

    view 'Framework Independent Review View' : GeneralView {
        satisfy requirement independentReviewViewpoint : 'Framework Independent Review Viewpoint';
        expose ToBeOperationalDomain::'To-be Operational Domain';
        expose FrameworkSystemContext::'Framework System Context';
        expose ToBeOperationalDomain::'Reproduce an Analysis';
        expose ToBeOperationalDomain::'Assess a Design Change';
        expose ToBeOperationalDomain::'Review an Early Design Justification';
        expose FrameworkMissionRequirements::'Complete and Valid Evidence Chains';
        expose FrameworkMissionRequirements::'Reproduce Reference Analyses';
        expose FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies';
        expose FrameworkMissionRequirements::'Framework Candidate Eligibility';
    }
} // package StakeholderViewpoints
