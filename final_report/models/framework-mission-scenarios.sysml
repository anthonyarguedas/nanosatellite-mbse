// Black-box mission scenarios derived from the six enterprise use cases.
package FrameworkMissionScenarios {
    private import ScalarValues::Boolean;
    private import ModelingMetadata::refinement;
    private import ToBeOperationalDomain::*;
    private import FrameworkBlackBoxFunctions::*;

    doc
    /* Each scenario keeps the Nanosatellite EPS Engineering Framework opaque. Actions are
     * allocated to domain participants to expose responsibility while preserving the black-box
     * abstraction. The set covers every enterprise use case and domain participant. It exercises
     * the six MOEs through case setup, controlled change, reproduction, comparison, and assurance.
     * Decision branches distinguish successful completion, incomplete evidence, and execution or
     * access failures.
     */

    action <'SC-01'> 'Maintain EPS Evidence Chain Scenario' {
        attribute 'records available' : Boolean;
        attribute 'external artifacts accepted' : Boolean;
        attribute 'chain valid' : Boolean;
        doc
        /* Trigger: the mission team designates a decision or externally produced artifact revision
         * for evidence control. Preconditions: the request names an evidence baseline and the
         * designated requirement set, tailored EPS model, or analysis result. Success: each artifact
         * source revision is registered, the complete chain is valid, and the assessment is retained.
         * Alternatives: unavailable records, rejected artifacts, and trace gaps remain explicit and
         * leave prior controlled content unchanged.
         */

        first start;
        then 'Submit designated decision or external artifact';
        action 'Submit designated decision or external artifact';
        then 'Establish affected chain scope';
        action 'Establish affected chain scope' : 'Scope Evidence Chain';
        then fork 'Collect externally produced records';
            then 'Supply requirement set and EPS model revisions';
            then 'Supply analysis result and retained evidence revisions';
        action 'Supply requirement set and EPS model revisions';
        then 'Records collected';
        action 'Supply analysis result and retained evidence revisions';
        then 'Records collected';
        join 'Records collected';
        then decide 'Records available?';
            if 'records available' then 'Verify and register external artifact revisions';
            if not 'records available' then 'Report unavailable records';
        action 'Verify and register external artifact revisions'
            : 'Register External Engineering Artifacts';
        then decide 'External artifacts accepted?';
            if 'external artifacts accepted' then 'Check links, baselines, versions, and provenance';
            if not 'external artifacts accepted' then 'Report rejected artifacts and preserve baseline';
        action 'Check links, baselines, versions, and provenance' : 'Validate Evidence Chain';
        then decide 'Chain valid?';
            if 'chain valid' then 'Register valid chain status';
            if not 'chain valid' then 'Report evidence gaps';
        action 'Register valid chain status' : 'Issue Evidence Chain Assessment';
        then 'Assessment prepared';
        action 'Report evidence gaps' : 'Issue Evidence Chain Assessment';
        then 'Assessment prepared';
        action 'Report rejected artifacts and preserve baseline'
            : 'Issue Evidence Chain Assessment';
        then 'Assessment prepared';
        action 'Report unavailable records' : 'Issue Evidence Chain Assessment';
        then 'Assessment prepared';
        merge 'Assessment prepared';
        then 'Retain registrations and chain assessment';
        action 'Retain registrations and chain assessment';
        then 'Receive chain and artifact status';
        action 'Receive chain and artifact status';
        then done;
    }

    part 'SC-01 Performers' {
        part missionTeam : 'Academic Mission Team' {
            perform
                'Maintain EPS Evidence Chain Scenario'
                        .'Submit designated decision or external artifact';
            perform
                'Maintain EPS Evidence Chain Scenario'.'Receive chain and artifact status';
        }
        part framework : 'Nanosatellite EPS Engineering Framework' {
            perform 'Maintain EPS Evidence Chain Scenario'.'Establish affected chain scope';
            perform
                'Maintain EPS Evidence Chain Scenario'
                        .'Verify and register external artifact revisions';
            perform
                'Maintain EPS Evidence Chain Scenario'
                        .'Check links, baselines, versions, and provenance';
            perform 'Maintain EPS Evidence Chain Scenario'.'Register valid chain status';
            perform 'Maintain EPS Evidence Chain Scenario'.'Report evidence gaps';
            perform
                'Maintain EPS Evidence Chain Scenario'
                        .'Report rejected artifacts and preserve baseline';
            perform 'Maintain EPS Evidence Chain Scenario'.'Report unavailable records';
        }
        part systemModel : 'Versioned System Model' {
            perform
                'Maintain EPS Evidence Chain Scenario'
                        .'Supply requirement set and EPS model revisions';
        }
        part evidenceRepository : 'Evidence Repository' {
            perform
                'Maintain EPS Evidence Chain Scenario'
                        .'Supply analysis result and retained evidence revisions';
            perform
                'Maintain EPS Evidence Chain Scenario'
                        .'Retain registrations and chain assessment';
        }
    }

    action <'SC-02'> 'Configure Framework for EPS Case Scenario' {
        attribute 'common core available' : Boolean;
        attribute 'adaptation accepted' : Boolean;
        doc
        /* Trigger: the mission team selects an EPS case for framework application.
         * Preconditions: the case objective, starting environment, and intended common-core and
         * generic EPS model revisions are identified.
         * Success: a controlled case configuration identifies the generic model baseline and declares
         * all parameters, extensions, mappings, and assumptions for external model tailoring.
         * Alternatives remain visibly incomplete or unavailable.
         */

        first start;
        then 'Declare EPS case, intended analyses, and starting environment';
        action 'Declare EPS case, intended analyses, and starting environment';
        then 'Supply generic model, common core, workflow, and minimum environment declaration';
        action 'Supply generic model, common core, workflow, and minimum environment declaration';
        then decide 'Common core available?';
            if 'common core available' then 'Establish declared minimum environment';
            if not 'common core available' then 'Report unavailable common core';
        action 'Establish declared minimum environment';
        then 'Capture environment, cost, parameters, extensions, mappings, and assumptions';
        action 'Capture environment, cost, parameters, extensions, mappings, and assumptions'
            : 'Capture Case Configuration';
        then 'Check configuration completeness and compatibility';
        action 'Check configuration completeness and compatibility' : 'Validate Case Configuration';
        then 'Review common-core boundary and adaptations';
        action 'Review common-core boundary and adaptations';
        then decide 'Adaptation accepted?';
            if 'adaptation accepted' then 'Confirm case configuration';
            if not 'adaptation accepted' then 'Report incomplete or unapproved configuration';
        action 'Confirm case configuration';
        then 'Register ready case configuration';
        action 'Register ready case configuration' : 'Issue Configuration Status';
        then 'Configuration status prepared';
        action 'Report incomplete or unapproved configuration' : 'Issue Configuration Status';
        then 'Configuration status prepared';
        action 'Report unavailable common core' : 'Issue Configuration Status';
        then 'Configuration status prepared';
        merge 'Configuration status prepared';
        then 'Retain case configuration status';
        action 'Retain case configuration status';
        then 'Receive configuration status';
        action 'Receive configuration status';
        then done;
    }

    part 'SC-02 Performers' {
        part missionTeam : 'Academic Mission Team' {
            perform
                'Configure Framework for EPS Case Scenario'
                        .'Declare EPS case, intended analyses, and starting environment';
            perform
                'Configure Framework for EPS Case Scenario'.'Establish declared minimum environment';
            perform 'Configure Framework for EPS Case Scenario'.'Confirm case configuration';
            perform 'Configure Framework for EPS Case Scenario'.'Receive configuration status';
        }
        part researcher : 'Academic Researcher' {
            perform
                'Configure Framework for EPS Case Scenario'
                        .'Review common-core boundary and adaptations';
        }
        part framework : 'Nanosatellite EPS Engineering Framework' {
            perform
                'Configure Framework for EPS Case Scenario'
                        .'Capture environment, cost, parameters, extensions, mappings, and assumptions';
            perform
                'Configure Framework for EPS Case Scenario'
                        .'Check configuration completeness and compatibility';
            perform 'Configure Framework for EPS Case Scenario'.'Register ready case configuration';
            perform
                'Configure Framework for EPS Case Scenario'
                        .'Report incomplete or unapproved configuration';
            perform 'Configure Framework for EPS Case Scenario'.'Report unavailable common core';
        }
        part systemModel : 'Versioned System Model' {
            perform
                'Configure Framework for EPS Case Scenario'
                        .'Supply generic model, common core, workflow, and minimum environment declaration';
        }
        part evidenceRepository : 'Evidence Repository' {
            perform 'Configure Framework for EPS Case Scenario'.'Retain case configuration status';
        }
    }

    action <'SC-03'> 'Reproduce Analysis Scenario' {
        attribute 'package complete' : Boolean;
        attribute 'execution completed' : Boolean;
        attribute 'within declared tolerance' : Boolean;
        doc
        /* Trigger: a reviewer requests reproduction of a designated analysis.
         * Preconditions: the request identifies the reported result and its intended baseline.
         * Success: a retained package records the controlled inputs, execution evidence, comparison,
         * and verdict. Missing inputs, execution failure, and result mismatch remain distinct outcomes.
         */

        first start;
        then 'Request reproduction of designated analysis';
        action 'Request reproduction of designated analysis';
        then 'Identify baseline, reported result, and tolerance';
        action 'Identify baseline, reported result, and tolerance' : 'Prepare Reproduction Package';
        then fork 'Collect reproduction package';
            then 'Supply controlled model and configuration';
            then 'Supply inputs, dependencies, and reported result';
        action 'Supply controlled model and configuration';
        then 'Reproduction package collected';
        action 'Supply inputs, dependencies, and reported result';
        then 'Reproduction package collected';
        join 'Reproduction package collected';
        then 'Check reproduction package';
        action 'Check reproduction package' : 'Prepare Reproduction Package';
        then decide 'Package complete?';
            if 'package complete' then 'Submit controlled execution';
            if not 'package complete' then 'Report missing reproduction evidence';
        action 'Submit controlled execution' : 'Coordinate Controlled Analysis';
        then 'Execute analysis and return raw results';
        action 'Execute analysis and return raw results';
        then decide 'Execution completed?';
            if 'execution completed' then 'Compare reproduced and reported results';
            if not 'execution completed' then 'Report execution failure';
        action 'Compare reproduced and reported results' : 'Evaluate Reproduced Result';
        then decide 'Within tolerance?';
            if 'within declared tolerance' then 'Record reproduction success';
            if not 'within declared tolerance' then 'Record result discrepancy';
        action 'Record reproduction success' : 'Issue Reproduction Verdict';
        then 'Verdict prepared';
        action 'Record result discrepancy' : 'Issue Reproduction Verdict';
        then 'Verdict prepared';
        action 'Report execution failure' : 'Coordinate Controlled Analysis';
        then 'Verdict prepared';
        action 'Report missing reproduction evidence' : 'Prepare Reproduction Package';
        then 'Verdict prepared';
        merge 'Verdict prepared';
        then 'Retain reproduction package';
        action 'Retain reproduction package';
        then 'Receive verdict and evidence';
        action 'Receive verdict and evidence';
        then done;
    }

    part 'SC-03 Performers' {
        part reviewer : Reviewer {
            perform 'Reproduce Analysis Scenario'.'Request reproduction of designated analysis';
            perform 'Reproduce Analysis Scenario'.'Receive verdict and evidence';
        }
        part framework : 'Nanosatellite EPS Engineering Framework' {
            perform
                'Reproduce Analysis Scenario'.'Identify baseline, reported result, and tolerance';
            perform 'Reproduce Analysis Scenario'.'Check reproduction package';
            perform 'Reproduce Analysis Scenario'.'Submit controlled execution';
            perform 'Reproduce Analysis Scenario'.'Compare reproduced and reported results';
            perform 'Reproduce Analysis Scenario'.'Record reproduction success';
            perform 'Reproduce Analysis Scenario'.'Record result discrepancy';
            perform 'Reproduce Analysis Scenario'.'Report execution failure';
            perform 'Reproduce Analysis Scenario'.'Report missing reproduction evidence';
        }
        part systemModel : 'Versioned System Model' {
            perform 'Reproduce Analysis Scenario'.'Supply controlled model and configuration';
        }
        part evidenceRepository : 'Evidence Repository' {
            perform
                'Reproduce Analysis Scenario'.'Supply inputs, dependencies, and reported result';
            perform 'Reproduce Analysis Scenario'.'Retain reproduction package';
        }
        part analysisTools : 'Analysis Tools' {
            perform 'Reproduce Analysis Scenario'.'Execute analysis and return raw results';
        }
    }

    action <'SC-04'> 'Assess Design Change Scenario' {
        attribute 'target baseline available' : Boolean;
        attribute 'updated evidence consistent' : Boolean;
        doc
        /* Trigger: the mission team submits a controlled EPS design change against a named baseline.
         * Preconditions: the request identifies the proposed change and target baseline.
         * Success: affected evidence is updated and a correct review package is issued. An absent
         * baseline or unresolved inconsistency prevents a successful change outcome.
         */

        first start;
        then 'Submit change request and target baseline';
        action 'Submit change request and target baseline';
        then 'Validate request and target baseline identity';
        action 'Validate request and target baseline identity' : 'Validate Change Request';
        then decide 'Target baseline available?';
            if 'target baseline available' then 'Collect change evidence';
            if not 'target baseline available' then 'Report unassessable change';
        fork 'Collect change evidence';
            then 'Supply dependency and trace records';
            then 'Supply prior evidence and configuration';
        action 'Supply dependency and trace records';
        then 'Change evidence collected';
        action 'Supply prior evidence and configuration';
        then 'Change evidence collected';
        join 'Change evidence collected';
        then 'Identify affected requirements, interfaces, assumptions, analyses, and verification';
        action 'Identify affected requirements, interfaces, assumptions, analyses, and verification'
            : 'Analyze Change Impact';
        then 'Present impact set and coverage gaps';
        action 'Present impact set and coverage gaps' : 'Analyze Change Impact';
        then 'Authorize change scope and submit revisions';
        action 'Authorize change scope and submit revisions';
        then 'Coordinate affected checks and analyses';
        action 'Coordinate affected checks and analyses' : 'Coordinate Controlled Analysis';
        then 'Execute affected analyses and return results';
        action 'Execute affected analyses and return results';
        then 'Validate regenerated evidence chain';
        action 'Validate regenerated evidence chain' : 'Validate Regenerated Evidence';
        then decide 'Updated evidence consistent?';
            if 'updated evidence consistent' then 'Prepare correct review package';
            if not 'updated evidence consistent' then 'Report unresolved change discrepancies';
        action 'Prepare correct review package' : 'Assemble Change Evidence Package';
        then 'Change outcome prepared';
        action 'Report unresolved change discrepancies' : 'Assemble Change Evidence Package';
        then 'Change outcome prepared';
        action 'Report unassessable change' : 'Validate Change Request';
        then 'Change outcome prepared';
        merge 'Change outcome prepared';
        then 'Retain change record and evidence package';
        action 'Retain change record and evidence package';
        then 'Receive change outcome';
        action 'Receive change outcome';
        then done;
    }

    part 'SC-04 Performers' {
        part missionTeam : 'Academic Mission Team' {
            perform 'Assess Design Change Scenario'.'Submit change request and target baseline';
            perform 'Assess Design Change Scenario'.'Authorize change scope and submit revisions';
            perform 'Assess Design Change Scenario'.'Receive change outcome';
        }
        part framework : 'Nanosatellite EPS Engineering Framework' {
            perform 'Assess Design Change Scenario'.'Validate request and target baseline identity';
            perform
                'Assess Design Change Scenario'
                        .'Identify affected requirements, interfaces, assumptions, analyses, and verification';
            perform 'Assess Design Change Scenario'.'Present impact set and coverage gaps';
            perform 'Assess Design Change Scenario'.'Coordinate affected checks and analyses';
            perform 'Assess Design Change Scenario'.'Validate regenerated evidence chain';
            perform 'Assess Design Change Scenario'.'Prepare correct review package';
            perform 'Assess Design Change Scenario'.'Report unresolved change discrepancies';
            perform 'Assess Design Change Scenario'.'Report unassessable change';
        }
        part systemModel : 'Versioned System Model' {
            perform 'Assess Design Change Scenario'.'Supply dependency and trace records';
        }
        part analysisTools : 'Analysis Tools' {
            perform 'Assess Design Change Scenario'.'Execute affected analyses and return results';
        }
        part evidenceRepository : 'Evidence Repository' {
            perform 'Assess Design Change Scenario'.'Supply prior evidence and configuration';
            perform 'Assess Design Change Scenario'.'Retain change record and evidence package';
        }
    }

    action <'SC-05'> 'Compare Candidate EPS Architectures Scenario' {
        attribute 'comparison basis compatible' : Boolean;
        attribute 'candidate analyses complete' : Boolean;
        doc
        /* Trigger: the mission team nominates EPS architecture candidates for a common comparison.
         * Preconditions: at least two candidate identifiers and the intended decision are supplied.
         * Success: raw results, uncertainty, feasibility, Pareto relations, and declared scoring are
         * packaged for a human decision. The EPS measures used here are separate from the
         * framework-level MOEs used later to compare framework physical architectures.
         */

        first start;
        then 'Nominate candidate EPS architectures';
        action 'Nominate candidate EPS architectures';
        then 'Declare common scenarios, measures, constraints, and protocol';
        action 'Declare common scenarios, measures, constraints, and protocol';
        then 'Supply controlled candidate models and configurations';
        action 'Supply controlled candidate models and configurations';
        then 'Check candidate comparability';
        action 'Check candidate comparability' : 'Validate Comparison Basis';
        then decide 'Comparison basis compatible?';
            if 'comparison basis compatible' then 'Submit common analysis requests';
            if not 'comparison basis compatible' then 'Report incomparable candidate evidence';
        action 'Submit common analysis requests' : 'Coordinate Controlled Analysis';
        then 'Evaluate candidates and return raw results and uncertainty';
        action 'Evaluate candidates and return raw results and uncertainty';
        then decide 'Candidate analyses complete?';
            if 'candidate analyses complete' then 'Retain raw candidate results';
            if not 'candidate analyses complete' then 'Report incomplete candidate analysis';
        action 'Retain raw candidate results';
        then 'Identify feasible and infeasible candidates';
        action 'Identify feasible and infeasible candidates' : 'Determine Candidate Feasibility';
        then 'Produce Pareto and declared-score comparison';
        action 'Produce Pareto and declared-score comparison' : 'Compare Candidate Architectures';
        then 'Examine sensitivity and uncertainty';
        action 'Examine sensitivity and uncertainty';
        then 'Package comparison for human decision';
        action 'Package comparison for human decision' : 'Issue Candidate Comparison';
        then 'Comparison outcome prepared';
        action 'Report incomplete candidate analysis' : 'Issue Candidate Comparison';
        then 'Comparison outcome prepared';
        action 'Report incomparable candidate evidence' : 'Issue Candidate Comparison';
        then 'Comparison outcome prepared';
        merge 'Comparison outcome prepared';
        then 'Receive candidate comparison';
        action 'Receive candidate comparison';
        then done;
    }

    part 'SC-05 Performers' {
        part missionTeam : 'Academic Mission Team' {
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Nominate candidate EPS architectures';
            perform 'Compare Candidate EPS Architectures Scenario'.'Receive candidate comparison';
        }
        part researcher : 'Academic Researcher' {
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Declare common scenarios, measures, constraints, and protocol';
            perform
                'Compare Candidate EPS Architectures Scenario'.'Examine sensitivity and uncertainty';
        }
        part framework : 'Nanosatellite EPS Engineering Framework' {
            perform 'Compare Candidate EPS Architectures Scenario'.'Check candidate comparability';
            perform
                'Compare Candidate EPS Architectures Scenario'.'Submit common analysis requests';
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Identify feasible and infeasible candidates';
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Produce Pareto and declared-score comparison';
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Package comparison for human decision';
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Report incomplete candidate analysis';
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Report incomparable candidate evidence';
        }
        part systemModel : 'Versioned System Model' {
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Supply controlled candidate models and configurations';
        }
        part analysisTools : 'Analysis Tools' {
            perform
                'Compare Candidate EPS Architectures Scenario'
                        .'Evaluate candidates and return raw results and uncertainty';
        }
        part evidenceRepository : 'Evidence Repository' {
            perform 'Compare Candidate EPS Architectures Scenario'.'Retain raw candidate results';
        }
    }

    action <'SC-06'> 'Review Early Design Justification Scenario' {
        attribute 'review package complete' : Boolean;
        attribute 'reproduction requested' : Boolean;
        attribute 'critical findings resolved' : Boolean;
        doc
        /* Trigger: the mission team submits claims from a named early-design baseline for review.
         * Preconditions: the review request identifies its claims, baseline, and reviewer.
         * Success: reviewer findings, dispositions, reproduction evidence when requested, and the
         * review outcome are retained. The reviewer determines the outcome.
         */

        first start;
        then 'Submit claims and named baseline for review';
        action 'Submit claims and named baseline for review';
        then fork 'Collect review evidence';
            then 'Supply controlled model and trace records';
            then 'Supply analyses, discrepancies, uncertainty, and instructions';
        action 'Supply controlled model and trace records';
        then 'Review evidence collected';
        action 'Supply analyses, discrepancies, uncertainty, and instructions';
        then 'Review evidence collected';
        join 'Review evidence collected';
        then 'Assemble and check review package';
        action 'Assemble and check review package' : 'Assemble Review Package';
        then decide 'Review package complete?';
            if 'review package complete' then 'Inspect claims, traces, and raw evidence';
            if not 'review package complete' then 'Report review-package gaps';
        action 'Inspect claims, traces, and raw evidence';
        then decide 'Reproduction requested?';
            if 'reproduction requested' then 'Support selected reproduction through SC-03';
            if not 'reproduction requested' then 'Evidence inspection complete';
        action 'Support selected reproduction through SC-03' : 'Coordinate Selected Reproduction';
        then 'Evaluate reproduction evidence';
        action 'Evaluate reproduction evidence';
        then 'Evidence inspection complete';
        merge 'Evidence inspection complete';
        then 'Record review findings';
        action 'Record review findings';
        then 'Link findings to evidence and discrepancy status';
        action 'Link findings to evidence and discrepancy status' : 'Manage Review Findings';
        then 'Submit corrections or dispositions';
        action 'Submit corrections or dispositions';
        then 'Assess finding resolution';
        action 'Assess finding resolution';
        then decide 'Critical findings resolved?';
            if 'critical findings resolved' then 'Record review outcome';
            if not 'critical findings resolved' then 'Keep critical findings open';
        action 'Record review outcome';
        then 'Review status prepared';
        action 'Keep critical findings open' : 'Manage Review Findings';
        then 'Review status prepared';
        action 'Report review-package gaps' : 'Assemble Review Package';
        then 'Review status prepared';
        merge 'Review status prepared';
        then 'Retain review package and outcome';
        action 'Retain review package and outcome';
        then 'Publish review status';
        action 'Publish review status' : 'Issue Review Status';
        then done;
    }

    part 'SC-06 Performers' {
        part missionTeam : 'Academic Mission Team' {
            perform
                'Review Early Design Justification Scenario'
                        .'Submit claims and named baseline for review';
            perform
                'Review Early Design Justification Scenario'.'Submit corrections or dispositions';
        }
        part reviewer : Reviewer {
            perform
                'Review Early Design Justification Scenario'
                        .'Inspect claims, traces, and raw evidence';
            perform 'Review Early Design Justification Scenario'.'Evaluate reproduction evidence';
            perform 'Review Early Design Justification Scenario'.'Record review findings';
            perform 'Review Early Design Justification Scenario'.'Assess finding resolution';
            perform 'Review Early Design Justification Scenario'.'Record review outcome';
        }
        part framework : 'Nanosatellite EPS Engineering Framework' {
            perform
                'Review Early Design Justification Scenario'.'Assemble and check review package';
            perform
                'Review Early Design Justification Scenario'
                        .'Support selected reproduction through SC-03';
            perform
                'Review Early Design Justification Scenario'
                        .'Link findings to evidence and discrepancy status';
            perform 'Review Early Design Justification Scenario'.'Keep critical findings open';
            perform 'Review Early Design Justification Scenario'.'Report review-package gaps';
            perform 'Review Early Design Justification Scenario'.'Publish review status';
        }
        part systemModel : 'Versioned System Model' {
            perform
                'Review Early Design Justification Scenario'
                        .'Supply controlled model and trace records';
        }
        part evidenceRepository : 'Evidence Repository' {
            perform
                'Review Early Design Justification Scenario'
                        .'Supply analyses, discrepancies, uncertainty, and instructions';
            perform
                'Review Early Design Justification Scenario'.'Retain review package and outcome';
        }
    }

    #refinement dependency 'Maintain EPS Evidence Chain Scenario' to 'Maintain EPS Evidence Chain';
    #refinement dependency
        'Configure Framework for EPS Case Scenario'
        to 'Configure Framework for an EPS Case';
    #refinement dependency 'Reproduce Analysis Scenario' to 'Reproduce an Analysis';
    #refinement dependency 'Assess Design Change Scenario' to 'Assess a Design Change';
    #refinement dependency
        'Compare Candidate EPS Architectures Scenario'
        to 'Compare Candidate EPS Architectures';
    #refinement dependency
        'Review Early Design Justification Scenario'
        to 'Review an Early Design Justification';
} // package FrameworkMissionScenarios
