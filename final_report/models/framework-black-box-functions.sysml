// Black-box functions and typed exchanges derived from the mission scenarios.
package FrameworkExchangeDefinitions {
    private import ScalarValues::Boolean;
    private import ScalarValues::String;

    doc
    /* These item definitions type information crossing the framework boundary. Aggregate packages
     * expose required content without selecting a repository format, transfer mechanism, or tool.
     */

    item def 'Baseline Reference' {
        attribute identifier : String;
        attribute revision : String;
    }

    item def 'Requirement Set';
    item def 'Interface Set';
    item def 'Assumption Set';
    item def 'Workflow Definition';
    item def 'Analysis Input Package';

    item def 'Analysis Result Package' {
        doc
        /* Raw results, execution status, and declared uncertainty from a controlled execution. */
    }

    item def 'Discrepancy Set';
    item def 'Verification Evidence';
    item def 'Trace and Provenance Records';

    item def 'Controlled Model Records' {
        item requirements : 'Requirement Set';
        item interfaces : 'Interface Set';
        item configuration : 'Baseline Reference';
        item traces : 'Trace and Provenance Records';
    }

    item def 'Retained Evidence Records' {
        item assumptions : 'Assumption Set';
        item analysisInputs : 'Analysis Input Package';
        item analysisResults : 'Analysis Result Package';
        item discrepancies : 'Discrepancy Set';
        item 'verification' : 'Verification Evidence';
        item traces : 'Trace and Provenance Records';
    }

    item def 'Evidence Chain Request' {
        item baseline : 'Baseline Reference';
        attribute designatedItem : String;
    }

    item def 'Evidence Chain Scope' {
        item request : 'Evidence Chain Request';
        item affectedTraces : 'Trace and Provenance Records';
    }

    item def 'Evidence Chain Assessment' {
        attribute recordsAvailable : Boolean;
        attribute chainValid : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Case Configuration Request' {
        attribute caseIdentifier : String;
        attribute intendedAnalyses : String;
        attribute startingEnvironment : String;
    }

    item def 'Common Core Package' {
        item baseline : 'Baseline Reference';
        item workflow : 'Workflow Definition';
        attribute minimumEnvironment : String;
    }

    item def 'Adaptation Decision' {
        attribute accepted : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Case Configuration Draft' {
        attribute environment : String;
        attribute directCostBasis : String;
        attribute parameters : String;
        attribute extensions : String;
        attribute mappings : String;
        item assumptions : 'Assumption Set';
    }

    item def 'Case Configuration Assessment' {
        attribute complete : Boolean;
        attribute compatible : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Controlled Case Configuration' {
        item baseline : 'Baseline Reference';
        item configuration : 'Case Configuration Draft';
    }

    item def 'Configuration Status' {
        attribute ready : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Reproduction Request' {
        item baseline : 'Baseline Reference';
        attribute designatedAnalysis : String;
        attribute reportedResult : String;
        attribute declaredTolerance : String;
    }

    item def 'Reproduction Package Assessment' {
        attribute complete : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Analysis Execution Request' {
        item baseline : 'Baseline Reference';
        item inputs : 'Analysis Input Package';
        item assumptions : 'Assumption Set';
        attribute designatedAnalysis : String;
    }

    item def 'Reproduction Assessment' {
        attribute executionCompleted : Boolean;
        attribute withinDeclaredTolerance : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Reproduction Verdict' {
        attribute successful : Boolean;
        item evidence : 'Verification Evidence';
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Design Change Request' {
        item targetBaseline : 'Baseline Reference';
        attribute proposedChange : String;
    }

    item def 'Change Request Assessment' {
        attribute targetBaselineAvailable : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Change Impact Assessment' {
        item affectedRequirements : 'Requirement Set';
        item affectedInterfaces : 'Interface Set';
        item affectedAssumptions : 'Assumption Set';
        attribute affectedAnalyses : String;
        item affectedVerification : 'Verification Evidence';
        item coverageGaps : 'Discrepancy Set';
    }

    item def 'Change Revision Package' {
        item targetBaseline : 'Baseline Reference';
        attribute authorized : Boolean;
        item revisedModel : 'Controlled Model Records';
        item revisedAssumptions : 'Assumption Set';
    }

    item def 'Change Evidence Package' {
        attribute correct : Boolean;
        item requestAssessment : 'Change Request Assessment';
        item revision : 'Change Revision Package';
        item impact : 'Change Impact Assessment';
        item results : 'Analysis Result Package';
        item chainAssessment : 'Evidence Chain Assessment';
        item 'verification' : 'Verification Evidence';
        item discrepancies : 'Discrepancy Set';
        doc
        /* Correct is true only when the request is assessable, the authorized revision has a new
         * baseline identity, and every affected result, verification item, trace, and discrepancy
         * passes its predeclared check.
         */
    }

    item def 'Candidate Comparison Request' {
        attribute decision : String;
        attribute candidateIdentifiers : String;
    }

    item def 'Comparison Protocol' {
        attribute commonScenarios : String;
        attribute measures : String;
        attribute constraints : String;
        attribute scoringRule : String;
    }

    item def 'Candidate Model Package' {
        item models : 'Controlled Model Records';
        attribute candidateIdentifiers : String;
    }

    item def 'Comparison Basis Assessment' {
        attribute compatible : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Candidate Feasibility Assessment' {
        attribute candidateStatus : String;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Candidate Comparison Assessment' {
        attribute paretoRelations : String;
        attribute declaredScores : String;
    }

    item def 'Sensitivity and Uncertainty Assessment' {
        attribute sensitivity : String;
        attribute uncertainty : String;
    }

    item def 'Candidate Comparison Package' {
        attribute complete : Boolean;
        item basisAssessment : 'Comparison Basis Assessment';
        item protocol : 'Comparison Protocol';
        item rawResults : 'Analysis Result Package';
        item feasibility : 'Candidate Feasibility Assessment';
        item comparison : 'Candidate Comparison Assessment';
        item sensitivityAndUncertainty : 'Sensitivity and Uncertainty Assessment';
        item discrepancies : 'Discrepancy Set';
        doc
        /* Complete is true only when the common basis is compatible, all requested candidate
         * analyses complete, and every mandatory package element is present.
         */
    }

    item def 'Design Review Request' {
        item baseline : 'Baseline Reference';
        attribute claims : String;
        attribute reviewerIdentifier : String;
    }

    item def 'Review Package Assessment' {
        attribute complete : Boolean;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Review Package' {
        item request : 'Design Review Request';
        item model : 'Controlled Model Records';
        item evidence : 'Retained Evidence Records';
        item assessment : 'Review Package Assessment';
    }

    item def 'Review Findings' {
        attribute findings : String;
        item discrepancies : 'Discrepancy Set';
    }

    item def 'Finding Disposition' {
        attribute dispositions : String;
        item revisedEvidence : 'Retained Evidence Records';
    }

    item def 'Linked Finding Set' {
        item findings : 'Review Findings';
        item dispositions : 'Finding Disposition';
        item reproduction : 'Reproduction Verdict';
        item traces : 'Trace and Provenance Records';
    }

    item def 'Review Outcome' {
        attribute criticalFindingsResolved : Boolean;
        attribute outcome : String;
    }

    item def 'Review Status' {
        attribute packageComplete : Boolean;
        item reviewOutcome : 'Review Outcome';
        item discrepancies : 'Discrepancy Set';
        doc
        /* Package complete restates the review-package completeness verdict at the terminal
         * boundary. Critical-finding resolution remains controlled by the reviewer outcome.
         */
    }
} // package FrameworkExchangeDefinitions

