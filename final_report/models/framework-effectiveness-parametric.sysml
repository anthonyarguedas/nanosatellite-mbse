// Literature-grounded MOEs and comparison model for feasible framework alternatives.
package FrameworkEffectivenessParametrics {
    private import ScalarValues::Real;
    private import ISQ::DurationValue;
    private import ParametersOfInterestMetadata::moe;

    attribute def Percent :> Real {
        doc
        /* A percentage in the closed interval from 0 to 100. */

        assert constraint { that >= 0.0 and that <= 100.0 }
    }

    attribute def Hours :> DurationValue {
        doc
        /* An elapsed duration reported in hours when an evaluation value is supplied. */
    }

    attribute def PersonHours :> Real {
        doc
        /* Human effort reported in person-hours for a declared evaluation activity. */

        assert constraint { that >= 0.0 }
    }

    attribute def CAD :> Real {
        doc
        /* Direct cost reported in Canadian dollars for a declared evaluation period. */

        assert constraint { that >= 0.0 }
    }

    attribute def Utility :> Real {
        doc
        /* A dimensionless normalized MOE utility in the closed interval from 0 to 1. */

        assert constraint { that >= 0.0 and that <= 1.0 }
    }

    attribute def Weight :> Utility {
        doc
        /* A nonnegative literature-salience weight. All objective weights sum to one. */
    }

    constraint def 'Change Turnaround Utility Mapping' {
        in moe : Hours;
        out utility : Utility;
        doc
        /* The mapping is fixed before alternatives are scored. Its anchors and shape are calibrated
         * from the common as-is baseline and declared bounds during system requirements analysis. */
    }

    constraint def 'Case Adaptation Utility Mapping' {
        in moe : PersonHours;
        out utility : Utility;
        doc
        /* The mapping is fixed before alternatives are scored. */
    }

    constraint def 'Independent Reproduction Utility Mapping' {
        in moe : PersonHours;
        out utility : Utility;
        doc
        /* The mapping is fixed before alternatives are scored. */
    }

    constraint def 'Framework Adoption Utility Mapping' {
        in moe : PersonHours;
        out utility : Utility;
        doc
        /* The mapping is fixed before alternatives are scored. */
    }

    constraint def 'Direct Cost Utility Mapping' {
        in moe : CAD;
        out utility : Utility;
        doc
        /* The mapping is fixed before alternatives are scored. */
    }

    constraint def 'Consistency Assurance Utility Mapping' {
        in moe : Percent;
        out utility : Utility;
        doc
        /* The mapping is fixed before alternatives are scored. */
    }

    constraint def 'Framework Comparison Equation' {
        in 'change turnaround utility' : Utility;
        in 'case adaptation utility' : Utility;
        in 'independent reproduction utility' : Utility;
        in 'framework adoption utility' : Utility;
        in 'direct cost utility' : Utility;
        in 'consistency assurance utility' : Utility;

        in 'change turnaround weight' : Weight;
        in 'case adaptation weight' : Weight;
        in 'independent reproduction weight' : Weight;
        in 'framework adoption weight' : Weight;
        in 'direct cost weight' : Weight;
        in 'consistency assurance weight' : Weight;

        out 'framework comparison score' : Utility;

        constraint {
            'change turnaround weight' + 'case adaptation weight' +
                'independent reproduction weight' + 'framework adoption weight' +
                'direct cost weight' + 'consistency assurance weight' == 1.0
        }
        constraint {
            'framework comparison score' ==
                'change turnaround weight' * 'change turnaround utility' +
                'case adaptation weight' * 'case adaptation utility' +
                'independent reproduction weight' * 'independent reproduction utility' +
                'framework adoption weight' * 'framework adoption utility' +
                'direct cost weight' * 'direct cost utility' +
                'consistency assurance weight' * 'consistency assurance utility'
        }
    }

    part def 'Academic Nanosatellite EPS Development Enterprise' {
        #moe attribute 'correct change turnaround time' : Hours {
            doc /* Elapsed time for a correct controlled-change response. Lower values are preferred. */
        }
        #moe attribute 'case adaptation effort' : PersonHours {
            doc /* Human effort to apply the common framework core to another EPS case. Lower values are preferred. */
        }
        #moe attribute 'independent reproduction effort' : PersonHours {
            doc /* Human effort for an independent analysis reproduction. Lower values are preferred. */
        }
        #moe attribute 'framework adoption effort' : PersonHours {
            doc /* Human effort to establish the minimum environment and reference workflow. Lower values are preferred. */
        }
        #moe attribute 'direct framework cost' : CAD {
            doc /* Direct framework cost over a declared evaluation period. Lower values are preferred. */
        }
        #moe attribute 'consistency assurance effectiveness' : Percent {
            doc /* Effectiveness at exposing discrepancies while limiting false findings. Higher values are preferred. */
        }
    }

    analysis 'Framework Effectiveness Analysis' {
        attribute 'framework comparison score' : Utility;
        part enterprise : 'Academic Nanosatellite EPS Development Enterprise';

        attribute 'change turnaround utility' : Utility;
        attribute 'case adaptation utility' : Utility;
        attribute 'independent reproduction utility' : Utility;
        attribute 'framework adoption utility' : Utility;
        attribute 'direct cost utility' : Utility;
        attribute 'consistency assurance utility' : Utility;

        attribute 'change turnaround weight' : Weight;
        attribute 'case adaptation weight' : Weight;
        attribute 'independent reproduction weight' : Weight;
        attribute 'framework adoption weight' : Weight;
        attribute 'direct cost weight' : Weight;
        attribute 'consistency assurance weight' : Weight;

        // Normalized topic shares from Akundi and Mondragon (2022), Table 4.
        constraint { 'change turnaround weight' == 0.1812 }
        constraint { 'case adaptation weight' == 0.1190 }
        constraint { 'independent reproduction weight' == 0.2509 }
        constraint { 'framework adoption weight' == 0.1190 }
        constraint { 'direct cost weight' == 0.1908 }
        constraint { 'consistency assurance weight' == 0.1391 }

        constraint 'change turnaround mapping' : 'Change Turnaround Utility Mapping' {
            in moe = enterprise.'correct change turnaround time';
            out utility = 'change turnaround utility';
        }
        constraint 'case adaptation mapping' : 'Case Adaptation Utility Mapping' {
            in moe = enterprise.'case adaptation effort';
            out utility = 'case adaptation utility';
        }
        constraint 'independent reproduction mapping' : 'Independent Reproduction Utility Mapping' {
            in moe = enterprise.'independent reproduction effort';
            out utility = 'independent reproduction utility';
        }
        constraint 'framework adoption mapping' : 'Framework Adoption Utility Mapping' {
            in moe = enterprise.'framework adoption effort';
            out utility = 'framework adoption utility';
        }
        constraint 'direct cost mapping' : 'Direct Cost Utility Mapping' {
            in moe = enterprise.'direct framework cost';
            out utility = 'direct cost utility';
        }
        constraint 'consistency assurance mapping' : 'Consistency Assurance Utility Mapping' {
            in moe = enterprise.'consistency assurance effectiveness';
            out utility = 'consistency assurance utility';
        }

        constraint 'comparison eq' : 'Framework Comparison Equation' {
            in 'change turnaround utility' = 'change turnaround utility';
            in 'case adaptation utility' = 'case adaptation utility';
            in 'independent reproduction utility' = 'independent reproduction utility';
            in 'framework adoption utility' = 'framework adoption utility';
            in 'direct cost utility' = 'direct cost utility';
            in 'consistency assurance utility' = 'consistency assurance utility';

            in 'change turnaround weight' = 'change turnaround weight';
            in 'case adaptation weight' = 'case adaptation weight';
            in 'independent reproduction weight' = 'independent reproduction weight';
            in 'framework adoption weight' = 'framework adoption weight';
            in 'direct cost weight' = 'direct cost weight';
            in 'consistency assurance weight' = 'consistency assurance weight';

            out 'framework comparison score' = 'framework comparison score';
        }
    }
}
