// Atomic mandatory black-box system requirements and their derivation metadata.
package FrameworkSystemRequirements {
    private import Base::Anything;
    private import ScalarValues::String;
    private import VerificationCases::VerificationMethodKind;
    private import ModelingMetadata::refinement;
    private import FrameworkBlackBoxSpecification
            ::'Specified Nanosatellite EPS Engineering Framework';

    metadata def BlackBoxRequirementTrace {
        doc
        /* Each leaf requirement records direct model references to its scenario basis and parent
         * mission requirement, plus its rationale, specified feature identifier, planned
         * verification method, and acceptance criterion. Detailed procedures and results are added
         * during Support System Integration and Verification.
         */

        ref sourceScenario : Anything [1..*];
        ref parentMissionRequirement : Anything [1..*];
        attribute rationale : String;
        attribute specifiedFeatureIdentifier : String;
        attribute verificationMethod : VerificationMethodKind [1..*];
        attribute acceptanceCriterion : String;
    }

    requirement <'SYS-00'> 'Framework Black-Box System Requirements' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Every candidate framework realization shall satisfy all functional, operational control,
         * interface, store, performance, quality, and resource-declaration requirements in this
         * specification. Project controls on the OOSEM comparison model are defined separately and
         * do not constrain candidate implementation.
         */
        require constraint statement {
            doc
            /* Every mandatory leaf requirement has a passing verification verdict. */
        }
    }

    requirement <'FUN-00'> 'Functional Requirements' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall perform every required black-box service function. */
        require constraint statement {
            doc
            /* FUN-01 through FUN-23 are satisfied. */
        }
    }

    requirement <'CTL-00'> 'Operational Control Requirements' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall control service invocation, outcomes, discrepancies, and recovery as
         * specified by SM-01 Framework Operational Control.
         */
        require constraint statement {
            doc
            /* CTL-01 through CTL-06 are satisfied. */
        }
    }

    requirement <'INT-00'> 'Interface Requirements' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall conform to every required typed boundary contract. */
        require constraint statement {
            doc
            /* INT-01 through INT-08 are satisfied. */
        }
    }

    requirement <'STO-00'> 'Store Requirements' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall preserve and retrieve the required controlled records. */
        require constraint statement {
            doc
            /* STO-01 through STO-04 are satisfied. */
        }
    }

    requirement <'PER-00'> 'Performance and Measurement Requirements' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall meet acceptance targets and report every comparative MOP. */
        require constraint statement {
            doc
            /* PER-01 through PER-11 are satisfied. */
        }
    }

    requirement <'QLT-00'> 'Quality Requirements' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Framework outputs shall preserve integrity, transparency, and explicit status. */
        require constraint statement {
            doc
            /* QLT-01 through QLT-05 are satisfied. */
        }
    }

    requirement <'RES-00'> 'Execution Resource Requirements' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall declare and support reconstruction of its execution environment. */
        require constraint statement {
            doc
            /* RES-01 and RES-02 are satisfied. */
        }
    }

    // Functional requirements derived from the 23 scenario-allocated subfunctions.
    requirement <'FUN-01'> 'Scope Designated Evidence Chain' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Given a valid Evidence Chain Request, the framework shall identify the named evidence
         * baseline, every designated external artifact revision, and every applicable relation and
         * endpoint in the evidence chain.
         */
        require constraint statement {
            doc
            /* The issued scope is complete for the request. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains';
        rationale = "A chain must be bounded before its completeness and validity can be assessed.";
        specifiedFeatureIdentifier = "F-01.1 Scope Evidence Chain";
        verificationMethod = (VerificationMethodKind::demo, VerificationMethodKind::test);
        acceptanceCriterion =
            "For a controlled fixture, the scope contains the oracle baseline, designated external artifact revisions, relations, and endpoints.";
    }

    requirement <'FUN-02'> 'Validate Evidence Chain' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall evaluate each scoped chain for record availability, accepted artifact
         * registration, producer and source-revision identity, endpoint resolution, baseline identity,
         * provenance preservation, required relation semantics, and unresolved discrepancies.
         */
        require constraint statement {
            doc
            /* Every applicable validity check has an explicit result. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "G-01 requires complete valid chains and G-03 forbids hidden critical inconsistencies.";
        specifiedFeatureIdentifier = "F-01.2 Validate Evidence Chain";
        verificationMethod = (VerificationMethodKind::analyze, VerificationMethodKind::test);
        acceptanceCriterion =
            "Complete, incomplete, unavailable, rejected-artifact, and inconsistent fixtures receive the corresponding assessment, registration status, and discrepancies.";
    }

    requirement <'FUN-03'> 'Issue Evidence Chain Assessment' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall issue an Evidence Chain Assessment that states record availability,
         * external-artifact acceptance, and chain validity and includes every Artifact Registration
         * Record and detected gap or discrepancy.
         */
        require constraint statement {
            doc
            /* One reviewable assessment is issued for each request. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale = "A visible assessment is the externally observable outcome of SC-01.";
        specifiedFeatureIdentifier = "F-01.3 Issue Evidence Chain Assessment";
        verificationMethod = VerificationMethodKind::demo;
        acceptanceCriterion =
            "Each nominal and exceptional SC-01 path emits and retains one assessment with the expected availability, artifact-acceptance, chain-validity, registration, and discrepancy content.";
    }

    requirement <'FUN-04'> 'Capture Case Configuration' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For each requested EPS case, the framework shall capture the common-core and generic EPS
         * model revisions, environment, direct-cost basis, parameters, extensions, mappings, and
         * assumptions in a Case Configuration Draft.
         */
        require constraint statement {
            doc
            /* The draft exposes every required configuration field. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        rationale = "G-04 requires declared case adaptations around one identified common core.";
        specifiedFeatureIdentifier = "F-02.1 Capture Case Configuration";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::demo);
        acceptanceCriterion =
            "A configured fixture contains the expected common-core and generic-model revisions and every required environment, cost, adaptation, and assumption field.";
    }

    requirement <'FUN-05'> 'Validate Case Configuration' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall assess each Case Configuration Draft for completeness, semantic
         * compatibility with the common core and identified generic EPS model, and approval of every
         * declared adaptation that an external MD capability may apply.
         */
        require constraint statement {
            doc
            /* The assessment distinguishes accepted and deficient drafts. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "A case cannot count toward G-04 when its configuration is incomplete, incompatible, or unapproved.";
        specifiedFeatureIdentifier = "F-02.2 Validate Case Configuration";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Known complete, missing-generic-model, incompatible, and unapproved drafts receive the oracle assessment and discrepancy set.";
    }

    requirement <'FUN-06'> 'Issue Controlled Case Configuration' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall issue either a Controlled Case Configuration with ready status when
         * its draft is complete, compatible, and approved, or a non-ready status with discrepancies
         * for every other outcome.
         */
        require constraint statement {
            doc
            /* Readiness is equivalent to accepted configuration. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        rationale = "SC-02 needs an unambiguous controlled starting point for each completed case.";
        specifiedFeatureIdentifier = "F-02.3 Issue Configuration Status";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Ready is issued exactly for accepted drafts, while every other path produces a non-ready status and its discrepancies.";
    }

    requirement <'FUN-07'> 'Prepare Reproduction Package' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall assemble and assess the named baseline, source-identified model,
         * inputs, assumptions, dependencies, environment, reported result revision, and predeclared
         * tolerances required to reproduce a designated analysis.
         */
        require constraint statement {
            doc
            /* Package completeness is explicit before execution. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Reproduce Analysis Scenario';
        parentMissionRequirement = FrameworkMissionRequirements::'Reproduce Reference Analyses';
        rationale =
            "A complete controlled package is the prerequisite for a valid reproduction verdict.";
        specifiedFeatureIdentifier = "F-03.1 Prepare Reproduction Package";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "The complete fixture yields an execution request, while omission of any mandatory package element yields an explicit incomplete assessment.";
    }

    requirement <'FUN-08'> 'Coordinate Controlled Analysis' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall submit each accepted Analysis Execution Request to the analysis
         * interface and return the corresponding raw Analysis Result Package without changing its
         * producer, source revision, evidence-baseline identity, inputs, assumptions, status, or
         * results. Result acceptance remains subject to the common transfer contract.
         */
        require constraint statement {
            doc
            /* Request and result identity remain correlated. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses'
        );
        rationale = "SC-03, SC-04, and SC-05 share one controlled analysis boundary.";
        specifiedFeatureIdentifier = "F-03.2 Coordinate Controlled Analysis";
        verificationMethod = (VerificationMethodKind::demo, VerificationMethodKind::test);
        acceptanceCriterion =
            "Each submitted request and returned raw result preserve the oracle correlation, producer, source revision, evidence baseline, inputs, assumptions, status, and payload, while an invalid result is rejected under INT-08.";
    }

    requirement <'FUN-09'> 'Evaluate Reproduced Result' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall compare every declared reproduced result with its reported result
         * using the result-specific tolerance, units, precision, and comparison rule fixed before
         * execution.
         */
        require constraint statement {
            doc
            /* Every declared result receives a tolerance verdict. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Reproduce Analysis Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "G-02 defines reproduction at the declared-result level and G-03 requires mismatches to remain visible.";
        specifiedFeatureIdentifier = "F-03.3 Evaluate Reproduced Result";
        verificationMethod = (VerificationMethodKind::analyze, VerificationMethodKind::test);
        acceptanceCriterion =
            "Boundary, in-tolerance, out-of-tolerance, unit-mismatch, and missing-result fixtures produce the oracle result-level verdicts.";
    }

    requirement <'FUN-10'> 'Issue Reproduction Verdict' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall issue a successful Reproduction Verdict only when the reproduction
         * package is complete, execution completes, and every declared result conforms to its
         * predeclared tolerance.
         */
        require constraint statement {
            doc
            /* Success is the conjunction of all reproduction checks. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Reproduce Analysis Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale = "A single explicit verdict operationalizes the noncompensable G-02 gate.";
        specifiedFeatureIdentifier = "F-03.4 Issue Reproduction Verdict";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "The verdict is successful exactly when all three conditions hold and otherwise identifies the applicable discrepancy.";
    }

    requirement <'FUN-11'> 'Validate Design Change Request' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall accept a Design Change Request for impact analysis only when the
         * proposed change and an available immutable target baseline are identified.
         */
        require constraint statement {
            doc
            /* Invalid or unresolved targets remain unassessable. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Assess Design Change Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale = "SC-04 measures change response against a named controlled starting point.";
        specifiedFeatureIdentifier = "F-04.1 Validate Change Request";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Valid named-baseline requests proceed, while missing, mutable, or unresolved baselines produce an unassessable-change discrepancy.";
    }

    requirement <'FUN-12'> 'Analyze Design Change Impact' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For each accepted change, the framework shall identify affected requirements, interfaces,
         * assumptions, analyses, verification evidence, trace relations, and coverage gaps.
         */
        require constraint statement {
            doc
            /* The reported impact set covers every declared evidence class. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Assess Design Change Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "Complete impact identification is necessary to regenerate a valid evidence chain.";
        specifiedFeatureIdentifier = "F-04.2 Analyze Change Impact";
        verificationMethod = (VerificationMethodKind::analyze, VerificationMethodKind::test);
        acceptanceCriterion =
            "For seeded changes, the reported affected set and coverage gaps equal the adjudicated oracle.";
    }

    requirement <'FUN-13'> 'Validate Regenerated Evidence' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* After an authorized revision, the framework shall validate every affected analysis result,
         * verification item, trace relation, and unresolved discrepancy against the revised baseline.
         */
        require constraint statement {
            doc
            /* Revised evidence is accepted only as one valid chain. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Assess Design Change Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "A change outcome is correct only when all affected evidence is regenerated and consistent.";
        specifiedFeatureIdentifier = "F-04.3 Validate Regenerated Evidence";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Complete and defective revision fixtures are accepted or rejected according to the adjudicated revised-chain oracle.";
    }

    requirement <'FUN-14'> 'Assemble Change Evidence Package' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall issue a Change Evidence Package containing an explicit correctness
         * status, the request assessment, impact set, authorized revision, raw analysis results,
         * chain assessment, verification evidence, and unresolved discrepancies.
         */
        require constraint statement {
            doc
            /* The package exposes the complete change outcome. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Assess Design Change Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "SC-04 requires one reviewable package for both correct and unresolved outcomes.";
        specifiedFeatureIdentifier = "F-04.4 Assemble Change Evidence Package";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::demo);
        acceptanceCriterion =
            "Each SC-04 terminal path emits a retained package with the exact controlled inputs, outputs, evidence, correctness status, and discrepancies.";
    }

    requirement <'FUN-15'> 'Validate Candidate Comparison Basis' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Before candidate evaluation, the framework shall confirm at least two identified candidate
         * EPS architectures and one common controlled set of scenarios, measures, constraints,
         * configurations, and comparison rules.
         */
        require constraint statement {
            doc
            /* Candidate comparability is explicit before execution. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "A common basis prevents incomparable evidence from producing a decision package.";
        specifiedFeatureIdentifier = "F-05.1 Validate Comparison Basis";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Only fixtures with two or more identified candidates and identical controlled comparison inputs receive a compatible basis verdict.";
    }

    requirement <'FUN-16'> 'Determine Candidate EPS Feasibility' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall classify each candidate EPS architecture as feasible or infeasible by
         * evaluating every mandatory EPS requirement and constraint in the declared comparison
         * protocol before ranking.
         */
        require constraint statement {
            doc
            /* Every candidate receives a gate status and evidence. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains';
        rationale = "Noncompensable EPS obligations must gate the candidate comparison.";
        specifiedFeatureIdentifier = "F-05.2 Determine Candidate Feasibility";
        verificationMethod = (VerificationMethodKind::analyze, VerificationMethodKind::test);
        acceptanceCriterion =
            "Candidate gate statuses and cited failed constraints match the controlled comparison oracle.";
    }

    requirement <'FUN-17'> 'Compare Feasible EPS Candidates' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall compare only feasible candidate EPS architectures using raw MOP
         * results, Pareto relations, and any scoring rule fixed in the Comparison Protocol before
         * results are observed.
         */
        require constraint statement {
            doc
            /* Pareto comparison precedes declared aggregate scoring. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains';
        rationale =
            "SC-05 supports a transparent human decision without compensating for infeasibility.";
        specifiedFeatureIdentifier = "F-05.3 Compare Candidate Architectures";
        verificationMethod = (VerificationMethodKind::analyze, VerificationMethodKind::test);
        acceptanceCriterion =
            "For a controlled candidate set, eligibility, Pareto relations, and declared scores match independent calculations and exclude infeasible candidates.";
    }

    requirement <'FUN-18'> 'Issue Candidate Comparison Package' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall issue a Candidate Comparison Package containing an explicit
         * completeness status, basis assessment, fixed protocol, raw results, feasibility verdicts,
         * Pareto relations, declared scores, sensitivity, uncertainty, and discrepancies.
         */
        require constraint statement {
            doc
            /* The complete comparison basis and result remain reviewable. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "A decision package must retain raw and derived evidence rather than expose only a rank.";
        specifiedFeatureIdentifier = "F-05.4 Issue Candidate Comparison";
        verificationMethod = VerificationMethodKind::inspect;
        acceptanceCriterion =
            "The completeness status matches package inspection, and every required protocol, evidence, result, uncertainty, and discrepancy field resolves to the controlled candidate baselines.";
    }

    requirement <'FUN-19'> 'Assemble Early Design Review Package' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For each Design Review Request, the framework shall assemble a completeness-assessed
         * package containing the named controlled model, claims, traces, assumptions, raw results,
         * uncertainty, verification evidence, discrepancies, and reproduction instructions.
         */
        require constraint statement {
            doc
            /* The reviewer receives a bounded complete or deficient package. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Review Early Design Justification Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "SC-06 requires an independently inspectable body of evidence for each named claim.";
        specifiedFeatureIdentifier = "F-06.1 Assemble Review Package";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Complete and deficient review fixtures receive the correct package content and completeness assessment.";
    }

    requirement <'FUN-20'> 'Coordinate Selected Review Reproduction' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* When a reviewer designates an analysis for reproduction, the framework shall execute the
         * same controlled package, comparison, and verdict protocol required by FUN-07 through
         * FUN-10 and return the resulting evidence to the reviewer.
         */
        require constraint statement {
            doc
            /* Review reproduction uses the common reproduction protocol. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Review Early Design Justification Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "Independent review and stand-alone reproduction require one consistent verdict meaning.";
        specifiedFeatureIdentifier = "F-06.2 Coordinate Selected Reproduction";
        verificationMethod = (VerificationMethodKind::demo, VerificationMethodKind::test);
        acceptanceCriterion =
            "A selected review reproduction produces the same request, raw result, tolerance assessment, and verdict as the equivalent SC-03 fixture.";
    }

    requirement <'FUN-21'> 'Manage Review Findings' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall link each review finding to its affected claim and evidence, recorded
         * disposition, reproduction verdict when applicable, trace records, and current discrepancy
         * status.
         */
        require constraint statement {
            doc
            /* Every finding has one reviewable disposition chain. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Review Early Design Justification Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "Findings must remain connected to evidence and resolution status for G-01 and G-03.";
        specifiedFeatureIdentifier = "F-06.3 Manage Review Findings";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Each seeded finding resolves to the expected claim, evidence, disposition, reproduction record, traces, and open or closed discrepancy.";
    }

    requirement <'FUN-22'> 'Issue Early Design Review Status' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall issue and retain a Review Status that reflects package completeness,
         * finding dispositions, reproduction evidence, reviewer outcome, and every unresolved
         * critical finding.
         */
        require constraint statement {
            doc
            /* Review status cannot hide an open critical finding. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Review Early Design Justification Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "SC-06 terminates in a controlled status while the reviewer retains authority over the outcome.";
        specifiedFeatureIdentifier = "F-06.4 Issue Review Status";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "The published status matches the reviewer outcome and remains non-accepted whenever the package is incomplete or a critical finding remains open.";
    }

    requirement <'FUN-23'> 'Register External Engineering Artifacts' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For every designated externally produced Requirement Set, EPS Model Artifact, and Analysis
         * Result Package, the framework shall issue an Artifact Registration Record that preserves
         * the artifact and producer identifiers, producing capability, source revision, controlled
         * evidence baseline, provenance, applicable traces, acceptance status, and discrepancies.
         * Only an accepted registration may be used in a valid evidence chain.
         */
        require constraint statement {
            doc
            /* Every designated external artifact has one complete accepted or rejected registration. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "G-01 requires source-controlled external endpoints and G-03 requires explicit non-destructive rejection.";
        specifiedFeatureIdentifier = "F-01.0 Register External Engineering Artifacts";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Valid requirement, tailored-model, and analysis-result fixtures receive complete accepted registrations. Missing-source, wrong-baseline, provenance-loss, trace-loss, and undeclared-tailoring fixtures receive rejected registrations with oracle discrepancies and leave controlled content unchanged.";
    }

    // Operational control requirements derived from all six mission scenarios.
    requirement <'CTL-01'> 'Establish Controlled Context Before Operational Work' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For each selected work context, the framework shall transition from ST-01 Unconfigured to
         * ST-02 Configuring only on an accepted Case Configuration Request, and shall enter ST-03
         * Controlled Baseline Ready only when the resulting Configuration Status is ready and its
         * Controlled Case Configuration identifies an immutable baseline.
         */
        require constraint statement {
            doc
            /* Operational work begins only from an accepted controlled case baseline. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale = "The other five scenario families depend on an identified controlled context.";
        specifiedFeatureIdentifier =
            "SM-01 states ST-01 through ST-03 and transitions T-01 through T-03";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Initial, complete, incomplete, incompatible, and unapproved configuration fixtures enter exactly the states selected by T-01 through T-03, and ST-03 always resolves to the expected immutable baseline.";
    }

    requirement <'CTL-02'> 'Dispatch Verified Requests to Their Service States' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* In ST-03 Controlled Baseline Ready, the framework shall dispatch each accepted Evidence
         * Chain, Reproduction, Design Change, Candidate Comparison, and Design Review Request to
         * ST-04 through ST-08 respectively, and shall invoke F-01, F-03, F-04, F-05, or F-06 for the
         * same selected work context. A new accepted Case Configuration Request shall invoke F-02 in
         * ST-02. A rejected boundary transfer shall leave the current state unchanged.
         */
        require constraint statement {
            doc
            /* Each verified request selects exactly its declared service state and function. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "The state machine integrates the six scenario functions without changing their black-box boundaries.";
        specifiedFeatureIdentifier = "SM-01 transitions T-04 through T-09";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Each accepted request fixture enters its mapped state and invokes its mapped service for the same context, while every rejected-transfer fixture leaves state and controlled content unchanged.";
    }

    requirement <'CTL-03'> 'Return to Ready Only After an Accepted Outcome' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* From ST-04 through ST-08, the framework shall return the selected context to ST-03 only
         * when the typed terminal outcome is respectively an available Evidence Chain Assessment
         * with all external artifacts accepted and the chain valid, a successful Reproduction
         * Verdict, a correct Change Evidence Package, a
         * complete Candidate Comparison Package, or a complete Review Status with all critical
         * findings resolved.
         */
        require constraint statement {
            doc
            /* Every nominal transition satisfies its typed outcome guard. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "A ready label must never conceal an incomplete, failed, or unresolved service outcome.";
        specifiedFeatureIdentifier = "SM-01 transitions T-10, T-12, T-14, T-16, and T-18";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Boundary-value fixtures for every nominal outcome enter ST-03 exactly when all applicable guard terms are true.";
    }

    requirement <'CTL-04'> 'Enter Discrepancy State on Exceptional Outcome' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* From ST-02 and ST-04 through ST-08, the framework shall enter ST-09 Discrepancy Open when
         * configuration is non-ready, evidence is unavailable, an external artifact is rejected,
         * the evidence chain is invalid, reproduction fails, a change package is incorrect, a
         * comparison package is incomplete, or review evidence is
         * incomplete or has unresolved critical findings. The triggering status and discrepancies
         * shall remain retained and visible.
         */
        require constraint statement {
            doc
            /* Every exceptional terminal outcome produces one explicit discrepancy state. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement =
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies';
        rationale = "Every scenario defines an exceptional path whose status must remain visible.";
        specifiedFeatureIdentifier = "SM-01 transitions T-03, T-11, T-13, T-15, T-17, and T-19";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Each seeded exceptional outcome enters ST-09, retains the oracle status and discrepancies, and emits no contradictory ready or successful status.";
    }

    requirement <'CTL-05'> 'Recover Through Controlled Retry and Revalidation' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* From ST-09 Discrepancy Open, the framework shall accept only a verified corrected service
         * request or an Evidence Chain Request for controlled revalidation. Revalidation shall enter
         * ST-10 Recovering and return to ST-03 only when all required records are available, every
         * designated external artifact is accepted, and the corrected chain is valid. A deficient
         * recovery shall return to ST-09 with its residual
         * discrepancies.
         */
        require constraint statement {
            doc
            /* Recovery is explicit, controlled, and evidence gated. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "A discrepancy closes only after a corrected controlled request passes its applicable outcome guard.";
        specifiedFeatureIdentifier = "SM-01 transitions T-20 through T-27";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Corrected, unchanged, and partially corrected fixtures follow the declared retry state. The evidence recovery route reaches ST-03 only after fully valid revalidation, and each service retry remains subject to CTL-03.";
    }

    requirement <'CTL-06'> 'Preserve Baseline Identity Across Control Transitions' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Every SM-01 transition shall preserve the selected context and evidence-baseline identity,
         * together with each external artifact's producer and source revision. A successful
         * controlled change shall assign a distinct successor baseline before ST-03 is re-entered,
         * while the target baseline remains immutable and retrievable. Rejected artifacts, failed
         * work, and recovery attempts shall not overwrite either baseline or any source revision.
         */
        require constraint statement {
            doc
            /* State change never destroys or silently changes controlled baseline identity. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "Every scenario depends on stable context and baseline identity across its control transitions.";
        specifiedFeatureIdentifier = "SM-01 all states and transitions, STO-04";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Observed transition traces preserve context, evidence baseline, producer, and source revision. Accepted changes create the oracle successor identifier, and rejected-artifact or overwrite attempts leave all prior baselines and source revisions unchanged and retrievable.";
    }

    // Typed interface requirements.
    requirement <'INT-01'> 'Mission Application Interface Contract' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall exchange mission-team requests, configuration decisions, change
         * revisions, findings, assessments, controlled configurations, evidence packages, and
         * statuses only through IF-01 using their defined item types and directions.
         */
        require constraint statement {
            doc
            /* IF-01 traffic conforms to its typed directed flows. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "The mission team initiates and receives the externally observable application services.";
        specifiedFeatureIdentifier = "IF-01 Mission Application Interface";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Interface inspection and scenario tests show only the declared IF-01 item types crossing in their declared directions.";
    }

    requirement <'INT-02'> 'Research Governance Interface Contract' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall exchange case drafts, adaptation decisions, comparison protocols, raw
         * results, sensitivity and uncertainty assessments, and candidate comparison packages only
         * through IF-02 using their defined item types and directions.
         */
        require constraint statement {
            doc
            /* IF-02 traffic conforms to its typed directed flows. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "Research governance supplies adaptation and comparison decisions without entering the framework boundary.";
        specifiedFeatureIdentifier = "IF-02 Research Governance Interface";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Interface inspection and SC-02 and SC-05 tests show only declared IF-02 item types and directions.";
    }

    requirement <'INT-03'> 'Independent Review Interface Contract' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall exchange reproduction requests and results, verdicts, review packages,
         * findings, reviewer outcomes, and review status only through IF-03 using their defined item
         * types and directions.
         */
        require constraint statement {
            doc
            /* IF-03 traffic conforms to its typed directed flows. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "The reviewer needs an independent boundary for reproduction and review evidence.";
        specifiedFeatureIdentifier = "IF-03 Independent Review Interface";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Interface inspection and SC-03 and SC-06 tests show only declared IF-03 item types and directions.";
    }

    requirement <'INT-04'> 'Model Control Interface Contract' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall exchange model-control information only through IF-04 using its
         * defined item types and directions, receiving externally authored requirement sets, generic
         * and tailored EPS models, common-core and candidate records with source revisions, and
         * returning artifact registrations, accepted case configurations, and authorized revisions.
         */
        require constraint statement {
            doc
            /* IF-04 traffic conforms to its typed directed flows. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "Every service depends on controlled model identity and explicit artifact acceptance without selecting a model repository implementation.";
        specifiedFeatureIdentifier = "IF-04 Model Control Interface";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Interface inspection and six scenario tests show only declared IF-04 item types and preserve producer, source-revision, generic-model, case-configuration, and evidence-baseline identity in their declared directions.";
    }

    requirement <'INT-05'> 'Analysis Execution Interface Contract' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall submit Analysis Execution Requests and receive corresponding raw,
         * source-identified, evidence-baselined Analysis Result Packages only through IF-05 using
         * their defined item types and directions.
         */
        require constraint statement {
            doc
            /* IF-05 traffic conforms to its typed directed flows. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "A typed tool-neutral boundary isolates controlled requests from analysis implementation choices.";
        specifiedFeatureIdentifier = "IF-05 Analysis Execution Interface";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Interface inspection and SC-03 through SC-05 tests show request-result correlation, producer and source-revision identity, evidence-baseline identity, and only declared IF-05 item types and directions.";
    }

    requirement <'INT-06'> 'Evidence Custody Interface Contract' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall retrieve retained evidence and submit artifact registrations,
         * accepted assessments, configurations, results, verdicts, change packages, comparisons,
         * review packages, and statuses only through IF-06 using their defined item types and
         * directions.
         */
        require constraint statement {
            doc
            /* IF-06 traffic conforms to its typed directed flows. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "Every scenario retains evidence while leaving the repository realization open.";
        specifiedFeatureIdentifier = "IF-06 Evidence Custody Interface";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "Interface inspection and six scenario tests show only declared IF-06 items and directions, with artifact registrations, identifiers, source revisions, and evidence-baseline references preserved.";
    }

    requirement <'INT-07'> 'Verify Boundary Transfer Before Acceptance' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Before accepting any incoming boundary item, the framework shall verify source and
         * configuration identity, structural completeness, identifier and quantity compatibility,
         * units and semantic compatibility, and provenance preservation. For an externally produced
         * engineering artifact, the framework shall additionally verify producer and source-revision
         * identity, evidence-baseline identity, and preservation of applicable trace relations.
         */
        require constraint statement {
            doc
            /* Acceptance requires every transfer check to pass. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "The cited reviews identify manual and automated transfer loss, semantic mismatch, and provenance loss as integrity risks.";
        specifiedFeatureIdentifier = "Transfer Verification Record on IF-01 through IF-06";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "A transfer is accepted exactly when all declared checks pass. Engineering-artifact fixtures additionally require the oracle producer, source revision, evidence baseline, provenance, and applicable traces.";
    }

    requirement <'INT-08'> 'Preserve Controlled Content After Rejected Transfer' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* When a boundary transfer is rejected, the framework shall leave controlled content and
         * prior source revisions unchanged and issue, return, and retain a Transfer Verification
         * Record containing every detected discrepancy.
         */
        require constraint statement {
            doc
            /* Rejection is visible and non-destructive. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement =
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies';
        rationale =
            "A failed transfer must not silently corrupt or replace the controlled baseline.";
        specifiedFeatureIdentifier = "Transfer Verification Record on IF-01 through IF-06";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Each seeded rejected transfer preserves the pre-transfer baseline, controlled content, and source revisions and returns and retains a record with the oracle discrepancies.";
    }

    // Required black-box stores.
    requirement <'STO-01'> 'Retain Controlled Model and Case Records' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall cause every accepted externally authored requirement set, generic or
         * tailored EPS model, controlled model record, common-core package, case configuration,
         * Artifact Registration Record, and authorized change revision to be retained with its
         * producer, source revision, unique identifier, immutable evidence-baseline reference,
         * approval state, applicable traces, and provenance.
         */
        require constraint statement {
            doc
            /* Accepted control artifacts remain retrievable. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "Controlled model, registration, and case identity anchor traceability, explicit discrepancy status, and case reuse.";
        specifiedFeatureIdentifier =
            "requiredRecords.modelRecords, requiredRecords.artifactRegistrations, and requiredRecords.caseConfigurations";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::demo);
        acceptanceCriterion =
            "Every accepted requirement and model fixture and its registration are retrievable with the same producer, source revision, identifier, evidence baseline, approval state, traces, and provenance.";
    }

    requirement <'STO-02'> 'Retain Raw Analysis Evidence' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall cause the producer, source revision, evidence baseline, assumptions,
         * controlled inputs, runtime dependencies, raw results, execution status, declared
         * uncertainty, Artifact Registration Record, and verification evidence for every designated
         * analysis to be retained for the evaluation period.
         */
        require constraint statement {
            doc
            /* Reproduction never depends only on a derived summary. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "Raw evidence, artifact registration, declared uncertainty, and explicit discrepancy status are necessary for independent reproduction and review.";
        specifiedFeatureIdentifier = "requiredRecords.evidenceRecords";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::demo);
        acceptanceCriterion =
            "All designated analysis fixtures remain retrievable with their producer, source revision, evidence baseline, registration, raw inputs, assumptions, dependencies, outputs, status, uncertainty, and verification evidence.";
    }

    requirement <'STO-03'> 'Retain Assessments, Verdicts, and Review Records' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall cause every issued Artifact Registration Record, assessment, verdict,
         * change package, comparison package, review package, review status, transfer verification,
         * and associated discrepancy to be retained for the evaluation period.
         */
        require constraint statement {
            doc
            /* Every externally issued decision record has custody. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "Reviewability requires the preservation of favorable and unfavorable outcomes.";
        specifiedFeatureIdentifier = "requiredRecords decision and verification records";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::demo);
        acceptanceCriterion =
            "Every issued nominal or exceptional fixture record is retrievable with its linked discrepancies and status.";
    }

    requirement <'STO-04'> 'Retrieve Immutable Baseline Records' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall preserve immutable evidence-baseline and external source-revision
         * identity by retrieving required records through unique artifact, source-revision, and
         * baseline identifiers, preventing overwrite of accepted baselines and source revisions, and
         * assigning a new baseline identifier to each accepted change.
         */
        require constraint statement {
            doc
            /* Retrieval is unambiguous and baseline history is immutable. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "Change impact and reproduction require stable access to both prior and revised evidence.";
        specifiedFeatureIdentifier = "requiredRecords and Baseline Reference";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Queries return only the named artifact revision and evidence baseline, overwrite attempts fail visibly, and an accepted change creates a distinct retrievable baseline while preserving every prior source revision.";
    }

    // Acceptance and comparative MOP requirements.
    requirement <'PER-01'> 'Achieve Complete Valid Trace Coverage' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* At the evaluation verdict, the framework shall achieve 100 percent valid trace coverage
         * over all applicable relations in every evidence chain and external artifact designated by
         * the fixed Framework Evaluation Manifest. A relation is valid only when each external
         * endpoint has an accepted registration with preserved source revision and provenance.
         */
        require constraint statement {
            doc
            /* MOP-01 equals 100 percent. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains';
        rationale = "MOP-01 directly operationalizes the noncompensable G-01 acceptance rule.";
        specifiedFeatureIdentifier = "MOP-01 valid trace coverage";
        verificationMethod = (VerificationMethodKind::analyze, VerificationMethodKind::test);
        acceptanceCriterion =
            "The independently recounted valid relation count equals the applicable relation count, every external endpoint registration is accepted and resolves to its source revision and evidence baseline, and reported coverage equals 100 percent.";
    }

    requirement <'PER-02'> 'Reproduce Every Designated Reference Analysis' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* At the evaluation verdict, the framework shall achieve 100 percent reproduction success
         * across all reference analyses designated by the fixed Framework Evaluation Manifest.
         */
        require constraint statement {
            doc
            /* MOP-02 equals 100 percent. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Reproduce Analysis Scenario';
        parentMissionRequirement = FrameworkMissionRequirements::'Reproduce Reference Analyses';
        rationale = "MOP-02 directly operationalizes the noncompensable G-02 acceptance rule.";
        specifiedFeatureIdentifier = "MOP-02 reference analysis reproduction success";
        verificationMethod = (VerificationMethodKind::analyze, VerificationMethodKind::test);
        acceptanceCriterion =
            "Every designated analysis completes from its controlled baseline and every declared result conforms to its predeclared tolerance.";
    }

    requirement <'PER-03'> 'Close Every Critical Discrepancy' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* At the evaluation verdict, the framework shall have zero unresolved discrepancies that
         * meet the criticality rule fixed in the Framework Evaluation Manifest.
         */
        require constraint statement {
            doc
            /* MOP-03 equals zero. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Review Early Design Justification Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies';
        rationale = "MOP-03 directly operationalizes the noncompensable G-03 acceptance rule.";
        specifiedFeatureIdentifier = "MOP-03 open critical discrepancy count";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::analyze);
        acceptanceCriterion =
            "The independent discrepancy ledger audit finds no unresolved item classified critical at the recorded verdict time.";
    }

    requirement <'PER-04'> 'Complete Two Contrasting EPS Cases' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* At the evaluation verdict, the framework shall have completed both contrasting EPS cases
         * identified by the Framework Evaluation Manifest using the declared common core and
         * mandatory workflow and evidence outputs.
         */
        require constraint statement {
            doc
            /* MOP-04 equals two. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        rationale = "MOP-04 directly operationalizes the required case count in G-04.";
        specifiedFeatureIdentifier = "MOP-04 completed contrasting case count";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::demo);
        acceptanceCriterion =
            "Exactly the two designated contrasting cases complete the reference workflow with the common core and all mandatory evidence.";
    }

    requirement <'PER-05'> 'Eliminate Undeclared Case Adaptations' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* At the evaluation verdict, the framework shall have zero case parameters, extensions, or
         * mappings used in either contrasting case without a corresponding approved declaration.
         */
        require constraint statement {
            doc
            /* MOP-05 equals zero. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        rationale = "MOP-05 protects the common-core claim in G-04 from hidden case customization.";
        specifiedFeatureIdentifier = "MOP-05 undeclared adaptation count";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::analyze);
        acceptanceCriterion =
            "The execution-to-configuration audit finds no parameter, extension, or mapping absent from the approved case declarations.";
    }

    requirement <'PER-06'> 'Measure Correct Change Turnaround Time' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For the designated SC-04 trial, the framework shall report wall-clock hours from valid
         * request acceptance to issue of the correct reviewable package with rankability enabled
         * only when the predeclared correctness checks pass.
         */
        require constraint statement {
            doc
            /* MOP-06 follows its fixed boundary and correctness gate. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Assess Design Change Scenario';
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale = "MOP-06 measures change responsiveness without rewarding an invalid result.";
        specifiedFeatureIdentifier = "MOP-06 correct change turnaround time";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::analyze);
        acceptanceCriterion =
            "Independent timestamps reproduce the reported duration, and rankability is false unless the impact and regenerated evidence match the oracle.";
    }

    requirement <'PER-07'> 'Measure Case Adaptation Effort' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For each designated SC-02 trial, the framework shall report active participant hours from
         * case request to acceptance of a complete controlled configuration, excluding waiting and
         * unattended execution.
         */
        require constraint statement {
            doc
            /* MOP-07 follows its fixed labor boundary. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        rationale = "MOP-07 quantifies the effort needed to reuse the common core across contexts.";
        specifiedFeatureIdentifier = "MOP-07 case adaptation effort";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::analyze);
        acceptanceCriterion =
            "The activity log independently sums to the reported person-hours and includes only active effort within the declared SC-02 boundaries.";
    }

    requirement <'PER-08'> 'Measure Independent Reproduction Effort' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For each designated SC-03 trial, the framework shall report active reviewer hours from
         * receipt of a complete package to a valid reproduction verdict with rankability enabled
         * only for successful reproduction.
         */
        require constraint statement {
            doc
            /* MOP-08 follows its fixed labor and success boundaries. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Reproduce Analysis Scenario';
        parentMissionRequirement = FrameworkMissionRequirements::'Reproduce Reference Analyses';
        rationale =
            "MOP-08 measures independent usability while preserving the G-02 correctness gate.";
        specifiedFeatureIdentifier = "MOP-08 independent reproduction effort";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::analyze);
        acceptanceCriterion =
            "The reviewer activity log reproduces the reported person-hours, and rankability is true only for a successful verdict.";
    }

    requirement <'PER-09'> 'Measure Framework Adoption Effort' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For the designated adoption trial, the framework shall report active participant hours
         * from the clean declared starting environment through correct completion of the reference
         * workflow.
         */
        require constraint statement {
            doc
            /* MOP-09 follows its fixed adoption boundary. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        rationale =
            "MOP-09 exposes the adoption burden reported for resource-constrained academic missions.";
        specifiedFeatureIdentifier = "MOP-09 framework adoption effort";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::analyze);
        acceptanceCriterion =
            "The adoption activity log reproduces the reported person-hours from the declared clean start through correct reference-workflow completion.";
    }

    requirement <'PER-10'> 'Measure Direct Framework Cost' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* For the declared evaluation period, the framework shall report incremental license,
         * required service, and computing charges in Canadian dollars while excluding labor and
         * pre-existing general infrastructure.
         */
        require constraint statement {
            doc
            /* MOP-10 follows its fixed cost boundary. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        rationale =
            "MOP-10 separates direct acquisition and operation cost from human-effort measures.";
        specifiedFeatureIdentifier = "MOP-10 direct framework cost";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::analyze);
        acceptanceCriterion =
            "The controlled charge ledger independently sums to the reported CAD value and contains no excluded labor or pre-existing infrastructure cost.";
    }

    requirement <'PER-11'> 'Measure Consistency Assurance Effectiveness' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* On the blinded controlled test set, the framework shall report true positives, false
         * positives, false negatives, and the resulting percentage
         * 100(2TP)/(2TP+FP+FN), where a true positive identifies the seeded discrepancy and its
         * affected artifact.
         */
        require constraint statement {
            doc
            /* MOP-11 and its raw counts are reproducible. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies';
        rationale =
            "MOP-11 measures discrepancy exposure while penalizing missed and false findings.";
        specifiedFeatureIdentifier = "MOP-11 consistency assurance effectiveness";
        verificationMethod = (VerificationMethodKind::analyze, VerificationMethodKind::test);
        acceptanceCriterion =
            "Independent adjudication reproduces TP, FP, FN, and the reported F1 percentage from the blinded test set.";
    }

    // Cross-cutting output-quality requirements.
    requirement <'QLT-01'> 'Identify Controlled Output Provenance' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Every controlled output issued by the framework shall identify its source request,
         * producing function, applicable item and producer identifiers, external source revision,
         * controlled evidence baseline, and trace and provenance records.
         */
        require constraint statement {
            doc
            /* Every controlled output resolves to its origin. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "Provenance and baseline identity are required to review and reproduce framework outputs.";
        specifiedFeatureIdentifier = "All F-01 through F-06 controlled outputs";
        verificationMethod = VerificationMethodKind::inspect;
        acceptanceCriterion =
            "A sample from every output type resolves to one source request, producing function, item and producer identity, external source revision, evidence baseline, and provenance chain.";
    }

    requirement <'QLT-02'> 'Expose Exceptional Outcomes' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall represent every missing, unavailable, incomplete, incompatible,
         * unversioned, untraceable, failed, out-of-tolerance, rejected, or unresolved outcome with an
         * explicit status that is never valid, ready, successful, feasible, resolved, or accepted.
         */
        require constraint statement {
            doc
            /* Exceptional status cannot be hidden by a nominal label. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario',
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement =
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies';
        rationale =
            "Every scenario includes an explicit exceptional path so that discrepancies remain reviewable.";
        specifiedFeatureIdentifier = "Exceptional outputs of F-01 through F-06";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Each seeded exceptional condition produces its explicit status and discrepancy and never produces a contradictory nominal label.";
    }

    requirement <'QLT-03'> 'Preserve Decision Transparency' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Every candidate comparison and design review package shall expose the fixed criteria,
         * assumptions, raw results, feasibility or completeness status, uncertainty, discrepancies,
         * and derived result used to support the human decision.
         */
        require constraint statement {
            doc
            /* A rank, score, or review label never replaces its evidence. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Compare Candidate EPS Architectures Scenario',
            FrameworkMissionScenarios::'Review Early Design Justification Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies'
        );
        rationale =
            "The reviews call for decision-aligned, measured, uncertainty-aware evidence rather than unsupported claims.";
        specifiedFeatureIdentifier = "F-05.4 and F-06.1 output packages";
        verificationMethod = VerificationMethodKind::inspect;
        acceptanceCriterion =
            "Every sampled comparison and review package contains all listed inputs, raw and derived outputs, uncertainty, status, and discrepancies.";
    }

    requirement <'QLT-04'> 'Gate Comparative Credit on Correctness' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* The framework shall mark change turnaround, case adaptation effort, and independent
         * reproduction effort as rankable only when their corresponding change package,
         * configuration, or reproduction verdict passes its predeclared correctness condition.
         */
        require constraint statement {
            doc
            /* An incorrect fast result receives no comparative credit. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario',
            FrameworkMissionScenarios::'Assess Design Change Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale = "Time and effort values must not compensate for invalid technical outcomes.";
        specifiedFeatureIdentifier = "MOP-06, MOP-07, and MOP-08 correctness gates";
        verificationMethod = VerificationMethodKind::test;
        acceptanceCriterion =
            "Nominal and failed fixtures show rankable true exactly when the corresponding predeclared correctness condition passes.";
    }

    requirement <'QLT-05'> 'Distinguish Common Core and Case Adaptations' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Every controlled case configuration and case evidence package shall distinguish the
         * unchanged common-core and generic-model identifiers from each approved case parameter,
         * extension, and mapping. Each EPS Model Artifact shall declare its model role. Each accepted
         * tailored model shall resolve to that generic-model baseline and the applicable approved
         * case-configuration baseline.
         */
        require constraint statement {
            doc
            /* Case-specific content is explicit and attributable. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Maintain EPS Evidence Chain Scenario',
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Complete and Valid Evidence Chains',
            FrameworkMissionRequirements::'Resolve Critical Evidence Inconsistencies',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "G-01 and G-03 require a valid registered tailored-model endpoint, while the reuse claim in G-04 depends on an auditable boundary between common and case-specific content.";
        specifiedFeatureIdentifier =
            "F-01.0 registrations, F-02 outputs, and requiredRecords.caseConfigurations";
        verificationMethod = (VerificationMethodKind::inspect, VerificationMethodKind::test);
        acceptanceCriterion =
            "For both cases, every executed element is classified as the named common core or one approved adaptation, every EPS model declares the oracle role, and each tailored-model fixture resolves to the oracle generic-model and approved case-configuration baselines.";
    }

    // Externally declared realization-resource characteristics.
    requirement <'RES-01'> 'Declare Minimum Execution Environment' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* Each controlled framework baseline shall declare its minimum computing, storage, network,
         * service, license, tool, and human-procedure prerequisites without requiring a particular
         * product unless imposed by a design constraint.
         */
        require constraint statement {
            doc
            /* The minimum environment is complete and product-neutral where open. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario';
        parentMissionRequirement =
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases';
        rationale =
            "A declared environment makes adoption effort, direct cost, and case compatibility measurable.";
        specifiedFeatureIdentifier = "declared minimum execution environment";
        verificationMethod = VerificationMethodKind::inspect;
        acceptanceCriterion =
            "The baseline declaration identifies every prerequisite category, version or capacity where applicable, acquisition condition, and any intentionally open product choice.";
    }

    requirement <'RES-02'> 'Reconstruct Controlled Execution Environment' {
        subject framework : 'Specified Nanosatellite EPS Engineering Framework';
        doc
        /* From a clean starting environment, the framework shall permit reconstruction of a
         * designated evaluation baseline using only its recorded revision, declared runtime
         * dependencies, configurations, acquisition instructions, and controlled procedures.
         */
        require constraint statement {
            doc
            /* The declared baseline can be established independently. */
        }
    }
    @BlackBoxRequirementTrace {
        sourceScenario = (
            FrameworkMissionScenarios::'Configure Framework for EPS Case Scenario',
            FrameworkMissionScenarios::'Reproduce Analysis Scenario'
        );
        parentMissionRequirement = (
            FrameworkMissionRequirements::'Reproduce Reference Analyses',
            FrameworkMissionRequirements::'Complete Contrasting Evaluation Cases'
        );
        rationale =
            "Independent reconstruction is required before adoption effort or analysis reproduction can be measured.";
        specifiedFeatureIdentifier = "declared runtime dependencies";
        verificationMethod = (VerificationMethodKind::demo, VerificationMethodKind::test);
        acceptanceCriterion =
            "An independent clean-environment trial establishes the named baseline and completes the reference workflow using only declared controlled inputs.";
    }

    // Organizational hierarchy. Leaf traces are carried by BlackBoxRequirementTrace metadata.
    #refinement dependency
        'Framework Black-Box System Requirements'
        to FrameworkMissionRequirements::'Candidate Framework Eligibility';
    #refinement dependency 'Functional Requirements' to 'Framework Black-Box System Requirements';
    #refinement dependency
        'Operational Control Requirements'
        to 'Framework Black-Box System Requirements';
    #refinement dependency 'Interface Requirements' to 'Framework Black-Box System Requirements';
    #refinement dependency 'Store Requirements' to 'Framework Black-Box System Requirements';
    #refinement dependency
        'Performance and Measurement Requirements'
        to 'Framework Black-Box System Requirements';
    #refinement dependency 'Quality Requirements' to 'Framework Black-Box System Requirements';
    #refinement dependency
        'Execution Resource Requirements'
        to 'Framework Black-Box System Requirements';
    #refinement dependency 'Scope Designated Evidence Chain' to 'Functional Requirements';
    #refinement dependency 'Validate Evidence Chain' to 'Functional Requirements';
    #refinement dependency 'Issue Evidence Chain Assessment' to 'Functional Requirements';
    #refinement dependency 'Capture Case Configuration' to 'Functional Requirements';
    #refinement dependency 'Validate Case Configuration' to 'Functional Requirements';
    #refinement dependency 'Issue Controlled Case Configuration' to 'Functional Requirements';
    #refinement dependency 'Prepare Reproduction Package' to 'Functional Requirements';
    #refinement dependency 'Coordinate Controlled Analysis' to 'Functional Requirements';
    #refinement dependency 'Evaluate Reproduced Result' to 'Functional Requirements';
    #refinement dependency 'Issue Reproduction Verdict' to 'Functional Requirements';
    #refinement dependency 'Validate Design Change Request' to 'Functional Requirements';
    #refinement dependency 'Analyze Design Change Impact' to 'Functional Requirements';
    #refinement dependency 'Validate Regenerated Evidence' to 'Functional Requirements';
    #refinement dependency 'Assemble Change Evidence Package' to 'Functional Requirements';
    #refinement dependency 'Validate Candidate Comparison Basis' to 'Functional Requirements';
    #refinement dependency 'Determine Candidate EPS Feasibility' to 'Functional Requirements';
    #refinement dependency 'Compare Feasible EPS Candidates' to 'Functional Requirements';
    #refinement dependency 'Issue Candidate Comparison Package' to 'Functional Requirements';
    #refinement dependency 'Assemble Early Design Review Package' to 'Functional Requirements';
    #refinement dependency 'Coordinate Selected Review Reproduction' to 'Functional Requirements';
    #refinement dependency 'Manage Review Findings' to 'Functional Requirements';
    #refinement dependency 'Issue Early Design Review Status' to 'Functional Requirements';
    #refinement dependency 'Register External Engineering Artifacts' to 'Functional Requirements';

    #refinement dependency
        'Establish Controlled Context Before Operational Work'
        to 'Operational Control Requirements';
    #refinement dependency
        'Dispatch Verified Requests to Their Service States'
        to 'Operational Control Requirements';
    #refinement dependency
        'Return to Ready Only After an Accepted Outcome'
        to 'Operational Control Requirements';
    #refinement dependency
        'Enter Discrepancy State on Exceptional Outcome'
        to 'Operational Control Requirements';
    #refinement dependency
        'Recover Through Controlled Retry and Revalidation'
        to 'Operational Control Requirements';
    #refinement dependency
        'Preserve Baseline Identity Across Control Transitions'
        to 'Operational Control Requirements';

    #refinement dependency 'Mission Application Interface Contract' to 'Interface Requirements';
    #refinement dependency 'Research Governance Interface Contract' to 'Interface Requirements';
    #refinement dependency 'Independent Review Interface Contract' to 'Interface Requirements';
    #refinement dependency 'Model Control Interface Contract' to 'Interface Requirements';
    #refinement dependency 'Analysis Execution Interface Contract' to 'Interface Requirements';
    #refinement dependency 'Evidence Custody Interface Contract' to 'Interface Requirements';
    #refinement dependency 'Verify Boundary Transfer Before Acceptance' to 'Interface Requirements';
    #refinement dependency
        'Preserve Controlled Content After Rejected Transfer'
        to 'Interface Requirements';

    #refinement dependency 'Retain Controlled Model and Case Records' to 'Store Requirements';
    #refinement dependency 'Retain Raw Analysis Evidence' to 'Store Requirements';
    #refinement dependency
        'Retain Assessments, Verdicts, and Review Records'
        to 'Store Requirements';
    #refinement dependency 'Retrieve Immutable Baseline Records' to 'Store Requirements';

    #refinement dependency
        'Achieve Complete Valid Trace Coverage'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Reproduce Every Designated Reference Analysis'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Close Every Critical Discrepancy'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Complete Two Contrasting EPS Cases'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Eliminate Undeclared Case Adaptations'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Measure Correct Change Turnaround Time'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Measure Case Adaptation Effort'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Measure Independent Reproduction Effort'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Measure Framework Adoption Effort'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Measure Direct Framework Cost'
        to 'Performance and Measurement Requirements';
    #refinement dependency
        'Measure Consistency Assurance Effectiveness'
        to 'Performance and Measurement Requirements';

    #refinement dependency 'Identify Controlled Output Provenance' to 'Quality Requirements';
    #refinement dependency 'Expose Exceptional Outcomes' to 'Quality Requirements';
    #refinement dependency 'Preserve Decision Transparency' to 'Quality Requirements';
    #refinement dependency 'Gate Comparative Credit on Correctness' to 'Quality Requirements';
    #refinement dependency 'Distinguish Common Core and Case Adaptations' to 'Quality Requirements';

    #refinement dependency
        'Declare Minimum Execution Environment'
        to 'Execution Resource Requirements';
    #refinement dependency
        'Reconstruct Controlled Execution Environment'
        to 'Execution Resource Requirements';
} // package FrameworkSystemRequirements
