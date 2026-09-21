// SysML v2 semantic counterpart of figures/framework-effectiveness-parametric.tex.
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
        /* A duration reported in hours when an evaluation value is supplied. */
    }

    constraint def 'Framework Effectiveness Equation' {
        in 'framework effectiveness' : Real;
        in 'traceability coverage' : Percent;
        in 'analysis reproducibility' : Percent;
        in 'evidence consistency' : Percent;
        in 'cross-case portability' : Percent;
        in 'change response time' : Hours;

        doc
        /*
         * Framework effectiveness is the weighted sum of the five MOE utilities.
         * Each utility maps its corresponding MOE to the interval from 0 to 1.
         * The utility mappings and weights are decision parameters selected before
         * candidate architectures are scored. This top-level constraint records the
         * objective and its bindings. It does not set mappings, weights, targets, or
         * a score.
         */
    }

    part def 'Academic Nanosatellite EPS Development Enterprise' {
        #moe attribute 'traceability coverage' : Percent;
        #moe attribute 'analysis reproducibility' : Percent;
        #moe attribute 'evidence consistency' : Percent;
        #moe attribute 'cross-case portability' : Percent;
        #moe attribute 'change response time' : Hours;
    }

    part 'Framework Effectiveness Analysis' {
        attribute 'framework effectiveness' : Real;
        part enterprise : 'Academic Nanosatellite EPS Development Enterprise';

        constraint 'effectiveness eq' : 'Framework Effectiveness Equation' {
            in 'framework effectiveness' = 'framework effectiveness';
            in 'traceability coverage' = enterprise.'traceability coverage';
            in 'analysis reproducibility' = enterprise.'analysis reproducibility';
            in 'evidence consistency' = enterprise.'evidence consistency';
            in 'cross-case portability' = enterprise.'cross-case portability';
            in 'change response time' = enterprise.'change response time';
        }
    }
}
