// Critical black-box properties, measures of performance, and common measurement protocol.
package FrameworkCriticalProperties {
    doc
    /* Evidence basis: buruso2026modelbased Sec. 4.4; rostamnia2026digitaltwin
     * Secs. 8.4-8.6 and Table 13; rojasramirez2022comparative Sec. 6.2. The reviews
     * justify the measurement concerns but do not provide numerical targets. The equations,
     * correctness gates, and measurement boundaries are explicit project operationalizations.
     */

    private import ScalarValues::Boolean;
    private import ScalarValues::Integer;
    private import ScalarValues::String;
    private import ParametersOfInterestMetadata::mop;
    private import ModelingMetadata::refinement;
    private import FrameworkEffectivenessParametrics::Percent;
    private import FrameworkEffectivenessParametrics::Hours;
    private import FrameworkEffectivenessParametrics::PersonHours;
    private import FrameworkEffectivenessParametrics::CAD;
    private import FrameworkEffectivenessParametrics
            ::'Academic Nanosatellite EPS Development Enterprise';
    private import FrameworkExchangeDefinitions::'Baseline Reference';
    private import ToBeOperationalDomain::'Nanosatellite EPS Engineering Framework';

    attribute def Count :> Integer {
        doc
        /* A dimensionless count that cannot be negative. */

        assert constraint { that >= 0 }
    }

    item def 'Framework Evaluation Manifest' {
        item baseline : 'Baseline Reference';
        attribute 'candidate architecture identifiers' : String;
        attribute 'candidate comparison model elements' : String;
        attribute 'OOSEM source baseline revision' : String;
        attribute 'designated evidence chains' : String;
        attribute 'designated external artifacts' : String;
        attribute 'designated reference analyses' : String;
        attribute 'declared result tolerances' : String;
        attribute 'criticality rule' : String;
        attribute 'common core identifier' : String;
        attribute 'timing and effort rules' : String;
        attribute 'direct cost boundary' : String;
        attribute 'utility anchors and mapping rules' : String;
        attribute 'consistency test set identifier' : String;
        attribute 'required contrasting case count' : Count;

        assert constraint { 'required contrasting case count' == 2 }

        doc
        /* The manifest is fixed before candidate framework results are observed. It identifies each
         * candidate architecture, its common SysML v2 comparison-model elements under MC-01, the
         * immutable OOSEM source revision under MC-02, the designated evidence chains, external
         * requirement sets, EPS models, analysis results, the controlled evaluation baseline,
         * result-specific tolerances, the discrepancy criticality rule, the common core, the two
         * required cases, all measurement boundaries, and the utility anchors and mapping rules used
         * after Pareto comparison. MC-01 and MC-02 control study artifacts and are not candidate
         * implementation requirements.
         */
    }

    part def 'Measured Nanosatellite EPS Engineering Framework'
        :> 'Nanosatellite EPS Engineering Framework' {
        #mop attribute <'MOP-01'> 'valid trace coverage' : Percent {
            doc
            /* Valid required trace relations divided by all applicable required trace relations for
             * the designated evidence chains. A relation is valid only when both ends resolve to the
             * controlled baseline, each externally produced endpoint has an accepted registration
             * preserving producer, source revision, and provenance, and the relation has the required
             * semantics.
             */
        }
        #mop attribute <'MOP-02'> 'reference analysis reproduction success' : Percent {
            doc
            /* Designated reference analyses that execute from the controlled baseline and reproduce
             * every declared result within its result-specific tolerance, divided by all designated
             * reference analyses.
             */
        }
        #mop attribute <'MOP-03'> 'open critical discrepancy count' : Count {
            doc
            /* Unresolved discrepancies classified as critical by the predeclared criticality rule at
             * the evaluation verdict time.
             */
        }
        #mop attribute <'MOP-04'> 'completed contrasting case count' : Count {
            doc
            /* Contrasting EPS cases that complete the reference workflow using the identified common
             * core and produce all mandatory evidence.
             */
        }
        #mop attribute <'MOP-05'> 'undeclared adaptation count' : Count {
            doc
            /* Case-specific parameters, extensions, or mappings used by a completed case without a
             * corresponding approved declaration.
             */
        }
        #mop attribute <'MOP-06'> 'correct change turnaround time' : Hours {
            doc
            /* Wall-clock time from acceptance of a valid change request against a named baseline to
             * issue of a correct reviewable evidence package. The value is rankable only when the
             * impact set and regenerated evidence pass the predeclared correctness checks.
             */
        }
        #mop attribute <'MOP-07'> 'case adaptation effort' : PersonHours {
            doc
            /* Sum of active human time used to configure one contrasting EPS case until its controlled
             * configuration is accepted. Waiting and unattended execution are excluded.
             */
        }
        #mop attribute <'MOP-08'> 'independent reproduction effort' : PersonHours {
            doc
            /* Sum of active reviewer time from receipt of a complete reproduction package to a valid
             * reproduction verdict. The value is rankable only for a successful reproduction.
             */
        }
        #mop attribute <'MOP-09'> 'framework adoption effort' : PersonHours {
            doc
            /* Sum of active human time needed from a clean declared starting environment to establish
             * the minimum environment and complete the reference workflow correctly.
             */
        }
        #mop attribute <'MOP-10'> 'direct framework cost' : CAD {
            doc
            /* Incremental licenses, required services, and computing charges over the declared
             * evaluation period. Labor and pre-existing general infrastructure are excluded.
             */
        }
        #mop attribute <'MOP-11'> 'consistency assurance effectiveness' : Percent {
            doc
            /* F1 score over a blinded test set containing seeded discrepancies and clean controls.
             * A true positive identifies the seeded discrepancy and its affected artifact. False
             * findings and missed seeded discrepancies reduce the score.
             */
        }
    }

    constraint def 'Trace Coverage Equation' {
        in 'valid required trace count' : Count;
        in 'applicable required trace count' : Count;
        out coverage : Percent;

        constraint { 'applicable required trace count' > 0 }
        constraint {
            coverage == (100.0 * 'valid required trace count') / 'applicable required trace count'
        }
    }

    constraint def 'Reproduction Success Equation' {
        in 'successful designated analysis count' : Count;
        in 'designated analysis count' : Count;
        out success : Percent;

        constraint { 'designated analysis count' > 0 }
        constraint {
            success ==
            (100.0 * 'successful designated analysis count') / 'designated analysis count'
        }
    }

    constraint def 'Consistency Assurance F1 Equation' {
        in 'true positive count' : Count;
        in 'false positive count' : Count;
        in 'false negative count' : Count;
        out effectiveness : Percent;

        constraint {
            2 * 'true positive count' + 'false positive count' + 'false negative count' > 0
        }
        constraint {
            effectiveness ==
            (100.0 * 2 * 'true positive count') /
            (2 * 'true positive count' + 'false positive count' + 'false negative count')
        }
    }

    constraint def 'Mission Acceptance Indicator Rule' {
        in 'valid trace coverage' : Percent;
        in 'reproduction success' : Percent;
        in 'open critical discrepancy count' : Count;
        in 'completed contrasting case count' : Count;
        in 'required contrasting case count' : Count;
        in 'undeclared adaptation count' : Count;
        out satisfied : Boolean;

        constraint {
            satisfied ==
            ('valid trace coverage' == 100.0 and
                'reproduction success' == 100.0 and
                'open critical discrepancy count' == 0 and
                'completed contrasting case count' == 'required contrasting case count' and
                'undeclared adaptation count' == 0)
        }
    }

    constraint def 'System MOP to Enterprise MOE Bindings' {
        in 'change turnaround mop' : Hours;
        in 'case adaptation mop' : PersonHours;
        in 'independent reproduction mop' : PersonHours;
        in 'framework adoption mop' : PersonHours;
        in 'direct cost mop' : CAD;
        in 'consistency assurance mop' : Percent;
        out 'change turnaround moe' : Hours;
        out 'case adaptation moe' : PersonHours;
        out 'independent reproduction moe' : PersonHours;
        out 'framework adoption moe' : PersonHours;
        out 'direct cost moe' : CAD;
        out 'consistency assurance moe' : Percent;

        constraint { 'change turnaround moe' == 'change turnaround mop' }
        constraint { 'case adaptation moe' == 'case adaptation mop' }
        constraint { 'independent reproduction moe' == 'independent reproduction mop' }
        constraint { 'framework adoption moe' == 'framework adoption mop' }
        constraint { 'direct cost moe' == 'direct cost mop' }
        constraint { 'consistency assurance moe' == 'consistency assurance mop' }
    }

    #refinement dependency
        'Measured Nanosatellite EPS Engineering Framework'::'valid trace coverage'
        to FrameworkMissionRequirements::'Complete and Valid Evidence Chains';
    #refinement dependency
        from
            'Measured Nanosatellite EPS Engineering Framework'
                ::'reference analysis reproduction success'
        to FrameworkMissionRequirements::'Reproduce Reference Analyses';
    #refinement dependency
        'Measured Nanosatellite EPS Engineering Framework'::'open critical discrepancy count'
        to FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies';
    #refinement dependency
        'Measured Nanosatellite EPS Engineering Framework'::'completed contrasting case count'
        to FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
    #refinement dependency
        'Measured Nanosatellite EPS Engineering Framework'::'undeclared adaptation count'
        to FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';

    analysis 'Framework Critical Properties Analysis' {
        item manifest : 'Framework Evaluation Manifest';
        part framework : 'Measured Nanosatellite EPS Engineering Framework';
        part enterprise : 'Academic Nanosatellite EPS Development Enterprise';

        attribute 'valid required trace count' : Count;
        attribute 'applicable required trace count' : Count;
        attribute 'successful designated analysis count' : Count;
        attribute 'designated analysis count' : Count;
        attribute 'consistency true positive count' : Count;
        attribute 'consistency false positive count' : Count;
        attribute 'consistency false negative count' : Count;
        attribute 'mission acceptance indicators satisfied' : Boolean;

        constraint traceCoverage : 'Trace Coverage Equation' {
            in 'valid required trace count' = 'valid required trace count';
            in 'applicable required trace count' = 'applicable required trace count';
            out coverage = framework.'valid trace coverage';
        }
        constraint reproductionSuccess : 'Reproduction Success Equation' {
            in 'successful designated analysis count' = 'successful designated analysis count';
            in 'designated analysis count' = 'designated analysis count';
            out success = framework.'reference analysis reproduction success';
        }
        constraint consistencyEffectiveness : 'Consistency Assurance F1 Equation' {
            in 'true positive count' = 'consistency true positive count';
            in 'false positive count' = 'consistency false positive count';
            in 'false negative count' = 'consistency false negative count';
            out effectiveness = framework.'consistency assurance effectiveness';
        }
        constraint missionAcceptance : 'Mission Acceptance Indicator Rule' {
            in 'valid trace coverage' = framework.'valid trace coverage';
            in 'reproduction success' = framework.'reference analysis reproduction success';
            in 'open critical discrepancy count' = framework.'open critical discrepancy count';
            in 'completed contrasting case count' = framework.'completed contrasting case count';
            in 'required contrasting case count' = manifest.'required contrasting case count';
            in 'undeclared adaptation count' = framework.'undeclared adaptation count';
            out satisfied = 'mission acceptance indicators satisfied';
        }
        constraint moeBindings : 'System MOP to Enterprise MOE Bindings' {
            in 'change turnaround mop' = framework.'correct change turnaround time';
            in 'case adaptation mop' = framework.'case adaptation effort';
            in 'independent reproduction mop' = framework.'independent reproduction effort';
            in 'framework adoption mop' = framework.'framework adoption effort';
            in 'direct cost mop' = framework.'direct framework cost';
            in 'consistency assurance mop' = framework.'consistency assurance effectiveness';
            out 'change turnaround moe' = enterprise.'correct change turnaround time';
            out 'case adaptation moe' = enterprise.'case adaptation effort';
            out 'independent reproduction moe' = enterprise.'independent reproduction effort';
            out 'framework adoption moe' = enterprise.'framework adoption effort';
            out 'direct cost moe' = enterprise.'direct framework cost';
            out 'consistency assurance moe' = enterprise.'consistency assurance effectiveness';
        }
    }
} // package FrameworkCriticalProperties
