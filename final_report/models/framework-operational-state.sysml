// Black-box operational control derived from the six mission scenarios.
package FrameworkOperationalState {
    private import FrameworkExchangeDefinitions::*;
    private import FrameworkBlackBoxFunctions::*;

    doc
    /* This state machine specifies control for one selected EPS case and controlled work context.
     * Separate occurrences may control separate contexts. The model leaves the global request
     * queue and throughput unconstrained. A request event is accepted only after its boundary
     * transfer satisfies INT-07. A rejected transfer leaves the current state unchanged under INT-08.
     */

    state def <'SM-01'> 'Framework Operational Control' {
        doc
        /* The framework establishes a controlled case baseline before accepting evidence,
         * reproduction, change, comparison, or review work for that context. Each active service
         * state invokes the corresponding black-box function. Evidence work registers designated
         * external artifact revisions before chain validation. A successful typed outcome returns
         * the context to Controlled Baseline Ready. Every rejected, deficient, failed, incompatible,
         * or unresolved outcome enters Discrepancy Open. Recovery requires controlled revalidation.
         */

        transition initializeControl first start then Unconfigured;

        state <'ST-01'> Unconfigured {
            doc
            /* No accepted controlled case configuration and baseline are available for the selected
             * work context. Only a verified Case Configuration Request can begin useful work.
             */
        }

        state <'ST-02'> Configuring {
            doc
            /* F-02 captures and validates the selected case, common-core revision, environment,
             * adaptations, mappings, assumptions, and baseline. Any previously accepted baseline
             * remains immutable while the new configuration is assessed.
             */
            do action configureCase : 'Configure Framework for EPS Case';
        }

        state <'ST-03'> 'Controlled Baseline Ready' {
            doc
            /* A complete, compatible, and approved case configuration identifies an immutable
             * controlled baseline. Verified requests can dispatch the applicable service function.
             */
        }

        state <'ST-04'> 'Assessing Evidence' {
            doc
            /* F-01 registers externally produced requirement, model, and result revisions, then
             * scopes and validates one designated evidence chain and issues its assessment.
             */
            do action assessEvidence : 'Maintain Evidence Chain';
        }

        state <'ST-05'> 'Reproducing Analysis' {
            doc
            /* F-03 prepares, executes, compares, and issues the verdict for one designated analysis. */
            do action reproduceAnalysis : 'Reproduce Designated Analysis';
        }

        state <'ST-06'> 'Assessing Change' {
            doc
            /* F-04 validates one change request, determines its impact, coordinates affected
             * analyses, and validates regenerated evidence. The target baseline remains immutable.
             * A correct accepted outcome identifies a distinct successor baseline.
             */
            do action assessChange : 'Assess Controlled Design Change';
        }

        state <'ST-07'> 'Comparing Candidates' {
            doc
            /* F-05 validates a common basis, evaluates candidate EPS architectures, applies the
             * feasibility gate, and issues raw, Pareto, scoring, sensitivity, and uncertainty evidence.
             */
            do action compareCandidates : 'Compare Candidate EPS Architectures';
        }

        state <'ST-08'> 'Under Review' {
            doc
            /* F-06 assembles review evidence, supports selected reproduction, links findings and
             * dispositions, and publishes the reviewer-controlled outcome.
             */
            do action supportReview : 'Support Early Design Review';
        }

        state <'ST-09'> 'Discrepancy Open' {
            doc
            /* The latest service outcome is unavailable, incomplete, incompatible, failed,
             * out-of-tolerance, rejected, or unresolved. Its discrepancy and baseline remain visible.
             * The selected context cannot be represented as ready or successful.
             */
        }

        state <'ST-10'> Recovering {
            doc
            /* F-01 revalidates the corrected evidence chain against its named controlled baseline.
             * Recovery succeeds only when all required records are available and the chain is valid.
             */
            do action validateRecovery : 'Maintain Evidence Chain';
        }

        transition <'T-01'> beginConfiguration
            first Unconfigured
            accept configurationRequest : 'Case Configuration Request'
            then Configuring;

        transition <'T-02'> configurationAccepted
            first Configuring
            accept acceptedConfiguration : 'Configuration Status'
            if acceptedConfiguration.ready then 'Controlled Baseline Ready';

        transition <'T-03'> configurationDeficient
            first Configuring
            accept deficientConfiguration : 'Configuration Status'
            if not deficientConfiguration.ready then 'Discrepancy Open';

        transition <'T-04'> reconfigureContext
            first 'Controlled Baseline Ready'
            accept replacementConfiguration : 'Case Configuration Request'
            then Configuring;

        transition <'T-05'> assessEvidenceRequest
            first 'Controlled Baseline Ready'
            accept evidenceRequest : 'Evidence Chain Request'
            then 'Assessing Evidence';

        transition <'T-06'> reproduceAnalysisRequest
            first 'Controlled Baseline Ready'
            accept reproductionRequest : 'Reproduction Request'
            then 'Reproducing Analysis';

        transition <'T-07'> assessChangeRequest
            first 'Controlled Baseline Ready'
            accept changeRequest : 'Design Change Request'
            then 'Assessing Change';

        transition <'T-08'> compareCandidatesRequest
            first 'Controlled Baseline Ready'
            accept comparisonRequest : 'Candidate Comparison Request'
            then 'Comparing Candidates';

        transition <'T-09'> reviewRequest
            first 'Controlled Baseline Ready'
            accept designReviewRequest : 'Design Review Request'
            then 'Under Review';

        transition <'T-10'> evidenceAccepted
            first 'Assessing Evidence'
            accept validEvidence : 'Evidence Chain Assessment'
            if (
                validEvidence.recordsAvailable and
                validEvidence.externalArtifactsAccepted and
                validEvidence.chainValid
            )
                then 'Controlled Baseline Ready';

        transition <'T-11'> evidenceDeficient
            first 'Assessing Evidence'
            accept deficientEvidence : 'Evidence Chain Assessment'
            if (
                not deficientEvidence.recordsAvailable or
                not deficientEvidence.externalArtifactsAccepted or
                not deficientEvidence.chainValid
            )
                then 'Discrepancy Open';

        transition <'T-12'> reproductionAccepted
            first 'Reproducing Analysis'
            accept successfulReproduction : 'Reproduction Verdict'
            if successfulReproduction.successful then 'Controlled Baseline Ready';

        transition <'T-13'> reproductionDeficient
            first 'Reproducing Analysis'
            accept failedReproduction : 'Reproduction Verdict'
            if not failedReproduction.successful then 'Discrepancy Open';

        transition <'T-14'> changeAccepted
            first 'Assessing Change'
            accept correctChange : 'Change Evidence Package'
            if correctChange.correct then 'Controlled Baseline Ready';

        transition <'T-15'> changeDeficient
            first 'Assessing Change'
            accept incorrectChange : 'Change Evidence Package'
            if not incorrectChange.correct then 'Discrepancy Open';

        transition <'T-16'> comparisonAccepted
            first 'Comparing Candidates'
            accept completeComparison : 'Candidate Comparison Package'
            if completeComparison.complete then 'Controlled Baseline Ready';

        transition <'T-17'> comparisonDeficient
            first 'Comparing Candidates'
            accept incompleteComparison : 'Candidate Comparison Package'
            if not incompleteComparison.complete then 'Discrepancy Open';

        transition <'T-18'> reviewAccepted
            first 'Under Review'
            accept acceptedReview : 'Review Status'
            if (
                acceptedReview.packageComplete and
                acceptedReview.reviewOutcome.criticalFindingsResolved
            )
                then 'Controlled Baseline Ready';

        transition <'T-19'> reviewDeficient
            first 'Under Review'
            accept deficientReview : 'Review Status'
            if (
                not deficientReview.packageComplete or
                not deficientReview.reviewOutcome.criticalFindingsResolved
            )
                then 'Discrepancy Open';

        transition <'T-20'> beginControlledRecovery
            first 'Discrepancy Open'
            accept recoveryEvidenceRequest : 'Evidence Chain Request'
            then Recovering;

        transition <'T-21'> retryConfiguration
            first 'Discrepancy Open'
            accept correctedConfiguration : 'Case Configuration Request'
            then Configuring;

        transition <'T-22'> retryReproduction
            first 'Discrepancy Open'
            accept correctedReproduction : 'Reproduction Request'
            then 'Reproducing Analysis';

        transition <'T-23'> retryChange
            first 'Discrepancy Open'
            accept correctedChange : 'Design Change Request'
            then 'Assessing Change';

        transition <'T-24'> retryComparison
            first 'Discrepancy Open'
            accept correctedComparison : 'Candidate Comparison Request'
            then 'Comparing Candidates';

        transition <'T-25'> retryReview
            first 'Discrepancy Open'
            accept correctedReview : 'Design Review Request'
            then 'Under Review';

        transition <'T-26'> recoveryAccepted
            first Recovering
            accept validRecovery : 'Evidence Chain Assessment'
            if (
                validRecovery.recordsAvailable and
                validRecovery.externalArtifactsAccepted and
                validRecovery.chainValid
            )
                then 'Controlled Baseline Ready';

        transition <'T-27'> recoveryDeficient
            first Recovering
            accept deficientRecovery : 'Evidence Chain Assessment'
            if (
                not deficientRecovery.recordsAvailable or
                not deficientRecovery.externalArtifactsAccepted or
                not deficientRecovery.chainValid
            )
                then 'Discrepancy Open';
    }
} // package FrameworkOperationalState
