// Mission-level acceptance requirements established during Analyze Stakeholder Needs.
package FrameworkMissionRequirements {
    private import ScalarValues::Boolean;
    private import FrameworkEffectivenessParametrics::'Academic Nanosatellite EPS Development Enterprise';
    private import ToBeOperationalDomain::earlyEPSDesignJustification;
    private import ModelingMetadata::refinement;

    requirement <'G-00'> 'Candidate Framework Eligibility' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        doc
        /* A candidate framework physical architecture enters comparison ranking only after it
         * satisfies G-01 through G-04 and every mandatory system requirement. This eligibility
         * conjunction is the evaluation rule adopted by this study. */

        require constraint statement {
            doc
            /* Only a feasible candidate enters comparison ranking. */
        }
    }

    requirement <'G-01'> 'Complete and Valid Evidence Chains' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        doc
        /* Every EPS design decision designated for framework evaluation has a complete and valid
         * evidence chain from its source need or requirement through the applicable design elements,
         * assumptions and input configuration, analysis result, and verification criterion.
         * Evidence basis: buruso2026modelbased Sec. 5.1 and Table 5;
         * vizitiu2025optimizing Sec. 4.7 and Table 3; rostamnia2026digitaltwin Table 13. */

        require constraint statement {
            doc
            /* Every designated decision has a complete and valid evidence chain. */
        }
    }

    requirement <'G-02'> 'Reproduce Reference Analyses' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        doc
        /* Every reference analysis designated for framework evaluation can be executed from its
         * controlled baseline and reproduces its reported result within the declared tolerance.
         * Evidence basis: rostamnia2026digitaltwin Secs. 8.4-8.6;
         * rojasramirez2022comparative Sec. 6.2. */

        require constraint statement {
            doc
            /* Every designated reference analysis reproduces within its declared tolerance. */
        }
    }

    requirement <'G-03'> 'Resolve Critical Evidence Inconsistencies' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        doc
        /* A framework evaluation baseline has no unresolved discrepancy classified as critical among
         * its requirements, model properties, interfaces, budgets, assumptions, and analysis inputs.
         * Evidence basis: vizitiu2025optimizing Sec. 4.7 and Table 3;
         * buruso2026modelbased Sec. 5.1 and Table 5; rostamnia2026digitaltwin Table 13. */

        require constraint statement {
            doc
            /* No critical evidence inconsistency remains unresolved. */
        }
    }

    requirement <'G-04'> 'Complete Contrasting Evaluation Cases' {
        subject enterprise : 'Academic Nanosatellite EPS Development Enterprise';
        doc
        /* The framework completes both selected contrasting EPS evaluation cases with the common core
         * information model and workflow, while identifying every approved case-specific parameter,
         * extension, and mapping. Evidence basis: buruso2026modelbased Sec. 5.1 and Table 5;
         * vizitiu2025optimizing Sec. 4.7 and Table 3; rostamnia2026digitaltwin Sec. 8.4. */

        require constraint statement {
            doc
            /* Both contrasting evaluation cases complete with all case-specific adaptations declared. */
        }
    }

    #refinement dependency 'Candidate Framework Eligibility' to earlyEPSDesignJustification;
    #refinement dependency 'Complete and Valid Evidence Chains' to 'Candidate Framework Eligibility';
    #refinement dependency 'Reproduce Reference Analyses' to 'Candidate Framework Eligibility';
    #refinement dependency 'Resolve Critical Evidence Inconsistencies' to 'Candidate Framework Eligibility';
    #refinement dependency 'Complete Contrasting Evaluation Cases' to 'Candidate Framework Eligibility';

    constraint def 'Candidate Eligibility Rule' {
        in 'G-01 satisfied' : Boolean;
        in 'G-02 satisfied' : Boolean;
        in 'G-03 satisfied' : Boolean;
        in 'G-04 satisfied' : Boolean;
        in 'mandatory system requirements satisfied' : Boolean;
        out eligible : Boolean;

        constraint {
            eligible == ('G-01 satisfied' and 'G-02 satisfied' and 'G-03 satisfied' and
                'G-04 satisfied' and 'mandatory system requirements satisfied')
        }
    }

    analysis 'Framework Candidate Eligibility' {
        attribute 'G-01 satisfied' : Boolean;
        attribute 'G-02 satisfied' : Boolean;
        attribute 'G-03 satisfied' : Boolean;
        attribute 'G-04 satisfied' : Boolean;
        attribute 'mandatory system requirements satisfied' : Boolean;
        attribute eligible : Boolean;

        constraint eligibility : 'Candidate Eligibility Rule' {
            in 'G-01 satisfied' = 'G-01 satisfied';
            in 'G-02 satisfied' = 'G-02 satisfied';
            in 'G-03 satisfied' = 'G-03 satisfied';
            in 'G-04 satisfied' = 'G-04 satisfied';
            in 'mandatory system requirements satisfied' = 'mandatory system requirements satisfied';
            out eligible = eligible;
        }
    }
}