package FrameworkBlackBoxFunctions {
    private import FrameworkExchangeDefinitions::*;

    doc
    /* The six service functions correspond to the enterprise use cases. Their nested functions are
     * reusable black-box behaviors typed onto the framework actions in the mission scenarios. The
     * model defines observable inputs and outputs only. It does not select internal components.
     */

    action def <'F-01.1'> 'Scope Evidence Chain' {
        in item request : 'Evidence Chain Request';
        out item scope : 'Evidence Chain Scope';
    }

    action def <'F-01.2'> 'Validate Evidence Chain' {
        in item scope : 'Evidence Chain Scope';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        out item assessment : 'Evidence Chain Assessment';
    }

    action def <'F-01.3'> 'Issue Evidence Chain Assessment' {
        in item assessment : 'Evidence Chain Assessment';
        out item issuedAssessment : 'Evidence Chain Assessment';
    }

    action def <'F-01'> 'Maintain Evidence Chain' {
        in item request : 'Evidence Chain Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        out item scope : 'Evidence Chain Scope';
        out item assessment : 'Evidence Chain Assessment';

        action scopeEvidenceChain : 'Scope Evidence Chain';
        action validateEvidenceChain : 'Validate Evidence Chain';
        action issueAssessment : 'Issue Evidence Chain Assessment';

        bind scopeEvidenceChain.request = request;
        bind scope = scopeEvidenceChain.scope;
        flow scopeEvidenceChain.scope to validateEvidenceChain.scope;
        bind validateEvidenceChain.modelRecords = modelRecords;
        bind validateEvidenceChain.evidenceRecords = evidenceRecords;
        flow validateEvidenceChain.assessment to issueAssessment.assessment;
        bind assessment = issueAssessment.issuedAssessment;
    }

    action def <'F-02.1'> 'Capture Case Configuration' {
        in item request : 'Case Configuration Request';
        in item commonCore : 'Common Core Package';
        out item draft : 'Case Configuration Draft';
    }

    action def <'F-02.2'> 'Validate Case Configuration' {
        in item draft : 'Case Configuration Draft';
        in item adaptationDecision : 'Adaptation Decision';
        out item assessment : 'Case Configuration Assessment';
    }

    action def <'F-02.3'> 'Issue Configuration Status' {
        in item draft : 'Case Configuration Draft';
        in item assessment : 'Case Configuration Assessment';
        out item configuration : 'Controlled Case Configuration';
        out item status : 'Configuration Status';
    }

    action def <'F-02'> 'Configure Framework for EPS Case' {
        in item request : 'Case Configuration Request';
        in item commonCore : 'Common Core Package';
        in item adaptationDecision : 'Adaptation Decision';
        out item draft : 'Case Configuration Draft';
        out item configuration : 'Controlled Case Configuration';
        out item status : 'Configuration Status';

        action captureConfiguration : 'Capture Case Configuration';
        action validateConfiguration : 'Validate Case Configuration';
        action issueStatus : 'Issue Configuration Status';

        bind captureConfiguration.request = request;
        bind captureConfiguration.commonCore = commonCore;
        flow captureConfiguration.draft to validateConfiguration.draft;
        bind draft = captureConfiguration.draft;
        bind validateConfiguration.adaptationDecision = adaptationDecision;
        flow captureConfiguration.draft to issueStatus.draft;
        flow validateConfiguration.assessment to issueStatus.assessment;
        bind configuration = issueStatus.configuration;
        bind status = issueStatus.status;
    }

    action def <'F-03.1'> 'Prepare Reproduction Package' {
        in item request : 'Reproduction Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        out item packageAssessment : 'Reproduction Package Assessment';
        out item executionRequest : 'Analysis Execution Request';
    }

    action def <'F-03.2'> 'Coordinate Controlled Analysis' {
        in item preparedRequest : 'Analysis Execution Request';
        in item returnedResult : 'Analysis Result Package';
        out item submittedRequest : 'Analysis Execution Request';
        out item acceptedResult : 'Analysis Result Package';
    }

    action def <'F-03.3'> 'Evaluate Reproduced Result' {
        in item request : 'Reproduction Request';
        in item packageAssessment : 'Reproduction Package Assessment';
        in item result : 'Analysis Result Package';
        out item assessment : 'Reproduction Assessment';
    }

    action def <'F-03.4'> 'Issue Reproduction Verdict' {
        in item assessment : 'Reproduction Assessment';
        out item verdict : 'Reproduction Verdict';
    }

    action def <'F-03'> 'Reproduce Designated Analysis' {
        in item request : 'Reproduction Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        in item returnedResult : 'Analysis Result Package';
        out item executionRequest : 'Analysis Execution Request';
        out item result : 'Analysis Result Package';
        out item verdict : 'Reproduction Verdict';

        action preparePackage : 'Prepare Reproduction Package';
        action coordinateAnalysis : 'Coordinate Controlled Analysis';
        action evaluateResult : 'Evaluate Reproduced Result';
        action issueVerdict : 'Issue Reproduction Verdict';

        bind preparePackage.request = request;
        bind preparePackage.modelRecords = modelRecords;
        bind preparePackage.evidenceRecords = evidenceRecords;
        flow preparePackage.executionRequest to coordinateAnalysis.preparedRequest;
        bind coordinateAnalysis.returnedResult = returnedResult;
        flow coordinateAnalysis.acceptedResult to evaluateResult.result;
        bind evaluateResult.request = request;
        flow preparePackage.packageAssessment to evaluateResult.packageAssessment;
        flow evaluateResult.assessment to issueVerdict.assessment;
        bind executionRequest = coordinateAnalysis.submittedRequest;
        bind result = coordinateAnalysis.acceptedResult;
        bind verdict = issueVerdict.verdict;
    }

    action def <'F-04.1'> 'Validate Change Request' {
        in item request : 'Design Change Request';
        out item assessment : 'Change Request Assessment';
    }

    action def <'F-04.2'> 'Analyze Change Impact' {
        in item request : 'Design Change Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        out item impact : 'Change Impact Assessment';
        out item executionRequest : 'Analysis Execution Request';
    }

    action def <'F-04.3'> 'Validate Regenerated Evidence' {
        in item impact : 'Change Impact Assessment';
        in item revisions : 'Change Revision Package';
        in item result : 'Analysis Result Package';
        out item assessment : 'Evidence Chain Assessment';
    }

    action def <'F-04.4'> 'Assemble Change Evidence Package' {
        in item requestAssessment : 'Change Request Assessment';
        in item impact : 'Change Impact Assessment';
        in item revisions : 'Change Revision Package';
        in item result : 'Analysis Result Package';
        in item chainAssessment : 'Evidence Chain Assessment';
        out item evidencePackage : 'Change Evidence Package';
    }

    action def <'F-04'> 'Assess Controlled Design Change' {
        in item request : 'Design Change Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        in item revisions : 'Change Revision Package';
        in item returnedResult : 'Analysis Result Package';
        out item executionRequest : 'Analysis Execution Request';
        out item impact : 'Change Impact Assessment';
        out item evidencePackage : 'Change Evidence Package';

        action validateRequest : 'Validate Change Request';
        action analyzeImpact : 'Analyze Change Impact';
        action coordinateAnalysis : 'Coordinate Controlled Analysis';
        action validateEvidence : 'Validate Regenerated Evidence';
        action assembleEvidence : 'Assemble Change Evidence Package';

        bind validateRequest.request = request;
        bind analyzeImpact.request = request;
        bind analyzeImpact.modelRecords = modelRecords;
        bind analyzeImpact.evidenceRecords = evidenceRecords;
        flow analyzeImpact.executionRequest to coordinateAnalysis.preparedRequest;
        bind coordinateAnalysis.returnedResult = returnedResult;
        flow analyzeImpact.impact to validateEvidence.impact;
        bind validateEvidence.revisions = revisions;
        flow coordinateAnalysis.acceptedResult to validateEvidence.result;
        flow analyzeImpact.impact to assembleEvidence.impact;
        flow validateRequest.assessment to assembleEvidence.requestAssessment;
        bind assembleEvidence.revisions = revisions;
        flow coordinateAnalysis.acceptedResult to assembleEvidence.result;
        flow validateEvidence.assessment to assembleEvidence.chainAssessment;
        bind executionRequest = coordinateAnalysis.submittedRequest;
        bind impact = analyzeImpact.impact;
        bind evidencePackage = assembleEvidence.evidencePackage;
    }

    action def <'F-05.1'> 'Validate Comparison Basis' {
        in item request : 'Candidate Comparison Request';
        in item protocol : 'Comparison Protocol';
        in item candidates : 'Candidate Model Package';
        out item assessment : 'Comparison Basis Assessment';
        out item executionRequest : 'Analysis Execution Request';
    }

    action def <'F-05.2'> 'Determine Candidate Feasibility' {
        in item protocol : 'Comparison Protocol';
        in item results : 'Analysis Result Package';
        out item feasibility : 'Candidate Feasibility Assessment';
    }

    action def <'F-05.3'> 'Compare Candidate Architectures' {
        in item protocol : 'Comparison Protocol';
        in item results : 'Analysis Result Package';
        in item feasibility : 'Candidate Feasibility Assessment';
        out item comparison : 'Candidate Comparison Assessment';
    }

    action def <'F-05.4'> 'Issue Candidate Comparison' {
        in item basisAssessment : 'Comparison Basis Assessment';
        in item protocol : 'Comparison Protocol';
        in item results : 'Analysis Result Package';
        in item feasibility : 'Candidate Feasibility Assessment';
        in item comparison : 'Candidate Comparison Assessment';
        in item sensitivityAndUncertainty : 'Sensitivity and Uncertainty Assessment';
        out item comparisonPackage : 'Candidate Comparison Package';
    }

    action def <'F-05'> 'Compare Candidate EPS Architectures' {
        in item request : 'Candidate Comparison Request';
        in item protocol : 'Comparison Protocol';
        in item candidates : 'Candidate Model Package';
        in item returnedResults : 'Analysis Result Package';
        in item sensitivityAndUncertainty : 'Sensitivity and Uncertainty Assessment';
        out item executionRequest : 'Analysis Execution Request';
        out item result : 'Analysis Result Package';
        out item comparisonPackage : 'Candidate Comparison Package';

        action validateBasis : 'Validate Comparison Basis';
        action coordinateAnalysis : 'Coordinate Controlled Analysis';
        action determineFeasibility : 'Determine Candidate Feasibility';
        action compareCandidates : 'Compare Candidate Architectures';
        action issueComparison : 'Issue Candidate Comparison';

        bind validateBasis.request = request;
        bind validateBasis.protocol = protocol;
        bind validateBasis.candidates = candidates;
        flow validateBasis.executionRequest to coordinateAnalysis.preparedRequest;
        bind coordinateAnalysis.returnedResult = returnedResults;
        bind determineFeasibility.protocol = protocol;
        flow coordinateAnalysis.acceptedResult to determineFeasibility.results;
        bind compareCandidates.protocol = protocol;
        flow coordinateAnalysis.acceptedResult to compareCandidates.results;
        flow determineFeasibility.feasibility to compareCandidates.feasibility;
        flow validateBasis.assessment to issueComparison.basisAssessment;
        bind issueComparison.protocol = protocol;
        flow coordinateAnalysis.acceptedResult to issueComparison.results;
        flow determineFeasibility.feasibility to issueComparison.feasibility;
        flow compareCandidates.comparison to issueComparison.comparison;
        bind issueComparison.sensitivityAndUncertainty = sensitivityAndUncertainty;
        bind executionRequest = coordinateAnalysis.submittedRequest;
        bind result = coordinateAnalysis.acceptedResult;
        bind comparisonPackage = issueComparison.comparisonPackage;
    }

    action def <'F-06.1'> 'Assemble Review Package' {
        in item request : 'Design Review Request';
        in item modelRecords : 'Controlled Model Records';
        in item evidenceRecords : 'Retained Evidence Records';
        out item reviewPackage : 'Review Package';
        out item assessment : 'Review Package Assessment';
    }

    action def <'F-06.2'> 'Coordinate Selected Reproduction' {
        in item reviewPackage : 'Review Package';
        out item verdict : 'Reproduction Verdict';
    }

    action def <'F-06.3'> 'Manage Review Findings' {
        in item findings : 'Review Findings';
        in item disposition : 'Finding Disposition';
        in item reproduction : 'Reproduction Verdict';
        out item linkedFindings : 'Linked Finding Set';
    }

    action def <'F-06.4'> 'Issue Review Status' {
        in item packageAssessment : 'Review Package Assessment';
        in item linkedFindings : 'Linked Finding Set';
        in item outcome : 'Review Outcome';
        out item status : 'Review Status';
    }

    action def <'F-06'> 'Support Early Design Review' {
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

        action assemblePackage : 'Assemble Review Package';
        action coordinateReproduction : 'Coordinate Selected Reproduction';
        action manageFindings : 'Manage Review Findings';
        action issueStatus : 'Issue Review Status';

        bind assemblePackage.request = request;
        bind assemblePackage.modelRecords = modelRecords;
        bind assemblePackage.evidenceRecords = evidenceRecords;
        flow assemblePackage.reviewPackage to coordinateReproduction.reviewPackage;
        bind manageFindings.findings = findings;
        bind manageFindings.disposition = disposition;
        flow coordinateReproduction.verdict to manageFindings.reproduction;
        flow assemblePackage.assessment to issueStatus.packageAssessment;
        flow manageFindings.linkedFindings to issueStatus.linkedFindings;
        bind issueStatus.outcome = outcome;
        bind reviewPackage = assemblePackage.reviewPackage;
        bind issuedFindings = findings;
        bind reproduction = coordinateReproduction.verdict;
        bind status = issueStatus.status;
    }

    action def 'Provide Framework Black Box Services' {
        action maintainEvidenceChain : 'Maintain Evidence Chain';
        action configureFrameworkForCase : 'Configure Framework for EPS Case';
        action reproduceDesignatedAnalysis : 'Reproduce Designated Analysis';
        action assessControlledDesignChange : 'Assess Controlled Design Change';
        action compareCandidateArchitectures : 'Compare Candidate EPS Architectures';
        action supportEarlyDesignReview : 'Support Early Design Review';
    }
} // package FrameworkBlackBoxFunctions
