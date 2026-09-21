// OOSEM logical activity realizations and allocations for the framework services.
package FrameworkLogicalServiceScenarios {
    private import ScalarValues::Boolean;
    private import ModelingMetadata::refinement;
    private import FrameworkExchangeDefinitions::*;
    private import FrameworkBlackBoxFunctions::*;
    private import FrameworkLogicalDecomposition::*;

    doc
    /* Each activity refines one black-box service without changing its boundary item types or
     * externally observable outcome. The performer groups allocate action occurrences to the
     * logical components defined by LA-00. Interface managers mediate boundary transfers,
     * application components realize the service logic, and infrastructure components apply shared
     * transfer assurance, baseline control, workflow control, evidence retention, and measurement.
     *
     * The shared F-03.2 Coordinate Controlled Analysis action is allocated to LAP-07 Controlled
     * Analysis Coordinator in all three services that invoke it. This repartitioning avoids
     * duplicating the same logical responsibility in the reproduction, change, and evaluation
     * managers. It does not select a tool, protocol, format, deployment, or physical component.
     */

    action <'LA-SC-01'> 'Maintain EPS Evidence Chain Logical Activity' {
        in item request : 'Evidence Chain Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        out item registrations : 'Artifact Registration Set';
        out item scope : 'Evidence Chain Scope';
        out item assessment : 'Evidence Chain Assessment';
        attribute evidenceOutcomeAccepted : Boolean;
        doc
        /* Realizes F-01. Inputs and outputs retain the F-01 signature. A failed transfer,
         * unavailable record, rejected artifact, or invalid chain is routed through workflow
         * control to an explicit assessment and retained discrepancy. No path replaces the prior
         * controlled evidence baseline without acceptance.
         */

        first start;
        then 'Receive evidence-chain request through IF-01';
        action 'Receive evidence-chain request through IF-01';
        then 'Verify model and evidence transfers';
        action 'Verify model and evidence transfers';
        then 'Resolve evidence baseline and source revisions';
        action 'Resolve evidence baseline and source revisions';
        then 'Scope designated evidence chain';
        action 'Scope designated evidence chain' : 'Scope Evidence Chain';
        then 'Register external artifacts';
        action 'Register external artifacts' : 'Register External Engineering Artifacts';
        then 'Validate designated evidence chain';
        action 'Validate designated evidence chain' : 'Validate Evidence Chain';
        then decide 'Evidence outcome accepted?';
            if evidenceOutcomeAccepted then 'Authorize evidence outcome';
            if not evidenceOutcomeAccepted then 'Record evidence discrepancy';
        action 'Authorize evidence outcome';
        then 'Evidence outcome determined';
        action 'Record evidence discrepancy';
        then 'Evidence outcome determined';
        merge 'Evidence outcome determined';
        then 'Issue evidence-chain assessment';
        action 'Issue evidence-chain assessment' : 'Issue Evidence Chain Assessment';
        then 'Retain registrations and assessment';
        action 'Retain registrations and assessment';
        then 'Publish evidence assessment through IF-01';
        action 'Publish evidence assessment through IF-01';
        then done;

        bind 'Scope designated evidence chain'.request = request;
        bind 'Register external artifacts'.modelRecords = modelRecords;
        bind 'Register external artifacts'.evidenceRecords = evidenceRecords;
        bind registrations = 'Register external artifacts'.registrations;
        flow 'Scope designated evidence chain'.scope to 'Validate designated evidence chain'.scope;
        bind 'Validate designated evidence chain'.modelRecords = modelRecords;
        bind 'Validate designated evidence chain'.evidenceRecords = evidenceRecords;
        flow
            'Register external artifacts'.registrations
            to 'Validate designated evidence chain'.registrations;
        flow
            'Validate designated evidence chain'.assessment
            to 'Issue evidence-chain assessment'.assessment;
        bind assessment = 'Issue evidence-chain assessment'.issuedAssessment;
    }

    part 'LA-SC-01 Logical Performers' {
        part missionApplicationInterface : 'Mission Application Interface Manager' {
            perform
                'Maintain EPS Evidence Chain Logical Activity'
                        .'Receive evidence-chain request through IF-01';
            perform
                'Maintain EPS Evidence Chain Logical Activity'
                        .'Publish evidence assessment through IF-01';
        }
        part modelControlInterface : 'Model Control Interface Manager' {
            perform
                'Maintain EPS Evidence Chain Logical Activity'.'Verify model and evidence transfers';
        }
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager' {
            perform
                'Maintain EPS Evidence Chain Logical Activity'.'Retain registrations and assessment';
        }
        part evidenceChainManager : 'Evidence Chain Manager' {
            perform
                'Maintain EPS Evidence Chain Logical Activity'.'Scope designated evidence chain';
            perform 'Maintain EPS Evidence Chain Logical Activity'.'Register external artifacts';
            perform
                'Maintain EPS Evidence Chain Logical Activity'.'Validate designated evidence chain';
            perform
                'Maintain EPS Evidence Chain Logical Activity'.'Issue evidence-chain assessment';
        }
        part workflowControlManager : 'Workflow Control Manager' {
            perform 'Maintain EPS Evidence Chain Logical Activity'.'Authorize evidence outcome';
            perform 'Maintain EPS Evidence Chain Logical Activity'.'Record evidence discrepancy';
        }
        part transferAssuranceManager : 'Transfer Assurance Manager' {
            perform
                'Maintain EPS Evidence Chain Logical Activity'.'Verify model and evidence transfers';
        }
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager' {
            perform
                'Maintain EPS Evidence Chain Logical Activity'
                        .'Resolve evidence baseline and source revisions';
        }
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager' {
            perform
                'Maintain EPS Evidence Chain Logical Activity'.'Retain registrations and assessment';
        }
    }

    action <'LA-SC-02'> 'Configure Framework for EPS Case Logical Activity' {
        in item request : 'Case Configuration Request';
        in item commonCore : 'Common Core Package';
        in item adaptationDecision : 'Adaptation Decision';
        out item draft : 'Case Configuration Draft';
        out item configuration : 'Controlled Case Configuration';
        out item status : 'Configuration Status';
        attribute configurationAccepted : Boolean;
        doc
        /* Realizes F-02. The activity preserves the generic EPS model and common-core identity
         * supplied by the external model-control boundary. It controls the resulting case
         * configuration and approved adaptations but leaves external tailored-model production open.
         */

        first start;
        then 'Receive case-configuration request through IF-01';
        action 'Receive case-configuration request through IF-01';
        then 'Verify common-core and generic-model transfer';
        action 'Verify common-core and generic-model transfer';
        then 'Resolve common-core and generic-model baselines';
        action 'Resolve common-core and generic-model baselines';
        then 'Capture case configuration';
        action 'Capture case configuration' : 'Capture Case Configuration';
        then 'Receive adaptation decision through IF-02';
        action 'Receive adaptation decision through IF-02';
        then 'Validate case configuration';
        action 'Validate case configuration' : 'Validate Case Configuration';
        then decide 'Configuration accepted?';
            if configurationAccepted then 'Authorize controlled case configuration';
            if not configurationAccepted then 'Record configuration discrepancy';
        action 'Authorize controlled case configuration';
        then 'Configuration outcome determined';
        action 'Record configuration discrepancy';
        then 'Configuration outcome determined';
        merge 'Configuration outcome determined';
        then 'Issue configuration status';
        action 'Issue configuration status' : 'Issue Configuration Status';
        then 'Retain controlled case configuration';
        action 'Retain controlled case configuration';
        then 'Publish configuration status through IF-01';
        action 'Publish configuration status through IF-01';
        then done;

        bind 'Capture case configuration'.request = request;
        bind 'Capture case configuration'.commonCore = commonCore;
        bind draft = 'Capture case configuration'.draft;
        flow 'Capture case configuration'.draft to 'Validate case configuration'.draft;
        bind 'Validate case configuration'.adaptationDecision = adaptationDecision;
        flow 'Capture case configuration'.draft to 'Issue configuration status'.draft;
        flow 'Validate case configuration'.assessment to 'Issue configuration status'.assessment;
        bind configuration = 'Issue configuration status'.configuration;
        bind status = 'Issue configuration status'.status;
    }

    part 'LA-SC-02 Logical Performers' {
        part missionApplicationInterface : 'Mission Application Interface Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Receive case-configuration request through IF-01';
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Publish configuration status through IF-01';
        }
        part researchGovernanceInterface : 'Research Governance Interface Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Receive adaptation decision through IF-02';
        }
        part modelControlInterface : 'Model Control Interface Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Verify common-core and generic-model transfer';
        }
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Retain controlled case configuration';
        }
        part caseConfigurationManager : 'Case Configuration Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'.'Capture case configuration';
            perform
                'Configure Framework for EPS Case Logical Activity'.'Validate case configuration';
            perform
                'Configure Framework for EPS Case Logical Activity'.'Issue configuration status';
        }
        part workflowControlManager : 'Workflow Control Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Authorize controlled case configuration';
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Record configuration discrepancy';
        }
        part transferAssuranceManager : 'Transfer Assurance Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Verify common-core and generic-model transfer';
        }
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Resolve common-core and generic-model baselines';
        }
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager' {
            perform
                'Configure Framework for EPS Case Logical Activity'
                        .'Retain controlled case configuration';
        }
    }

    action <'LA-SC-03'> 'Reproduce Designated Analysis Logical Activity' {
        in item request : 'Reproduction Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        in item returnedResult : 'Analysis Result Package';
        out item executionRequest : 'Analysis Execution Request';
        out item result : 'Analysis Result Package';
        out item verdict : 'Reproduction Verdict';
        attribute reproductionSuccessful : Boolean;
        doc
        /* Realizes F-03. The review boundary receives the verdict while the analysis-execution
         * boundary carries the controlled request and correlated raw result. The shared coordinator
         * accepts neither an altered baseline nor an uncorrelated result.
         */

        first start;
        then 'Receive reproduction request through IF-03';
        action 'Receive reproduction request through IF-03';
        then 'Resolve designated baseline and tolerance';
        action 'Resolve designated baseline and tolerance';
        then 'Prepare reproduction package';
        action 'Prepare reproduction package' : 'Prepare Reproduction Package';
        then 'Verify reproduction-package transfers';
        action 'Verify reproduction-package transfers';
        then 'Submit controlled execution through IF-05';
        action 'Submit controlled execution through IF-05';
        then 'Receive correlated analysis result through IF-05';
        action 'Receive correlated analysis result through IF-05';
        then 'Coordinate controlled analysis';
        action 'Coordinate controlled analysis' : 'Coordinate Controlled Analysis';
        then 'Evaluate reproduced result';
        action 'Evaluate reproduced result' : 'Evaluate Reproduced Result';
        then decide 'Reproduction successful?';
            if reproductionSuccessful then 'Authorize reproduction verdict';
            if not reproductionSuccessful then 'Record reproduction discrepancy';
        action 'Authorize reproduction verdict';
        then 'Reproduction outcome determined';
        action 'Record reproduction discrepancy';
        then 'Reproduction outcome determined';
        merge 'Reproduction outcome determined';
        then 'Issue reproduction verdict';
        action 'Issue reproduction verdict' : 'Issue Reproduction Verdict';
        then 'Record reproduction measurement';
        action 'Record reproduction measurement';
        then 'Retain reproduction evidence';
        action 'Retain reproduction evidence';
        then 'Publish verdict through IF-03';
        action 'Publish verdict through IF-03';
        then done;

        bind 'Prepare reproduction package'.request = request;
        bind 'Prepare reproduction package'.modelRecords = modelRecords;
        bind 'Prepare reproduction package'.evidenceRecords = evidenceRecords;
        flow
            'Prepare reproduction package'.executionRequest
            to 'Coordinate controlled analysis'.preparedRequest;
        bind 'Coordinate controlled analysis'.returnedResult = returnedResult;
        flow 'Coordinate controlled analysis'.acceptedResult to 'Evaluate reproduced result'.result;
        bind 'Evaluate reproduced result'.request = request;
        flow
            'Prepare reproduction package'.packageAssessment
            to 'Evaluate reproduced result'.packageAssessment;
        flow 'Evaluate reproduced result'.assessment to 'Issue reproduction verdict'.assessment;
        bind executionRequest = 'Coordinate controlled analysis'.submittedRequest;
        bind result = 'Coordinate controlled analysis'.acceptedResult;
        bind verdict = 'Issue reproduction verdict'.verdict;
    }

    part 'LA-SC-03 Logical Performers' {
        part independentReviewInterface : 'Independent Review Interface Manager' {
            perform
                'Reproduce Designated Analysis Logical Activity'
                        .'Receive reproduction request through IF-03';
            perform
                'Reproduce Designated Analysis Logical Activity'.'Publish verdict through IF-03';
        }
        part analysisExecutionInterface : 'Analysis Execution Interface Manager' {
            perform
                'Reproduce Designated Analysis Logical Activity'
                        .'Submit controlled execution through IF-05';
            perform
                'Reproduce Designated Analysis Logical Activity'
                        .'Receive correlated analysis result through IF-05';
        }
        part analysisReproductionManager : 'Analysis Reproduction Manager' {
            perform 'Reproduce Designated Analysis Logical Activity'.'Prepare reproduction package';
            perform 'Reproduce Designated Analysis Logical Activity'.'Evaluate reproduced result';
            perform 'Reproduce Designated Analysis Logical Activity'.'Issue reproduction verdict';
        }
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator' {
            perform
                'Reproduce Designated Analysis Logical Activity'.'Coordinate controlled analysis';
        }
        part workflowControlManager : 'Workflow Control Manager' {
            perform
                'Reproduce Designated Analysis Logical Activity'.'Authorize reproduction verdict';
            perform
                'Reproduce Designated Analysis Logical Activity'.'Record reproduction discrepancy';
        }
        part transferAssuranceManager : 'Transfer Assurance Manager' {
            perform
                'Reproduce Designated Analysis Logical Activity'
                        .'Verify reproduction-package transfers';
        }
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager' {
            perform
                'Reproduce Designated Analysis Logical Activity'
                        .'Resolve designated baseline and tolerance';
        }
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager' {
            perform 'Reproduce Designated Analysis Logical Activity'.'Retain reproduction evidence';
        }
        part evaluationMeasurementManager : 'Evaluation Measurement Manager' {
            perform
                'Reproduce Designated Analysis Logical Activity'.'Record reproduction measurement';
        }
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager' {
            perform 'Reproduce Designated Analysis Logical Activity'.'Retain reproduction evidence';
        }
    }

    action <'LA-SC-04'> 'Assess Controlled Design Change Logical Activity' {
        in item request : 'Design Change Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        in item revisions : 'Change Revision Package';
        in item returnedResult : 'Analysis Result Package';
        out item executionRequest : 'Analysis Execution Request';
        out item impact : 'Change Impact Assessment';
        out item evidencePackage : 'Change Evidence Package';
        attribute changeCorrect : Boolean;
        doc
        /* Realizes F-04. The target remains immutable. A passing outcome identifies a distinct
         * successor baseline. A failed assessment retains the impact, status, and discrepancies
         * without registering a replacement source revision.
         */

        first start;
        then 'Receive change request and revisions through IF-01';
        action 'Receive change request and revisions through IF-01';
        then 'Verify controlled change transfers';
        action 'Verify controlled change transfers';
        then 'Resolve immutable target baseline';
        action 'Resolve immutable target baseline';
        then 'Validate change request';
        action 'Validate change request' : 'Validate Change Request';
        then 'Analyze change impact';
        action 'Analyze change impact' : 'Analyze Change Impact';
        then 'Submit affected execution through IF-05';
        action 'Submit affected execution through IF-05';
        then 'Receive affected analysis result through IF-05';
        action 'Receive affected analysis result through IF-05';
        then 'Coordinate controlled analysis';
        action 'Coordinate controlled analysis' : 'Coordinate Controlled Analysis';
        then 'Validate regenerated evidence';
        action 'Validate regenerated evidence' : 'Validate Regenerated Evidence';
        then decide 'Change correct?';
            if changeCorrect then 'Authorize successor baseline';
            if not changeCorrect then 'Record unresolved change discrepancy';
        action 'Authorize successor baseline';
        then 'Change outcome determined';
        action 'Record unresolved change discrepancy';
        then 'Change outcome determined';
        merge 'Change outcome determined';
        then 'Assemble change evidence package';
        action 'Assemble change evidence package' : 'Assemble Change Evidence Package';
        then 'Register accepted revision through IF-04';
        action 'Register accepted revision through IF-04';
        then 'Record change measurement';
        action 'Record change measurement';
        then 'Retain change evidence';
        action 'Retain change evidence';
        then 'Publish change outcome through IF-01';
        action 'Publish change outcome through IF-01';
        then done;

        bind 'Validate change request'.request = request;
        bind 'Analyze change impact'.request = request;
        bind 'Analyze change impact'.modelRecords = modelRecords;
        bind 'Analyze change impact'.evidenceRecords = evidenceRecords;
        flow
            'Analyze change impact'.executionRequest
            to 'Coordinate controlled analysis'.preparedRequest;
        bind 'Coordinate controlled analysis'.returnedResult = returnedResult;
        flow 'Analyze change impact'.impact to 'Validate regenerated evidence'.impact;
        bind 'Validate regenerated evidence'.revisions = revisions;
        flow
            'Coordinate controlled analysis'.acceptedResult
            to 'Validate regenerated evidence'.result;
        flow 'Analyze change impact'.impact to 'Assemble change evidence package'.impact;
        flow
            'Validate change request'.assessment
            to 'Assemble change evidence package'.requestAssessment;
        bind 'Assemble change evidence package'.revisions = revisions;
        flow
            'Coordinate controlled analysis'.acceptedResult
            to 'Assemble change evidence package'.result;
        flow
            'Validate regenerated evidence'.assessment
            to 'Assemble change evidence package'.chainAssessment;
        bind executionRequest = 'Coordinate controlled analysis'.submittedRequest;
        bind impact = 'Analyze change impact'.impact;
        bind evidencePackage = 'Assemble change evidence package'.evidencePackage;
    }

    part 'LA-SC-04 Logical Performers' {
        part missionApplicationInterface : 'Mission Application Interface Manager' {
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Receive change request and revisions through IF-01';
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Publish change outcome through IF-01';
        }
        part modelControlInterface : 'Model Control Interface Manager' {
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Register accepted revision through IF-04';
        }
        part analysisExecutionInterface : 'Analysis Execution Interface Manager' {
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Submit affected execution through IF-05';
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Receive affected analysis result through IF-05';
        }
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager' {
            perform 'Assess Controlled Design Change Logical Activity'.'Retain change evidence';
        }
        part designChangeAssessmentManager : 'Design Change Assessment Manager' {
            perform 'Assess Controlled Design Change Logical Activity'.'Validate change request';
            perform 'Assess Controlled Design Change Logical Activity'.'Analyze change impact';
            perform
                'Assess Controlled Design Change Logical Activity'.'Validate regenerated evidence';
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Assemble change evidence package';
        }
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator' {
            perform
                'Assess Controlled Design Change Logical Activity'.'Coordinate controlled analysis';
        }
        part workflowControlManager : 'Workflow Control Manager' {
            perform
                'Assess Controlled Design Change Logical Activity'.'Authorize successor baseline';
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Record unresolved change discrepancy';
        }
        part transferAssuranceManager : 'Transfer Assurance Manager' {
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Verify controlled change transfers';
        }
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager' {
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Resolve immutable target baseline';
            perform
                'Assess Controlled Design Change Logical Activity'.'Authorize successor baseline';
            perform
                'Assess Controlled Design Change Logical Activity'
                        .'Register accepted revision through IF-04';
        }
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager' {
            perform 'Assess Controlled Design Change Logical Activity'.'Retain change evidence';
        }
        part evaluationMeasurementManager : 'Evaluation Measurement Manager' {
            perform 'Assess Controlled Design Change Logical Activity'.'Record change measurement';
        }
    }

    action <'LA-SC-05'> 'Compare Candidate EPS Architectures Logical Activity' {
        in item request : 'Candidate Comparison Request';
        in item protocol : 'Comparison Protocol';
        in item candidates : 'Candidate Model Package';
        in item returnedResults : 'Analysis Result Package';
        in item sensitivityAndUncertainty : 'Sensitivity and Uncertainty Assessment';
        out item executionRequest : 'Analysis Execution Request';
        out item result : 'Analysis Result Package';
        out item comparisonPackage : 'Candidate Comparison Package';
        attribute comparisonBasisAccepted : Boolean;
        doc
        /* Realizes F-05. The logical activity retains the declared common comparison basis,
         * feasibility gate, raw results, Pareto relations, score, sensitivity, uncertainty, and
         * discrepancies. It does not choose an EPS candidate or an analysis product.
         */

        first start;
        then 'Receive candidate-comparison request through IF-01';
        action 'Receive candidate-comparison request through IF-01';
        then 'Receive comparison protocol through IF-02';
        action 'Receive comparison protocol through IF-02';
        then 'Verify candidate-model transfers';
        action 'Verify candidate-model transfers';
        then 'Resolve candidate and comparison baselines';
        action 'Resolve candidate and comparison baselines';
        then 'Validate comparison basis';
        action 'Validate comparison basis' : 'Validate Comparison Basis';
        then decide 'Comparison basis accepted?';
            if comparisonBasisAccepted then 'Submit common execution through IF-05';
            if not comparisonBasisAccepted then 'Record comparison-basis discrepancy';
        action 'Submit common execution through IF-05';
        then 'Receive candidate results through IF-05';
        action 'Receive candidate results through IF-05';
        then 'Coordinate controlled analysis';
        action 'Coordinate controlled analysis' : 'Coordinate Controlled Analysis';
        then 'Determine candidate feasibility';
        action 'Determine candidate feasibility' : 'Determine Candidate Feasibility';
        then 'Compare feasible candidates';
        action 'Compare feasible candidates' : 'Compare Candidate Architectures';
        then 'Receive sensitivity and uncertainty through IF-02';
        action 'Receive sensitivity and uncertainty through IF-02';
        then 'Comparison outcome determined';
        action 'Record comparison-basis discrepancy';
        then 'Comparison outcome determined';
        merge 'Comparison outcome determined';
        then 'Issue candidate comparison';
        action 'Issue candidate comparison' : 'Issue Candidate Comparison';
        then 'Record comparison measurement';
        action 'Record comparison measurement';
        then 'Retain candidate comparison';
        action 'Retain candidate comparison';
        then 'Publish candidate comparison through IF-01';
        action 'Publish candidate comparison through IF-01';
        then done;

        bind 'Validate comparison basis'.request = request;
        bind 'Validate comparison basis'.protocol = protocol;
        bind 'Validate comparison basis'.candidates = candidates;
        flow
            'Validate comparison basis'.executionRequest
            to 'Coordinate controlled analysis'.preparedRequest;
        bind 'Coordinate controlled analysis'.returnedResult = returnedResults;
        bind 'Determine candidate feasibility'.protocol = protocol;
        flow
            'Coordinate controlled analysis'.acceptedResult
            to 'Determine candidate feasibility'.results;
        bind 'Compare feasible candidates'.protocol = protocol;
        flow
            'Coordinate controlled analysis'.acceptedResult
            to 'Compare feasible candidates'.results;
        flow
            'Determine candidate feasibility'.feasibility
            to 'Compare feasible candidates'.feasibility;
        flow 'Validate comparison basis'.assessment to 'Issue candidate comparison'.basisAssessment;
        bind 'Issue candidate comparison'.protocol = protocol;
        flow
            'Coordinate controlled analysis'.acceptedResult to 'Issue candidate comparison'.results;
        flow
            'Determine candidate feasibility'.feasibility
            to 'Issue candidate comparison'.feasibility;
        flow 'Compare feasible candidates'.comparison to 'Issue candidate comparison'.comparison;
        bind 'Issue candidate comparison'.sensitivityAndUncertainty = sensitivityAndUncertainty;
        bind executionRequest = 'Coordinate controlled analysis'.submittedRequest;
        bind result = 'Coordinate controlled analysis'.acceptedResult;
        bind comparisonPackage = 'Issue candidate comparison'.comparisonPackage;
    }

    part 'LA-SC-05 Logical Performers' {
        part missionApplicationInterface : 'Mission Application Interface Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Receive candidate-comparison request through IF-01';
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Publish candidate comparison through IF-01';
        }
        part researchGovernanceInterface : 'Research Governance Interface Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Receive comparison protocol through IF-02';
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Receive sensitivity and uncertainty through IF-02';
        }
        part modelControlInterface : 'Model Control Interface Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Verify candidate-model transfers';
        }
        part analysisExecutionInterface : 'Analysis Execution Interface Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Submit common execution through IF-05';
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Receive candidate results through IF-05';
        }
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'.'Retain candidate comparison';
        }
        part candidateEvaluationManager : 'Candidate Evaluation Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'.'Validate comparison basis';
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Determine candidate feasibility';
            perform
                'Compare Candidate EPS Architectures Logical Activity'.'Compare feasible candidates';
            perform
                'Compare Candidate EPS Architectures Logical Activity'.'Issue candidate comparison';
        }
        part controlledAnalysisCoordinator : 'Controlled Analysis Coordinator' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Coordinate controlled analysis';
        }
        part workflowControlManager : 'Workflow Control Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Record comparison-basis discrepancy';
        }
        part transferAssuranceManager : 'Transfer Assurance Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Verify candidate-model transfers';
        }
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Resolve candidate and comparison baselines';
        }
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'.'Retain candidate comparison';
        }
        part evaluationMeasurementManager : 'Evaluation Measurement Manager' {
            perform
                'Compare Candidate EPS Architectures Logical Activity'
                        .'Record comparison measurement';
        }
    }

    action <'LA-SC-06'> 'Review Early Design Justification Logical Activity' {
        in item request : 'Design Review Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        in item findings : 'Review Findings';
        in item disposition : 'Finding Disposition';
        in item outcome : 'Review Outcome';
        out item reviewPackage : 'Review Package';
        out item issuedFindings : 'Review Findings';
        out item reproduction : 'Reproduction Verdict';
        out item status : 'Review Status';
        attribute reviewAccepted : Boolean;
        doc
        /* Realizes F-06. The reviewer retains outcome authority. Selected reproduction invokes the
         * common controlled-reproduction capability through the review and analysis-execution
         * boundaries. Incomplete packages and unresolved critical findings remain explicit.
         */

        first start;
        then 'Receive review request through IF-01';
        action 'Receive review request through IF-01';
        then 'Verify review-package transfers';
        action 'Verify review-package transfers';
        then 'Resolve review baseline and evidence';
        action 'Resolve review baseline and evidence';
        then 'Assemble review package';
        action 'Assemble review package' : 'Assemble Review Package';
        then 'Publish review package through IF-03';
        action 'Publish review package through IF-03';
        then 'Coordinate selected reproduction';
        action 'Coordinate selected reproduction' : 'Coordinate Selected Reproduction';
        then 'Invoke common reproduction protocol';
        action 'Invoke common reproduction protocol';
        then 'Receive reviewer findings through IF-03';
        action 'Receive reviewer findings through IF-03';
        then 'Manage review findings';
        action 'Manage review findings' : 'Manage Review Findings';
        then 'Receive finding disposition through IF-01';
        action 'Receive finding disposition through IF-01';
        then decide 'Review accepted?';
            if reviewAccepted then 'Authorize review outcome';
            if not reviewAccepted then 'Record review discrepancy';
        action 'Authorize review outcome';
        then 'Review outcome determined';
        action 'Record review discrepancy';
        then 'Review outcome determined';
        merge 'Review outcome determined';
        then 'Issue review status';
        action 'Issue review status' : 'Issue Review Status';
        then 'Retain review package and status';
        action 'Retain review package and status';
        then 'Publish review status through IF-03';
        action 'Publish review status through IF-03';
        then done;

        bind 'Assemble review package'.request = request;
        bind 'Assemble review package'.modelRecords = modelRecords;
        bind 'Assemble review package'.evidenceRecords = evidenceRecords;
        flow
            'Assemble review package'.reviewPackage
            to 'Coordinate selected reproduction'.reviewPackage;
        bind 'Manage review findings'.findings = findings;
        bind 'Manage review findings'.disposition = disposition;
        flow 'Coordinate selected reproduction'.verdict to 'Manage review findings'.reproduction;
        flow 'Assemble review package'.assessment to 'Issue review status'.packageAssessment;
        flow 'Manage review findings'.linkedFindings to 'Issue review status'.linkedFindings;
        bind 'Issue review status'.outcome = outcome;
        bind reviewPackage = 'Assemble review package'.reviewPackage;
        bind issuedFindings = findings;
        bind reproduction = 'Coordinate selected reproduction'.verdict;
        bind status = 'Issue review status'.status;
    }

    part 'LA-SC-06 Logical Performers' {
        part missionApplicationInterface : 'Mission Application Interface Manager' {
            perform
                'Review Early Design Justification Logical Activity'
                        .'Receive review request through IF-01';
            perform
                'Review Early Design Justification Logical Activity'
                        .'Receive finding disposition through IF-01';
        }
        part independentReviewInterface : 'Independent Review Interface Manager' {
            perform
                'Review Early Design Justification Logical Activity'
                        .'Publish review package through IF-03';
            perform
                'Review Early Design Justification Logical Activity'
                        .'Receive reviewer findings through IF-03';
            perform
                'Review Early Design Justification Logical Activity'
                        .'Publish review status through IF-03';
        }
        part analysisExecutionInterface : 'Analysis Execution Interface Manager' {
            perform
                'Review Early Design Justification Logical Activity'
                        .'Invoke common reproduction protocol';
        }
        part evidenceCustodyInterface : 'Evidence Custody Interface Manager' {
            perform
                'Review Early Design Justification Logical Activity'
                        .'Retain review package and status';
        }
        part designReviewManager : 'Design Review Manager' {
            perform 'Review Early Design Justification Logical Activity'.'Assemble review package';
            perform
                'Review Early Design Justification Logical Activity'
                        .'Coordinate selected reproduction';
            perform 'Review Early Design Justification Logical Activity'.'Manage review findings';
            perform 'Review Early Design Justification Logical Activity'.'Issue review status';
        }
        part analysisReproductionManager : 'Analysis Reproduction Manager' {
            perform
                'Review Early Design Justification Logical Activity'
                        .'Invoke common reproduction protocol';
        }
        part workflowControlManager : 'Workflow Control Manager' {
            perform 'Review Early Design Justification Logical Activity'.'Authorize review outcome';
            perform
                'Review Early Design Justification Logical Activity'.'Record review discrepancy';
        }
        part transferAssuranceManager : 'Transfer Assurance Manager' {
            perform
                'Review Early Design Justification Logical Activity'
                        .'Verify review-package transfers';
        }
        part baselineAndConfigurationManager : 'Baseline and Configuration Manager' {
            perform
                'Review Early Design Justification Logical Activity'
                        .'Resolve review baseline and evidence';
        }
        part evidenceAndProvenanceManager : 'Evidence and Provenance Manager' {
            perform
                'Review Early Design Justification Logical Activity'
                        .'Retain review package and status';
        }
    }

    #refinement dependency
        'Maintain EPS Evidence Chain Logical Activity'
        to 'Maintain Evidence Chain';
    #refinement dependency
        'Configure Framework for EPS Case Logical Activity'
        to 'Configure Framework for EPS Case';
    #refinement dependency
        'Reproduce Designated Analysis Logical Activity'
        to 'Reproduce Designated Analysis';
    #refinement dependency
        'Assess Controlled Design Change Logical Activity'
        to 'Assess Controlled Design Change';
    #refinement dependency
        'Compare Candidate EPS Architectures Logical Activity'
        to 'Compare Candidate EPS Architectures';
    #refinement dependency
        'Review Early Design Justification Logical Activity'
        to 'Support Early Design Review';
} // package FrameworkLogicalServiceScenarios
